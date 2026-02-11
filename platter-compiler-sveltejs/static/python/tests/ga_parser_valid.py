import unittest
import os
import logging
from pathlib import Path
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser

# Suppress debug logs from parser during tests
logging.getLogger().setLevel(logging.CRITICAL)


class TestParserValidPrograms(unittest.TestCase):
    """Test that all valid .platter files parse successfully without errors."""
    
    # Class variable to store failed tests
    failed_tests = []
    
    @classmethod
    def setUpClass(cls):
        """Set up paths for valid test programs."""
        tests_dir = Path(__file__).parent
        cls.valid_tests_dir = tests_dir / 'syntax_programs' / 'valid_tests'
        cls.platter_files = sorted(cls.valid_tests_dir.glob('*.platter'))
        
        if not cls.platter_files:
            raise ValueError(f"No .platter files found in {cls.valid_tests_dir}")
    
    def parse_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Parse a .platter file and return (success, message).
        
        Args:
            file_path: Path to the .platter file
            
        Returns:
            (True, "No Syntax Error") if parsing succeeds
            (False, error_message) if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            parser.parse_program()
            
            return True, "No Syntax Error"
            
        except Exception as e:
            return False, str(e)
    
    def test_all_valid_programs(self):
        """Test all .platter files in valid_tests directory."""
        passed_count = 0
        
        for platter_file in self.platter_files:
            with self.subTest(file=platter_file.name):
                success, message = self.parse_file(platter_file)
                
                try:
                    self.assertTrue(
                        success,
                        f"Expected no error, but got: {message}"
                    )
                    passed_count += 1
                    
                except AssertionError as e:
                    # Store failed test information
                    with open(platter_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    TestParserValidPrograms.failed_tests.append({
                        'file': platter_file.name,
                        'code': code,
                        'error': message
                    })
                    raise
    
    @classmethod
    def tearDownClass(cls):
        """Write detailed summary to file after all tests complete."""
        total_tests = len(cls.platter_files)
        passed_count = total_tests - len(cls.failed_tests)
        
        # Get the syntax_programs directory
        results_file = cls.valid_tests_dir.parent / 'valid_test_results.txt'
        
        # Write results to file
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"VALID PARSER TEST SUMMARY: {passed_count}/{total_tests} tests passed\n")
            f.write(f"{'='*70}\n\n")
            
            if cls.failed_tests:
                f.write(f"FAILURES: These files should parse successfully but failed\n\n")
                for fail in cls.failed_tests:
                    f.write(f"[FAILED] {fail['file']}\n")
                    f.write(f"-" * 70 + "\n")
                    f.write(f"Code:\n")
                    # Print code with line numbers
                    code_lines = fail['code'].split('\n')
                    for idx, line in enumerate(code_lines, 1):
                        f.write(f"  {idx:3d} | {line}\n")
                    f.write(f"\nError Output:\n{fail['error']}\n")
                    f.write(f"{'='*70}\n\n")
            else:
                f.write("✓ All valid programs parsed successfully!\n")
        
        # Also print summary to console
        print(f"\n{'='*70}")
        print(f"VALID PARSER TEST SUMMARY: {passed_count}/{total_tests} tests passed")
        print(f"{'='*70}")
        if cls.failed_tests:
            print(f"\n⚠ {len(cls.failed_tests)} file(s) failed to parse:")
            for fail in cls.failed_tests:
                print(f"  - {fail['file']}")
        print(f"\nDetailed results written to: {results_file}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
