"""
Control Flow Checking Pass for Platter Language
Validates control flow statements (break, continue, return)
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes


class ControlFlowChecker:
    """Performs control flow checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
        self.in_loop = 0
        self.in_function = False
        self.current_function_has_return = False
    
    def check(self, ast_root: Program):
        """Run control flow checking pass"""
        # Check function bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (treat as a function)
        if ast_root.start_platter:
            old_in_function = self.in_function
            self.in_function = True
            self._check_platter(ast_root.start_platter)
            self.in_function = old_in_function
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check function declaration"""
        old_in_function = self.in_function
        old_has_return = self.current_function_has_return
        
        self.in_function = True
        self.current_function_has_return = False
        
        # Check function body
        if node.body:
            self._check_platter(node.body)
        
        # Check if non-void function has return statement
        if node.return_type != "void" and not self.current_function_has_return:
            self.error_handler.add_warning(
                f"Function '{node.name}' may not return a value in all code paths",
                node,
                ErrorCodes.MISSING_RETURN
            )
        
        self.in_function = old_in_function
        self.current_function_has_return = old_has_return
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        for stmt in node.statements:
            self._check_statement(stmt)
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, BreakStatement):
            self._check_break_statement(node)
        elif isinstance(node, ContinueStatement):
            self._check_continue_statement(node)
        elif isinstance(node, ReturnStatement):
            self._check_return_statement(node)
        elif isinstance(node, IfStatement):
            self._check_if_statement(node)
        elif isinstance(node, SwitchStatement):
            self._check_switch_statement(node)
        elif isinstance(node, WhileLoop):
            self._check_while_loop(node)
        elif isinstance(node, DoWhileLoop):
            self._check_do_while_loop(node)
        elif isinstance(node, ForLoop):
            self._check_for_loop(node)
        elif isinstance(node, Platter):
            self._check_platter(node)
    
    def _check_break_statement(self, node: BreakStatement):
        """Check break statement is inside a loop or switch"""
        if self.in_loop == 0:
            self.error_handler.add_error(
                "break statement outside of loop",
                node,
                ErrorCodes.BREAK_OUTSIDE_LOOP
            )
    
    def _check_continue_statement(self, node: ContinueStatement):
        """Check continue statement is inside a loop"""
        if self.in_loop == 0:
            self.error_handler.add_error(
                "continue statement outside of loop",
                node,
                ErrorCodes.CONTINUE_OUTSIDE_LOOP
            )
    
    def _check_return_statement(self, node: ReturnStatement):
        """Check return statement is inside a function"""
        if not self.in_function:
            self.error_handler.add_error(
                "return statement outside of function",
                node,
                ErrorCodes.RETURN_OUTSIDE_FUNCTION
            )
        else:
            self.current_function_has_return = True
    
    def _check_if_statement(self, node: IfStatement):
        """Check if statement"""
        # Track if all branches return
        then_returns = self._block_has_return(node.then_block)
        
        elif_returns = []
        for _, elif_block in node.elif_clauses:
            elif_returns.append(self._block_has_return(elif_block))
        
        else_returns = False
        if node.else_block:
            else_returns = self._block_has_return(node.else_block)
        
        # If all branches return, mark function as having return
        if then_returns and (not node.elif_clauses or all(elif_returns)) and else_returns:
            self.current_function_has_return = True
        
        # Check branches
        self._check_platter(node.then_block)
        for _, elif_block in node.elif_clauses:
            self._check_platter(elif_block)
        if node.else_block:
            self._check_platter(node.else_block)
    
    def _check_switch_statement(self, node: SwitchStatement):
        """Check switch statement"""
        # Allow break in switch
        self.in_loop += 1
        
        # Check cases
        for case in node.cases:
            for stmt in case.statements:
                self._check_statement(stmt)
        
        # Check default case
        if node.default:
            for stmt in node.default:
                self._check_statement(stmt)
        
        self.in_loop -= 1
    
    def _check_while_loop(self, node: WhileLoop):
        """Check while loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _check_do_while_loop(self, node: DoWhileLoop):
        """Check do-while loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _check_for_loop(self, node: ForLoop):
        """Check for loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _block_has_return(self, block: Platter) -> bool:
        """Check if a block definitely has a return statement"""
        for stmt in block.statements:
            if isinstance(stmt, ReturnStatement):
                return True
            elif isinstance(stmt, IfStatement):
                # Check if all branches return
                then_returns = self._block_has_return(stmt.then_block)
                
                elif_returns = []
                for _, elif_block in stmt.elif_clauses:
                    elif_returns.append(self._block_has_return(elif_block))
                
                else_returns = False
                if stmt.else_block:
                    else_returns = self._block_has_return(stmt.else_block)
                
                if then_returns and (not stmt.elif_clauses or all(elif_returns)) and else_returns:
                    return True
        
        return False
