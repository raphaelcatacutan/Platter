"""
Virtual Machine Interpreter for Platter Compiler
Executes generated assembly code and manages runtime state
"""

from enum import Enum
from typing import List, Dict, Any, Optional
import re


class VMOpCode(Enum):
    """VM Operation Codes"""
    PUSH = "PUSH"
    POP = "POP"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    LOAD = "LOAD"
    STORE = "STORE"
    LOADL = "LOADL"
    STOREL = "STOREL"
    LABEL = "LABEL"
    JUMP = "JUMP"
    JUMPEQ = "JUMPEQ"
    JUMPNE = "JUMPNE"
    JUMPLT = "JUMPLT"
    JUMPLE = "JUMPLE"
    JUMPGT = "JUMPGT"
    JUMPGE = "JUMPGE"
    CALL = "CALL"
    RETURN = "RETURN"
    ENTER = "ENTER"
    LEAVE = "LEAVE"
    COMMENT = "COMMENT"
    HALT = "HALT"


class VirtualMachine:
    """Stack-based Virtual Machine for executing Platter assembly code"""

    def __init__(self, max_stack_size: int = 10000):
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.labels: Dict[str, int] = {}
        self.pc = 0  # Program counter
        self.instructions: List[tuple] = []
        self.halted = False
        self.output: List[str] = []
        self.max_stack_size = max_stack_size
        self.call_stack: List[int] = []
        self.local_vars: Dict[str, Any] = {}

    def parse_assembly(self, assembly_code: str) -> None:
        """Parse assembly code into instruction list"""
        lines = assembly_code.strip().split('\n')
        self.instructions = []
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse instruction
            parts = line.split()
            if not parts:
                continue
            
            opcode = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle labels
            if opcode == "LABEL":
                label_name = args[0] if args else f"label_{line_num}"
                self.labels[label_name] = len(self.instructions)
            
            self.instructions.append((opcode, args))

    def execute(self) -> str:
        """Execute the loaded instruction stream"""
        self.output = []
        self.pc = 0
        self.halted = False

        try:
            while self.pc < len(self.instructions) and not self.halted:
                opcode, args = self.instructions[self.pc]
                self._execute_instruction(opcode, args)
                self.pc += 1
        except Exception as e:
            self.output.append(f"⚠️  Runtime Error: {str(e)}")
            return self._format_output()

        return self._format_output()

    def _execute_instruction(self, opcode: str, args: List[str]) -> None:
        """Execute a single instruction"""
        
        if opcode == "PUSH":
            value = self._parse_value(args[0])
            self.stack.append(value)
        
        elif opcode == "POP":
            if self.stack:
                self.stack.pop()
        
        elif opcode == "ADD":
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            self.stack.append(a + b)
        
        elif opcode == "SUB":
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            self.stack.append(a - b)
        
        elif opcode == "MUL":
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            self.stack.append(a * b)
        
        elif opcode == "DIV":
            b = self.stack.pop() if self.stack else 1
            a = self.stack.pop() if self.stack else 0
            if b != 0:
                self.stack.append(a // b)
            else:
                raise RuntimeError("Division by zero")
        
        elif opcode == "MOD":
            b = self.stack.pop() if self.stack else 1
            a = self.stack.pop() if self.stack else 0
            if b != 0:
                self.stack.append(a % b)
            else:
                raise RuntimeError("Modulo by zero")
        
        elif opcode == "LOAD":
            var_name = args[0]
            value = self.variables.get(var_name, 0)
            self.stack.append(value)
        
        elif opcode == "STORE":
            var_name = args[0]
            value = self.stack.pop() if self.stack else 0
            self.variables[var_name] = value
        
        elif opcode == "LOADL":
            var_name = args[0]
            value = self.local_vars.get(var_name, 0)
            self.stack.append(value)
        
        elif opcode == "STOREL":
            var_name = args[0]
            value = self.stack.pop() if self.stack else 0
            self.local_vars[var_name] = value
        
        elif opcode == "LABEL":
            # Labels are handled during parsing
            pass
        
        elif opcode == "JUMP":
            label = args[0]
            if label in self.labels:
                self.pc = self.labels[label] - 1
        
        elif opcode == "JUMPEQ":
            label = args[0]
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            if a == b and label in self.labels:
                self.pc = self.labels[label] - 1
        
        elif opcode == "JUMPNE":
            label = args[0]
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            if a != b and label in self.labels:
                self.pc = self.labels[label] - 1
        
        elif opcode == "JUMPLT":
            label = args[0]
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            if a < b and label in self.labels:
                self.pc = self.labels[label] - 1
        
        elif opcode == "JUMPGT":
            label = args[0]
            b = self.stack.pop() if self.stack else 0
            a = self.stack.pop() if self.stack else 0
            if a > b and label in self.labels:
                self.pc = self.labels[label] - 1
        
        elif opcode == "RETURN":
            result = self.stack.pop() if self.stack else 0
            self.output.append(f"Return Value: {result}")
        
        elif opcode == "HALT":
            self.halted = True
        
        elif opcode == "COMMENT":
            # Skip comments
            pass
        
        elif opcode == "ENTER":
            # Function entry - clear local variables
            self.local_vars = {}
        
        elif opcode == "LEAVE":
            # Function exit - clear local variables
            self.local_vars = {}
        
        else:
            # Unknown opcode - skip
            pass

    def _parse_value(self, value_str: str) -> Any:
        """Parse a value (could be number, string, or variable)"""
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                # Could be a variable or string
                if value_str.startswith('"') and value_str.endswith('"'):
                    return value_str[1:-1]
                return value_str

    def _format_output(self) -> str:
        """Format execution output for display"""
        output_lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "🖥️  VIRTUAL MACHINE EXECUTION RESULTS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]
        
        if self.output:
            output_lines.extend(self.output)
        else:
            output_lines.append("Program executed successfully (no output)")
        
        output_lines.extend([
            "",
            "📊 FINAL STATE:",
            f"Variables: {self.variables if self.variables else 'None'}",
            f"Stack: {self.stack if self.stack else 'Empty'}",
            f"Status: {'✅ Halted' if self.halted else '⚠️  Running (no HALT)'}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ])
        
        return "\n".join(output_lines)


def run_assembly(assembly_code: str) -> str:
    """Convenience function to run assembly code"""
    vm = VirtualMachine()
    vm.parse_assembly(assembly_code)
    return vm.execute()
