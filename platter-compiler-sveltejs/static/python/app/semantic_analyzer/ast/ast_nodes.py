# Complete AST Nodes for Platter Language

# Base node
class ASTNode:
    def __init__(self, node_type="ASTNode"): 
        self.node_type = node_type
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

# ============================================================================
# Program Structure
# ============================================================================

class Program(ASTNode):
    """Root node of the AST"""
    def __init__(self): 
        super().__init__("Program")
        self.global_decl = []  # List of declaration nodes
        self.recipe_decl = []  # List of RecipeDecl nodes
        self.start_platter = None  # Platter node
    
    def add_global_decl(self, node): 
        if node:
            self.global_decl.append(node)
        
    def add_recipe_decl(self, node): 
        if node:
            self.recipe_decl.append(node)

    def set_start_platter(self, node): 
        self.start_platter = node
    
    def __repr__(self):
        return f"Program(global_decl={len(self.global_decl)}, recipe_decl={len(self.recipe_decl)}, start_platter={'Yes' if self.start_platter else 'No'})"

# ============================================================================
# Declarations
# ============================================================================

class VarDecl(ASTNode):
    """Variable declaration (ingredient/scalar)"""
    def __init__(self, data_type, identifier, init_value=None):
        super().__init__("VarDecl")
        self.data_type = data_type  # "piece", "sip", "flag", "chars"
        self.identifier = identifier  # String
        self.init_value = init_value  # Expression node or None
    
    def __repr__(self):
        return f"VarDecl({self.data_type} {self.identifier}, init={'Yes' if self.init_value else 'No'})"

class ArrayDecl(ASTNode):
    """Array declaration"""
    def __init__(self, data_type, dimensions, identifier, init_value=None):
        super().__init__("ArrayDecl")
        self.data_type = data_type
        self.dimensions = dimensions  # int: number of dimensions
        self.identifier = identifier
        self.init_value = init_value  # ArrayLiteral or Expression
    
    def __repr__(self):
        return f"ArrayDecl({self.data_type}[{self.dimensions}] {self.identifier})"

class TablePrototype(ASTNode):
    """Table type definition"""
    def __init__(self, name, fields):
        super().__init__("TablePrototype")
        self.name = name
        self.fields = fields  # List of FieldDecl nodes
    
    def __repr__(self):
        return f"TablePrototype({self.name}, {len(self.fields)} fields)"

class FieldDecl(ASTNode):
    """Field in a table prototype"""
    def __init__(self, data_type, dimensions, identifier):
        super().__init__("FieldDecl")
        self.data_type = data_type  # "piece", "sip", "flag", "chars", or table name
        self.dimensions = dimensions  # int
        self.identifier = identifier
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"FieldDecl({self.data_type}{dims} {self.identifier})"

class TableDecl(ASTNode):
    """Table instance declaration"""
    def __init__(self, table_type, identifier, init_value=None, dimensions=0):
        super().__init__("TableDecl")
        self.table_type = table_type  # String: name of table type
        self.identifier = identifier
        self.init_value = init_value  # TableLiteral or None
        self.dimensions = dimensions
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"TableDecl({self.table_type}{dims} {self.identifier})"

class RecipeDecl(ASTNode):
    """Function/recipe declaration"""
    def __init__(self, return_type, return_dims, name, params, body):
        super().__init__("RecipeDecl")
        self.return_type = return_type
        self.return_dims = return_dims  # int
        self.name = name
        self.params = params  # List of ParamDecl nodes
        self.body = body  # Platter node
    
    def __repr__(self):
        dims = f"[{self.return_dims}]" if self.return_dims > 0 else ""
        return f"RecipeDecl({self.return_type}{dims} {self.name}({len(self.params)} params))"

class ParamDecl(ASTNode):
    """Function parameter"""
    def __init__(self, data_type, dimensions, identifier):
        super().__init__("ParamDecl")
        self.data_type = data_type
        self.dimensions = dimensions
        self.identifier = identifier
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"ParamDecl({self.data_type}{dims} {self.identifier})"

# ============================================================================
# Statements
# ============================================================================

class Platter(ASTNode):
    """Block/compound statement"""
    def __init__(self, local_decls=None, statements=None):
        super().__init__("Platter")
        self.local_decls = local_decls or []
        self.statements = statements or []
    
    def add_local_decl(self, node):
        if node:
            self.local_decls.append(node)
    
    def add_statement(self, node):
        if node:
            self.statements.append(node)
    
    def __repr__(self):
        return f"Platter(decls={len(self.local_decls)}, stmts={len(self.statements)})"

class Assignment(ASTNode):
    """Assignment statement"""
    def __init__(self, target, operator, value):
        super().__init__("Assignment")
        self.target = target  # Identifier or accessor node
        self.operator = operator  # "=", "+=", "-=", "*=", "/=", "%="
        self.value = value  # Expression node
    
    def __repr__(self):
        return f"Assignment({self.operator})"

class IfStatement(ASTNode):
    """Conditional statement (check/alt/instead)"""
    def __init__(self, condition, then_block, elif_clauses=None, else_block=None):
        super().__init__("IfStatement")
        self.condition = condition  # Expression
        self.then_block = then_block  # Platter
        self.elif_clauses = elif_clauses or []  # List of (condition, block) tuples
        self.else_block = else_block  # Platter or None
    
    def add_elif(self, condition, block):
        self.elif_clauses.append((condition, block))
    
    def __repr__(self):
        return f"IfStatement(elifs={len(self.elif_clauses)}, else={'Yes' if self.else_block else 'No'})"

class SwitchStatement(ASTNode):
    """Switch statement (menu)"""
    def __init__(self, expr, cases, default=None):
        super().__init__("SwitchStatement")
        self.expr = expr  # Expression to switch on
        self.cases = cases or []  # List of CaseClause nodes
        self.default = default  # Statements list or None
    
    def add_case(self, case_node):
        self.cases.append(case_node)
    
    def __repr__(self):
        return f"SwitchStatement({len(self.cases)} cases, default={'Yes' if self.default else 'No'})"

class CaseClause(ASTNode):
    """Case in a switch statement"""
    def __init__(self, value, statements):
        super().__init__("CaseClause")
        self.value = value  # Literal value
        self.statements = statements  # List of statement nodes
    
    def __repr__(self):
        return f"CaseClause({len(self.statements)} stmts)"

class WhileLoop(ASTNode):
    """While loop (repeat)"""
    def __init__(self, condition, body):
        super().__init__("WhileLoop")
        self.condition = condition
        self.body = body  # Platter
    
    def __repr__(self):
        return f"WhileLoop()"

class DoWhileLoop(ASTNode):
    """Do-while loop (order...repeat)"""
    def __init__(self, body, condition):
        super().__init__("DoWhileLoop")
        self.body = body
        self.condition = condition
    
    def __repr__(self):
        return f"DoWhileLoop()"

class ForLoop(ASTNode):
    """For loop (pass)"""
    def __init__(self, init, update, condition, body):
        super().__init__("ForLoop")
        self.init = init  # Assignment or None
        self.update = update  # Assignment
        self.condition = condition  # Expression
        self.body = body  # Platter
    
    def __repr__(self):
        return f"ForLoop()"

class ReturnStatement(ASTNode):
    """Return statement (serve)"""
    def __init__(self, value=None):
        super().__init__("ReturnStatement")
        self.value = value  # Expression or None
    
    def __repr__(self):
        return f"ReturnStatement(has_value={'Yes' if self.value else 'No'})"

class BreakStatement(ASTNode):
    """Break statement (stop)"""
    def __init__(self):
        super().__init__("BreakStatement")
    
    def __repr__(self):
        return "BreakStatement()"

class ContinueStatement(ASTNode):
    """Continue statement (next)"""
    def __init__(self):
        super().__init__("ContinueStatement")
    
    def __repr__(self):
        return "ContinueStatement()"

class ExpressionStatement(ASTNode):
    """Expression used as statement"""
    def __init__(self, expr):
        super().__init__("ExpressionStatement")
        self.expr = expr
    
    def __repr__(self):
        return f"ExpressionStatement({self.expr})"

# ============================================================================
# Expressions
# ============================================================================

class BinaryOp(ASTNode):
    """Binary operation"""
    def __init__(self, left, operator, right):
        super().__init__("BinaryOp")
        self.left = left
        self.operator = operator  # "+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=", "and", "or"
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.operator})"

class UnaryOp(ASTNode):
    """Unary operation"""
    def __init__(self, operator, operand):
        super().__init__("UnaryOp")
        self.operator = operator  # "not", "-"
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.operator})"

class Identifier(ASTNode):
    """Variable reference"""
    def __init__(self, name):
        super().__init__("Identifier")
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"

class ArrayAccess(ASTNode):
    """Array element access"""
    def __init__(self, array, index):
        super().__init__("ArrayAccess")
        self.array = array  # Expression
        self.index = index  # Expression
    
    def __repr__(self):
        return f"ArrayAccess()"

class TableAccess(ASTNode):
    """Table field access"""
    def __init__(self, table, field):
        super().__init__("TableAccess")
        self.table = table  # Expression
        self.field = field  # String
    
    def __repr__(self):
        return f"TableAccess(.{self.field})"

class FunctionCall(ASTNode):
    """Function call"""
    def __init__(self, name, args=None):
        super().__init__("FunctionCall")
        self.name = name
        self.args = args or []
    
    def add_arg(self, arg):
        self.args.append(arg)
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {len(self.args)} args)"

class CastExpr(ASTNode):
    """Type cast expression"""
    def __init__(self, target_type, expr):
        super().__init__("CastExpr")
        self.target_type = target_type  # "piece", "sip", "flag", "chars"
        self.expr = expr
    
    def __repr__(self):
        return f"CastExpr(to{self.target_type})"

# ============================================================================
# Literals
# ============================================================================

class Literal(ASTNode):
    """Literal value"""
    def __init__(self, value_type, value):
        super().__init__("Literal")
        self.value_type = value_type  # "piece", "sip", "flag", "chars"
        self.value = value
    
    def __repr__(self):
        return f"Literal({self.value_type}: {self.value})"

class ArrayLiteral(ASTNode):
    """Array literal"""
    def __init__(self, elements=None):
        super().__init__("ArrayLiteral")
        self.elements = elements or []
    
    def add_element(self, elem):
        if elem:
            self.elements.append(elem)
    
    def __repr__(self):
        return f"ArrayLiteral([{len(self.elements)}])"

class TableLiteral(ASTNode):
    """Table literal"""
    def __init__(self, field_inits=None):
        super().__init__("TableLiteral")
        self.field_inits = field_inits or []  # List of (field_name, value) tuples
    
    def add_field(self, field_name, value):
        self.field_inits.append((field_name, value))
    
    def __repr__(self):
        return f"TableLiteral({len(self.field_inits)} fields)"