from pprint import pprint

import logging as log
from pprint import pprint
import subprocess
import sys
from app.lexer.token import Token
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser

COPY_ERROR_TO_CLIPBOARD = True


def set_clipboard(text):
    if not COPY_ERROR_TO_CLIPBOARD:
        return
    try: subprocess.run('clip', input=text.encode('utf-16le'), check=True, shell=True)
    except Exception:
        pass  

if __name__ == "__main__":
    filepath = sys.argv[1]
    include_whitespace = False 


    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    tokens = [
        t for t in tokens
        if t.type not in ("comment", "space", "newline", "tab") or include_whitespace
    ]
    
    try:
        print("\n\nLEXICAL:")
        pprint(tokens)
        print((" ".join(t.type for t in tokens if not "comment" in t.type )))
        set_clipboard((" ".join(t.type for t in tokens if not "comment" in t.type )))   
        
        
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
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
