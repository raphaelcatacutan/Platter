"""
Converts the Platter Test Scripts TSV file to Python format for unit testing.
This script reads the TSV file and txt test files, then generates a syntax_tscripts.py file
with test cases in the required format.
"""

import re
import os

def escape_string(s):
    """Escape special characters in string for Python code."""
    # Escape backslashes first, then quotes
    s = s.replace('\\', '\\\\')
    s = s.replace('"""', r'\"\"\"')
    return s

def parse_txt_file(txt_path):
    """Parse a txt file with Number:X, Code:"...", Expected:"..." format."""
    test_cases = []
    
    if not os.path.exists(txt_path):
        return test_cases
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Number:" to get individual test cases
    entries = re.split(r'\nNumber:', content)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        # Add back "Number:" if it was removed by split
        if not entry.startswith('Number:'):
            entry = 'Number:' + entry
        
        # Extract number
        number_match = re.search(r'Number:(\d+)', entry)
        # Extract code
        code_match = re.search(r'Code:"([^"]*)"', entry, re.DOTALL)
        # Extract expected
        expected_match = re.search(r'Expected:"([^"]*)"', entry, re.DOTALL)
        
        if number_match and code_match and expected_match:
            test_cases.append({
                'number': number_match.group(1),
                'code': code_match.group(1),
                'expected_output': expected_match.group(1)
            })
    
    return test_cases

def parse_tsv_manually(tsv_path):
    """Parse TSV file with special handling for embedded newlines in cells."""
    test_cases = []
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by actual line endings
    lines = content.split('\n')
    
    # Skip header
    i = 1
    
    while i < len(lines):
        line = lines[i].rstrip('\r')
        
        # Check if this line starts with a number followed by tab (new entry)
        if re.match(r'^\d+\t', line):
            # Split by tabs to get all columns
            parts = line.split('\t')
            
            number = parts[0].strip()
            code = parts[1] if len(parts) > 1 else ""  # Handle missing columns
            expected = parts[2].strip() if len(parts) > 2 else ""
            
            # Check if code or expected might continue on next line(s)
            j = i + 1
            while j < len(lines):
                next_line = lines[j].rstrip('\r')
                # If next line doesn't start with number+tab and is not empty, it's a continuation
                if next_line and not re.match(r'^\d+\t', next_line):
                    # This is a continuation - could be part of code field or other fields
                    continuation_parts = next_line.split('\t')
                    
                    # If we don't have expected yet and there are multiple parts, 
                    # this might have the expected output
                    if not expected and len(continuation_parts) > 1:
                        # Likely format: <code_cont>\t<expected>\t...
                        code_cont = continuation_parts[0]
                        expected = continuation_parts[1].strip()
                        code += '\n' + code_cont
                    else:
                        # Just code continuation
                        code_cont = continuation_parts[0]
                        code += '\n' + code_cont
                    
                    j += 1
                else:
                    break
            
            # Now strip the complete code
            code = code.strip()
            
            # Move to next entry
            i = j
            
            # Only add if there's actual code
            if number and code:
                test_case = {
                    'number': number,
                    'code': code,
                    'expected_output': expected
                }
                test_cases.append(test_case)
        else:
            i += 1
    
    return test_cases

def generate_python_file(test_cases, output_path):
    """Generate the Python file with test cases."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# Auto-generated from TSV and TXT files. Do not edit manually.\n')
        f.write('# Generated using convert_tsv_to_python.py\n\n')
        f.write('SYNTAX_TSCRIPTS = [\n')
        
        for i, test in enumerate(test_cases):
            # Escape the code string
            code_escaped = escape_string(test['code'])
            expected_escaped = escape_string(test['expected_output'])
            
            f.write('    {\n')
            f.write(f'        "number": {test["number"]},\n')
            f.write(f'        "code": """{code_escaped}""",\n')
            f.write(f'        "expected_output": """{expected_escaped}"""\n')
            f.write('    }')
            
            # Add comma if not the last item
            if i < len(test_cases) - 1:
                f.write(',\n')
            else:
                f.write('\n')
        
        f.write(']\n')

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    syntax_programs_dir = os.path.dirname(script_dir)
    
    # Define paths
    tsv_file = os.path.join(script_dir, "Platter - Test Scripts - Syntax.tsv")
    no_error_file = os.path.join(syntax_programs_dir, "no_error.txt")
    with_error_file = os.path.join(syntax_programs_dir, "with_error.txt")
    output_file = os.path.join(syntax_programs_dir, "syntax_tscripts.py")
    
    # Check if TSV file exists
    if not os.path.exists(tsv_file):
        print(f"Error: TSV file not found at {tsv_file}")
        exit(1)
    
    # Parse all sources
    test_cases = []
    
    # Parse TSV file
    tsv_cases = parse_tsv_manually(tsv_file)
    test_cases.extend(tsv_cases)
    print(f"Loaded {len(tsv_cases)} tests from TSV")
    
    # Parse no_error.txt
    no_error_cases = parse_txt_file(no_error_file)
    test_cases.extend(no_error_cases)
    print(f"Loaded {len(no_error_cases)} tests from no_error.txt")
    
    # Parse with_error.txt
    with_error_cases = parse_txt_file(with_error_file)
    test_cases.extend(with_error_cases)
    print(f"Loaded {len(with_error_cases)} tests from with_error.txt")
    
    # Sort by test number
    test_cases.sort(key=lambda x: int(x['number']))
    
    # Convert to Python file
    generate_python_file(test_cases, output_file)
    
    print(f"\nTotal: {len(test_cases)} test cases converted")
    print(f"Output written to: {output_file}")
    print(f"\nYou can now run the tests using: python -m unittest tests.gad_parser")

def generate_python_file(test_cases, output_path):
    """Generate the Python file with test cases."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# Auto-generated from TSV and TXT files. Do not edit manually.\n')
        f.write('# Generated using convert_tsv_to_python.py\n\n')
        f.write('SYNTAX_TSCRIPTS = [\n')
        
        for i, test in enumerate(test_cases):
            # Escape the code string
            code_escaped = escape_string(test['code'])
            expected_escaped = escape_string(test['expected_output'])
            
            f.write('    {\n')
            f.write(f'        "number": {test["number"]},\n')
            f.write(f'        "code": """{code_escaped}""",\n')
            f.write(f'        "expected_output": """{expected_escaped}"""\n')
            f.write('    }')
            
            # Add comma if not the last item
            if i < len(test_cases) - 1:
                f.write(',\n')
            else:
                f.write('\n')
        
        f.write(']\n')
