"""
Constant Folding Optimization Pass

This optimization evaluates constant expressions at compile time.
Examples:
    t1 = 2 + 3    ->   t1 = 5
    t2 = 10 * 5   ->   t2 = 50
    t3 = 7 > 3    ->   t3 = true
"""

from typing import List, Optional, Union
from .optimizer import OptimizationPass
from app.intermediate_code.tac import *
from app.intermediate_code.quadruple import *


class ConstantFoldingPass(OptimizationPass):
    """Performs constant folding on TAC and Quadruples"""
    
    def __init__(self):
        super().__init__("Constant Folding")
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Optimize TAC instructions by folding constants"""
        self.reset_stats()
        optimized = []
        
        for instr in instructions:
            if isinstance(instr, TACBinaryOp):
                folded = self._fold_binary_op_tac(instr)
                if folded:
                    optimized.append(folded)
                    self.changes_made += 1
                else:
                    optimized.append(instr)
            elif isinstance(instr, TACUnaryOp):
                folded = self._fold_unary_op_tac(instr)
                if folded:
                    optimized.append(folded)
                    self.changes_made += 1
                else:
                    optimized.append(instr)
            else:
                optimized.append(instr)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Optimize quadruples by folding constants"""
        self.reset_stats()
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            if quad.operator in ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', 'and', 'or']:
                folded = self._fold_binary_op_quad(quad)
                if folded:
                    new_table.emit(folded.operator, folded.arg1, folded.arg2, folded.result)
                    self.changes_made += 1
                else:
                    new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            elif quad.operator in ['unary-', 'not']:
                folded = self._fold_unary_op_quad(quad)
                if folded:
                    new_table.emit(folded.operator, folded.arg1, folded.arg2, folded.result)
                    self.changes_made += 1
                else:
                    new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            else:
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
        
        return new_table
    
    def _fold_binary_op_tac(self, instr: TACBinaryOp) -> Optional[TACAssignment]:
        """Try to fold a binary operation"""
        val1 = self._parse_literal(instr.arg1)
        val2 = self._parse_literal(instr.arg2)
        
        if val1 is None or val2 is None:
            return None
        
        result = self._evaluate_binary(val1, instr.operator, val2)
        if result is not None:
            return TACAssignment(instr.result, str(result))
        
        return None
    
    def _fold_unary_op_tac(self, instr: TACUnaryOp) -> Optional[TACAssignment]:
        """Try to fold a unary operation"""
        val = self._parse_literal(instr.arg1)
        
        if val is None:
            return None
        
        result = self._evaluate_unary(instr.operator, val)
        if result is not None:
            return TACAssignment(instr.result, str(result))
        
        return None
    
    def _fold_binary_op_quad(self, quad: Quadruple) -> Optional[Quadruple]:
        """Try to fold a binary operation quadruple"""
        val1 = self._parse_literal(quad.arg1)
        val2 = self._parse_literal(quad.arg2)
        
        if val1 is None or val2 is None:
            return None
        
        result = self._evaluate_binary(val1, quad.operator, val2)
        if result is not None:
            return Quadruple('=', str(result), None, quad.result)
        
        return None
    
    def _fold_unary_op_quad(self, quad: Quadruple) -> Optional[Quadruple]:
        """Try to fold a unary operation quadruple"""
        val = self._parse_literal(quad.arg1)
        
        if val is None:
            return None
        
        result = self._evaluate_unary(quad.operator, val)
        if result is not None:
            return Quadruple('=', str(result), None, quad.result)
        
        return None
    
    def _parse_literal(self, value: str) -> Optional[Union[int, float, bool]]:
        """Parse a literal value from string"""
        if value is None:
            return None
        
        # If value contains a decimal point, always parse as float (sip)
        # This preserves type information for sip literals like "999999999999999.0"
        if '.' in value:
            try:
                return float(value)
            except ValueError:
                pass
        
        # Try int (must be before boolean check to avoid '1' → True, '0' → False)
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try boolean (only explicit string literals, not numeric strings)
        if value in ('true', 'True'):
            return True
        if value in ('false', 'False'):
            return False
        
        return None
    
    def _evaluate_binary(self, left: Union[int, float, bool], 
                        op: str, 
                        right: Union[int, float, bool]) -> Optional[Union[int, float, bool]]:
        """Evaluate binary operation"""
        try:
            result = None
            if op == '+':
                result = left + right
            elif op == '-':
                result = left - right
            elif op == '*':
                result = left * right
            elif op == '/':
                if right == 0:
                    return None  # Don't fold division by zero
                # Integer division for ints, float division for floats
                if isinstance(left, int) and isinstance(right, int):
                    result = left // right
                else:
                    result = left / right
            elif op == '%':
                if right == 0:
                    return None
                result = left % right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op == 'and':
                return bool(left) and bool(right)
            elif op == 'or':
                return bool(left) or bool(right)
            
            # Check for numeric overflow on arithmetic results
            if result is not None and op in ('+', '-', '*', '/', '%'):
                if self._check_overflow(result, left, right, op):
                    return None  # Don't fold if overflow detected
            
            return result
        except (TypeError, ZeroDivisionError, ValueError):
            return None
        
        return None
    
    def _check_overflow(self, result: Union[int, float], left: Union[int, float, bool], 
                       right: Union[int, float, bool], op: str) -> bool:
        """Check if result exceeds numeric limits. Returns True if overflow detected."""
        # piece: max 15 digits (±999,999,999,999,999)
        PIECE_MAX = 999_999_999_999_999
        # sip: max 15 non-fractional + 7 fractional digits
        # Due to floating-point precision issues, we check digit count instead of magnitude
        
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        left_is_float = isinstance(left, float)
        right_is_float = isinstance(right, float)
        
        # Both operands are integers → result should be piece
        if left_is_int and right_is_int and isinstance(result, int):
            if abs(result) > PIECE_MAX:
                return True  # Overflow detected
        # Either operand is float → result should be sip
        elif (left_is_float or right_is_float) and isinstance(result, float):
            # Check digit count for sip (15 non-fractional + 7 fractional digits)
            # Convert to string and count digits (handling scientific notation)
            result_str = f"{abs(result):.7f}"  # Format with 7 decimal places
            # Count non-fractional digits
            if '.' in result_str:
                integer_part = result_str.split('.')[0]
            else:
                integer_part = result_str
            non_fractional_digits = len(integer_part)
            
            if non_fractional_digits > 15:
                return True  # Overflow detected for sip
        # Integer division of piece/piece produces piece
        elif op == "/" and left_is_int and right_is_int and isinstance(result, int):
            if abs(result) > PIECE_MAX:
                return True  # Overflow detected
        
        return False  # No overflow
    
    def _evaluate_unary(self, op: str, value: Union[int, float, bool]) -> Optional[Union[int, float, bool]]:
        """Evaluate unary operation"""
        try:
            result = None
            if op in ('-', 'unary-'):
                result = -value
                # Check overflow for negation
                if isinstance(value, int) and not isinstance(value, bool):
                    if abs(result) > 999_999_999_999_999:
                        return None  # Overflow detected
                elif isinstance(value, float):
                    if abs(result) > 999_999_999_999_999.9999999:
                        return None  # Overflow detected
            elif op == 'not':
                result = not bool(value)
            
            return result
        except (TypeError, ValueError):
            return None
        
        return None
