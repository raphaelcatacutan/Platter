"""
Table-Driven LL(1) Parser (Based on HTML cfg_visual.html)

This is a Python implementation of the table-driven LL(1) parser algorithm
used in cfg_visual.html. It provides better error messages by computing
context-aware expected tokens based on the full parsing stack.
"""

from pprint import pprint
import subprocess
from app.lexer.token import Token
from app.lexer.lexer import Lexer
from app.utils.FileHandler import run_file

# Global flag to enable/disable clipboard copy on syntax errors
COPY_ERROR_TO_CLIPBOARD = True


def set_clipboard(text):
    """Copy text to clipboard on Windows."""
    if not COPY_ERROR_TO_CLIPBOARD:
        return
    try:
        subprocess.run('clip', input=text.encode('utf-16le'), check=True, shell=True)
    except Exception:
        pass  # Silently fail if clipboard isn't available


class TableDrivenParser:
    def __init__(self, grammar_file, tokens):
        """Initialize parser with grammar and tokens.
        
        Args:
            grammar_file: Path to TSV file containing grammar rules
            tokens: List of Token objects from lexer (will filter whitespace/comments)
        """
        # Filter tokens
        self.tokens = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")]
        
        # Add EOF token
        if self.tokens:
            last_token = self.tokens[-1]
            self.tokens.append(Token("EOF", "$", last_token.line, last_token.col))
        else:
            self.tokens.append(Token("EOF", "$", 1, 1))
        
        # Grammar structures
        self.grammar = {}  # {non_terminal: [[rhs1], [rhs2], ...]}
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
        self.parse_table = {}  # {non_terminal: {terminal: [production]}}
        self.first_sets = {}
        self.follow_sets = {}
        
        # Parse grammar from TSV
        self.parse_grammar(grammar_file)
        self.check_undefined_non_terminals()
        self.build_ll1_table()
    
    def parse_grammar(self, grammar_file):
        """Parse grammar from TSV file format."""
        with open(grammar_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) < 3:
                    continue
                
                # Format: <index>\t<lhs>\t→\t<rhs_tokens...>
                lhs = parts[1].strip()
                
                if not lhs.startswith('<'):
                    continue
                
                if not self.start_symbol:
                    self.start_symbol = lhs
                
                self.non_terminals.add(lhs)
                
                # Get RHS tokens (skip index, lhs, arrow)
                rhs = [t.strip() for t in parts[3:] if t.strip()]
                
                if not self.grammar.get(lhs):
                    self.grammar[lhs] = []
                self.grammar[lhs].append(rhs)
                
                # Collect terminals
                for token in rhs:
                    if not token.startswith('<') and token != 'λ':
                        self.terminals.add(token)
        
        # Convert undefined non-terminals to terminals
        for lhs in list(self.grammar.keys()):
            for rhs in self.grammar[lhs]:
                for token in rhs:
                    if token.startswith('<') and token not in self.non_terminals:
                        self.terminals.add(token)
    
    def check_undefined_non_terminals(self):
        """Check for non-terminals that are referenced but not defined."""
        # Collect all symbols that look like non-terminals from RHS
        referenced = set()
        for lhs in self.grammar.keys():
            for rhs in self.grammar[lhs]:
                for token in rhs:
                    if token.startswith('<') and token.endswith('>'):
                        referenced.add(token)
        
        # Find undefined non-terminals (referenced but not in grammar)
        undefined = referenced - self.non_terminals
        
        if undefined:
            print("\n⚠️  Undefined Non-Terminals (referenced but not defined):")
            for nt in sorted(undefined):
                print(f"   - {nt}")
            print()
    
    def build_ll1_table(self):
        """Build LL(1) parsing table with FIRST/FOLLOW sets."""
        # Initialize
        for nt in self.non_terminals:
            self.first_sets[nt] = set()
            self.follow_sets[nt] = set()
            self.parse_table[nt] = {}
        
        self.follow_sets[self.start_symbol].add('$')
        
        # Compute FIRST sets
        changed = True
        while changed:
            changed = False
            for lhs in self.non_terminals:
                for rhs in self.grammar[lhs]:
                    first_rhs = self.get_first_seq(rhs)
                    for symbol in first_rhs:
                        if symbol not in self.first_sets[lhs]:
                            self.first_sets[lhs].add(symbol)
                            changed = True
        
        # Compute FOLLOW sets
        changed = True
        while changed:
            changed = False
            for lhs in self.non_terminals:
                for rhs in self.grammar[lhs]:
                    trailer = set(self.follow_sets[lhs])
                    
                    # Process RHS from right to left
                    for i in range(len(rhs) - 1, -1, -1):
                        B = rhs[i]
                        
                        if B in self.non_terminals:
                            # Add trailer to FOLLOW(B)
                            for symbol in trailer:
                                if symbol not in self.follow_sets[B]:
                                    self.follow_sets[B].add(symbol)
                                    changed = True
                            
                            # Update trailer
                            first_B = self.first_sets[B]
                            if 'λ' in first_B:
                                trailer.update(first_B - {'λ'})
                            else:
                                trailer = set(first_B)
                        else:
                            if B != 'λ':
                                trailer = {B}
        
        # Fill parse table - PRIORITY FIX (concrete rules first, then lambda)
        for lhs in self.non_terminals:
            # Pass 1: Fill concrete rules
            for rhs in self.grammar[lhs]:
                first_rhs = self.get_first_seq(rhs)
                for terminal in first_rhs:
                    if terminal != 'λ':
                        self.parse_table[lhs][terminal] = rhs
            
            # Pass 2: Fill lambda rules only in empty slots
            for rhs in self.grammar[lhs]:
                first_rhs = self.get_first_seq(rhs)
                if 'λ' in first_rhs:
                    for follow_symbol in self.follow_sets[lhs]:
                        if follow_symbol not in self.parse_table[lhs]:
                            self.parse_table[lhs][follow_symbol] = rhs
    
    def get_first_seq(self, sequence):
        """Compute FIRST set of a sequence of symbols."""
        result = set()
        all_nullable = True
        
        for symbol in sequence:
            if symbol == 'λ' or symbol == '':
                continue
            
            # Terminal
            if symbol not in self.non_terminals:
                result.add(symbol)
                all_nullable = False
                break
            
            # Non-terminal
            first_symbol = self.first_sets[symbol]
            result.update(first_symbol - {'λ'})
            
            if 'λ' not in first_symbol:
                all_nullable = False
                break
        
        if all_nullable:
            result.add('λ')
        
        return result
    
    def parse(self):
        """Run table-driven LL(1) parsing with detailed trace."""
        # Tokenize input
        token_strings = [t.value if t.type == 'EOF' else t.type for t in self.tokens]
        
        # Initialize stack
        stack = ['$', self.start_symbol]
        cursor = 0
        steps = 0
        trace = []
        
        trace.append(f"=== LL(1) Parsing Trace ===")
        trace.append(f"Grammar: {len(self.non_terminals)} non-terminals, {len(self.terminals)} terminals")
        trace.append(f"Input: {len(token_strings) - 1} tokens\n")
        trace.append(f"{'STACK':<40} {'INPUT':<30} {'ACTION':<50}")
        trace.append("-" * 120)
        
        while stack:
            if steps > 1000:
                trace.append("ERROR: Infinite loop protection triggered")
                return False, "\n".join(trace)
            
            steps += 1
            top = stack[-1]
            current = token_strings[cursor] if cursor < len(token_strings) else '$'
            
            # Format for display
            stack_view = ' '.join(stack).replace('<', '').replace('>', '')
            input_view = ' '.join(token_strings[cursor:cursor+10])
            
            # End of input
            if top == '$':
                if current == '$':
                    return True, "No Syntax Error"
                else:
                    expected = self.get_expected_tokens(stack)
                    expected_str = ', '.join([f"'{t}'" for t in expected])
                    error_msg = f"Unexpected '{current}', expected {expected_str}"
                    trace.append(f"{stack_view:<40} {input_view:<30} ERROR: {error_msg:<50}")
                    return False, "\n".join(trace)
            
            # Match terminal
            if top == current:
                stack.pop()
                action = f"✓ Match terminal '{current}'"
                trace.append(f"{stack_view:<40} {input_view:<30} {action:<50}")
                cursor += 1
            # Expand non-terminal
            elif top in self.non_terminals:
                rule = self.parse_table.get(top, {}).get(current)
                
                if not rule:
                    expected = self.get_expected_tokens(stack)
                    expected_list = ', '.join([f"'{t}'" for t in expected])
                    token_obj = self.tokens[cursor] if cursor < len(self.tokens) else self.tokens[-1]
                    error_msg = f"Syntax Error: Unexpected '{current}' at line {token_obj.line}, col {token_obj.col}. Expected {expected_list}."
                    set_clipboard(f":{token_obj.line}:{token_obj.col}")
                    return False, error_msg
                
                stack.pop()
                
                # Push RHS in reverse (skip λ)
                if not (len(rule) == 1 and rule[0] == 'λ'):
                    for i in range(len(rule) - 1, -1, -1):
                        stack.append(rule[i])
                
                rule_str = f"Expand {top} → {' '.join(rule) if rule and rule[0] != 'λ' else 'ε'}"
                trace.append(f"{stack_view:<40} {input_view:<30} {rule_str:<50}")
            else:
                # Unexpected situation
                expected = self.get_expected_tokens(stack)
                expected_list = ', '.join([f"'{t}'" for t in expected])
                token_obj = self.tokens[cursor] if cursor < len(self.tokens) else self.tokens[-1]
                error_msg = f"Syntax Error: Unexpected '{current}' at line {token_obj.line}, col {token_obj.col}. Expected {expected_list}."
                set_clipboard(f":{token_obj.line}:{token_obj.col}")
                return False, error_msg
        
        return False, "Unexpected end of parse"
    
    def get_expected_tokens(self, stack):
        """Compute expected tokens based on current stack (context-aware).
        
        This is the key difference from the recursive descent parser!
        We compute FIRST of the remaining parse sequence.
        """
        # Reverse stack to get proper sequence
        sequence = list(reversed(stack))
        expected = self.get_first_seq(sequence)
        
        # Filter out lambda
        return [t for t in expected if t not in ('λ', '')]
    
    def get_expected(self):
        # Tokenize input
        token_strings = [t.value if t.type == 'EOF' else t.type for t in self.tokens]
        
        # Initialize stack
        stack = ['$', self.start_symbol]
        cursor = 0
        steps = 0
        
        while stack:
            if steps > 1000:
                return []
            
            steps += 1
            top = stack[-1]
            current = token_strings[cursor] if cursor < len(token_strings) else '$'
            
            # End of input
            if top == '$':
                if current == '$':
                    return []  # No error
                else:
                    expected = self.get_expected_tokens(stack)
                    return expected
            
            # Match terminal
            if top == current:
                stack.pop()
                cursor += 1
            # Expand non-terminal
            elif top in self.non_terminals:
                rule = self.parse_table.get(top, {}).get(current)
                
                if not rule:
                    expected = self.get_expected_tokens(stack)
                    return expected
                
                stack.pop()
                
                # Push RHS in reverse (skip λ)
                if not (len(rule) == 1 and rule[0] == 'λ'):
                    for i in range(len(rule) - 1, -1, -1):
                        stack.append(rule[i])
            else:
                # Unexpected situation
                expected = self.get_expected_tokens(stack)
                return expected
        
        return []


if __name__ == "__main__":
    """Test the table-driven parser."""

    filepath = "./tests/sample_program.txt"
    include_whitespace = False # choice == 'y'


    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    tokens = [
        t for t in tokens
        if t.type not in ("comment", "space", "newline", "tab") or include_whitespace
    ]
    
    grammar_file = "app/utils/sources/test.tsv"
    try:
        print("\n\nLEXICAL:")
        pprint(tokens)
        print((" ".join(t.type for t in tokens if not "comment" in t.type )))
        set_clipboard((" ".join(t.type for t in tokens if not "comment" in t.type )))   
        parser = TableDrivenParser(grammar_file, tokens)
        a, e = parser.parse()
        print("\n\nSYNTAX:")
        print(e)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
