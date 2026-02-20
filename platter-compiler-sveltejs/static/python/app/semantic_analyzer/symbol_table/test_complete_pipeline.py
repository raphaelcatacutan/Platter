"""
Test the complete semantic analysis pipeline with symbol table output
"""

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import print_ast
from app.semantic_analyzer.symbol_table import build_symbol_table, print_symbol_table
from app.semantic_analyzer.symbol_table.symbol_table_output import (
    format_symbol_table_compact,
    format_symbol_table_summary,
    get_symbol_table_status_message
)


def test_complete_analysis(source_code: str):
    """Test complete analysis pipeline including symbol table"""
    print("\n" + "="*80)
    print("SOURCE CODE:")
    print("="*80)
    print(source_code)
    print()
    
    try:
        # Step 1: Lex
        print("Step 1: Lexical Analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        print(f"✓ Generated {len(tokens)} tokens")
        
        # Step 2: Parse
        print("\nStep 2: Parsing to AST...")
        parser = ASTParser(tokens)
        ast = parser.parse_program()
        print("✓ AST created")
        
        # Step 3: Print AST
        print("\n" + "="*80)
        print("AST Structure:")
        print("="*80)
        print_ast(ast, format="pretty")
        
        # Step 4: Build Symbol Table
        print("\n" + "="*80)
        print("Building Symbol Table")
        print("="*80)
        symbol_table = build_symbol_table(ast)
        print_symbol_table(symbol_table)
        
        # Step 5: Show Summary
        print("\n" + "="*80)
        print("Symbol Table Summary:")
        print("="*80)
        summary = format_symbol_table_summary(symbol_table)
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print(f"\n{get_symbol_table_status_message(symbol_table)}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test cases
test_case_1 = """
ingredient piece count = 0;
ingredient sip price = 9.99;

table Product {
    ingredient chars name;
    ingredient sip cost;
}

ingredient Product item;
"""

test_case_2 = """
table Point {
    ingredient piece x;
    ingredient piece y;
}

ingredient Point[] points;

recipe piece getX(piece index) {
    serve points[index].x;
}

recipe void main() {
    ingredient piece result = getX(0);
}
"""

test_case_3 = """
ingredient piece[][] matrix;

recipe void processMatrix() {
    ingredient piece i;
    ingredient piece j;
    
    pass (i = 0; i < 10; i = i + 1) {
        pass (j = 0; j < 10; j = j + 1) {
            matrix[i][j] = i * j;
        }
    }
}
"""


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# COMPLETE SEMANTIC ANALYSIS PIPELINE TEST")
    print("# Including Symbol Table Output")
    print("#"*80)
    
    print("\n\n" + "█"*80)
    print("█ TEST 1: Simple Variables and Tables")
    print("█"*80)
    test_complete_analysis(test_case_1)
    
    print("\n\n" + "█"*80)
    print("█ TEST 2: Functions and Array Access")
    print("█"*80)
    test_complete_analysis(test_case_2)
    
    print("\n\n" + "█"*80)
    print("█ TEST 3: Multidimensional Arrays in Loops")
    print("█"*80)
    test_complete_analysis(test_case_3)
    
    print("\n" + "#"*80)
    print("# ALL TESTS COMPLETED")
    print("#"*80)
