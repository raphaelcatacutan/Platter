"""
Code Generator for Platter Language

Converts optimized intermediate representation (TAC/Quadruples)
into executable target code for the Platter Virtual Machine.
"""

import sys
import os
from typing import List, Dict, Optional

# Add parent directories to path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)
sys.path.insert(0, app_dir)

from app.intermediate_code.tac import *
from app.intermediate_code.quadruple import Quadruple, QuadrupleTable
from .target_instructions import *
from .memory_allocator import MemoryAllocator, Scope


class CodeGenerator:
    """Generates target code from intermediate representation"""
    
    def __init__(self):
        self.code_section = CodeSection("main")
        self.memory_allocator = MemoryAllocator()
        self.label_map: Dict[str, str] = {}  # IR label -> target label
        self.function_map: Dict[str, int] = {}  # function -> address
        
    def generate_from_tac(self, instructions: List[TACInstruction]) -> CodeSection:
        """Generate target code from TAC instructions"""
        self.code_section = CodeSection("main")
        
        # Emit program header
        self.code_section.emit(InstructionBuilder.comment("=== Platter Program ==="))
        self.code_section.emit(InstructionBuilder.comment("Generated from TAC"))
        self.code_section.emit(InstructionBuilder.comment(""))
        
        # Process each TAC instruction
        for instr in instructions:
            self._generate_from_tac_instruction(instr)
        
        # Emit halt at end
        self.code_section.emit(InstructionBuilder.halt("End of program"))
        
        return self.code_section
    
    def _generate_from_tac_instruction(self, instr: TACInstruction):
        """Generate code for a single TAC instruction"""
        
        if isinstance(instr, TACComment):
            self.code_section.emit(InstructionBuilder.comment(instr.comment))
        
        elif isinstance(instr, TACAssignment):
            self._gen_assignment(instr)
        
        elif isinstance(instr, TACBinaryOp):
            self._gen_binary_op(instr)
        
        elif isinstance(instr, TACUnaryOp):
            self._gen_unary_op(instr)
        
        elif isinstance(instr, TACLabel):
            self.code_section.emit(InstructionBuilder.label(instr.name))
        
        elif isinstance(instr, TACGoto):
            self.code_section.emit(InstructionBuilder.jump(instr.target))
        
        elif isinstance(instr, TACConditionalGoto):
            self._gen_conditional_goto(instr)
        
        elif isinstance(instr, TACFunctionBegin):
            self._gen_function_begin(instr)
        
        elif isinstance(instr, TACFunctionEnd):
            self._gen_function_end(instr)
        
        elif isinstance(instr, TACParam):
            self._gen_param(instr)
        
        elif isinstance(instr, TACFunctionCall):
            self._gen_function_call(instr)
        
        elif isinstance(instr, TACReturn):
            self._gen_return(instr)
        
        elif isinstance(instr, TACArrayAccess):
            self._gen_array_access(instr)
        
        elif isinstance(instr, TACArrayAssign):
            self._gen_array_assign(instr)
        
        elif isinstance(instr, TACCast):
            self._gen_cast(instr)
        
        elif isinstance(instr, TACAllocate):
            self._gen_allocate(instr)
    
    def _gen_assignment(self, instr: TACAssignment):
        """Generate code for assignment: result = arg1"""
        # Load value
        if self._is_constant(instr.arg1):
            self.code_section.emit(InstructionBuilder.push(instr.arg1, f"{instr.result} = {instr.arg1}"))
        else:
            var = self.memory_allocator.get_or_allocate(instr.arg1)
            scope = "global" if var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg1, scope, f"{instr.result} = {instr.arg1}"))
        
        # Store to result
        result_var = self.memory_allocator.get_or_allocate(instr.result)
        result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope))
    
    def _gen_binary_op(self, instr: TACBinaryOp):
        """Generate code for binary operation: result = arg1 op arg2"""
        # Load arg1
        if self._is_constant(instr.arg1):
            self.code_section.emit(InstructionBuilder.push(instr.arg1))
        else:
            var1 = self.memory_allocator.get_or_allocate(instr.arg1)
            scope1 = "global" if var1.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg1, scope1))
        
        # Load arg2
        if self._is_constant(instr.arg2):
            self.code_section.emit(InstructionBuilder.push(instr.arg2))
        else:
            var2 = self.memory_allocator.get_or_allocate(instr.arg2)
            scope2 = "global" if var2.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg2, scope2))
        
        # Perform operation
        self.code_section.emit(InstructionBuilder.binary_op(instr.operator, f"{instr.result} = {instr.arg1} {instr.operator} {instr.arg2}"))
        
        # Store result
        result_var = self.memory_allocator.get_or_allocate(instr.result)
        result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope))
    
    def _gen_unary_op(self, instr: TACUnaryOp):
        """Generate code for unary operation: result = op arg1"""
        # Load arg
        if self._is_constant(instr.arg1):
            self.code_section.emit(InstructionBuilder.push(instr.arg1))
        else:
            var = self.memory_allocator.get_or_allocate(instr.arg1)
            scope = "global" if var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg1, scope))
        
        # Perform operation
        self.code_section.emit(InstructionBuilder.unary_op(instr.operator, f"{instr.result} = {instr.operator}{instr.arg1}"))
        
        # Store result
        result_var = self.memory_allocator.get_or_allocate(instr.result)
        result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope))
    
    def _gen_conditional_goto(self, instr: TACConditionalGoto):
        """Generate code for conditional goto"""
        # Load condition
        if self._is_constant(instr.condition):
            self.code_section.emit(InstructionBuilder.push(instr.condition))
        else:
            var = self.memory_allocator.get_or_allocate(instr.condition)
            scope = "global" if var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.condition, scope))
        
        # Jump based on condition
        if instr.jump_if_true:
            self.code_section.emit(InstructionBuilder.jump_if_true(instr.target, f"if {instr.condition} goto {instr.target}"))
        else:
            self.code_section.emit(InstructionBuilder.jump_if_false(instr.target, f"if not {instr.condition} goto {instr.target}"))
    
    def _gen_function_begin(self, instr: TACFunctionBegin):
        """Generate function prologue"""
        self.memory_allocator.enter_function(instr.func_name)
        
        # Emit function label
        self.code_section.emit(InstructionBuilder.label(f"func_{instr.func_name}", f"Function: {instr.func_name}"))
        
        # Will emit ENTER later when we know local count
        self.function_map[instr.func_name] = len(self.code_section)
    
    def _gen_function_end(self, instr: TACFunctionEnd):
        """Generate function epilogue"""
        # Get local variable count
        num_locals = self.memory_allocator.get_local_count()
        
        # Insert ENTER at function start
        if instr.func_name in self.function_map:
            func_start = self.function_map[instr.func_name]
            enter_instr = InstructionBuilder.enter(instr.func_name, num_locals, f"{num_locals} local variables")
            self.code_section.instructions.insert(func_start, enter_instr)
        
        # Emit LEAVE
        self.code_section.emit(InstructionBuilder.leave(f"End of {instr.func_name}"))
        
        self.memory_allocator.exit_function()
    
    def _gen_param(self, instr: TACParam):
        """Generate code for function parameter"""
        # Load parameter value
        if self._is_constant(instr.arg):
            self.code_section.emit(InstructionBuilder.push(instr.arg, f"param: {instr.arg}"))
        else:
            var = self.memory_allocator.get_or_allocate(instr.arg)
            scope = "global" if var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg, scope, f"param: {instr.arg}"))
    
    def _gen_function_call(self, instr: TACFunctionCall):
        """Generate function call"""
        # Call function (parameters already pushed)
        self.code_section.emit(InstructionBuilder.call(instr.function_name, instr.num_args, f"call {instr.function_name}"))
        
        # Store return value if needed
        if instr.result:
            result_var = self.memory_allocator.get_or_allocate(instr.result)
            result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope, f"store return value"))
    
    def _gen_return(self, instr: TACReturn):
        """Generate return statement"""
        if instr.value:
            # Load return value
            if self._is_constant(instr.value):
                self.code_section.emit(InstructionBuilder.push(instr.value))
            else:
                var = self.memory_allocator.get_or_allocate(instr.value)
                scope = "global" if var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(instr.value, scope))
            
            self.code_section.emit(InstructionBuilder.return_instr(True, f"return {instr.value}"))
        else:
            self.code_section.emit(InstructionBuilder.return_instr(False, "return"))
    
    def _gen_array_access(self, instr: TACArrayAccess):
        """Generate array access: result = array[index]"""
        # Load array base
        array_var = self.memory_allocator.get_or_allocate(instr.array)
        array_scope = "global" if array_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.load_var(instr.array, array_scope))
        
        # Load index
        if self._is_constant(instr.index):
            self.code_section.emit(InstructionBuilder.push(instr.index))
        else:
            index_var = self.memory_allocator.get_or_allocate(instr.index)
            index_scope = "global" if index_var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.index, index_scope))
        
        # Array load
        self.code_section.emit(InstructionBuilder.array_load(f"{instr.result} = {instr.array}[{instr.index}]"))
        
        # Store result
        result_var = self.memory_allocator.get_or_allocate(instr.result)
        result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope))
    
    def _gen_array_assign(self, instr: TACArrayAssign):
        """Generate array assignment: array[index] = value"""
        # Load array base
        array_var = self.memory_allocator.get_or_allocate(instr.array)
        array_scope = "global" if array_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.load_var(instr.array, array_scope))
        
        # Load index
        if self._is_constant(instr.index):
            self.code_section.emit(InstructionBuilder.push(instr.index))
        else:
            index_var = self.memory_allocator.get_or_allocate(instr.index)
            index_scope = "global" if index_var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.index, index_scope))
        
        # Load value
        if self._is_constant(instr.value):
            self.code_section.emit(InstructionBuilder.push(instr.value))
        else:
            value_var = self.memory_allocator.get_or_allocate(instr.value)
            value_scope = "global" if value_var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.value, value_scope))
        
        # Array store
        self.code_section.emit(InstructionBuilder.array_store(f"{instr.array}[{instr.index}] = {instr.value}"))
    
    def _gen_cast(self, instr: TACCast):
        """Generate type cast"""
        # Load value
        if self._is_constant(instr.arg):
            self.code_section.emit(InstructionBuilder.push(instr.arg))
        else:
            var = self.memory_allocator.get_or_allocate(instr.arg)
            scope = "global" if var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.load_var(instr.arg, scope))
        
        # Cast
        self.code_section.emit(InstructionBuilder.cast(instr.target_type, f"cast to {instr.target_type}"))
        
        # Store result
        result_var = self.memory_allocator.get_or_allocate(instr.result)
        result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
        self.code_section.emit(InstructionBuilder.store_var(instr.result, result_scope))
    
    def _gen_allocate(self, instr: TACAllocate):
        """Generate memory allocation"""
        # Allocate in memory manager
        is_array = (instr.alloc_type == "array")
        size = int(instr.size) if instr.size.isdigit() else 1
        self.memory_allocator.allocate_local(instr.result, is_array=is_array, size=size)
    
    def _is_constant(self, value: str) -> bool:
        """Check if value is a constant"""
        if value in ('true', 'false', 'True', 'False'):
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def generate_from_quads(self, quad_table: QuadrupleTable) -> CodeSection:
        """Generate target code from quadruples"""
        self.code_section = CodeSection("main")
        
        # Emit program header
        self.code_section.emit(InstructionBuilder.comment("=== Platter Program ==="))
        self.code_section.emit(InstructionBuilder.comment("Generated from Quadruples"))
        self.code_section.emit(InstructionBuilder.comment(""))
        
        # Process each quadruple
        for quad in quad_table.quadruples:
            self._generate_from_quad(quad)
        
        # Emit halt at end
        self.code_section.emit(InstructionBuilder.halt("End of program"))
        
        return self.code_section
    
    def _generate_from_quad(self, quad: Quadruple):
        """Generate code for a single quadruple"""
        op = quad.operator
        
        if op == '=':
            # Assignment
            if self._is_constant(quad.arg1):
                self.code_section.emit(InstructionBuilder.push(quad.arg1))
            else:
                var = self.memory_allocator.get_or_allocate(quad.arg1)
                scope = "global" if var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope))
            
            result_var = self.memory_allocator.get_or_allocate(quad.result)
            result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
            self.code_section.emit(InstructionBuilder.store_var(quad.result, result_scope))
        
        elif op in ['+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', 'and', 'or']:
            # Binary operation
            # Load arg1
            if self._is_constant(quad.arg1):
                self.code_section.emit(InstructionBuilder.push(quad.arg1))
            else:
                var1 = self.memory_allocator.get_or_allocate(quad.arg1)
                scope1 = "global" if var1.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope1))
            
            # Load arg2
            if self._is_constant(quad.arg2):
                self.code_section.emit(InstructionBuilder.push(quad.arg2))
            else:
                var2 = self.memory_allocator.get_or_allocate(quad.arg2)
                scope2 = "global" if var2.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg2, scope2))
            
            # Operation
            self.code_section.emit(InstructionBuilder.binary_op(op))
            
            # Store result
            if quad.result:
                result_var = self.memory_allocator.get_or_allocate(quad.result)
                result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.store_var(quad.result, result_scope))
        
        elif op in ['unary-', 'not']:
            # Unary operation
            if self._is_constant(quad.arg1):
                self.code_section.emit(InstructionBuilder.push(quad.arg1))
            else:
                var = self.memory_allocator.get_or_allocate(quad.arg1)
                scope = "global" if var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope))
            
            op_clean = '-' if op == 'unary-' else op
            self.code_section.emit(InstructionBuilder.unary_op(op_clean))
            
            if quad.result:
                result_var = self.memory_allocator.get_or_allocate(quad.result)
                result_scope = "global" if result_var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.store_var(quad.result, result_scope))
        
        elif op == 'goto':
            self.code_section.emit(InstructionBuilder.jump(quad.result))
        
        elif op == 'if':
            if self._is_constant(quad.arg1):
                self.code_section.emit(InstructionBuilder.push(quad.arg1))
            else:
                var = self.memory_allocator.get_or_allocate(quad.arg1)
                scope = "global" if var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope))
            
            self.code_section.emit(InstructionBuilder.jump_if_true(quad.result))
        
        elif op == 'ifFalse':
            if self._is_constant(quad.arg1):
                self.code_section.emit(InstructionBuilder.push(quad.arg1))
            else:
                var = self.memory_allocator.get_or_allocate(quad.arg1)
                scope = "global" if var.scope == Scope.GLOBAL else "local"
                self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope))
            
            self.code_section.emit(InstructionBuilder.jump_if_false(quad.result))
        
        elif op == 'label':
            self.code_section.emit(InstructionBuilder.label(quad.result))
        
        elif op == 'return':
            if quad.arg1:
                if self._is_constant(quad.arg1):
                    self.code_section.emit(InstructionBuilder.push(quad.arg1))
                else:
                    var = self.memory_allocator.get_or_allocate(quad.arg1)
                    scope = "global" if var.scope == Scope.GLOBAL else "local"
                    self.code_section.emit(InstructionBuilder.load_var(quad.arg1, scope))
                self.code_section.emit(InstructionBuilder.return_instr(True))
            else:
                self.code_section.emit(InstructionBuilder.return_instr(False))
