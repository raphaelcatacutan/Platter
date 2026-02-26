"""
Register and Memory Allocator for Code Generation

Manages variable-to-memory mappings and provides a simple
register allocation strategy for the virtual machine.
"""

from typing import Dict, Set, Optional, List
from dataclasses import dataclass
from enum import Enum


class Scope(Enum):
    """Variable scope"""
    GLOBAL = "global"
    LOCAL = "local"
    PARAMETER = "parameter"
    TEMPORARY = "temporary"


@dataclass
class Variable:
    """Represents a variable in memory"""
    name: str
    scope: Scope
    address: int
    data_type: Optional[str] = None
    is_array: bool = False
    size: int = 1
    
    def __str__(self) -> str:
        scope_str = self.scope.value
        type_str = f":{self.data_type}" if self.data_type else ""
        array_str = f"[{self.size}]" if self.is_array else ""
        return f"{self.name}{type_str}{array_str} @{self.address} ({scope_str})"


class MemoryAllocator:
    """Manages memory allocation for variables"""
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.global_offset = 0
        self.local_offset = 0
        self.param_offset = 0
        self.temp_offset = 0
        
        # Scope stack for nested scopes
        self.scope_stack: List[Dict[str, Variable]] = [{}]
        self.current_function: Optional[str] = None
    
    def enter_scope(self):
        """Enter a new scope (e.g., function)"""
        self.scope_stack.append({})
        self.local_offset = 0
        self.param_offset = 0
        self.temp_offset = 0
    
    def exit_scope(self):
        """Exit current scope"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    
    def enter_function(self, func_name: str):
        """Enter function scope"""
        self.current_function = func_name
        self.enter_scope()
    
    def exit_function(self):
        """Exit function scope"""
        self.exit_scope()
        self.current_function = None
    
    def allocate_global(self, name: str, data_type: str = None, 
                       is_array: bool = False, size: int = 1) -> Variable:
        """Allocate a global variable"""
        if name in self.variables:
            return self.variables[name]
        
        var = Variable(
            name=name,
            scope=Scope.GLOBAL,
            address=self.global_offset,
            data_type=data_type,
            is_array=is_array,
            size=size
        )
        
        self.variables[name] = var
        self.global_offset += size
        
        return var
    
    def allocate_local(self, name: str, data_type: str = None,
                      is_array: bool = False, size: int = 1) -> Variable:
        """Allocate a local variable"""
        full_name = f"{self.current_function}.{name}" if self.current_function else name
        
        if full_name in self.scope_stack[-1]:
            return self.scope_stack[-1][full_name]
        
        var = Variable(
            name=name,
            scope=Scope.LOCAL,
            address=self.local_offset,
            data_type=data_type,
            is_array=is_array,
            size=size
        )
        
        self.scope_stack[-1][full_name] = var
        self.variables[full_name] = var
        self.local_offset += size
        
        return var
    
    def allocate_parameter(self, name: str, data_type: str = None) -> Variable:
        """Allocate a function parameter"""
        full_name = f"{self.current_function}.{name}" if self.current_function else name
        
        var = Variable(
            name=name,
            scope=Scope.PARAMETER,
            address=self.param_offset,
            data_type=data_type
        )
        
        self.scope_stack[-1][full_name] = var
        self.variables[full_name] = var
        self.param_offset += 1
        
        return var
    
    def allocate_temporary(self, temp_name: str) -> Variable:
        """Allocate a temporary variable"""
        full_name = f"{self.current_function}.{temp_name}" if self.current_function else temp_name
        
        if full_name in self.scope_stack[-1]:
            return self.scope_stack[-1][full_name]
        
        var = Variable(
            name=temp_name,
            scope=Scope.TEMPORARY,
            address=self.temp_offset,
            data_type="piece"  # Temporaries default to piece
        )
        
        self.scope_stack[-1][full_name] = var
        self.variables[full_name] = var
        self.temp_offset += 1
        
        return var
    
    def get_variable(self, name: str) -> Optional[Variable]:
        """Get variable by name (search scopes)"""
        # Try current function scope first
        if self.current_function:
            full_name = f"{self.current_function}.{name}"
            if full_name in self.variables:
                return self.variables[full_name]
        
        # Try current scope
        for scope_vars in reversed(self.scope_stack):
            if name in scope_vars:
                return scope_vars[name]
        
        # Try global scope
        if name in self.variables:
            return self.variables[name]
        
        # If it's a temporary or not found, allocate it
        if name.startswith('t'):
            return self.allocate_temporary(name)
        
        return None
    
    def get_or_allocate(self, name: str) -> Variable:
        """Get variable or allocate it if not found"""
        var = self.get_variable(name)
        if var is None:
            # Allocate as temporary or local
            if name.startswith('t'):
                var = self.allocate_temporary(name)
            else:
                var = self.allocate_local(name)
        return var
    
    def get_local_count(self) -> int:
        """Get count of local variables in current scope"""
        return self.local_offset + self.temp_offset
    
    def get_stats(self) -> Dict[str, int]:
        """Get allocation statistics"""
        return {
            'total_variables': len(self.variables),
            'global_variables': self.global_offset,
            'local_variables': self.local_offset,
            'parameters': self.param_offset,
            'temporaries': self.temp_offset
        }
    
    def print_allocation_table(self):
        """Print variable allocation table"""
        print("\n" + "="*70)
        print("VARIABLE ALLOCATION TABLE")
        print("="*70)
        
        print(
"\nGlobals:")
        for name, var in self.variables.items():
            if var.scope == Scope.GLOBAL:
                print(f"  {var}")
        
        print("\nLocals:")
        for name, var in self.variables.items():
            if var.scope in (Scope.LOCAL, Scope.PARAMETER, Scope.TEMPORARY):
                print(f"  {var}")
        
        stats = self.get_stats()
        print("\nStatistics:")
        print(f"  Total variables: {stats['total_variables']}")
        print(f"  Global variables: {stats['global_variables']}")
        print(f"  Local variables: {stats['local_variables']}")
        print(f"  Parameters: {stats['parameters']}")
        print(f"  Temporaries: {stats['temporaries']}")
        print("="*70 + "\n")


class RegisterAllocator:
    """
    Simple register allocator for virtual machine
    
    Uses a stack-based approach with virtual registers
    """
    
    def __init__(self, num_registers: int = 16):
        self.num_registers = num_registers
        self.register_map: Dict[str, int] = {}  # variable -> register
        self.free_registers: Set[int] = set(range(num_registers))
        self.spill_count = 0
    
    def allocate(self, var_name: str) -> Optional[int]:
        """Allocate a register for a variable"""
        if var_name in self.register_map:
            return self.register_map[var_name]
        
        if self.free_registers:
            reg = self.free_registers.pop()
            self.register_map[var_name] = reg
            return reg
        
        # Need to spill
        self.spill_count += 1
        return None
    
    def free(self, var_name: str):
        """Free register for a variable"""
        if var_name in self.register_map:
            reg = self.register_map[var_name]
            self.free_registers.add(reg)
            del self.register_map[var_name]
    
    def get_register(self, var_name: str) -> Optional[int]:
        """Get register number for variable"""
        return self.register_map.get(var_name)
    
    def reset(self):
        """Reset allocator"""
        self.register_map.clear()
        self.free_registers = set(range(self.num_registers))
        self.spill_count = 0
