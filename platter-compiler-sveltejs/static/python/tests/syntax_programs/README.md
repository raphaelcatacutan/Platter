# Platter Parser Test Framework

This directory contains the complete test framework for the Platter language parser.

## Directory Structure

```
syntax_programs/
├── tsv/
│   ├── Platter - Test Scripts - Syntax.tsv  # Master TSV file with test cases
│   └── convert_tsv_to_python.py             # Conversion script
├── no_error.txt                              # Additional test cases (no errors)
├── with_error.txt                            # Additional test cases (with errors)
├── syntax_tscripts.py                        # Auto-generated test data (DO NOT EDIT)
├── test_results.txt                          # Test execution results
└── README.md                                 # This file
```

## Files

- **tsv/Platter - Test Scripts - Syntax.tsv**: The master TSV file containing all test cases from the spreadsheet
- **tsv/convert_tsv_to_python.py**: Conversion script that generates Python test data from TSV and TXT sources
- **no_error.txt**: Additional test cases in simple text format (expects no syntax errors)
- **with_error.txt**: Additional test cases in simple text format (expects syntax errors)
- **syntax_tscripts.py**: Auto-generated Python file with all test cases (DO NOT EDIT MANUALLY)
- **test_results.txt**: Output file containing detailed test results (generated after each test run)

## Test Case Format

### TSV Format
The TSV file has the following columns:
- **Number**: Test case number
- **Test Case/Test Scenario**: The Platter code to test
- **Expected Output**: Expected parser output ("No Syntax Error" or "Syntax Error: ...")
- **Actual Output**: (Not used by automated tests, for manual tracking)
- **Test Result**: (Not used by automated tests, for manual tracking)
- **CFG**: (Not used by automated tests, for manual tracking)

### TXT Format
The TXT files use this format:
```
Number:1
Code:"start(){}"
Expected:"No Syntax Error"
```

## Workflow

### 1. Adding/Updating Test Cases

You can add test cases in either format:

**Option A: Edit the TSV file**
```
tsv/Platter - Test Scripts - Syntax.tsv
```

**Option B: Edit the TXT files**
- For tests expecting no errors: `no_error.txt`
- For tests expecting errors: `with_error.txt`

### 2. Converting to Python

After updating any test source file, regenerate the Python test data:

```powershell
cd tests/syntax_programs/tsv
python convert_tsv_to_python.py
```

This will:
- Parse the TSV file
- Parse both TXT files
- Merge all test cases
- Sort by test number
- Generate `syntax_tscripts.py` in the `syntax_programs` directory

### 3. Running Tests

**Using npm (recommended):**
```powershell
cd platter-compiler-webapp
npm test
```

**Using Python directly:**
```powershell
cd platter-compiler-sveltejs/static/python
python -m unittest discover -s tests -p "ga_*.py" -v
```

**Running specific test file:**
```powershell
python -m unittest tests.ga_parser
# or
python -m unittest tests.gad_parser
```

## Test Output

### Console Output
The test framework provides clean console output without debug logs:
- Test execution summary
- Count of passed/failed tests
- Path to detailed results file

### Test Results File
Detailed results are written to `test_results.txt` in this directory.

Format:
```
======================================================================
TEST SUMMARY: 56/134 tests passed
======================================================================

[FAILED] Test #1
----------------------------------------------------------------------
Code:
   1 | flag of x = (x + 1) * ("HELLO") > 1; # not allowed start() {}

Expected: Syntax Error: Unexpected 'chars_lit' at line 1, col 24. Expected '(', 'search', 'size', 'piece_lit', 'fact', 'pow', 'id', 'topiece'.
Actual:   Syntax Error: Unexpected 'chars_lit' at line 1, col 24. Expected 'topiece', 'size', 'search', 'fact', 'pow', 'piece_lit', 'id', '('.
======================================================================
```

Each failed test shows:
- Test number
- The code being tested with line numbers
- Expected output
- Actual output

## GitHub Workflows

The tests are automatically run in GitHub Actions via `.github/workflows/run-tests.yml`:
- Runs on push and pull requests
- Executes: `python -m unittest discover -s tests -p "ga_*.py" -v`
- Both `ga_parser.py` and `ga_lexer.py` are discovered and tested

## Notes

- Debug logs from the parser are suppressed during testing
- Test numbers should be unique across all sources
- The conversion script merges and sorts tests by number
- Results are always written to `syntax_programs/test_results.txt`
- The auto-generated files should not be edited manually
