# IR Interpreter Flow Guide

## Overview

This guide explains `static/python/app/interpreter/ir_interpreter.py`.

This file executes optimized TAC directly. It is the runtime stage of the IR pipeline.

The core pieces are:

- `InterpreterError`
- `InputPauseSignal`
- `Frame`
- `TACInterpreter`
- `run_tac(...)`

---

## Role in the Pipeline

In `+page.svelte`, the interpreter is used like this:

```python
interpreter = TACInterpreter(optimized_tac)
exec_result = interpreter.run()
```

So the interpreter receives the final optimized TAC and turns it into:

- printed program output
- final global variable values
- success, pause, or error status

---

## Runtime Objects

### `Frame`

A `Frame` represents one variable scope.

It stores:

- `func_name`
- `vars`
- `parent`

Lookup behavior:

1. read from the current frame first
2. fall back to the parent frame if needed
3. raise `InterpreterError` if the name does not exist

This is how recipe-local variables stay separate while still allowing access to globals.

### `call_stack`

The interpreter stores saved caller state here during function calls.

Each saved entry contains:

- `pc`
- `frame`
- `result_var`

### `param_stack`

Arguments collected by `param` instructions are stored here until a `call` consumes them.

---

## Initialization Flow

`TACInterpreter.__init__(instructions, stdin_lines=None)` prepares the runtime before execution begins.

### Step 1: store inputs

It stores:

- the TAC instruction list
- captured output buffer
- optional pre-fed input lines

### Step 2: build jump maps

It scans all instructions once to build:

- `label_map`: label name to instruction index
- `func_map`: function name to `TACFunctionBegin` index

This gives constant-time jumps for control flow and function calls.

### Step 3: build function skip map

It also builds:

- `func_skip_map`

This map tells the interpreter where to resume after skipping a full function body.

That matters because during top-level execution:

- normal recipe bodies are skipped
- `start` is not skipped

### Step 4: initialize runtime state

It creates:

- `pc = 0`
- empty `call_stack`
- empty `param_stack`
- `global_frame`
- `current_frame = global_frame`

It also initializes output, exit-code, and input-tracking fields.

---

## Public Execution Flow

`run()` is the public entry point.

Its behavior is:

1. verify that `start` exists when execution begins at `pc == 0`
2. call `_execute()`
3. catch pause or error conditions
4. return a summary dictionary

### Success result

On success it returns fields such as:

- `success: True`
- `paused: False`
- `output`
- `exit_message`
- `stdin_consumed`
- `globals`

### Paused result

If `take()` needs more input, `InputPauseSignal` is caught and the result includes:

- `success: False`
- `paused: True`
- `error`
- partial `output`

### Error result

If execution fails, `run()` translates internal error wording into Platter-friendly terms and returns:

- `success: False`
- `paused: False`
- `error`
- `terminate_message`

---

## Main Loop

`_execute()` is the instruction-walking loop.

Its logic is:

```text
while pc < len(instructions)
   read current instruction
   if top-level and entering a non-start function:
       jump past its body
   else:
       advance pc
       dispatch instruction
```

The important rule is this:

- when the interpreter is still in the global frame, recipe bodies are skipped
- only `start` executes inline at top level
- other recipes execute only when called

That is the key to how a flat TAC list still behaves like a function-based program.

---

## Dispatch Flow

`_dispatch(instr)` is the runtime switchboard.

It checks the instruction class and executes the matching behavior.

### No-op style instructions

These produce no runtime effect:

- `TACComment`
- `TACNop`
- `TACFunctionBegin`
- `TACFunctionEnd`
- `TACLabel`

### Assignment and expressions

- `TACAssignment`: load the source, then store it
- `TACBinaryOp`: load both operands, evaluate operator, store result
- `TACUnaryOp`: load operand, evaluate, store result
- `TACCast`: cast the loaded value, then store it

### Allocation

- `TACAllocate(..., "array")` becomes a Python list of `None`
- `TACAllocate(..., "table")` becomes a Python dict

### Array and table access

- `TACArrayAccess` reads `arr[index]`
- `TACArrayAssign` writes `arr[index] = value`
- `TACTableAccess` reads `table[field]`
- `TACTableAssign` writes `table[field] = value`

### Function call protocol

`TACParam` pushes argument values into `param_stack`.

`TACFunctionCall` then:

1. slices the last `num_params` values from `param_stack`
2. checks whether the target is a built-in or user-defined function
3. executes the built-in directly or creates a new call frame
4. jumps into the called function body

For user-defined recipes:

- caller state is pushed to `call_stack`
- a child `Frame` is created with `global_frame` as parent
- arguments are bound to `p0`, `p1`, and so on
- `pc` jumps to one instruction after the target `TACFunctionBegin`

### Jumps

- `TACGoto` sets `pc` to the resolved label location
- `TACConditionalGoto` converts the condition to a boolean and jumps depending on `negated`

### Return

`TACReturn` has two cases:

1. if there is no caller on `call_stack`, this is the outermost return and execution ends
2. otherwise caller state is restored and the return value is written into the caller's result variable

---

## Built-in Function Flow

Built-ins are declared in `BUILTINS`.

Some are lambda-based, but many are handled explicitly in `_call_builtin(...)`.

### Type conversions

- `topiece`
- `tosip`
- `tochars`

### I/O

- `bill`
- `take`

`bill` appends processed text into `self.output_lines`.

`take` reads from `stdin_lines` if available. If not enough input exists, it raises `InputPauseSignal` so the web runtime can pause instead of blocking.

### Math and formatting

- `pow`
- `sqrt`
- `fact`
- `cut`

### Collection helpers

- `size`
- `sort`
- `reverse`
- `append`
- `remove`
- `search`
- `matches`

An important design detail is that array-style built-ins like `append`, `sort`, and `reverse` return new arrays rather than mutating the original one in place.

---

## Value Resolution and Storage

### `_load(name)`

This method resolves:

- `up` and `down`
- Python-style booleans that may appear after optimization
- integer literals
- float literals
- quoted string literals
- named variables from the current frame chain

### `_store(name, value)`

This method writes values into the current frame.

Before storing into non-temp variables, it validates numeric limits:

- `piece`: max 15 digits
- `sip`: max 15 non-fractional digits with 7 decimal places

Temp variables are excluded from this validation so large intermediate results can still exist during expression evaluation.

---

## Operator Evaluation

### `_eval_binary(...)`

Handles operators such as:

- arithmetic
- comparisons
- `and`
- `or`

Special rule:

- integer divided by integer uses truncated integer division for `piece/piece`

It also converts divide-by-zero into `InterpreterError("Division by zero")`.

### `_eval_unary(...)`

Handles:

- unary `-`
- logical `not`

### `_eval_cast(...)`

Casts values to:

- `piece`
- `sip`
- `chars`
- `flag`

---

## Platter-Friendly Output and Errors

The interpreter includes helper methods so runtime behavior stays aligned with Platter terms instead of raw Python terms.

Examples:

- `_platter_type(...)`
- `_platter_type_descriptor(...)`
- `_format_platter_value(...)`
- `_format_exit_code_display()`
- `_translate_error(...)`

These helpers are why returned values and runtime errors are displayed using terms like `piece`, `sip`, `flag`, and `chars`.

---

## Convenience Wrapper

The file ends with:

```python
run_tac(instructions, stdin_lines=None)
```

This helper simply constructs a `TACInterpreter` and returns `interpreter.run()`.

It is a small wrapper, but it gives the rest of the system a one-call way to execute optimized TAC.

---

## Mental Model

The easiest way to understand `ir_interpreter.py` is:

- the generator turns the AST into a flat TAC program
- the optimizer cleans that TAC
- the interpreter walks that TAC with a program counter, call stack, and frame chain

So this file is the runtime engine for the compiler pipeline.
