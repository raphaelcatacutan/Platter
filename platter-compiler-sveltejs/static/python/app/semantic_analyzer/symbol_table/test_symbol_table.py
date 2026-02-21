"""
Test file demonstrating Symbol Table functionality
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table import build_symbol_table, print_symbol_table


def create_test_ast_simple():
    """Create a simple test AST"""
    program = Program()
    
    # Global variable: piece myVar = 5
    var_decl = VarDecl("piece", "myVar", Literal("piece", 5))
    program.add_global_decl(var_decl)
    
    # Array: piece[] numbers
    array_decl = ArrayDecl("piece", 1, "numbers")
    program.add_global_decl(array_decl)
    
    return program


def create_test_ast_with_table():
    """Create AST with table (struct) definition"""
    program = Program()
    
    # Table prototype: Point with piece x, piece y
    point_fields = [
        FieldDecl("piece", 0, "x"),
        FieldDecl("piece", 0, "y")
    ]
    point_proto = TablePrototype("Point", point_fields)
    program.add_global_decl(point_proto)
    
    # Table instance: Point origin
    point_decl = TableDecl("Point", "origin")
    program.add_global_decl(point_decl)
    
    # Array of tables: Point[] points
    points_array = TableDecl("Point", "points", None, 1)
    program.add_global_decl(points_array)
    
    return program


def create_test_ast_nested_tables():
    """Create AST with nested table structures"""
    program = Program()
    
    # Inner table: Address
    address_fields = [
        FieldDecl("chars", 0, "street"),
        FieldDecl("chars", 0, "city"),
        FieldDecl("piece", 0, "zipcode")
    ]
    address_proto = TablePrototype("Address", address_fields)
    program.add_global_decl(address_proto)
    
    # Outer table: Person with Address field
    person_fields = [
        FieldDecl("chars", 0, "name"),
        FieldDecl("piece", 0, "age"),
        FieldDecl("Address", 0, "address"),  # Nested table
        FieldDecl("piece", 1, "scores")  # Array field
    ]
    person_proto = TablePrototype("Person", person_fields)
    program.add_global_decl(person_proto)
    
    # Person instance
    person_decl = TableDecl("Person", "employee")
    program.add_global_decl(person_decl)
    
    return program


def create_test_ast_with_function():
    """Create AST with function declaration"""
    program = Program()
    
    # Function: piece add(piece a, piece b)
    params = [
        ParamDecl("piece", 0, "a"),
        ParamDecl("piece", 0, "b")
    ]
    
    # Function body
    body = Platter()
    
    # Local variable: piece result = a + b
    add_expr = BinaryOp(Identifier("a"), "+", Identifier("b"))
    result_decl = VarDecl("piece", "result", add_expr)
    body.add_local_decl(result_decl)
    
    # Return result
    return_stmt = ReturnStatement(Identifier("result"))
    body.add_statement(return_stmt)
    
    recipe = RecipeDecl("piece", 0, "add", params, body)
    program.add_recipe_decl(recipe)
    
    return program


def create_test_ast_scoping():
    """Create AST to test scoping rules"""
    program = Program()
    
    # Global: piece globalVar = 10
    global_var = VarDecl("piece", "globalVar", Literal("piece", 10))
    program.add_global_decl(global_var)
    
    # Function with local variables
    params = []
    body = Platter()
    
    # Local: piece localVar = 20
    local_var = VarDecl("piece", "localVar", Literal("piece", 20))
    body.add_local_decl(local_var)
    
    # Nested block
    inner_block = Platter()
    inner_var = VarDecl("piece", "innerVar", Literal("piece", 30))
    inner_block.add_local_decl(inner_var)
    
    # Assignment using all three variables
    sum_expr = BinaryOp(
        BinaryOp(Identifier("globalVar"), "+", Identifier("localVar")),
        "+",
        Identifier("innerVar")
    )
    assignment = Assignment(Identifier("localVar"), "=", sum_expr)
    inner_block.add_statement(assignment)
    
    body.add_statement(inner_block)
    
    recipe = RecipeDecl("void", 0, "testScope", params, body)
    program.add_recipe_decl(recipe)
    
    return program


def create_test_ast_with_errors():
    """Create AST that should produce semantic errors"""
    program = Program()
    
    # Error 1: Undefined type
    bad_var = VarDecl("undefined_type", "badVar")
    program.add_global_decl(bad_var)
    
    # Error 2: Duplicate declaration
    var1 = VarDecl("piece", "duplicate", Literal("piece", 1))
    var2 = VarDecl("sip", "duplicate", Literal("sip", 2.5))
    program.add_global_decl(var1)
    program.add_global_decl(var2)
    
    # Error 3: Type mismatch in assignment
    params = []
    body = Platter()
    
    # piece x = 10
    x_decl = VarDecl("piece", "x", Literal("piece", 10))
    body.add_local_decl(x_decl)
    
    # x = "hello"  // Error: can't assign chars to piece
    bad_assign = Assignment(Identifier("x"), "=", Literal("chars", "hello"))
    body.add_statement(bad_assign)
    
    # Error 4: Undefined variable
    undef_var_stmt = ExpressionStatement(Identifier("undefinedVar"))
    body.add_statement(undef_var_stmt)
    
    # Error 5: Return outside function
    recipe = RecipeDecl("void", 0, "testErrors", params, body)
    program.add_recipe_decl(recipe)
    
    # Break outside loop
    main_body = Platter()
    main_body.add_statement(BreakStatement())
    program.set_start_platter(main_body)
    
    return program


def create_test_ast_array_access():
    """Test array and table access type checking"""
    program = Program()
    
    # Array: piece[] numbers
    array_decl = ArrayDecl("piece", 1, "numbers", ArrayLiteral([
        Literal("piece", 1),
        Literal("piece", 2),
        Literal("piece", 3)
    ]))
    program.add_global_decl(array_decl)
    
    # Table: Point
    point_fields = [
        FieldDecl("piece", 0, "x"),
        FieldDecl("piece", 0, "y")
    ]
    point_proto = TablePrototype("Point", point_fields)
    program.add_global_decl(point_proto)
    
    point_decl = TableDecl("Point", "pt")
    program.add_global_decl(point_decl)
    
    # Function to test access
    params = []
    body = Platter()
    
    # piece val = numbers[0]
    array_access = ArrayAccess(Identifier("numbers"), Literal("piece", 0))
    val_decl = VarDecl("piece", "val", array_access)
    body.add_local_decl(val_decl)
    
    # piece x = pt.x
    table_access = TableAccess(Identifier("pt"), "x")
    x_decl = VarDecl("piece", "x", table_access)
    body.add_local_decl(x_decl)
    
    # Error: Access non-existent field
    bad_access = TableAccess(Identifier("pt"), "z")
    z_decl = VarDecl("piece", "z", bad_access)
    body.add_local_decl(z_decl)
    
    recipe = RecipeDecl("void", 0, "testAccess", params, body)
    program.add_recipe_decl(recipe)
    
    return program


def create_test_ast_multidimensional():
    """Test multidimensional arrays"""
    program = Program()
    
    # 2D array: piece[][] matrix
    matrix_decl = ArrayDecl("piece", 2, "matrix")
    program.add_global_decl(matrix_decl)
    
    # 3D array: sip[][][] tensor
    tensor_decl = ArrayDecl("sip", 3, "tensor")
    program.add_global_decl(tensor_decl)
    
    # Function to access multidimensional arrays
    params = []
    body = Platter()
    
    # piece[] row = matrix[0]  // Access 2D -> 1D
    row_access = ArrayAccess(Identifier("matrix"), Literal("piece", 0))
    row_decl = ArrayDecl("piece", 1, "row", row_access)  # Note: dimension is 1
    body.add_local_decl(row_decl)
    
    # piece element = matrix[0][0]  // Access 2D -> 0D
    element_access = ArrayAccess(
        ArrayAccess(Identifier("matrix"), Literal("piece", 0)),
        Literal("piece", 0)
    )
    element_decl = VarDecl("piece", "element", element_access)
    body.add_local_decl(element_decl)
    
    recipe = RecipeDecl("void", 0, "testMultiDim", params, body)
    program.add_recipe_decl(recipe)
    
    return program


def run_test(name: str, ast_creator):
    """Run a test case"""
    print("\n" + "="*70)
    print(f"TEST: {name}")
    print("="*70)
    
    ast = ast_creator()
    symbol_table = build_symbol_table(ast)
    print_symbol_table(symbol_table)


def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# Symbol Table Tests for Platter Language")
    print("#"*70)
    
    run_test("Simple Variables and Arrays", create_test_ast_simple)
    run_test("Table (Struct) Definition and Instance", create_test_ast_with_table)
    run_test("Nested Table Structures", create_test_ast_nested_tables)
    run_test("Function Declaration with Locals", create_test_ast_with_function)
    run_test("Scoping Rules", create_test_ast_scoping)
    run_test("Semantic Errors Detection", create_test_ast_with_errors)
    run_test("Array and Table Access", create_test_ast_array_access)
    run_test("Multidimensional Arrays", create_test_ast_multidimensional)
    
    print("\n" + "#"*70)
    print("# All Tests Complete")
    print("#"*70)


if __name__ == "__main__":
    main()
