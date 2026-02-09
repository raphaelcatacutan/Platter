from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from pathlib import Path
import os
import importlib.util

class TestParser():
    
    # ===== CONFIGURATION =====
    # Specify the directory where testscript.py is located
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
    TESTSCRIPT_DIR = PROJECT_ROOT / "static/python/app/utils/sources"
    
    # Name of the Python file containing test scripts (without .py extension)
    TESTSCRIPT_FILE = "testscript"
    
    # Output directory path (relative or absolute)
    OUTPUT_DIR = PROJECT_ROOT / "static/python/app/utils/sources" # If None, uses the directory of this script
    
    # Output filename
    OUTPUT_FILENAME = "testscript_output.txt"
    # ========================

    def msg(self, num, code, exp_outp, act_outp, result, file):
        message = (
            f"============ CODE #{num} ================\n"
            f"CODE:\n{code}\n"
            f"EXPECTED OUTPUT: {exp_outp}\n"
            f"ACTUAL OUTPUT: {act_outp}\n"
            f"SYNTAX OUTPUT: {result}\n"
            f"=====================================\n\n"
        )
        file.write(message)

    def run_script(self):
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Determine the testscript module path
        testscript_path = os.path.join(script_dir, "..", "..", self.TESTSCRIPT_DIR, f"{self.TESTSCRIPT_FILE}.py")
        testscript_path = os.path.abspath(testscript_path)
        
        # Dynamically load the testscript module
        spec = importlib.util.spec_from_file_location(self.TESTSCRIPT_FILE, testscript_path)
        testscript_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(testscript_module)
        SYNTAX_TSCRIPTS = testscript_module.SYNTAX_TSCRIPTS
        
        # Determine output directory
        if self.OUTPUT_DIR:
            output_dir = self.OUTPUT_DIR
        else:
            output_dir = script_dir
        
        output_file = os.path.join(output_dir, self.OUTPUT_FILENAME)
        
        with open(output_file, 'w') as f:
            for script in SYNTAX_TSCRIPTS:
                lexer = Lexer(script["code"])
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                result = ""

                try:
                    result = parser.parse_program()
                    self.msg(script["number"], 
                             script["code"], 
                             script["expected_output"], 
                             script["actual_output"],
                             None if result else "No Syntax Error",
                             f)

                except SyntaxError as e:
                    self.msg(script["number"], 
                             script["code"], 
                             script["expected_output"], 
                             script["actual_output"],
                             e,
                             f)
        
        print(f"Output written to {output_file}")

if __name__=="__main__":
    tester = TestParser()
    tester.run_script()