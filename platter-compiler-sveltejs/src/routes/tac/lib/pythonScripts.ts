/**
 * Code Analysis Module
 * Contains lexical, syntax, and semantic analysis functions
 * for the Platter programming language compiler
 */

import type { Token, TermMsg, AnalysisResult, LexerRow } from './types';

/**
 * Python script for semantic analysis
 * This is the core script that runs in Pyodide
 */
const SEMANTIC_PYTHON_SCRIPT = `
import sys
import re
import json
import importlib

# Force reload of modified modules to clear cache
def _ensure_parent_packages(module_name):
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        parent_name = '.'.join(parts[:i])
        if parent_name not in sys.modules:
            importlib.import_module(parent_name)

def _safe_reload(module_name):
    if module_name in sys.modules:
        try:
            _ensure_parent_packages(module_name)
            importlib.reload(sys.modules[module_name])
        except Exception as reload_err:
            print(f"[Reload Warning] {module_name}: {reload_err}")

for module_name in [
    'app.semantic_analyzer.symbol_table.types',
    'app.semantic_analyzer.symbol_table.symbol_table',
    'app.semantic_analyzer.symbol_table.symbol_table_builder',
    'app.semantic_analyzer.semantic_passes.error_handler',
    'app.semantic_analyzer.semantic_passes.scope_checker',
    'app.semantic_analyzer.semantic_passes.type_checker',
    'app.semantic_analyzer.semantic_passes.control_flow_checker',
    'app.semantic_analyzer.semantic_passes.function_checker',
    'app.semantic_analyzer.semantic_analyzer',
    'app.intermediate_code.tac',
    'app.intermediate_code.quadruple',
    'app.intermediate_code.ir_generator',
    'app.intermediate_code.output_formatter',
    'app.intermediate_code.optimizer',
    'app.intermediate_code.constant_folding',
    'app.intermediate_code.propagation',
    'app.intermediate_code.dead_code_elimination',
    'app.intermediate_code.algebraic_simplification',
    'app.intermediate_code.optimizer_manager',
    'app.intermediate_code.ir_interpreter',
]:
    _safe_reload(module_name)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import ASTReader, print_ast
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table import print_symbol_table
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_for_console

result = None
try:
    lexer = Lexer(code_input)
    tokens = lexer.tokenize()
    parser = ASTParser(tokens)
    ast = parser.parse_program()
    
    # AST and Symbol Table output disabled - only TAC logs enabled
    symbol_table, error_handler = analyze_program(ast)
    
    reader = ASTReader(ast)
    ast_json = reader.to_json(indent=2)
    
    symbol_table_data = format_symbol_table_for_console(symbol_table)
    symbol_table_json = json.dumps(symbol_table_data)
    
    ir_tac_text = ""
    ir_quads_text = ""
    ir_tac_optimized_text = ""
    execution_output = ""
    execution_success = False
    execution_paused = False
    execution_stdin_consumed = 0
    execution_error = ""
    execution_globals = {}
    
    print(f"[PYTHON] run_ir_pipeline = {run_ir_pipeline if 'run_ir_pipeline' in globals() else 'NOT SET'}")
    
    if run_ir_pipeline:
        print("[PYTHON] Entering IR pipeline")
        try:
            ir_gen = __import__('app.intermediate_code.ir_generator', fromlist=['IRGenerator']).IRGenerator()
            tac_instructions, quad_table = ir_gen.generate(ast)
            formatter = __import__('app.intermediate_code.output_formatter', fromlist=['IRFormatter']).IRFormatter()
            ir_tac_text = formatter.format_tac_text(tac_instructions)
            ir_quads_text = formatter.format_quadruples_text(quad_table)

            # TAC Output
            print("")
            print("=" * 80)
            print("Intermediate Code (Three Address Code)")
            print("=" * 80)
            print(ir_tac_text)

            optimizer_module = __import__('app.intermediate_code.optimizer_manager', fromlist=['OptimizerManager', 'OptimizationLevel'])
            OptimizerManager = optimizer_module.OptimizerManager
            OptimizationLevel = optimizer_module.OptimizationLevel
            optimizer = OptimizerManager(OptimizationLevel.STANDARD)
            optimized_tac = optimizer.optimize_tac(tac_instructions)
            ir_tac_optimized_text = formatter.format_tac_text(optimized_tac)

            print("")
            print("=" * 80)
            print("Optimized IR (Three Address Code - Standard Level)")
            print("=" * 80)
            print(ir_tac_optimized_text)

            print("")
            print("=" * 80)
            print("Program Execution (IR Interpreter)")
            print("=" * 80)

            TACInterpreter = __import__('app.intermediate_code.ir_interpreter', fromlist=['TACInterpreter']).TACInterpreter
            
            stdin_inputs = json.loads(accumulated_inputs_json) if 'accumulated_inputs_json' in globals() else []
            is_resuming_flag = is_resuming_execution if 'is_resuming_execution' in globals() else False
            
            print(f"[EXEC] Inputs: {stdin_inputs}, Resuming: {is_resuming_flag}")
            
            # Clear interpreter if starting fresh (not resuming)
            if not is_resuming_flag:
                if '_global_tac_interpreter' in globals():
                    del globals()['_global_tac_interpreter']
                if '_prev_stdin_count' in globals():
                    del globals()['_prev_stdin_count']
                if '_prev_output_length' in globals():
                    del globals()['_prev_output_length']
            
            # Check if we're resuming execution
            is_resuming = False
            if is_resuming_flag and '_global_tac_interpreter' in globals() and '_prev_stdin_count' in globals():
                prev_count = globals()['_prev_stdin_count']
                new_count = len(stdin_inputs)
                # We're resuming if we have new inputs beyond what was previously consumed
                if new_count > prev_count:
                    is_resuming = True
                    new_inputs = stdin_inputs[prev_count:]
                    tac_interpreter = globals()['_global_tac_interpreter']
                    print(f"[RESUME] Calling resume with: {new_inputs}")
                    exec_result = tac_interpreter.resume(new_inputs)
            
            if not is_resuming:
                # First run or fresh execution - create new interpreter
                tac_interpreter = TACInterpreter(optimized_tac, stdin_lines=stdin_inputs)
                print(f"[RUN] New interpreter, inputs: {stdin_inputs}")
                exec_result = tac_interpreter.run()
                # Store the interpreter globally for potential resume
                globals()['_global_tac_interpreter'] = tac_interpreter
                # Track output length for next resume
                globals()['_prev_output_length'] = 0
            
            # Update the stdin count for next time
            globals()['_prev_stdin_count'] = len(stdin_inputs)
            print(f"[RESULT] Success: {exec_result.get('success')}, Paused: {exec_result.get('paused')}, Output length: {len(exec_result.get('output', ''))}")
            
            full_output = exec_result.get("output", "")
            execution_success = exec_result.get("success", False)
            execution_paused = exec_result.get("paused", False)
            execution_stdin_consumed = exec_result.get("stdin_consumed", 0)
            execution_error = exec_result.get("error", "")
            execution_globals = exec_result.get("globals", {})
            
            # When resuming, only return the NEW output (not already displayed)
            prev_output_len = globals().get('_prev_output_length', 0)
            execution_output = full_output[prev_output_len:]  # Only new output
            globals()['_prev_output_length'] = len(full_output)  # Update for next time
            print(f"[OUTPUT] Previous length: {prev_output_len}, Full length: {len(full_output)}, New output: '{execution_output}'")

            if execution_success:
                print("[Execution OK]")
            elif execution_paused:
                print(f"[Execution Paused] Awaiting input")
            else:
                print(f"[Execution Error] {execution_error}")

            if execution_output:
                print(execution_output)
            elif execution_success:
                print("(no output)")
        except Exception as ir_err:
            import traceback
            error_details = traceback.format_exc()
            print(f"IR generation error: {str(ir_err)}")
            print("Full traceback:")
            print(error_details)
            execution_output = ""
            execution_success = False
            execution_paused = False
            execution_stdin_consumed = 0
            execution_error = str(ir_err) + "\\n\\nTraceback:\\n" + error_details
            execution_globals = {}
    # IR pipeline execution complete
    
    if error_handler.has_errors():
        error_list = []
        error_details = []
        error_messages = []
        warning_messages = []
        error_markers = []

        print("")
        print("="*80)
        
        sorted_errors = sorted(error_handler.get_errors(), key=lambda e: 0 if getattr(e.severity, "name", "") == "ERROR" else 1)
        for err in sorted_errors:
            error_list.append(str(err))
            severity_label = "ERROR" if err.severity.name == "ERROR" else "WARNING"
            if severity_label == "ERROR":
                error_messages.append(err.message)
            else:
                warning_messages.append(err.message)
            position_info = f" at line {err.line}, column {err.column}" if err.line and err.column else ""
            error_details.append(f"[{severity_label}] {err.message}{position_info}")
            
            position_log = f"Line: {err.line}, Column: {err.column}" if err.line and err.column else "Position: Unknown"
            print(f"{severity_label}: {err.message}")
            print(f"  > {position_log}")
            print(f"  > Error Code: {err.error_code or 'N/A'}")
            if err.node:
                print(f"  > Node Type: {err.node.node_type}")
            print()
            
            if err.line and err.column:
                error_markers.append({
                    "line": err.line,
                    "col": err.column,
                    "value": err.error_code or "semantic_error",
                    "message": err.message,
                    "severity": severity_label
                })
        
        error_count = error_handler.get_error_count()
        warning_count = error_handler.get_warning_count()
        if error_count > 0:
            detailed_message = f"Semantic analysis failed with {error_count} error(s) and {warning_count} warning(s)\\n"
        else:
            detailed_message = f"No semantic errors with {warning_count} warning(s)\\n"
        for detail in error_details:
            detailed_message += f"{detail}\\n"
        
        result = {
            "success": False, 
            "message": detailed_message,
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "execution_output": execution_output,
            "execution_success": execution_success,
            "execution_paused": execution_paused,
            "execution_stdin_consumed": execution_stdin_consumed,
            "execution_error": execution_error,
            "execution_globals": json.dumps(execution_globals),
            "errors": error_list,
            "semantic_errors": json.dumps(error_messages),
            "semantic_warnings": json.dumps(warning_messages),
            "error_markers": json.dumps(error_markers)
        }
    else:
        warning_messages_success = []
        warning_markers_success = []
        if error_handler.has_warnings():
            for warn in error_handler.get_errors():
                if warn.severity.name == "WARNING":
                    warning_messages_success.append(warn.message)
                    if warn.line and warn.column:
                        warning_markers_success.append({
                            "line": warn.line,
                            "col": warn.column,
                            "value": warn.error_code or "semantic_warning",
                            "message": warn.message,
                            "severity": "warning"
                        })
        
        warning_msg = f" with {len(warning_messages_success)} warning(s)" if warning_messages_success else ""
        result = {
            "success": True, 
            "message": f"No semantic errors{warning_msg}",
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "execution_output": execution_output,
            "execution_success": execution_success,
            "execution_paused": execution_paused,
            "execution_stdin_consumed": execution_stdin_consumed,
            "execution_error": execution_error,
            "execution_globals": json.dumps(execution_globals),
            "semantic_warnings": json.dumps(warning_messages_success),
            "error_markers": json.dumps(warning_markers_success)
        }
except SyntaxError as e:
    error_msg = str(e)
    print(f"[PYTHON ERROR] SyntaxError: {error_msg}")
    match = re.search(r'line (\\d+), col (\\d+)', error_msg)
    if match:
        line = int(match.group(1))
        col = int(match.group(2))
        result = {"success": False, "message": error_msg, "error": {"line": line, "col": col, "message": error_msg}}
    else:
        result = {"success": False, "message": error_msg}
except Exception as e:
    import traceback
    error_msg = str(e)
    traceback_str = traceback.format_exc()
    print(f"[PYTHON ERROR] Exception: {error_msg}")
    print(f"[PYTHON ERROR] Traceback:\\n{traceback_str}")
    result = {
        "success": False, 
        "message": f"Semantic analysis failed: {error_msg}",
        "execution_output": "",
        "execution_success": False,
        "execution_paused": False,
        "execution_stdin_consumed": 0,
        "execution_error": error_msg,
        "execution_globals": "{}"
    }

result
`;

/**
 * Python script for syntax analysis
 */
const SYNTAX_PYTHON_SCRIPT = `
import sys
import re
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser

result = None
try:
    lexer = Lexer(code_input)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    parser.parse_program()
    
    result = {"success": True, "message": "No Syntax Error"}
except SyntaxError as e:
    error_msg = str(e)
    match = re.search(r'line (\\d+), col (\\d+)', error_msg)
    if match:
        line = int(match.group(1))
        col = int(match.group(2))
        result = {"success": False, "message": error_msg, "error": {"line": line, "col": col, "message": error_msg}}
    else:
        result = {"success": False, "message": error_msg}
except Exception as e:
    result = {"success": False, "message": f"Syntax analysis failed: {str(e)}"}

result
`;

/**
 * Python script for lexical analysis
 */
const LEXICAL_PYTHON_SCRIPT = `
from app.lexer.lexer import Lexer

lexer = Lexer(code_input)
tokenize = lexer.tokenize()
tokens = []

for token in tokenize:
    if token is None:
        break
    tokens.append({
        "type": token.type,
        "value": token.value or '\\\\0',
        "line": token.line,
        "col": token.col
    })

tokens
`;

export {
	SEMANTIC_PYTHON_SCRIPT,
	SYNTAX_PYTHON_SCRIPT,
	LEXICAL_PYTHON_SCRIPT
};
