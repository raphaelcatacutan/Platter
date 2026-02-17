"""
Format and post-process the generated AST parser.
Similar to FormatParser but for AST parser generation.
"""

from pathlib import Path
import sys
import subprocess
import re
from collections import OrderedDict


# ============= CONFIGURATION =============
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SOURCES_DIR = PROJECT_ROOT / "static/python/app/utils/sources"
AST_DIR = PROJECT_ROOT / "static/python/app/semantic_analyzer/ast"

AST_PARSER_FILE = AST_DIR / "ast_parser_program.py"

# ============= STEP 1: Run AST Generator =============
def run_ast_generator():
    """Run ASTProductionGenerator"""
    print("=" * 60)
    print("STEP 1: Running AST generator...")
    print("=" * 60)
    
    print("\n[1/1] Running ASTProductionGenerator...")
    subprocess.run(
        [sys.executable, "-m", "app.utils.ASTProductionGenerator"],
        cwd=PROJECT_ROOT / "static/python",
        check=True
    )
    
    print("\n✓ AST Generator completed successfully!")


# ============= STEP 2: Post-process ast_parser_program.py =============
def post_process_ast_parser():
    """Apply transformations to generated ast_parser_program.py"""
    print("\n" + "=" * 60)
    print("STEP 2: Post-processing AST parser...")
    print("=" * 60)
    
    if not AST_PARSER_FILE.exists():
        print(f"ERROR: {AST_PARSER_FILE} not found!")
        return None
    
    content = AST_PARSER_FILE.read_text(encoding='utf-8')
    
    # Apply naming transformations
    print("\n[1/3] Applying <id> → id_ transformations...")
    content = apply_id_transformations(content)
    
    print("[2/3] Applying tail transformations...")
    content = apply_tail_transformations(content)
    
    print("[3/3] Indenting production functions to be class methods...")
    content = indent_production_functions(content)
    
    # Save processed file
    AST_PARSER_FILE.write_text(content, encoding='utf-8')
    print("\n✓ AST Parser post-processing completed!")
    
    return content


def apply_id_transformations(content):
    """Transform <id> references to id_ """
    # Replace FIRST_SET["<id_>"] to FIRST_SET["<id>"]
    content = re.sub(r'FIRST_SET\["<id_>"\]', 'FIRST_SET["<id>"]', content)
    return content


def apply_tail_transformations(content):
    """Apply tail naming transformations"""
    transformations = {
        '<__tail>': '<]_tail>',
        '<__tail_loop>': '<]_tail_loop>',
        '<]_tail_menu>': '<]_tail_menu>',
    }
    
    for old, new in transformations.items():
        old_func = _safe_func_name(old)
        new_func = _safe_func_name(new)
        
        if old_func != new_func:
            content = re.sub(rf'\bdef {old_func}\(self\):', f'def {new_func}(self):', content)
            content = re.sub(rf'self\.{old_func}\(\)', f'self.{new_func}()', content)
    
    return content


def indent_production_functions(content):
    """Indent production functions after parse_program to make them class methods"""
    # Find where parse_program ends (look for the else clause and its closing)
    # Pattern: find parse_program method, then find where it ends
    match = re.search(
        r'(.*?def parse_program\(self\):.*?else:\s*self\.parse_token\(self\.error_arr\)\s*\n)',
        content, 
        re.DOTALL
    )
    
    if not match:
        print("⚠ Warning: Could not find parse_program method end. Skipping indentation.")
        return content
    
    header = match.group(1)
    remaining = content[len(header):]
    
    # Indent all remaining lines by 4 spaces (to make them class methods)
    indented_lines = []
    for line in remaining.split('\n'):
        if line.strip():  # Only indent non-empty lines
            indented_lines.append('    ' + line)
        else:
            indented_lines.append(line)
    
    indented_remaining = '\n'.join(indented_lines)
    
    # Combine header with indented productions
    return header + '\n' + indented_remaining


def _safe_func_name(nonterminal: str) -> str:
    """Convert nonterminal to safe function name"""
    import keyword
    name = nonterminal.strip('<>')
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not name:
        name = "_"
    if name[0].isdigit():
        name = "_" + name
    if keyword.iskeyword(name) or name in dir(__builtins__):
        name = name + "_"
    return name


# ============= MAIN =============
def main():
    print("\n" + "=" * 60)
    print("FORMAT AST PARSER - Build Backend AST Components")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Run AST generator
        run_ast_generator()
        
        # Step 2: Post-process
        post_process_ast_parser()
        
        print("\n" + "=" * 60)
        print("✓ AST PARSER BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ BUILD FAILED: {e}")
        print("=" * 60 + "\n")
        raise


if __name__ == "__main__":
    main()
