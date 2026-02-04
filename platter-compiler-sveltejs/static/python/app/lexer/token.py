class Token:
    """Represents a token with its type, value, line number, and column."""

    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"{self.type:<25} | line={self.line:<4} | col={self.col:<4} | {self.value :<25}"

    InvalidCharacter = "Invalid Character"
    InvalidLexeme = "Invalid Lexeme"
    InvalidLexemeExceeds = "Invalid Lexeme Exceeds"
    InvalidLexemeReserved = "Invalid Reserved Word Delimeter"