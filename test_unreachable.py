#!/usr/bin/env python3
"""Test that unreachable code after serve is now a warning"""

import sys
sys.path.insert(0, 'platter-compiler-sveltejs/static/python')

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

code = """
start() {
    piece of x;
    serve 0;
    x = 1;
}
"""

# Tokenize
lexer = Lexer(code)
tokens = lexer.tokenize()

# Parse
parser = Parser(tokens)
ast = parser.parse_program()

# Semantic analysis
analyzer = SemanticAnalyzer()
symbol_table = analyzer.analyze(ast)

# Check results
error_handler = analyzer.error_handler
print(f"Errors: {error_handler.get_error_count()}")
print(f"Warnings: {error_handler.get_warning_count()}")

if error_handler.get_error_count() == 0 and error_handler.get_warning_count() == 1:
    print("✓ SUCCESS: Unreachable code is now a warning, not an error")
    for err in error_handler.get_errors():
        print(f"  [{err.severity.name}] [{err.error_code}] {err.message}")
else:
    print("✗ FAILED: Expected 0 errors and 1 warning")
    for err in error_handler.get_errors():
        print(f"  [{err.severity.name}] [{err.error_code}] {err.message}")
