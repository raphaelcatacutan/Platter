"""
Function Checking Pass for Platter Language
Validates function calls, parameter matching, and return types
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import TypeInfo, Symbol, SymbolKind
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes
from typing import Optional, List


class FunctionChecker:
    """Performs function call checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
    
    def check(self, ast_root: Program):
        """Run function checking pass"""
        # Check global declarations
        for decl in ast_root.global_decl:
            if isinstance(decl, VarDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, ArrayDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, TableDecl) and decl.init_value:
                self._check_expression(decl.init_value)
        
        # Check function bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (navigate to its existing scope)
        if ast_root.start_platter:
            if self.symbol_table.navigate_to_scope("start_platter_1"):
                self._check_platter(ast_root.start_platter)
                self.symbol_table.exit_scope()
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check function declaration"""
        # Check function body (navigate to existing function scope)
        if node.body:
            scope_name = node.name  # The builder removed 'recipe_' prefix
            if self.symbol_table.navigate_to_scope(scope_name):
                self._check_platter(node.body)
                self.symbol_table.exit_scope()
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        # Check local declarations
        for decl in node.local_decls:
            if isinstance(decl, VarDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, ArrayDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, TableDecl) and decl.init_value:
                self._check_expression(decl.init_value)
        
        # Check statements
        for stmt in node.statements:
            self._check_statement(stmt)
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, Assignment):
            self._check_expression(node.target)
            self._check_expression(node.value)
        elif isinstance(node, ReturnStatement):
            if node.value:
                self._check_expression(node.value)
        elif isinstance(node, IfStatement):
            self._check_expression(node.condition)
            self._check_platter(node.then_block)
            for elif_cond, elif_block in node.elif_clauses:
                self._check_expression(elif_cond)
                self._check_platter(elif_block)
            if node.else_block:
                self._check_platter(node.else_block)
        elif isinstance(node, SwitchStatement):
            self._check_expression(node.expr)
            for case in node.cases:
                for value in case.values:
                    self._check_expression(value)
                for stmt in case.statements:
                    self._check_statement(stmt)
            if node.default:
                for stmt in node.default:
                    self._check_statement(stmt)
        elif isinstance(node, WhileLoop):
            self._check_expression(node.condition)
            self._check_platter(node.body)
        elif isinstance(node, DoWhileLoop):
            self._check_platter(node.body)
            self._check_expression(node.condition)
        elif isinstance(node, ForLoop):
            if node.init:
                if isinstance(node.init, Assignment):
                    self._check_expression(node.init.target)
                    self._check_expression(node.init.value)
            if node.condition:
                self._check_expression(node.condition)
            if node.update:
                if isinstance(node.update, Assignment):
                    self._check_expression(node.update.target)
                    self._check_expression(node.update.value)
            self._check_platter(node.body)
        elif isinstance(node, Platter):
            self._check_platter(node)
        elif isinstance(node, ExpressionStatement):
            self._check_expression(node.expr)
    
    def _check_expression(self, expr: ASTNode):
        """Check expression for function calls"""
        if expr is None:
            return
        
        if isinstance(expr, FunctionCall):
            self._check_function_call(expr)
        elif isinstance(expr, BinaryOp):
            self._check_expression(expr.left)
            self._check_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._check_expression(expr.operand)
        elif isinstance(expr, ArrayAccess):
            self._check_expression(expr.array)
            self._check_expression(expr.index)
        elif isinstance(expr, TableAccess):
            self._check_expression(expr.table)
        elif isinstance(expr, CastExpr):
            self._check_expression(expr.expr)
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._check_expression(elem)
        elif isinstance(expr, TableLiteral):
            for field_name, value in expr.field_inits:
                self._check_expression(value)
    
    def _check_function_call(self, node: FunctionCall):
        """Check function call arguments"""
        # Look up function symbol
        func_symbol = self.symbol_table.lookup_symbol(node.name)
        if not func_symbol:
            # Error already reported by scope_checker
            return
        
        if func_symbol.kind != SymbolKind.FUNCTION:
            # Error already reported by scope_checker
            return
        
        # Get function parameters
        params = self._get_function_parameters(node.name)
        if params is None:
            # Could not determine parameters
            return
        
        # Check argument count
        if len(node.args) != len(params):
            self.error_handler.add_error(
                f"Function '{node.name}' expects {len(params)} argument(s), got {len(node.args)}",
                node,
                ErrorCodes.ARGUMENT_COUNT_MISMATCH
            )
            return
        
        # Check argument types
        for i, (arg, param) in enumerate(zip(node.args, params)):
            arg_type = self._get_expression_type(arg)
            param_type = param.type_info
            
            if arg_type and not param_type.is_compatible_with(arg_type):
                self.error_handler.add_error(
                    f"Argument {i+1} of function '{node.name}': "
                    f"expected {param_type}, got {arg_type}",
                    arg,
                    ErrorCodes.ARGUMENT_TYPE_MISMATCH
                )
        
        # Recursively check arguments
        for arg in node.args:
            self._check_expression(arg)
    
    def _get_function_parameters(self, func_name: str) -> Optional[List[Symbol]]:
        """Get function parameters from the AST or symbol table"""
        # Look up the function symbol
        func_symbol = self.symbol_table.lookup_symbol(func_name)
        if not func_symbol or func_symbol.kind != SymbolKind.FUNCTION:
            return None
        
        # Find the function's scope (recipe scope)
        func_scope = None
        for child in self.symbol_table.global_scope.children:
            if child.name == func_name:
                func_scope = child
                break
        
        if not func_scope:
            return None
        
        # Get parameters (symbols with kind PARAMETER)
        params = []
        for name, symbol in func_scope.symbols.items():
            if symbol.kind == SymbolKind.PARAMETER:
                params.append(symbol)
        
        return params
    
    def _get_expression_type(self, expr: ASTNode) -> Optional[TypeInfo]:
        """Get the type of an expression (simplified version)"""
        if expr is None:
            return None
        
        if isinstance(expr, Literal):
            return TypeInfo(expr.value_type, 0)
        
        elif isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:
                return symbol.type_info
            return None
        
        elif isinstance(expr, BinaryOp):
            left_type = self._get_expression_type(expr.left)
            if expr.operator in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
                return TypeInfo("flag", 0)
            return left_type
        
        elif isinstance(expr, UnaryOp):
            if expr.operator == '!':
                return TypeInfo("flag", 0)
            return self._get_expression_type(expr.operand)
        
        elif isinstance(expr, ArrayAccess):
            array_type = self._get_expression_type(expr.array)
            if array_type and array_type.dimensions > 0:
                return array_type.get_element_type()
            return None
        
        elif isinstance(expr, TableAccess):
            table_type = self._get_expression_type(expr.table)
            if table_type and table_type.is_table:
                return table_type.get_field_type(expr.field)
            return None
        
        elif isinstance(expr, FunctionCall):
            func_symbol = self.symbol_table.lookup_symbol(expr.name)
            if func_symbol:
                return func_symbol.type_info
            return None
        
        elif isinstance(expr, CastExpr):
            dims = expr.dimensions if expr.dimensions is not None else 0
            return TypeInfo(expr.target_type, dims)
        
        elif isinstance(expr, ArrayLiteral):
            if expr.elements:
                first_type = self._get_expression_type(expr.elements[0])
                if first_type:
                    return TypeInfo(first_type.base_type, first_type.dimensions + 1, 
                                  first_type.table_fields if first_type.is_table else None)
            return None
        
        elif isinstance(expr, TableLiteral):
            # Build field types from literal
            field_types = {}
            for field_name, value in expr.field_inits:
                field_type = self._get_expression_type(value)
                if field_type:
                    field_types[field_name] = field_type
            return TypeInfo("anonymous_table", 0, field_types)
        
        return None
