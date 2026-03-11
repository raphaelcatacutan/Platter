"""
Scope Checking Pass for Platter Language
Validates symbol declarations, definitions, and usage
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import Symbol, SymbolKind
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes
from app.semantic_analyzer.builtin_recipes import is_builtin_recipe
from typing import Set


class ScopeChecker:
    """Performs scope checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
        self.used_symbols: Set[str] = set()
        # Track scope counters to match symbol table builder's naming
        self.scope_type_counters: dict[str, int] = {
            'check': 0, 'alt': 0, 'instead': 0,
            'pass': 0, 'repeat': 0, 'order_repeat': 0,
            'menu': 0, 'choice': 0, 'usual': 0,
            'block': 0
        }
    
    def check(self, ast_root: Program):
        """Run scope checking pass"""
        # First check for undeclared symbols found during symbol table building
        self._check_undeclared_symbols()
        
        # Check for undefined symbols in expressions
        for decl in ast_root.global_decl:
            if isinstance(decl, IngrDecl):
                self._check_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
        
        # Check function bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (navigate to its existing scope)
        if ast_root.start_platter:
            if self.symbol_table.navigate_to_scope("start_platter"):
                self._check_platter(ast_root.start_platter)
                self.symbol_table.exit_scope()
        
        # Check for unused ingredients (warnings)
        self._check_unused_symbols()
    
    def _check_undeclared_symbols(self):
        """Check for symbols that were used before being declared (forward references)"""
        for name, phantom_symbol in self.symbol_table.undeclared_symbols.items():
            if not phantom_symbol.accessed_in_scopes:
                continue
            
            # Check if this symbol exists in the symbol table by searching all scopes
            # If it does, it means it was used before declaration (forward reference)
            actual_symbol = self._find_symbol_in_any_scope(name)
            if actual_symbol:
                # Found a forward reference - symbol was used before declaration
                first_access_scope = phantom_symbol.accessed_in_scopes[0]
                self.error_handler.add_error(
                    f"Undefined ingredient '{name}' in '{first_access_scope}' (used before declaration)",
                    None,
                    ErrorCodes.UNDEFINED_SYMBOL
                )
    
    def _find_symbol_in_any_scope(self, name: str):
        """Search for a symbol in any scope (including child scopes)"""
        return self._search_scope_tree(self.symbol_table.global_scope, name)
    
    def _search_scope_tree(self, scope, name: str):
        """Recursively search scope tree for a symbol"""
        if name in scope.symbols:
            return scope.symbols[name]
        for child in scope.children:
            result = self._search_scope_tree(child, name)
            if result:
                return result
        return None
    
    def _check_var_decl(self, node: IngrDecl):
        """Check ingredient declaration"""
        # Check if type is defined
        if not self.symbol_table.is_type_defined(node.data_type):
            self.error_handler.add_error(
                f"Undefined type '{node.data_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_array_decl(self, node: ArrayDecl):
        """Check array declaration"""
        # Check if type is defined
        if not self.symbol_table.is_type_defined(node.data_type):
            self.error_handler.add_error(
                f"Undefined type '{node.data_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check dimensions
        if node.dimensions is not None and node.dimensions <= 0:
            self.error_handler.add_error(
                f"Array dimensions must be positive, got {node.dimensions}",
                node,
                ErrorCodes.INVALID_DIMENSION
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_table_decl(self, node: TableDecl):
        """Check table declaration"""
        # Check if table type is defined
        if not self.symbol_table.lookup_table_type(node.table_type):
            self.error_handler.add_error(
                f"Undefined table type '{node.table_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check dimensions if it's an array of tables
        if node.dimensions is not None and node.dimensions < 0:
            self.error_handler.add_error(
                f"Array dimensions must be positive, got {node.dimensions}",
                node,
                ErrorCodes.INVALID_DIMENSION
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check recipe declaration"""
        # Check serve type
        if not self.symbol_table.is_type_defined(node.return_type):
            self.error_handler.add_error(
                f"Undefined serve type '{node.return_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check spice types
        for spice in node.params:
            if not self.symbol_table.is_type_defined(spice.data_type):
                self.error_handler.add_error(
                    f"Undefined spice type '{spice.data_type}' in spice '{spice.identifier}'",
                    spice,
                    ErrorCodes.UNDEFINED_TYPE
                )
        
        # Check recipe body (navigate to existing recipe scope)
        if node.body:
            scope_name = node.name  # The builder removed 'recipe_' prefix
            if self.symbol_table.navigate_to_scope(scope_name):
                self._check_platter(node.body)
                self.symbol_table.exit_scope()
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        # Check local declarations
        for decl in node.local_decls:
            if isinstance(decl, IngrDecl):
                self._check_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
            else:
                self._check_statement(decl)
        
        # Check statements
        for stmt in node.statements:
            self._check_statement(stmt)
    
    def _navigate_and_check_scope(self, scope_type: str, check_func, *args):
        """Navigate into a scope, run a check function, then exit
        
        Args:
            scope_type: The type of scope ('check', 'pass', 'repeat', etc.)
            check_func: The function to call while in the scope
            *args: Arguments to pass to check_func
        """
        self.scope_type_counters[scope_type] += 1
        scope_name = f"{scope_type}_{self.scope_type_counters[scope_type]}"
        
        if self.symbol_table.navigate_to_scope(scope_name):
            check_func(*args)
            self.symbol_table.exit_scope()
        else:
            # Scope not found - this shouldn't happen if builder and checker are in sync
            # But check anyway without navigation
            check_func(*args)
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, Assignment):
            self._check_expression(node.target)
            self._check_expression(node.value)
        elif isinstance(node, ServeStatement):
            if node.value:
                self._check_expression(node.value)
        elif isinstance(node, CheckStatement):
            self._check_expression(node.condition)
            # Navigate into check scope for then_block
            self._navigate_and_check_scope('check', self._check_platter, node.then_block)
            # Navigate into alt scope for each elif_block
            for elif_cond, elif_block in node.elif_clauses:
                self._check_expression(elif_cond)
                self._navigate_and_check_scope('alt', self._check_platter, elif_block)
            # Navigate into instead scope for else_block
            if node.else_block:
                self._navigate_and_check_scope('instead', self._check_platter, node.else_block)
        elif isinstance(node, MenuStatement):
            self._check_expression(node.expr)
            for case in node.cases:
                self._check_expression(case.value)
                # Navigate into choice scope
                def check_choice_stmts():
                    for stmt in case.statements:
                        self._check_statement(stmt)
                self._navigate_and_check_scope('choice', check_choice_stmts)
            if node.default:
                # Navigate into usual scope
                def check_usual_stmts():
                    for stmt in node.default:
                        self._check_statement(stmt)
                self._navigate_and_check_scope('usual', check_usual_stmts)
        elif isinstance(node, RepeatLoop):
            self._check_expression(node.condition)
            # Navigate into repeat scope
            self._navigate_and_check_scope('repeat', self._check_platter, node.body)
        elif isinstance(node, OrderRepeatLoop):
            # Navigate into order_repeat scope
            def check_order_repeat():
                self._check_platter(node.body)
                self._check_expression(node.condition)
            self._navigate_and_check_scope('order_repeat', check_order_repeat)
        elif isinstance(node, PassLoop):
            # Navigate into pass scope
            def check_pass_loop():
                # Check init, condition, and update expressions (these are in pass scope)
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
                # Check loop body
                self._check_platter(node.body)
            self._navigate_and_check_scope('pass', check_pass_loop)
        elif isinstance(node, Platter):
            # Navigate into block scope
            self._navigate_and_check_scope('block', self._check_platter, node)
        elif isinstance(node, ExpressionStatement):
            self._check_expression(node.expr)
    
    def _check_expression(self, expr: ASTNode):
        """Check expression for undefined symbols"""
        if expr is None:
            return
        
        if isinstance(expr, Identifier):
            # Check if symbol is defined
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if not symbol:
                scope_name = self.symbol_table.current_scope.name
                self.error_handler.add_error(
                    f"Undefined ingredient '{expr.name}' in '{scope_name}'",
                    expr,
                    ErrorCodes.UNDEFINED_SYMBOL
                )
            else:
                # Mark symbol as used
                self.used_symbols.add(expr.name)
        
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
        
        elif isinstance(expr, RecipeCall):
            # Check if recipe is defined (including built-in recipes)
            if is_builtin_recipe(expr.name):
                # Built-in recipes are always available
                self.used_symbols.add(expr.name)
            else:
                recipe_symbol = self.symbol_table.lookup_symbol(expr.name)
                if not recipe_symbol:
                    scope_name = self.symbol_table.current_scope.name
                    self.error_handler.add_error(
                        f"Undefined recipe '{expr.name}' in '{scope_name}'",
                        expr,
                        ErrorCodes.UNDEFINED_RECIPE
                    )
                elif recipe_symbol.kind != SymbolKind.FUNCTION:
                    self.error_handler.add_error(
                        f"'{expr.name}' is not a recipe",
                        expr,
                        ErrorCodes.UNDEFINED_RECIPE
                    )
                else:
                    # Mark recipe as used
                    self.used_symbols.add(expr.name)
            
            # Check flavors (arguments)
            for arg in expr.args:
                self._check_expression(arg)
        
        elif isinstance(expr, CastExpr):
            # Check target type is defined
            if not self.symbol_table.is_type_defined(expr.target_type):
                self.error_handler.add_error(
                    f"Undefined type '{expr.target_type}' in cast",
                    expr,
                    ErrorCodes.UNDEFINED_TYPE
                )
            self._check_expression(expr.expr)
        
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._check_expression(elem)
        
        elif isinstance(expr, TableLiteral):
            for field_name, value, line, col in expr.field_inits:
                self._check_expression(value)
    
    def _check_unused_symbols(self):
        """Check for unused ingredients and issue warnings"""
        # Recursively check all scopes
        self._check_scope_for_unused(self.symbol_table.global_scope)
    
    def _check_scope_for_unused(self, scope):
        """Recursively check scope and children for unused symbols"""
        for name, symbol in scope.symbols.items():
            # Skip functions and table types
            if symbol.kind in [SymbolKind.FUNCTION, SymbolKind.TABLE_TYPE]:
                continue
            
            # Check if symbol was used
            if name not in self.used_symbols:
                self.error_handler.add_warning(
                    f"Unused ingredient '{name}'",
                    symbol.declaration_node,
                    ErrorCodes.UNUSED_INGREDIENT
                )
        
        # Check child scopes
        for child in scope.children:
            self._check_scope_for_unused(child)
