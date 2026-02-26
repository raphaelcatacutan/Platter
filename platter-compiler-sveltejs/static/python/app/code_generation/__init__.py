"""
Code Generation Package for Platter Language

This package provides tools for generating executable target code
from the optimized intermediate representation (IR).

Modules:
- target_instructions: Target instruction set definitions
- memory_allocator: Memory and register allocation
- code_generator: Main code generator that converts IR to target code
- code_emitter: Emits executable code in various formats
"""

from .target_instructions import (
    OpCode,
    TargetInstruction,
    InstructionBuilder,
    CodeSection
)

from .memory_allocator import (
    MemoryAllocator,
    RegisterAllocator,
    Scope,
    Variable
)

from .code_generator import CodeGenerator
from .code_emitter import CodeEmitter, save_code

__all__ = [
    # Target Instructions
    'OpCode',
    'TargetInstruction',
    'InstructionBuilder',
    'CodeSection',
    
    # Memory Management
    'MemoryAllocator',
    'RegisterAllocator',
    'Scope',
    'Variable',
    
    # Code Generation
    'CodeGenerator',
    
    # Code Emission
    'CodeEmitter',
    'save_code',
]

__version__ = '1.0.0'

