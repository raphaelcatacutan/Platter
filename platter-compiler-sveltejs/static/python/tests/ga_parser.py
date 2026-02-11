from typing import Any
import unittest
import os
import logging
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from tests.syntax_programs.syntax_tscripts import SYNTAX_TSCRIPTS

# Suppress debug logs from parser during tests
logging.getLogger().setLevel(logging.CRITICAL)

def check_parse(script: dict[str, Any]):
    """
    Parse the given script and return the result message.
    This matches the behavior of parser_program.py's main block.
    """
    lexer = Lexer(script["code"])
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    try:
        parser.parse_program()
        return "No Syntax Error"
    except Exception as e:
        return str(e)

class TestParser(unittest.TestCase):
    # Class variable to store failed tests
    failed_tests = []
    
    def test_syntax_scripts(self):
        """Test all syntax scripts from TSV and TXT files."""
        passed_count = 0
        
        for script in SYNTAX_TSCRIPTS:
            test_num = script["number"]
            expected_output = script["expected_output"]
            actual_output = check_parse(script)
            
            with self.subTest(test_number=test_num):
                try:
                    self.assertEqual(actual_output, expected_output)
                    passed_count += 1
                except AssertionError:
                    # Store failed test information
                    TestParser.failed_tests.append({
                        'number': test_num,
                        'code': script["code"],
                        'expected': expected_output,
                        'actual': actual_output
                    })
                    raise
    
    @classmethod
    def tearDownClass(cls):
        """Write detailed summary to file after all tests complete."""
        total_tests = len(SYNTAX_TSCRIPTS)
        passed_count = total_tests - len(cls.failed_tests)
        
        # Get the syntax_programs directory
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        syntax_programs_dir = os.path.join(tests_dir, 'syntax_programs')
        results_file = os.path.join(syntax_programs_dir, 'test_results.txt')
        
        # Write results to file
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"TEST SUMMARY: {passed_count}/{total_tests} tests passed\n")
            f.write(f"{'='*70}\n\n")
            
            if cls.failed_tests:
                for fail in cls.failed_tests:
                    f.write(f"[FAILED] Test #{fail['number']}\n")
                    f.write(f"-" * 70 + "\n")
                    f.write(f"Code:\n")
                    # Print code with line numbers
                    code_lines = fail['code'].split('\n')
                    for idx, line in enumerate(code_lines, 1):
                        f.write(f"  {idx:2d} | {line}\n")
                    f.write(f"\nExpected: {fail['expected']}\n")
                    f.write(f"Actual:   {fail['actual']}\n")
                    f.write(f"{'='*70}\n\n")
            else:
                f.write("All tests passed!\n")
        
        # Also print summary to console
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY: {passed_count}/{total_tests} tests passed")
        print(f"{'='*70}")
        print(f"Detailed results written to: {results_file}")

if __name__ == "__main__":
    unittest.main(verbosity=2)