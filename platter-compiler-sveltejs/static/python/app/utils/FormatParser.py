


from pathlib import Path
import re
import sys
import subprocess
from collections import OrderedDict


# ============= CONFIGURATION =============
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SOURCES_DIR = PROJECT_ROOT / "static/python/app/utils/sources"
PARSER_DIR = PROJECT_ROOT / "static/python/app/parser"
UTILS_DIR = PROJECT_ROOT / "static/python/app/utils"

PRODUCTIONS_FILE = SOURCES_DIR / "productions.py"
PARSER_PROGRAM_FILE = PARSER_DIR / "parser_program.py"
FIRST_SET_FILE = PARSER_DIR / "first_set.py"

# ============= STEP 1: Run Transformers =============
def run_transformers():
    """Run t_sets and g_prod scripts"""
    print("=" * 60)
    print("STEP 1: Running transformers...")
    print("=" * 60)
    
    # Run PredictSetTransformer and FirstSetTransformer
    print("\n[1/2] Running PredictSetTransformer...")
    subprocess.run(
        [sys.executable, "-m", "app.utils.PredictSetTransformer"],
        cwd=PROJECT_ROOT / "static/python",
        check=True
    )
    
    print("\n[2/2] Running FirstSetTransformer...")
    subprocess.run(
        [sys.executable, "-m", "app.utils.FirstSetTransformer"],
        cwd=PROJECT_ROOT / "static/python",
        check=True
    )
    
    # Run ProductionGenerator
    print("\n[3/3] Running ProductionGenerator...")
    subprocess.run(
        [sys.executable, "-m", "app.utils.ProductionGenerator"],
        cwd=PROJECT_ROOT / "static/python",
        check=True
    )
    
    print("\n✓ Transformers completed successfully!")


# ============= STEP 2: Post-process productions.py =============
def post_process_productions():
    """Apply transformations to generated productions.py"""
    print("\n" + "=" * 60)
    print("STEP 2: Post-processing productions...")
    print("=" * 60)
    
    if not PRODUCTIONS_FILE.exists():
        raise FileNotFoundError(f"productions.py not found at {PRODUCTIONS_FILE}")
    
    content = PRODUCTIONS_FILE.read_text(encoding='utf-8')
    
    # Remove program() function if it exists
    print("\n[1/4] Removing program() function...")
    content = remove_program_function(content)
    
    # Apply renaming transformations
    print("[2/4] Applying <id> → id_ transformations...")
    content = apply_id_transformations(content)
    
    print("[3/4] Applying tail transformations...")
    content = apply_tail_transformations(content)
    
    print("[4/4] Removing unnecessary 'else: pass' statements...")
    content = remove_else_pass_from_tails(content)
    
    # Save processed file
    PRODUCTIONS_FILE.write_text(content, encoding='utf-8')
    print("\n✓ Productions post-processing completed!")
    
    return content


def remove_program_function(content):
    """Remove the program() function from productions"""
    # Match function from "def program(self):" to the next "def " or end of file
    pattern = r'def program\(self\):.*?(?=\ndef [a-z_]+\(self\):|$)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content


def apply_id_transformations(content):
    """Transform <id> references to id_ """
    # Replace function definition
    # content = re.sub(r'\bdef id\(self\):', 'def id_(self):', content)
    
    # Replace FIRST_SET["<id>"] to FIRST_SET["id_"]
    content = re.sub(r'FIRST_SET\["<id_>"\]', 'FIRST_SET["<id>"]', content)
    
    # Replace self.id() calls to self.id_()
    # content = re.sub(r'self\.id\(\)', 'self.id_()', content)
    
    # # Replace PREDICT_SET["<id>"] to PREDICT_SET["id_"]
    # content = re.sub(r'PREDICT_SET\["<id>"\]', 'PREDICT_SET["id_"]', content)
    
    return content


def apply_tail_transformations(content):
    """Apply tail naming transformations: <__tail> → <]_tail>"""
    transformations = {
        '<__tail>': '<]_tail>',
        '<__tail_loop>': '<]_tail_loop>',
        '<]_tail_menu>': '<]_tail_menu>',  # This seems to already be correct
    }
    
    for old, new in transformations.items():
        # Replace in function names
        old_func = old.replace('<', '').replace('>', '').replace('__', '_').replace(']_', '_')
        new_func = new.replace('<', '').replace('>', '').replace('__', '_').replace(']', '')
        
        # More comprehensive replacement
        content = content.replace(f'def {old_func}(self):', f'def {new_func}(self):', 1)
        content = content.replace(f'self.{old_func}()', f'self.{new_func}()')
        
        # Replace in FIRST_SET and PREDICT_SET references
        content = content.replace(f'FIRST_SET["{old}"]', f'FIRST_SET["{new}"]')
        content = content.replace(f'PREDICT_SET["{old}"]', f'PREDICT_SET["{new}"]')
    
    return content


def remove_else_pass_from_tails(content):
    """Remove 'else: pass' from tail functions, but keep pass for empty productions"""
    # Only remove pass from tail functions where the production is empty (=>  )
    # Pattern: finds tail functions with empty production (=> followed by whitespace only)
    # Example: """    X <...tail>	=>	    """
    #          elif ...:
    #              pass
    
    pattern = r'(""".*?<.*?tail.*?>.*?=>\s+""")\s+elif self\.tokens\[self\.pos\]\.type in PREDICT_SET\[.*?\]:\s+pass'
    content = re.sub(pattern, r'\1\n', content, flags=re.MULTILINE)
    
    return content


# ============= STEP 3: Merge into parser_program.py =============
def merge_into_parser_program(productions_content):
    """Replace production functions in parser_program.py"""
    print("\n" + "=" * 60)
    print("STEP 3: Merging productions into parser_program.py...")
    print("=" * 60)
    
    if not PARSER_PROGRAM_FILE.exists():
        raise FileNotFoundError(f"parser_program.py not found at {PARSER_PROGRAM_FILE}")
    
    parser_content = PARSER_PROGRAM_FILE.read_text(encoding='utf-8')
    
    # Find where parse_program function ends
    # We want to keep everything up to and including parse_program, then replace the rest
    match = re.search(r'(.*?def parse_program\(self\):.*?log\.info\("Exit: " \+ self\.tokens\[self\.pos\]\.type\) # J\s*\n)', 
                     parser_content, re.DOTALL)
    
    if not match:
        print("⚠ Warning: Could not find parse_program function end marker. Using alternative method...")
        # Alternative: Find the end of parse_program by looking for the next def
        match = re.search(r'(.*?def parse_program\(self\):.*?)(?=\n\s*def [a-z_]+\(self\):)', 
                         parser_content, re.DOTALL)
    
    if match:
        header = match.group(1)
        
        # Indent all lines in productions_content by 4 spaces to make them class methods
        indented_lines = []
        for line in productions_content.split('\n'):
            if line.strip():  # Only indent non-empty lines
                indented_lines.append('    ' + line)
            else:
                indented_lines.append(line)
        indented_productions = '\n'.join(indented_lines)
        
        # Combine header with indented productions
        new_content = header + "\n" + indented_productions
        
        PARSER_PROGRAM_FILE.write_text(new_content, encoding='utf-8')
        print("\n✓ Successfully merged productions into parser_program.py!")
    else:
        print("✗ Error: Could not determine where to split parser_program.py")
        raise ValueError("Could not find parse_program function boundary")


# ============= STEP 4: Remove duplicates from first_set.py =============
def remove_duplicates_from_first_set():
    """Remove duplicate entries from first_set.py"""
    print("\n" + "=" * 60)
    print("STEP 4: Removing duplicates from first_set.py...")
    print("=" * 60)
    
    if not FIRST_SET_FILE.exists():
        raise FileNotFoundError(f"first_set.py not found at {FIRST_SET_FILE}")
    
    content = FIRST_SET_FILE.read_text(encoding='utf-8')
    
    # Extract the dictionary
    match = re.search(r'FIRST_SET = \{(.*?)\}', content, re.DOTALL)
    if not match:
        print("⚠ Warning: Could not parse FIRST_SET dictionary")
        return
    
    dict_content = match.group(1)
    
    # Parse entries
    entries = OrderedDict()
    pattern = r"'([^']+)':\s*\[(.*?)\](?=,\s*'|\s*$)"
    
    for m in re.finditer(pattern, dict_content, re.DOTALL):
        key = m.group(1)
        values_str = m.group(2)
        
        # Parse values - handle both quoted strings and special items
        values = []
        for val in re.findall(r"'([^']*)'", values_str):
            if val not in values:  # Remove duplicates within each list
                values.append(val)
        
        # Only keep unique keys (first occurrence)
        if key not in entries:
            entries[key] = values
    
    # Rebuild the file
    lines = ["# Auto-generated by predict set generator. Do not edit by hand.\n"]
    lines.append("FIRST_SET = {\n")
    
    for i, (key, values) in enumerate(entries.items()):
        values_str = ", ".join(f"'{v}'" for v in values)
        comma = "," if i < len(entries) - 1 else ""
        lines.append(f"    '{key}': [{values_str}]{comma}\n")
    
    lines.append("}\n")
    
    new_content = "".join(lines)
    FIRST_SET_FILE.write_text(new_content, encoding='utf-8')
    
    print(f"\nRemoved duplicates from first_set.py (found {len(entries)} unique entries)")


# ============= MAIN =============
def main():
    """Main automation workflow"""
    print("\n" + "=" * 60)
    print("CFG UPDATE AUTOMATION")
    print("=" * 60)
    
    try:
        # Step 1: Run transformers
        run_transformers()
        
        # Step 2: Post-process productions
        productions_content = post_process_productions()
        
        # Step 3: Merge into parser_program.py
        merge_into_parser_program(productions_content)
        
        # Step 4: Remove duplicates from first_set.py
        remove_duplicates_from_first_set()
        
        # Step 5: Clean up temporary productions.py file
        if PRODUCTIONS_FILE.exists():
            PRODUCTIONS_FILE.unlink()
            print("\n✓ Cleaned up temporary productions.py")
        
        print("✓ CFG UPDATE COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
