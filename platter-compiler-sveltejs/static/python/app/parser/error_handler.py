from app.parser.cfg_visual import TableDrivenParser

shared_state = {'input_tokens': []}

class ErrorHandler:
  def __init__(self, error_type, tok, expected_toklist=None):
        
        
        grammar_file = "app/utils/sources/test.tsv"

        try:
            parser = TableDrivenParser(grammar_file, shared_state['input_tokens'])
            expected = parser.get_expected()
            d = ", ".join(f"'{e}'" for e in expected)
        except Exception as e:
            print("Error", e)
            d = ""
        
        if not tok:
                raise SyntaxError(f"Syntax Error: Unexpected EOF. Expected {d}.",)        
        errors = {
            "EOF":f"Syntax Error: Unexpected EOF. Expected {d}.",
            "Unexpected_err": f"Syntax Error: Unexpected '{tok.type}' at line {tok.line}, col {tok.col}. Expected {d}.",
            "ExpectedEOF_err": f"Syntax Error: Unexpected token '{tok.type}' after start platter, Expected EOF (line {tok.line}, col {tok.col})",
        }
        raise SyntaxError(errors[error_type])