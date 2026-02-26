"""
Code Generation Examples

Demonstrates the complete compilation pipeline from source code
through lexing, parsing, AST, IR generation, optimization, and
finally code generation for the Platter Virtual Machine.
"""

import sys
import os

# Add parent directories to path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)
sys.path.insert(0, app_dir)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.optimizer_manager import OptimizerManager, OptimizationLevel
from app.code_generation.code_generator import CodeGenerator
from app.code_generation.code_emitter import CodeEmitter, save_code


def compile_to_target_code(source_code: str, optimize: bool = True, 
                           optimization_level: int = OptimizationLevel.STANDARD,
                           verbose: bool = True):
    """
    Complete compilation pipeline
    
    Args:
        source_code: Platter source code
        optimize: Whether to optimize IR
        optimization_level: Optimization level (O0-O3)
        verbose: Print progress information
        
    Returns:
        CodeSection with generated target code
    """
    try:
        if verbose:
            print("\n" + "="*70)
            print("PLATTER COMPILER - FULL COMPILATION PIPELINE")
            print("="*70)
        
        # Step 1: Lexical Analysis
        if verbose:
            print("\n[Step 1/6] Lexical Analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        if verbose:
            print(f"  [OK] Generated {len(tokens)} tokens")
        
        # Step 2: Parsing & AST Construction
        if verbose:
            print("\n[Step 2/6] Parsing & AST Construction...")
        ast_parser = ASTParser(tokens)
        ast = ast_parser.parse_program()
        if verbose:
            print(f"  [OK] AST constructed")
        
        # Step 3: IR Generation
        if verbose:
            print("\n[Step 3/6] Intermediate Code Generation...")
        ir_gen = IRGenerator()
        tac_instructions, quad_table = ir_gen.generate(ast)
        if verbose:
            print(f"  [OK] Generated {len(tac_instructions)} TAC instructions")
        
        # Step 4: Optimization (optional)
        if optimize:
            if verbose:
                print(f"\n[Step 4/6] Code Optimization (Level {optimization_level})...")
            optimizer = OptimizerManager(optimization_level)
            tac_instructions = optimizer.optimize_tac(tac_instructions)
            if verbose:
                stats = optimizer.get_stats()
                print(f"  [OK] {stats.get('total_changes', 0)} optimizations applied")
        else:
            if verbose:
                print("\n[Step 4/6] Code Optimization... SKIPPED")
        
        # Step 5: Code Generation
        if verbose:
            print("\n[Step 5/6] Target Code Generation...")
        code_gen = CodeGenerator()
        code_section = code_gen.generate_from_tac(tac_instructions)
        if verbose:
            print(f"  [OK] Generated {len(code_section)} target instructions")
        
        # Step 6: Code Emission
        if verbose:
            print("\n[Step 6/6] Code Emission...")
        emitter = CodeEmitter(code_section)
        if verbose:
            print(f"  [OK] Code ready for output")
        
        if verbose:
            print("\n" + "="*70)
            print("COMPILATION SUCCESSFUL!")
            print("="*70 + "\n")
        
        return code_section, emitter
        
    except Exception as e:
        print(f"\n[ERROR] Compilation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def example_simple_program():
    """Example 1: Simple arithmetic program"""
    print("\n" + "="*80)
    print("EXAMPLE 1: SIMPLE ARITHMETIC PROGRAM")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 10;
    piece of y = 20;
    piece of sum = x + y;
    serve sum;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    code_section, emitter = compile_to_target_code(source_code, optimize=True)
    
    if code_section:
        print("\n[GENERATED CODE]")
        print(emitter.emit_text(include_addresses=True))
        
        print("\n" + emitter.emit_statistics())


def example_conditional():
    """Example 2: Conditional statements"""
    print("\n" + "="*80)
    print("EXAMPLE 2: CONDITIONAL STATEMENTS")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 15;
    piece of result = 0;
    
    check (x > 10) {
        result = x * 2;
    }
    
    serve result;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    code_section, emitter = compile_to_target_code(source_code, optimize=True)
    
    if code_section:
        print("\n[GENERATED CODE]")
        print(emitter.emit_text(include_addresses=True))


def example_loops():
    """Example 3: Loop structures"""
    print("\n" + "="*80)
    print("EXAMPLE 3: LOOPS")
    print("="*80)
    
    source_code = """
start() {
    piece of sum = 0;
    piece of i = 0;
    
    repeat (i < 5) {
        sum = sum + i;
        i = i + 1;
    }
    
    serve sum;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    code_section, emitter = compile_to_target_code(source_code, optimize=True)
    
    if code_section:
        print("\n[GENERATED CODE]")
        print(emitter.emit_text(include_addresses=True))


def example_with_optimization_comparison():
    """Example 4: Compare unoptimized vs optimized code"""
    print("\n" + "="*80)
    print("EXAMPLE 4: OPTIMIZATION COMPARISON")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 2 + 3;
    piece of y = x * 1;
    piece of z = y + 0;
    piece of unused = 100;
    piece of result = z * 2;
    serve result;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    # Unoptimized
    print("\n" + "-"*70)
    print("[WITHOUT OPTIMIZATION]")
    print("-"*70)
    code_section_unopt, emitter_unopt = compile_to_target_code(
        source_code, optimize=False, verbose=False
    )
    if code_section_unopt:
        print(emitter_unopt.emit_text(include_addresses=True))
        print(f"\nTotal Instructions: {len(code_section_unopt)}")
    
    # Optimized
    print("\n" + "-"*70)
    print("[WITH OPTIMIZATION (O2)]")
    print("-"*70)
    code_section_opt, emitter_opt = compile_to_target_code(
        source_code, optimize=True, optimization_level=OptimizationLevel.STANDARD,
        verbose=False
    )
    if code_section_opt:
        print(emitter_opt.emit_text(include_addresses=True))
        print(f"\nTotal Instructions: {len(code_section_opt)}")
    
    if code_section_unopt and code_section_opt:
        reduction = len(code_section_unopt) - len(code_section_opt)
        percentage = (reduction / len(code_section_unopt)) * 100
        print(f"\nCode Size Reduction: {reduction} instructions ({percentage:.1f}%)")


def example_save_to_files():
    """Example 5: Save generated code to files"""
    print("\n" + "="*80)
    print("EXAMPLE 5: SAVE CODE TO FILES")
    print("="*80)
    
    source_code = """
start() {
    piece of a = 10;
    piece of b = 20;
    piece of max = 0;
    
    check (a > b) {
        max = a;
    } alternate {
        max = b;
    }
    
    serve max;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    code_section, emitter = compile_to_target_code(source_code, optimize=True, verbose=False)
    
    if code_section:
        # Save to files
        output_dir = os.path.dirname(os.path.abspath(__file__))
        base_filename = os.path.join(output_dir, "generated_code")
        
        print("\n[SAVING CODE TO FILES]")
        save_code(code_section, base_filename)
        
        print("\n[CODE PREVIEW]")
        print(emitter.emit_text(include_addresses=True)[:500] + "...")


def main():
    """Run all examples"""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "PLATTER COMPILER - CODE GENERATION EXAMPLES".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    
    try:
        example_simple_program()
        example_conditional()
        example_loops()
        example_with_optimization_comparison()
        example_save_to_files()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
