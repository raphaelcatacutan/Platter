from pprint import pprint

import logging as log
import subprocess
import sys
from app.lexer.token import Token
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import print_ast
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table import print_symbol_table
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.output_formatter import IRFormatter
from app.code_optimization.optimizer_manager import OptimizerManager, OptimizationLevel
from app.interpreter.ir_interpreter import TACInterpreter

COPY_ERROR_TO_CLIPBOARD = True


def set_clipboard(text):
    if not COPY_ERROR_TO_CLIPBOARD:
        return
    try: subprocess.run('clip', input=text.encode('utf-16le'), check=True, shell=True)
    except Exception:
        pass  


def load_source_only(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw_text = f.read()

    lines = raw_text.splitlines()
    end_indexes = [i for i, line in enumerate(lines) if line.strip() == "--end"]
    if not end_indexes:
        return raw_text
    return "\n".join(lines[:end_indexes[0]])

if __name__ == "__main__":
    filepath = sys.argv[1]
    include_whitespace = False

    source = load_source_only(filepath)

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    tokens = [
        t for t in tokens
        if t.type not in ("comment", "space", "newline", "tab") or include_whitespace
    ]
    
    try:
        print("=" * 80)
        print("\n\nLEXICAL:")
        pprint(tokens)
        print((" ".join(t.type for t in tokens if not "comment" in t.type )))
        set_clipboard((" ".join(t.type for t in tokens if not "comment" in t.type )))   
        
        
        print("=" * 80)
        print("\n\nSYNTAX:")
        log.disable(log.WARNING) 
        parser = Parser(tokens)
        python_error = None
        try:
            parser.parse_program()
            python_error = "No Syntax Error"
            print(python_error)
        except SyntaxError as e:
            python_error = str(e)
            print(python_error)

            
        print("=" * 80)
        print("\n\nSEMANTIC ANALYSIS:")
        
        # Disable all logging for semantic analysis in this file only
        log.disable(log.CRITICAL)
        
        try:
            # Parse AST
            ast_parser = ASTParser(tokens)
            ast = ast_parser.parse_program()
            
            # Run semantic analysis
            symbol_table, error_handler = analyze_program(ast)
            
            # Print AST Structure (capture and filter output)
            print("\nAST Structure:")
            import io
            from contextlib import redirect_stdout
            
            ast_buffer = io.StringIO()
            with redirect_stdout(ast_buffer):
                print_ast(ast, format="pretty")
            print(ast_buffer.getvalue())
            
            # Print Symbol Table (capture and filter output)
            print("\nSymbol Table:")
            symbol_buffer = io.StringIO()
            with redirect_stdout(symbol_buffer):
                print_symbol_table(symbol_table, error_handler)
            
            # Filter out unwanted sections and fix border characters
            symbol_output = symbol_buffer.getvalue()
            
            # Replace double-line borders with single-line borders for STATISTICS and ISSUES
            symbol_output = symbol_output.replace('╔', '')
            symbol_output = symbol_output.replace('╗', '')
            symbol_output = symbol_output.replace('╚', '')
            symbol_output = symbol_output.replace('╝', '')
            symbol_output = symbol_output.replace('╠', '')
            symbol_output = symbol_output.replace('╣', '')
            symbol_output = symbol_output.replace('║', '')
            symbol_output = symbol_output.replace('═', '')
            
            lines = symbol_output.split('\n')
            
            # Find where user-defined symbols section starts and skip all before it
            start_idx = None
            for i, line in enumerate(lines):
                if 'USER-DEFINED SYMBOLS' in line:
                    # Skip this header and continue 3 lines (for the box)
                    start_idx = i + 3
                    break
            
            # If no user-defined symbols section found, show everything
            if start_idx is None:
                print(symbol_output)
            else:
                # Print only from user-defined symbols onwards
                print('\n'.join(lines[start_idx:]))
            
            # Print Errors/Issues (if any)
            if error_handler.has_errors() or error_handler.has_warnings():
                print("\nErrors/Issues:")
                for err in error_handler.get_errors():
                    print(f"  {err}")
            
            # Generate and display IR (TAC) if no errors
            if not error_handler.has_errors():
                print("\n" + "=" * 80)
                print("INTERMEDIATE CODE GENERATION (TAC)")
                print("=" * 80)
                
                try:
                    # Generate IR
                    ir_gen = IRGenerator()
                    tac_instructions, quad_table = ir_gen.generate(ast)
                    formatter = IRFormatter()
                    
                    # Display TAC
                    ir_tac_text = formatter.format_tac_text(tac_instructions)
                    print("\nThree Address Code:")
                    print("-" * 80)
                    print(ir_tac_text)
                    
                    # Optimize TAC
                    optimizer = OptimizerManager(OptimizationLevel.STANDARD)
                    optimized_tac = optimizer.optimize_tac(tac_instructions)
                    ir_tac_optimized_text = formatter.format_tac_text(optimized_tac)
                    
                    print("\nOptimized TAC:")
                    print("-" * 80)
                    print(ir_tac_optimized_text)
                    
                    print("\nExecution Output:")
                    print("-" * 80)
                    interpreter = TACInterpreter(optimized_tac)
                    printed_output_len = 0
                    pending_input_echo = None
                    final_output = ""
                    while True:
                        exec_result = interpreter.run()

                        # Stream only newly produced output so execution feels like a real terminal run.
                        current_output = exec_result.get("output", "")
                        if len(current_output) > printed_output_len:
                            new_output = current_output[printed_output_len:]

                            # Suppress interpreter's echoed take() input so terminal input appears only once.
                            if pending_input_echo and new_output.startswith(pending_input_echo):
                                new_output = new_output[len(pending_input_echo):]
                            pending_input_echo = None

                            print(new_output, end="")
                            printed_output_len = len(current_output)

                        if exec_result.get("success"):
                            final_output = exec_result.get("output", "")
                            break
                        if exec_result.get("paused"):
                            try:
                                line = input()
                            except EOFError:
                                print("\n[Execution Error] Input stream ended while waiting for take().")
                                exec_result = {
                                    "success": False,
                                    "error": "Input stream ended while waiting for take().",
                                    "output": exec_result.get("output", ""),
                                    "globals": exec_result.get("globals", {}),
                                }
                                final_output = exec_result.get("output", "")
                                break

                            # Process escape sequences in user input
                            line = line.replace('\\n', '\n').replace('\\t', '\t')
                            pending_input_echo = line + "\n"
                            interpreter.stdin_lines.append(line)
                            continue
                        break
                    
                    # Print any runtime error that occurred
                    if not exec_result.get("success") and exec_result.get("error"):
                        print(f"\n{exec_result.get('error')}")
                    
                    # Set clipboard to the full execution output
                    set_clipboard(final_output)
                except Exception as ir_err:
                    print(f"\nIR generation error: {ir_err}")
                    import traceback
                    traceback.print_exc()
                
        except SyntaxError as e:
            print(f"\nSyntax Error: {e}")
        except Exception as e:
            print(f"\nSemantic analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Re-enable logging after semantic analysis
            log.disable(log.NOTSET)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
