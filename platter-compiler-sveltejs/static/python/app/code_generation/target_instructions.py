"""
Target Instruction Set for Platter Virtual Machine

Defines a stack-based virtual machine instruction set for code generation.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class OpCode(Enum):
    """Virtual Machine Operation Codes"""
    
    # Stack Operations
    PUSH = "PUSH"           # Push value onto stack
    POP = "POP"             # Pop value from stack
    DUP = "DUP"             # Duplicate top of stack
    SWAP = "SWAP"           # Swap top two stack values
    
    # Memory Operations
    LOAD = "LOAD"           # Load from memory address
    STORE = "STORE"         # Store to memory address
    LOAD_LOCAL = "LOADL"    # Load local variable
    STORE_LOCAL = "STOREL"  # Store local variable
    LOAD_GLOBAL = "LOADG"   # Load global variable
    STORE_GLOBAL = "STOREG" # Store global variable
    
    # Arithmetic Operations
    ADD = "ADD"             # Addition
    SUB = "SUB"             # Subtraction
    MUL = "MUL"             # Multiplication
    DIV = "DIV"             # Division
    MOD = "MOD"             # Modulo
    NEG = "NEG"             # Negate (unary minus)
    
    # Comparison Operations
    EQ = "EQ"               # Equal
    NE = "NE"               # Not equal
    LT = "LT"               # Less than
    LE = "LE"               # Less than or equal
    GT = "GT"               # Greater than
    GE = "GE"               # Greater than or equal
    
    # Logical Operations
    AND = "AND"             # Logical AND
    OR = "OR"               # Logical OR
    NOT = "NOT"             # Logical NOT
    
    # Control Flow
    JUMP = "JUMP"           # Unconditional jump
    JUMP_IF_TRUE = "JT"     # Jump if true
    JUMP_IF_FALSE = "JF"    # Jump if false
    LABEL = "LABEL"         # Label (pseudo-instruction)
    
    # Function Operations
    CALL = "CALL"           # Call function
    RETURN = "RETURN"       # Return from function
    ENTER = "ENTER"         # Function prologue
    LEAVE = "LEAVE"         # Function epilogue
    
    # Array/Table Operations
    ARRAY_LOAD = "ALOAD"    # Load from array
    ARRAY_STORE = "ASTORE"  # Store to array
    TABLE_LOAD = "TLOAD"    # Load from table
    TABLE_STORE = "TSTORE"  # Store to table
    ALLOC_ARRAY = "ALLOCA"  # Allocate array
    ALLOC_TABLE = "ALLOCT"  # Allocate table
    
    # Type Conversion
    CAST_INT = "TOINT"      # Cast to piece (int)
    CAST_FLOAT = "TOFLOAT"  # Cast to sip (float)
    CAST_BOOL = "TOBOOL"    # Cast to flag (bool)
    CAST_STRING = "TOSTR"   # Cast to chars (string)
    
    # I/O Operations
    PRINT = "PRINT"         # Print value
    READ = "READ"           # Read input
    
    # Special
    HALT = "HALT"           # Halt execution
    NOP = "NOP"             # No operation
    COMMENT = "COMMENT"     # Comment (pseudo-instruction)


@dataclass
class TargetInstruction:
    """Represents a target machine instruction"""
    opcode: OpCode
    operand1: Optional[str] = None
    operand2: Optional[str] = None
    operand3: Optional[str] = None
    comment: Optional[str] = None
    
    def __str__(self) -> str:
        """Format instruction as string"""
        parts = [self.opcode.value]
        
        if self.operand1 is not None:
            parts.append(str(self.operand1))
        if self.operand2 is not None:
            parts.append(str(self.operand2))
        if self.operand3 is not None:
            parts.append(str(self.operand3))
        
        instr = " ".join(parts)
        
        if self.comment:
            instr = f"{instr:30} # {self.comment}"
        
        return instr
    
    def __repr__(self) -> str:
        return self.__str__()


class InstructionBuilder:
    """Helper class to build target instructions"""
    
    @staticmethod
    def push(value: str, comment: str = None) -> TargetInstruction:
        """Push constant onto stack"""
        return TargetInstruction(OpCode.PUSH, value, comment=comment)
    
    @staticmethod
    def pop(comment: str = None) -> TargetInstruction:
        """Pop value from stack"""
        return TargetInstruction(OpCode.POP, comment=comment)
    
    @staticmethod
    def load_var(var_name: str, scope: str = "local", comment: str = None) -> TargetInstruction:
        """Load variable value"""
        if scope == "global":
            return TargetInstruction(OpCode.LOAD_GLOBAL, var_name, comment=comment)
        return TargetInstruction(OpCode.LOAD_LOCAL, var_name, comment=comment)
    
    @staticmethod
    def store_var(var_name: str, scope: str = "local", comment: str = None) -> TargetInstruction:
        """Store to variable"""
        if scope == "global":
            return TargetInstruction(OpCode.STORE_GLOBAL, var_name, comment=comment)
        return TargetInstruction(OpCode.STORE_LOCAL, var_name, comment=comment)
    
    @staticmethod
    def binary_op(op: str, comment: str = None) -> TargetInstruction:
        """Generate binary operation"""
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '<=': OpCode.LE,
            '>': OpCode.GT,
            '>=': OpCode.GE,
            'and': OpCode.AND,
            'or': OpCode.OR,
        }
        opcode = op_map.get(op, OpCode.NOP)
        return TargetInstruction(opcode, comment=comment)
    
    @staticmethod
    def unary_op(op: str, comment: str = None) -> TargetInstruction:
        """Generate unary operation"""
        op_map = {
            '-': OpCode.NEG,
            'not': OpCode.NOT,
        }
        opcode = op_map.get(op, OpCode.NOP)
        return TargetInstruction(opcode, comment=comment)
    
    @staticmethod
    def jump(label: str, comment: str = None) -> TargetInstruction:
        """Unconditional jump"""
        return TargetInstruction(OpCode.JUMP, label, comment=comment)
    
    @staticmethod
    def jump_if_true(label: str, comment: str = None) -> TargetInstruction:
        """Jump if condition is true"""
        return TargetInstruction(OpCode.JUMP_IF_TRUE, label, comment=comment)
    
    @staticmethod
    def jump_if_false(label: str, comment: str = None) -> TargetInstruction:
        """Jump if condition is false"""
        return TargetInstruction(OpCode.JUMP_IF_FALSE, label, comment=comment)
    
    @staticmethod
    def label(name: str, comment: str = None) -> TargetInstruction:
        """Define a label"""
        return TargetInstruction(OpCode.LABEL, name, comment=comment)
    
    @staticmethod
    def call(func_name: str, num_args: int = 0, comment: str = None) -> TargetInstruction:
        """Call function"""
        return TargetInstruction(OpCode.CALL, func_name, str(num_args), comment=comment)
    
    @staticmethod
    def return_instr(has_value: bool = False, comment: str = None) -> TargetInstruction:
        """Return from function"""
        value = "1" if has_value else "0"
        return TargetInstruction(OpCode.RETURN, value, comment=comment)
    
    @staticmethod
    def enter(func_name: str, num_locals: int = 0, comment: str = None) -> TargetInstruction:
        """Function prologue"""
        return TargetInstruction(OpCode.ENTER, func_name, str(num_locals), comment=comment)
    
    @staticmethod
    def leave(comment: str = None) -> TargetInstruction:
        """Function epilogue"""
        return TargetInstruction(OpCode.LEAVE, comment=comment)
    
    @staticmethod
    def array_load(comment: str = None) -> TargetInstruction:
        """Load from array (array and index on stack)"""
        return TargetInstruction(OpCode.ARRAY_LOAD, comment=comment)
    
    @staticmethod
    def array_store(comment: str = None) -> TargetInstruction:
        """Store to array (array, index, value on stack)"""
        return TargetInstruction(OpCode.ARRAY_STORE, comment=comment)
    
    @staticmethod
    def cast(target_type: str, comment: str = None) -> TargetInstruction:
        """Type cast"""
        cast_map = {
            'piece': OpCode.CAST_INT,
            'sip': OpCode.CAST_FLOAT,
            'flag': OpCode.CAST_BOOL,
            'chars': OpCode.CAST_STRING,
        }
        opcode = cast_map.get(target_type, OpCode.NOP)
        return TargetInstruction(opcode, comment=comment)
    
    @staticmethod
    def comment(text: str) -> TargetInstruction:
        """Add comment"""
        return TargetInstruction(OpCode.COMMENT, text)
    
    @staticmethod
    def halt(comment: str = None) -> TargetInstruction:
        """Halt execution"""
        return TargetInstruction(OpCode.HALT, comment=comment)
    
    @staticmethod
    def nop(comment: str = None) -> TargetInstruction:
        """No operation"""
        return TargetInstruction(OpCode.NOP, comment=comment)


class CodeSection:
    """Represents a section of code"""
    
    def __init__(self, name: str = "main"):
        self.name = name
        self.instructions: List[TargetInstruction] = []
        self.labels: dict = {}  # label -> instruction_index
    
    def emit(self, instruction: TargetInstruction):
        """Emit an instruction"""
        self.instructions.append(instruction)
        
        # Track labels
        if instruction.opcode == OpCode.LABEL:
            self.labels[instruction.operand1] = len(self.instructions) - 1
    
    def get_address(self, label: str) -> Optional[int]:
        """Get instruction address for a label"""
        return self.labels.get(label)
    
    def __len__(self) -> int:
        return len(self.instructions)
    
    def __iter__(self):
        return iter(self.instructions)
    
    def __getitem__(self, index):
        return self.instructions[index]
