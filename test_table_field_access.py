import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'platter-compiler-sveltejs', 'static', 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import analyze_program

code = """
table of Food = [
    chars of food_name;
    piece[] of qty_set;
];

Food of chips = [
    food_name = "oishi";
    qty_set = [1, 2, 3];
];

start(){  
    piece[] of a = chips:qty_set;
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()

# Check the AST structure for the init expression
print("=== AST STRUCTURE ===\n")
if ast.start_platter and ast.start_platter.local_decls:
    for decl in ast.start_platter.local_decls:
        if hasattr(decl, 'init_value'):
            print(f"Declaration: {decl}")
            print(f"  init_value type: {type(decl.init_value).__name__}")
            if hasattr(decl.init_value, 'table'):
                print(f"  table: {decl.init_value.table}")
                print(f"  field: {decl.init_value.field}")

# Run semantic analysis
symbol_table, error_handler = analyze_program(ast)

print("\n=== DEBUGGING TABLE FIELD ACCESS TYPE ===\n")

# Look up chips symbol
chips_symbol = symbol_table.lookup_symbol('chips')
if chips_symbol:
    print(f"chips symbol found:")
    print(f"  - base_type: {chips_symbol.type_info.base_type}")
    print(f"  - dimensions: {chips_symbol.type_info.dimensions}")
    print(f"  - is_table: {chips_symbol.type_info.is_table}")
    print(f"  - table_fields: {chips_symbol.type_info.table_fields}")
    if chips_symbol.type_info.table_fields:
        print(f"  - qty_set field type: {chips_symbol.type_info.table_fields.get('qty_set')}")
        qty_set_type = chips_symbol.type_info.get_field_type('qty_set')
        print(f"  - get_field_type('qty_set'): {qty_set_type}")
        if qty_set_type:
            print(f"    - base_type: {qty_set_type.base_type}")
            print(f"    - dimensions: {qty_set_type.dimensions}")
else:
    print("chips symbol not found")

print("\n=== ERRORS ===")
for error in error_handler.errors:
    print(f"{error}")
