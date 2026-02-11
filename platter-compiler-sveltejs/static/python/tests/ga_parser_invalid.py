import unittest
import os
import logging
from pathlib import Path
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser

# Suppress debug logs from parser during tests
logging.getLogger().setLevel(logging.CRITICAL)


class TestParserInvalidPrograms(unittest.TestCase):
    """Test that all invalid .platter files produce parse errors as expected."""
    
    # Class variable to store failed tests
    failed_tests = []
    
    @classmethod
    def setUpClass(cls):
        """Set up paths for invalid test programs."""
        tests_dir = Path(__file__).parent
        cls.invalid_tests_dir = tests_dir / 'syntax_programs' / 'invalid_tests'
        cls.platter_files = sorted(cls.invalid_tests_dir.glob('*.platter'))
        
        # It's okay if there are no files yet
        if not cls.platter_files:
            print(f"ℹ No .platter files found in {cls.invalid_tests_dir}")
    
    def parse_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Parse a .platter file and return (has_error, message).
        
        Args:
            file_path: Path to the .platter file
            
        Returns:
            (True, error_message) if parsing fails (expected for invalid tests)
            (False, "No Syntax Error") if parsing succeeds (unexpected for invalid tests)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            parser.parse_program()
            
            return False, "No Syntax Error"
            
        except Exception as e:
            return True, str(e)
    
    def test_all_invalid_programs(self):
        """Test all .platter files in invalid_tests directory."""
        if not self.platter_files:
            self.skipTest("No invalid test files found")
        
        passed_count = 0
        
        for platter_file in self.platter_files:
            with self.subTest(file=platter_file.name):
                has_error, message = self.parse_file(platter_file)
                
                try:
                    self.assertTrue(
                        has_error,
                        f"Expected a syntax error, but parsing succeeded"
                    )
                    passed_count += 1
                    
                except AssertionError as e:
                    # Store failed test information
                    with open(platter_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    TestParserInvalidPrograms.failed_tests.append({
                        'file': platter_file.name,
                        'code': code,
                        'message': message
                    })
                    raise
    
    @classmethod
    def tearDownClass(cls):
        """Write detailed summary to file after all tests complete."""
        if not cls.platter_files:
            return
        
        total_tests = len(cls.platter_files)
        passed_count = total_tests - len(cls.failed_tests)
        
        # Get the syntax_programs directory
        results_file = cls.invalid_tests_dir.parent / 'invalid_test_results.txt'
        
        # Write results to file
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"INVALID PARSER TEST SUMMARY: {passed_count}/{total_tests} tests passed\n")
            f.write(f"{'='*70}\n\n")
            
            if cls.failed_tests:
                f.write(f"FAILURES: These files should produce errors but parsed successfully\n\n")
                for fail in cls.failed_tests:
                    f.write(f"[FAILED] {fail['file']}\n")
                    f.write(f"-" * 70 + "\n")
                    f.write(f"Code:\n")
                    # Print code with line numbers
                    code_lines = fail['code'].split('\n')
                    for idx, line in enumerate(code_lines, 1):
                        f.write(f"  {idx:3d} | {line}\n")
                    f.write(f"\nExpected: Syntax error\n")
                    f.write(f"Actual:   {fail['message']}\n")
                    f.write(f"{'='*70}\n\n")
            else:
                f.write("✓ All invalid programs correctly produced errors!\n")
        
        # Also print summary to console
        print(f"\n{'='*70}")
        print(f"INVALID PARSER TEST SUMMARY: {passed_count}/{total_tests} tests passed")
        print(f"{'='*70}")
        if cls.failed_tests:
            print(f"\n⚠ {len(cls.failed_tests)} file(s) incorrectly parsed successfully:")
            for fail in cls.failed_tests:
                print(f"  - {fail['file']}")
        print(f"\nDetailed results written to: {results_file}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
