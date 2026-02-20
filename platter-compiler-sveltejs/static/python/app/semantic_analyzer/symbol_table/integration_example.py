"""
Integration Example: Using Symbol Table with Parsed Platter Code

This example demonstrates how to integrate the symbol table with the actual
Platter parser to perform semantic analysis on real code.
"""

from app.semantic_analyzer.ast.ast_parser_program import parse_program
from app.semantic_analyzer.ast.ast_reader import print_ast
from app.semantic_analyzer.symbol_table import build_symbol_table, print_symbol_table
from app.lexer.lexer import Lexer


def analyze_platter_code(source_code: str, show_ast: bool = False):
    """
    Complete analysis pipeline: Lexer → Parser → Symbol Table
    
    Args:
        source_code: Platter source code string
        show_ast: Whether to print the AST before symbol table
    """
    print("="*70)
    print("SOURCE CODE:")
    print("="*70)
    print(source_code)
    print()
    
    try:
        # Step 1: Lexical Analysis
        print("Step 1: Lexical Analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        print(f"✓ Generated {len(tokens)} tokens")
        print()
        
        # Step 2: Parse to AST
        print("Step 2: Parsing to AST...")
        ast_root = parse_program(source_code)
        print("✓ AST constructed successfully")
        print()
        
        if show_ast:
            print_ast(ast_root)
        
        # Step 3: Build Symbol Table
        print("Step 3: Building Symbol Table...")
        symbol_table = build_symbol_table(ast_root)
        print("✓ Symbol table built")
        print()
        
        # Step 4: Display Results
        print_symbol_table(symbol_table)
        
        return symbol_table
        
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# Example 1: Simple Program with Variables
# ============================================================================

example1 = """
ingredient piece count = 0;
ingredient sip temperature = 98.6;
ingredient flag isReady = true;
ingredient chars message = "Hello";
"""

# ============================================================================
# Example 2: Arrays and Multidimensional Arrays
# ============================================================================

example2 = """
ingredient piece[] numbers;
ingredient sip[][] matrix;
ingredient chars[] names;
"""

# ============================================================================
# Example 3: Table (Struct) Definition
# ============================================================================

example3 = """
table Point {
    ingredient piece x;
    ingredient piece y;
}

table Circle {
    ingredient Point center;
    ingredient sip radius;
}

ingredient Point origin;
ingredient Circle myCircle;
ingredient Point[] points;
"""

# ============================================================================
# Example 4: Function with Local Variables
# ============================================================================

example4 = """
recipe piece add(piece a, piece b) {
    ingredient piece result;
    result = a + b;
    serve result;
}

recipe void printSum() {
    ingredient piece x = 5;
    ingredient piece y = 10;
    ingredient piece sum = add(x, y);
}
"""

# ============================================================================
# Example 5: Scoping and Nested Blocks
# ============================================================================

example5 = """
ingredient piece global = 100;

recipe void testScoping() {
    ingredient piece local = 50;
    
    plate {
        ingredient piece inner = 25;
        local = global + inner;
    }
    
    check (local > 50) {
        ingredient piece blockVar = 10;
        global = global + blockVar;
    }
}
"""

# ============================================================================
# Example 6: Loops and Control Flow
# ============================================================================

example6 = """
recipe void loopTest() {
    ingredient piece i;
    ingredient piece sum = 0;
    
    pass (i = 0; i < 10; i = i + 1) {
        sum = sum + i;
        
        check (sum > 20) {
            stop;
        }
    }
    
    repeat (sum < 100) {
        sum = sum + 1;
    }
}
"""

# ============================================================================
# Example 7: Complex Nested Structures
# ============================================================================

example7 = """
table Address {
    ingredient chars street;
    ingredient chars city;
    ingredient piece zipcode;
}

table Person {
    ingredient chars name;
    ingredient piece age;
    ingredient Address address;
    ingredient piece[] scores;
}

table Company {
    ingredient chars name;
    ingredient Person[] employees;
}

ingredient Company myCompany;

recipe void accessNestedData() {
    ingredient chars employeeName = myCompany.employees[0].name;
    ingredient chars city = myCompany.employees[0].address.city;
    ingredient piece firstScore = myCompany.employees[0].scores[0];
}
"""

# ============================================================================
# Example 8: Error Detection
# ============================================================================

example8_errors = """
// This example contains intentional errors

ingredient undefined_type badVar;     // Error: undefined type
ingredient piece x = 10;
ingredient piece x = 20;               // Error: duplicate declaration

recipe void errorTest() {
    ingredient piece num = "text";     // Error: type mismatch
    ingredient piece result = unknown; // Error: undefined variable
    
    stop;                              // Error: break outside loop
    
    serve "hello";                     // Error: wrong return type
}

recipe piece badReturn() {
    serve;                             // Error: missing return value
}
"""

# ============================================================================
# Example 9: Array and Table Access
# ============================================================================

example9 = """
table Data {
    ingredient piece value;
}

ingredient piece[] numbers;
ingredient Data[][] dataMatrix;

recipe void accessTest() {
    ingredient piece num = numbers[5];
    ingredient piece val = dataMatrix[0][1].value;
    
    // This will generate an error:
    ingredient piece bad = numbers.field;  // Error: array is not a table
}
"""

# ============================================================================
# Example 10: Complete Program
# ============================================================================

example10_complete = """
table Student {
    ingredient chars name;
    ingredient piece id;
    ingredient sip gpa;
}

ingredient Student[] students;
ingredient piece studentCount = 0;

recipe void addStudent(chars name, piece id, sip gpa) {
    ingredient Student newStudent;
    newStudent.name = name;
    newStudent.id = id;
    newStudent.gpa = gpa;
    
    students[studentCount] = newStudent;
    studentCount = studentCount + 1;
}

recipe sip calculateAverageGPA() {
    ingredient sip total = 0.0;
    ingredient piece i;
    
    pass (i = 0; i < studentCount; i = i + 1) {
        total = total + students[i].gpa;
    }
    
    serve total / toSip(studentCount);
}

recipe void printHighAchievers() {
    ingredient piece i;
    
    pass (i = 0; i < studentCount; i = i + 1) {
        check (students[i].gpa >= 3.5) {
            // Print student name (placeholder for actual print)
            ingredient chars name = students[i].name;
        }
    }
}

start plate {
    addStudent("Alice", 1001, 3.8);
    addStudent("Bob", 1002, 3.2);
    addStudent("Charlie", 1003, 3.9);
    
    ingredient sip avg = calculateAverageGPA();
    printHighAchievers();
}
"""


def main():
    """Run all examples"""
    print("\n" + "#"*70)
    print("# SYMBOL TABLE INTEGRATION EXAMPLES")
    print("# Platter Language Semantic Analysis")
    print("#"*70)
    print()
    
    examples = [
        ("Simple Variables", example1),
        ("Arrays and Multidimensional Arrays", example2),
        ("Table (Struct) Definitions", example3),
        ("Functions with Parameters", example4),
        ("Scoping and Nested Blocks", example5),
        ("Loops and Control Flow", example6),
        ("Complex Nested Structures", example7),
        ("Error Detection", example8_errors),
        ("Array and Table Access", example9),
        ("Complete Program", example10_complete),
    ]
    
    for i, (title, code) in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"EXAMPLE {i}: {title}")
        print(f"{'='*70}\n")
        
        analyze_platter_code(code, show_ast=False)
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "#"*70)
    print("# ALL EXAMPLES COMPLETED")
    print("#"*70)


if __name__ == "__main__":
    # Run a single example for quick testing
    print("Running Example: Complex Nested Structures")
    analyze_platter_code(example7, show_ast=False)
    
    # Uncomment to run all examples interactively:
    # main()
