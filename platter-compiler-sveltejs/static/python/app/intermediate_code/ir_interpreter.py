"""
TAC Interpreter for Platter Language

Executes optimized Three Address Code (TAC) instructions directly in Python.
No assembly or machine code generation needed — runs the IR as a tree-walking
interpreter over the flat TAC instruction list.
"""

from typing import List, Dict, Any, Optional
from .tac import (
    TACInstruction, TACAssignment, TACBinaryOp, TACUnaryOp,
    TACArrayAccess, TACArrayAssign, TACTableAccess, TACTableAssign,
    TACLabel, TACGoto, TACConditionalGoto, TACFunctionCall, TACParam,
    TACReturn, TACFunctionBegin, TACFunctionEnd, TACComment, TACAllocate,
    TACCast, TACNop
)


class InterpreterError(Exception):
    pass


class ReturnSignal(Exception):
    """Used to unwind the call stack on return."""
    def __init__(self, value=None):
        self.value = value


class InputPauseSignal(Exception):
    """Raised when take() needs more user input than currently provided."""
    def __init__(self, message: str):
        self.message = message


class Frame:
    """A single call-stack frame with its own variable store."""
    def __init__(self, func_name: str, parent: "Frame | None" = None):
        self.func_name = func_name
        self.vars: Dict[str, Any] = {}
        self.parent = parent  # access global frame for globals

    def get(self, name: str) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise InterpreterError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any):
        self.vars[name] = value


class TACInterpreter:
    """
    Interprets a flat list of optimized TAC instructions.

    Execution model:
    - A program counter (pc) walks through instructions sequentially.
    - Labels are pre-indexed for O(1) jumps.
    - Functions are stored as {name: start_pc} tables.
    - A call stack of Frame objects handles variable scoping.
    - A param_stack accumulates arguments before CALL.
    - Built-in functions (topiece, tosip, tochars, bill, take, pow, sqrt, rand, size, etc.) are handled natively.
    """

    # ── Built-in functions ─────────────────────────────────────────────────────
    # Keys must match the exact token/function names used in Platter source code.
    # Semantics follow the Platter Documentation specification exactly.
    BUILTINS: Dict[str, Any] = {
        # Type conversions
        "topiece": lambda args: int(float(args[0])) if args else 0,
        "tosip":   lambda args: float(args[0]) if args else 0.0,
        "tochars": lambda args: str(args[0]) if args else "",

        # Math, Formatting, Random
        "pow":     lambda args: args[0] ** args[1],                        # pow(base, exp) → piece
        "sqrt":    lambda args: round(args[0] ** 0.5, 7),                  # sqrt(piece) → sip, 7 fractional digits
        "fact":    None,  # handled in _call_builtin (factorial)
        "cut":     None,  # handled in _call_builtin (numeric formatting)
        "rand":    lambda args: round(__import__('random').random(), 7),    # rand() → sip 0.0000000–0.9999999, no args

        # String operation
        "copy":    None,  # handled in _call_builtin (chars slicing)

        # Collection ops — all serve NEW arrays, never mutate originals
        "size":    lambda args: len(args[0]) if args else 0,               # size(array) → piece
        "sort":    lambda args: sorted(args[0]),                           # sort(array) → new sorted array
        "reverse": lambda args: list(reversed(args[0])),                   # reverse(array) → new reversed array
        "append":  lambda args: args[0] + [args[1]],                       # append(array, val) → new array with val added
        "remove":  None,  # handled in _call_builtin (remove by index)
        "search":  None,  # handled in _call_builtin (return first matching index)
        "matches": None,  # handled in _call_builtin (deep equality → flag)

        # I/O — bill = print/output, take = input (handled specially in _call_builtin)
        "bill":    None,
        "take":    None,
    }

    def __init__(self, instructions: List[TACInstruction],
                 stdin_lines: Optional[List[str]] = None):
        """
        Args:
            instructions: Optimized TAC instruction list from IRGenerator.
            stdin_lines:  Optional list of strings fed to scan() calls instead
                          of blocking on real stdin (useful for web/Pyodide).
        """
        self.instructions = instructions
        self.output_lines: List[str] = []          # captured stdout
        self.stdin_lines = list(stdin_lines or [])  # pre-fed input
        self._stdin_idx = 0

        # Pre-process: build label→pc and function→pc maps
        self.label_map: Dict[str, int] = {}        # label_name → instruction index
        self.func_map: Dict[str, int] = {}         # func_name  → instruction index of FUNC_BEGIN

        for i, instr in enumerate(self.instructions):
            if isinstance(instr, TACLabel):
                self.label_map[instr.label] = i
            elif isinstance(instr, TACFunctionBegin):
                self.func_map[instr.func_name] = i

        # Build FUNC_BEGIN → FUNC_END skip map so we can jump over recipe bodies
        self.func_skip_map: Dict[int, int] = {}  # pc of FUNC_BEGIN → pc after FUNC_END
        depth = 0
        begin_pc = -1
        for i, instr in enumerate(self.instructions):
            if isinstance(instr, TACFunctionBegin):
                depth += 1
                if depth == 1:
                    begin_pc = i
            elif isinstance(instr, TACFunctionEnd):
                depth -= 1
                if depth == 0 and begin_pc >= 0:
                    self.func_skip_map[begin_pc] = i + 1  # resume after FUNC_END
                    begin_pc = -1

        # Runtime state
        self.pc: int = 0
        self.call_stack: List[Dict] = []   # saved frames for call/return
        self.param_stack: List[Any] = []   # params pushed before a CALL
        self.global_frame = Frame("__global__")
        self.current_frame: Frame = self.global_frame

    # ── Public entry point ─────────────────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        """
        Execute the program starting from pc=0.
        Global inits run first, then recipe bodies are skipped until 'start' is reached
        and executed inline.  Recipe calls go through _call_function as normal.
        Returns a summary dict with output, final global vars, and status.
        """
        if "start" not in self.func_map:
            raise InterpreterError("No 'start' function found in IR.")

        self.pc = 0
        return self._run_from_current_pc()

    def resume(self, additional_stdin: List[str]) -> Dict[str, Any]:
        """
        Resume execution from where it paused after adding more stdin input.
        
        Args:
            additional_stdin: New input lines to append to stdin buffer
            
        Returns:
            Same dict format as run()
        """
        print(f"[RESUME] Called with additional_stdin: {additional_stdin}")
        print(f"[RESUME] Current PC: {self.pc}")
        print(f"[RESUME] Current stdin_lines before extend: {self.stdin_lines}")
        print(f"[RESUME] Current _stdin_idx: {self._stdin_idx}")
        
        # Add new stdin lines to the buffer
        self.stdin_lines.extend(additional_stdin)
        print(f"[RESUME] stdin_lines after extend: {self.stdin_lines}")
        
        # Continue execution from current pc (don't reset to 0!)
        print(f"[RESUME] Calling _run_from_current_pc() from PC {self.pc}")
        return self._run_from_current_pc()

    def _run_from_current_pc(self) -> Dict[str, Any]:
        """Common execution logic used by both run() and resume()."""
        print(f"[_run_from_current_pc] Starting execution from PC: {self.pc}")
        print(f"[_run_from_current_pc] Total instructions: {len(self.instructions)}")
        try:
            self._execute()
            print(f"[_run_from_current_pc] Execution completed normally")
        except ReturnSignal:
            print(f"[_run_from_current_pc] Caught ReturnSignal")
            pass
        except InputPauseSignal as p:
            print(f"[_run_from_current_pc] Caught InputPauseSignal - execution paused")
            print(f"[_run_from_current_pc] Current PC when paused: {self.pc}")
            # CRITICAL FIX: PC was incremented before the instruction that raised InputPauseSignal
            # We need to decrement it so that when we resume, we re-execute the same instruction
            self.pc -= 1
            print(f"[_run_from_current_pc] Decremented PC to {self.pc} for resume")
            print(f"[_run_from_current_pc] stdin_consumed: {self._stdin_idx}")
            return {
                "success": False,
                "paused": True,
                "error": "",  # No error message needed - just waiting for input
                "output": "".join(self.output_lines),
                "stdin_consumed": self._stdin_idx,
                "globals": {k: v for k, v in self.global_frame.vars.items()
                            if not k.startswith("t")},
            }
        except InterpreterError as e:
            return {
                "success": False,
                "paused": False,
                "error": str(e),
                "output": "".join(self.output_lines),
                "stdin_consumed": self._stdin_idx,
            }

        return {
            "success": True,
            "paused": False,
            "output": "".join(self.output_lines),
            "stdin_consumed": self._stdin_idx,
            "globals": {k: v for k, v in self.global_frame.vars.items()
                        if not k.startswith("t")},  # hide temps
        }

    # ── Main execution loop ────────────────────────────────────────────────────

    def _execute(self):
        print(f"[_execute] Starting loop, PC={self.pc}, total instructions={len(self.instructions)}")
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            print(f"[_execute] PC={self.pc}: {type(instr).__name__} - {instr}")

            # When scanning the top-level (we are in the global frame), skip over
            # recipe bodies — they will be executed only when called via _call_function.
            # The 'start' body is NOT skipped; it executes inline.
            if (isinstance(instr, TACFunctionBegin)
                    and self.current_frame is self.global_frame
                    and instr.func_name != "start"):
                skip_to = self.func_skip_map.get(self.pc)
                if skip_to is not None:
                    print(f"[_execute] Skipping function {instr.func_name}, jumping to PC={skip_to}")
                    self.pc = skip_to
                    continue

            self.pc += 1
            print(f"[_execute] Dispatching instruction, PC now={self.pc}")
            self._dispatch(instr)
        print(f"[_execute] Loop ended, PC={self.pc}")

    def _dispatch(self, instr: TACInstruction):
        t = type(instr)
        print(f"[_dispatch] Called with type: {t.__name__}, instruction: {instr}")
        print(f"[_dispatch] Type comparison - TACFunctionCall check: {t is TACFunctionCall}")

        if t is TACComment or t is TACNop or t is TACFunctionBegin or t is TACFunctionEnd:
            print(f"[_dispatch] No-op instruction, returning")
            return  # no-ops

        elif t is TACLabel:
            print(f"[_dispatch] Label instruction, returning")
            return  # labels are markers, not actions

        elif t is TACAssignment:
            print(f"[_dispatch] TACAssignment")
            self._store(instr.result, self._load(instr.arg1))

        elif t is TACBinaryOp:
            left  = self._load(instr.arg1)
            right = self._load(instr.arg2)
            self._store(instr.result, self._eval_binary(instr.operator, left, right))

        elif t is TACUnaryOp:
            val = self._load(instr.arg1)
            self._store(instr.result, self._eval_unary(instr.operator, val))

        elif t is TACCast:
            val = self._load(instr.arg)
            self._store(instr.result, self._eval_cast(instr.target_type, val))

        elif t is TACAllocate:
            if instr.alloc_type == "array":
                size = int(self._load(instr.size))
                self._store(instr.result, [None] * size)
            else:  # table
                self._store(instr.result, {})

        elif t is TACArrayAccess:
            arr   = self._load(instr.array)
            index = int(self._load(instr.index))
            if not isinstance(arr, list):
                raise InterpreterError(f"'{instr.array}' is not an array")
            self._store(instr.result, arr[index])

        elif t is TACArrayAssign:
            arr   = self._load(instr.array)
            index = int(self._load(instr.index))
            val   = self._load(instr.value)
            if not isinstance(arr, list):
                raise InterpreterError(f"'{instr.array}' is not an array")
            arr[index] = val

        elif t is TACTableAccess:
            tbl = self._load(instr.table)
            if not isinstance(tbl, dict):
                raise InterpreterError(f"'{instr.table}' is not a table")
            self._store(instr.result, tbl.get(instr.field))

        elif t is TACTableAssign:
            tbl = self._load(instr.table)
            val = self._load(instr.value)
            if not isinstance(tbl, dict):
                raise InterpreterError(f"'{instr.table}' is not a table")
            tbl[instr.field] = val

        elif t is TACParam:
            val = self._load(instr.arg)
            print(f"[_dispatch] TACParam: pushing {val} onto param_stack")
            self.param_stack.append(val)

        elif t is TACFunctionCall:
            print(f"[_dispatch] TACFunctionCall: {instr.func_name}, num_params={instr.num_params}, param_stack={self.param_stack}")
            args = self.param_stack[-instr.num_params:] if instr.num_params else []
            self.param_stack = self.param_stack[:-instr.num_params] if instr.num_params else self.param_stack
            print(f"[_dispatch] Calling function '{instr.func_name}' with args: {args}")
            result = self._call_function(instr.func_name, args)
            print(f"[_dispatch] Function '{instr.func_name}' returned: {result}")
            if instr.result:
                self._store(instr.result, result)

        elif t is TACGoto:
            self.pc = self._resolve_label(instr.label)

        elif t is TACConditionalGoto:
            cond = self._load(instr.condition)
            cond_bool = self._to_bool(cond)
            jump = (not cond_bool) if instr.negated else cond_bool
            if jump:
                self.pc = self._resolve_label(instr.label)

        elif t is TACReturn:
            val = self._load(instr.value) if instr.value else None
            raise ReturnSignal(val)

        else:
            pass  # unknown instruction — skip silently

    # ── Function call / return ─────────────────────────────────────────────────

    def _call_function(self, name: str, args: List[Any]) -> Any:
        print(f"[_call_function] Called: {name}, args={args}, is_builtin={name in self.BUILTINS}")
        # Built-in functions
        if name in self.BUILTINS:
            return self._call_builtin(name, args)

        if name not in self.func_map:
            raise InterpreterError(f"Undefined function '{name}'")

        # Save caller state
        saved = {
            "pc": self.pc,
            "frame": self.current_frame,
        }
        self.call_stack.append(saved)

        # New frame — child of global so recipes can't see start's locals
        new_frame = Frame(name, parent=self.global_frame)
        # Bind parameters by position as p0, p1, ...
        for i, val in enumerate(args):
            new_frame.set(f"p{i}", val)
        self.current_frame = new_frame

        # Jump to function body (one past FUNC_BEGIN)
        self.pc = self.func_map[name] + 1

        return_value = None
        try:
            self._execute()
        except ReturnSignal as r:
            return_value = r.value

        # Restore caller state
        saved = self.call_stack.pop()
        self.pc = saved["pc"]
        self.current_frame = saved["frame"]

        return return_value

    def _process_string_literal(self, text: str) -> str:
        """Process escape sequences and remove quotes from string literals."""
        # If text is a quoted string literal, remove quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Process escape sequences
        text = text.replace('\\n', '\n')   # \n -> newline
        text = text.replace('\\t', '\t')   # \t -> tab
        text = text.replace('\\\\', '\\')  # \\ -> backslash
        text = text.replace('\\"', '"')   # \" -> quote
        
        return text

    def _call_builtin(self, name: str, args: List[Any]) -> Any:
        print(f"[_call_builtin] Calling: {name}, args={args}")
        fn = self.BUILTINS[name]

        # ── I/O ──────────────────────────────────────────────────────────
        if name == "bill":
            # bill(chars_value) → outputs text, serves ""
            text = str(args[0]) if args else ""
            # Process escape sequences and remove quotes
            text = self._process_string_literal(text)
            print(f"[bill()] Appending to output: '{text}', current output_lines length: {len(self.output_lines)}")
            self.output_lines.append(text)
            # Also print to console in real-time so user sees output as it happens
            print(text, end='')
            print(f"[bill()] New output_lines length: {len(self.output_lines)}")
            return ""

        elif name == "take":
            # take() → no flavors, awaits input, serves chars
            print(f"[take()] Called - stdin_idx: {self._stdin_idx}, stdin_lines: {self.stdin_lines}")
            if self._stdin_idx < len(self.stdin_lines):
                val = self.stdin_lines[self._stdin_idx]
                self._stdin_idx += 1
                print(f"[take()] Returning value: '{val}', new stdin_idx: {self._stdin_idx}")
                return val
            else:
                # Get input from user via JavaScript prompt
                print(f"[take()] Requesting input from user via prompt")
                import js
                user_input = js.prompt("Enter input:")
                if user_input is None or user_input == "":
                    user_input = ""
                user_input = str(user_input)
                print(f"[take()] User entered: '{user_input}'")
                # Add to stdin_lines for potential future take() calls
                self.stdin_lines.append(user_input)
                self._stdin_idx += 1
                return user_input

        # ── Math/Formatting ──────────────────────────────────────────────
        elif name == "fact":
            # fact(non-negative piece) → piece (factorial)
            n = int(args[0])
            if n < 0:
                raise InterpreterError("fact() requires a non-negative piece value")
            result = 1
            for i in range(2, n + 1):
                result *= i
            return result

        elif name == "cut":
            # cut(sip_value, format_sip) → chars
            # format X.Y : X = digits before decimal, Y = digits after
            value = float(args[0])
            fmt = float(args[1])
            before = int(fmt)
            after  = int(round((fmt - before) * 10))
            neg = value < 0
            abs_val = abs(value)
            int_part = int(abs_val)
            frac_part = abs_val - int_part
            int_str = str(int_part).zfill(before)
            frac_str = f"{frac_part:.{after}f}"[2:]  # strip "0."
            result = f"{int_str}.{frac_str}" if after > 0 else int_str
            if neg:
                result = "-" + result
            return result

        elif name == "copy":
            # copy(chars, start_pos, end_pos) → chars (1-based inclusive)
            text = str(args[0])
            start = int(args[1])
            end = int(args[2])
            if start < 1 or end < 1 or start > len(text) or end > len(text):
                return ""
            return text[start - 1:end]

        # ── Collection ops ───────────────────────────────────────────────
        elif name == "remove":
            # remove(array, index) → new array with element at index removed
            arr = list(args[0])   # copy
            idx = int(args[1])
            if idx < 0 or idx >= len(arr):
                raise InterpreterError(f"remove() index {idx} out of range")
            arr.pop(idx)
            return arr

        elif name == "search":
            # search(array, value) → piece (first matching index, or -1)
            arr = args[0]
            val = args[1]
            for i, elem in enumerate(arr):
                if elem == val:
                    return i
            return -1

        elif name == "matches":
            # matches(array|table, array|table) → flag (up/down as bool)
            return args[0] == args[1]

        # ── Generic lambda-based builtins ────────────────────────────────
        else:
            if fn is None:
                raise InterpreterError(f"Built-in '{name}' has no implementation")
            return fn(args)

    # ── Variable load / store ──────────────────────────────────────────────────

    def _load(self, name: str) -> Any:
        """Resolve a name or literal to a Python value."""
        if name is None:
            return None
        # Check for empty variable names (TAC generation bug)
        if isinstance(name, str) and name.strip() == "":
            raise InterpreterError("TAC instruction references an empty variable name (TAC generation error)")
        # Platter boolean literals: up = true, down = false
        if name == "up":
            return True
        if name == "down":
            return False
        # Also accept Python-style booleans from IR (generated by optimizer)
        if name in ("true", "True"):
            return True
        if name in ("false", "False"):
            return False
        # Numeric literals
        try:
            return int(name)
        except (ValueError, TypeError):
            pass
        try:
            return float(name)
        except (ValueError, TypeError):
            pass
        # String literals  "hello"
        if isinstance(name, str) and name.startswith('"') and name.endswith('"'):
            return name[1:-1]
        if isinstance(name, str) and name.startswith("'") and name.endswith("'"):
            return name[1:-1]
        # Variable lookup
        return self.current_frame.get(name)

    def _store(self, name: str, value: Any):
        self.current_frame.set(name, value)

    # ── Operator evaluation ────────────────────────────────────────────────────

    def _eval_binary(self, op: str, left: Any, right: Any) -> Any:
        ops = {
            "+":   lambda a, b: a + b,
            "-":   lambda a, b: a - b,
            "*":   lambda a, b: a * b,
            "/":   lambda a, b: a / b,
            "%":   lambda a, b: a % b,
            "==":  lambda a, b: a == b,
            "!=":  lambda a, b: a != b,
            ">":   lambda a, b: a > b,
            "<":   lambda a, b: a < b,
            ">=":  lambda a, b: a >= b,
            "<=":  lambda a, b: a <= b,
            "and": lambda a, b: a and b,
            "or":  lambda a, b: a or b,
        }
        if op not in ops:
            raise InterpreterError(f"Unknown binary operator '{op}'")
        try:
            return ops[op](left, right)
        except ZeroDivisionError:
            raise InterpreterError("Division by zero")

    def _eval_unary(self, op: str, val: Any) -> Any:
        if op == "-":
            return -val
        if op in ("not", "!"):
            return not self._to_bool(val)
        raise InterpreterError(f"Unknown unary operator '{op}'")

    def _eval_cast(self, target_type: str, val: Any) -> Any:
        casts = {
            "piece": lambda v: int(float(v)),
            "sip":   lambda v: float(v),
            "chars": lambda v: str(v),
            "flag":  lambda v: bool(v),
        }
        if target_type not in casts:
            raise InterpreterError(f"Unknown cast type '{target_type}'")
        return casts[target_type](val)

    def _to_bool(self, val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            # Platter: "down" = false, "up" = true
            return val.lower() not in ("down", "false", "0", "")
        return bool(val)

    def _resolve_label(self, label: str) -> int:
        if label not in self.label_map:
            raise InterpreterError(f"Undefined label '{label}'")
        return self.label_map[label]


# ── Convenience function ───────────────────────────────────────────────────────

def run_tac(instructions: List[TACInstruction],
            stdin_lines: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run optimized TAC instructions and return execution result.

    Args:
        instructions: Optimized TAC from OptimizerManager.optimize_tac()
        stdin_lines:  Optional pre-fed input lines for scan() calls.

    Returns:
        {
            "success": bool,
            "output":  str,          # captured print output
            "globals": dict,         # final values of named variables
            "error":   str | None,   # error message if not success
        }
    """
    interpreter = TACInterpreter(instructions, stdin_lines=stdin_lines)
    return interpreter.run()
