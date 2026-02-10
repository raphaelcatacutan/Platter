from app.lexer.lexer import Lexer
from app.lexer.token import Token
from app.parser.error_handler import ErrorHandler
from app.parser.predict_set import PREDICT_SET
from app.parser.predict_set_m import PREDICT_SET_M 
from app.utils.FileHandler import run_file
import logging as log

# To disable logs, set level=log.CRITICAL. 
# To enable logs, set level=log.DEBUG
log.basicConfig(level=log.DEBUG, format='%(levelname)s: <%(funcName)s> | %(message)s') # J

class Parser():
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")] # filter out ws and comments
        if not self.tokens: 
            raise ErrorHandler("EOF", None, PREDICT_SET["<program>"])
        
        # Add EOF token at the end to prevent index out of range errors
        last_token = self.tokens[-1]
        self.tokens.append(Token("EOF", "EOF", last_token.line, last_token.col))
        
        self.pos = 0
        # Track parenthesis and bracket balancing
        self.paren_counter = 0
        self.bracket_counter = 0
    
    def parse_token(self, tok):
        """Parse and consume a specific token type"""
        if self.pos >= len(self.tokens):
            raise ErrorHandler("EOF", None, tok)    
        
        if self.tokens[self.pos].type == tok: 
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: MATCH!") # J
            
            # Track opening parenthesis and brackets
            if tok == '(':
                self.paren_counter += 1
            elif tok == '[':
                self.bracket_counter += 1
            # Track closing parenthesis and brackets
            elif tok == ')':
                self.paren_counter -= 1
            elif tok == ']':
                self.bracket_counter -= 1
            
            self.pos += 1

        else:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: INVALID!\n") # J
            
            # Filter out closing delimiters from expected tokens if there are no unclosed pairs
            filtered_tok = tok
            if isinstance(tok, list):
                # If tok is a list of expected tokens, filter it
                filtered_tok = [t for t in tok if not ((t == ')' and self.paren_counter <= 0) or (t == ']' and self.bracket_counter <= 0))]
            elif tok == ')' and self.paren_counter <= 0:
                # If expecting only ')', but no unclosed '(', don't show it
                filtered_tok = []
            elif tok == ']' and self.bracket_counter <= 0:
                # If expecting only ']', but no unclosed '[', don't show it
                filtered_tok = []
            
            raise ErrorHandler("Unexpected_err", self.tokens[self.pos], filtered_tok if filtered_tok else tok)

    def parse_program(self):
        """ 1 <program> -> <global_decl> <recipe_decl> start() <platter>"""
        # Parse global declarations
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['piece', 'chars', 'sip', 'flag', 'table', 'id']:
            self.global_decl()
        
        # Parse recipe declarations (prepare functions)
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['prepare']:
            self.recipe_decl()

        # Parse start() platter
        if self.pos >= len(self.tokens):
            raise ErrorHandler("EOF", None, "start")
        
        self.parse_token("start")
        self.parse_token("(")
        self.parse_token(")")
        self.platter()
        
        # Ensure we've consumed all tokens (should be at EOF token now)
        if self.pos < len(self.tokens) and self.tokens[self.pos].type != "EOF":
            raise ErrorHandler("ExpectedEOF_err", self.tokens[self.pos], None)
    
    def global_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 2 <global_decl>	=>	piece	<piece_decl>	<global_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<global_decl>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.global_decl()

            """ 3 <global_decl>	=>	chars	<chars_decl>	<global_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.global_decl()

            """ 4 <global_decl>	=>	sip	<sip_decl>	<global_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.global_decl()
            
            """ 5 <global_decl>	=>	flag	<flag_decl>	<global_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.global_decl()            

            """ 6 <global_decl>	=>	<table_prototype>	<global_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_4"]:
            self.table_prototype()
            self.global_decl()

            """ 7 <global_decl>	=>	id	<table_decl>	<global_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_5"]:
            self.parse_token("id")
            self.table_decl()
            self.global_decl()

            """ 8 <global_decl>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_6"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<global_decl>"])
        
        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 9 <piece_decl>	=>	of	<piece_id>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_decl>"]:
            self.parse_token("of")
            self.piece_id()
            self.parse_token(";")
        
            """ 10 <piece_decl>	=>	<decl_type>	"""
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_decl>_1"]:
            self.decl_type()
            
        else: self.parse_token(PREDICT_SET_M["<piece_decl>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J
        
        """ 11 <piece_id>	    =>	id	<piece_ingredient_init>	<piece_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id>"]:
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 12 <piece_ingredient_init>	=>	=	<strict_piece_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """ 13 <piece_ingredient_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<piece_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 14 <strict_piece_expr>	=>	<strict_piece_term>	<strict_piece_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr>"]:
            self.strict_piece_term()
            self.strict_piece_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 15 <strict_piece_term>	=>	<strict_piece_factor>	<strict_piece_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term>"]:
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_term>"])
        
        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 16 <strict_piece_factor>	=>	<ret_piece> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>"]:
            self.ret_piece()
            
            """ 17 <strict_piece_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_1"]:
            self.id_()

            """ 18 <strict_piece_factor>	=>	(	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_2"]:
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<strict_piece_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_piece(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 19 <ret_piece>	=>	topiece	(	<any_expr>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_piece>"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
        
            """ 20 <ret_piece>	=>	size	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_1"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 21 <ret_piece>	=>	search	(	<strict_array_expr>	,	<value>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_2"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")
        
            """ 22 <ret_piece>	=>	fact	(	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_3"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 23 <ret_piece>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_4"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """ 24 <ret_piece>	=>	piece_lit """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_5"]:
            self.parse_token("piece_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_piece>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def any_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 25 <any_expr>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<any_expr>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()
        
            """ 26 <any_expr>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()
            
            """ 27 <any_expr>	=>	<ret_chars>	<chars_add_tail>	<chars_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_rel_gate()
        
            """ 28 <any_expr>	=>	<ret_flag>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            
            """ 29 <any_expr>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
            
            """ 30 <any_expr>	=>	(	<paren_dispatch> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_5"]:
            self.parse_token("(")
            self.paren_dispatch()
            
            """ 31 <any_expr>	=>	not	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_6"]:
            self.parse_token("not")
            self.must_be_flag()

        else: self.parse_token(PREDICT_SET_M["<any_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 32 <piece_mult_tail>	=>	*	<piece_factor>	<piece_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>"]:
            self.parse_token("*")
            self.piece_factor()
            self.piece_mult_tail()
        
            """ 33 <piece_mult_tail>	=>	/	<piece_factor>	<piece_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_1"]:
            self.parse_token("/")
            self.piece_factor()
            self.piece_mult_tail()
            
            """ 34 <piece_mult_tail>	=>	%	<piece_factor>	<piece_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_2"]:
            self.parse_token("%")
            self.piece_factor()
            self.piece_mult_tail()
            
            """ 35 <piece_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_3"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<piece_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 36 <piece_factor>	=>	<ret_piece> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_factor>"]:
            self.ret_piece()
            
            """ 37 <piece_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_factor>_1"]:
            self.id_()
            
            """ 38 <piece_factor>	=>	(	<piece_inner_dispatch> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_factor>_2"]:
            self.parse_token("(")
            self.piece_inner_dispatch()

        else: self.parse_token(PREDICT_SET_M["<piece_factor>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J
        
        """ 39 <id>	=>	id	<id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<id>"]:
            self.parse_token("id")
            self.id_tail()

            """ 40 <id> => <ret_array> <array_accessor> """
        elif self.tokens[self.pos].type in PREDICT_SET["<id>_1"]:
            self.ret_array()
            self.array_accessor()
        else: self.parse_token(PREDICT_SET_M["<id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 40 <id_tail>	=>	<call_tailopt>	"""
        if self.tokens[self.pos].type in PREDICT_SET["<id_tail>"]:
            self.call_tailopt()
        
            """ 41 <id_tail>	=>	<accessor_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_tail>_1"]:
            self.accessor_tail()

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tailopt(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 42 <call_tailopt>	=>	(	<flavor>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")
            
            """ 43 <call_tailopt>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<call_tailopt>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 44 <flavor>	=>	<value>	<flavor_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor>"]:
            self.value()
            self.flavor_tail()
            
            """ 45 <flavor>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flavor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def value(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 46 <value>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<value>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()
            
            """ 47 <value>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()
            
            """ 48 <value>	=>	<ret_chars>	<chars_add_tail>	<chars_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_rel_gate()
            
            """ 49 <value>	=>	<ret_flag>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            
            """ 50 <value>	=>	(	<paren_dispatch> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_4"]:
            self.parse_token("(")
            self.paren_dispatch()
            
            """ 51 <value>	=>	not	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_5"]:
            self.parse_token("not")
            self.must_be_flag()
            
            """ 52 <value>	=>	[	<notation_val>	] """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_6"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")
            
            """ 53 <value>	=>	<ret_array> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_7"]:
            self.ret_array()
            
            """ 54 <value>	=>	id	<id_tail>   <univ_mult_tail>	<univ_add_tail>	<univ_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_8"]:
            self.parse_token("id")
            self.id_tail()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
        else: self.parse_token(PREDICT_SET_M["<value>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def notation_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 156 <notation_val>	=>	<array_element> """
        if self.tokens[self.pos].type in PREDICT_SET["<notation_val>"]:
            self.array_element()
            
            """ 157 <notation_val>	=>	id	<array_or_table> """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_1"]:
            self.parse_token("id")
            self.array_or_table()
            
            """ 158 <notation_val>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<notation_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 159 <array_element>	=>	piece_lit	<element_value_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element>"]:
            self.parse_token("piece_lit")
            self.element_value_tail()
            
            """ 160 <array_element>	=>	sip_lit	<element_value_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_1"]:
            self.parse_token("sip_lit")
            self.element_value_tail()
            
            """ 161 <array_element>	=>	flag_lit	<element_value_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_2"]:
            self.parse_token("flag_lit")
            self.element_value_tail()
            
            """ 162 <array_element>	=>	chars_lit	<element_value_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_3"]:
            self.parse_token("chars_lit")
            self.element_value_tail()
            
            """ 163 <array_element>	=>	[	<notation_val>	]	<element_value_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_4"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")
            self.element_value_tail()

        else: self.parse_token(PREDICT_SET_M["<array_element>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_value_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 164 <element_value_tail>	=>	,	<array_element_id> """
        if self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>"]:
            self.parse_token(",")
            self.array_element_id()
            
            """ 165 <element_value_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<element_value_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 166 <array_element_id>	=>	id	<element_value_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_id>"]:
            self.parse_token("id")
            self.element_value_tail()
            
            """ 167 <array_element_id>	=>	<array_element> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_1"]:
            self.array_element()
            
            """ 168 <array_element_id>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<array_element_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_sip(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 85 <ret_sip>	=>	sqrt	(	<strict_piece_expr>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_sip>"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 86 <ret_sip>	=>	rand	( ) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_1"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")
            
            """ 87 <ret_sip>	=>	tosip	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_2"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            
            """ 88 <ret_sip>	=>	sip_lit """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_3"]:
            self.parse_token("sip_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_sip>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_flag(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 151 <ret_flag>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_flag>"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")
            
            """ 152 <ret_flag>	=>	toflag	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_1"]:
            self.parse_token("toflag")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            
            """ 153 <ret_flag>	=>	flag_lit """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_2"]:
            self.parse_token("flag_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_flag>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_datas_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 154 <strict_datas_expr>	=>	[	<notation_val>	] """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")
            
            """ 155 <strict_datas_expr>	=>	<id>    <id_tail>   """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_1"]:
            self.id_()
            self.id_tail()
            
            """ 156 <strict_datas_expr>	=>	<ret_array>   """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_2"]:
            self.ret_array()

        else: self.parse_token(PREDICT_SET_M["<strict_datas_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_array(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 250 <ret_array>	=>	append	(	<strict_array_expr>	,	<value>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_array>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")
            
            """ 251 <ret_array>	=>	sort	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_1"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 252 <ret_array>	=>	reverse	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_2"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 253 <ret_array>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_3"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<ret_array>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_array_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 254 <strict_array_expr>	=>	[	<array_element_id>	] """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>"]:
            self.parse_token("[")
            self.array_element_id()
            self.parse_token("]")
            
            """ 255 <strict_array_expr>	=>	<id>    <id_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_1"]:
            self.id_()
            self.id_tail()
        
            """ 256 <strict_array_expr>	=>	<ret_array> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_2"]:
            self.ret_array()    
        
        else: self.parse_token(PREDICT_SET_M["<strict_array_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_chars(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 111 <ret_chars>	=>	bill	(	<strict_chars_expr>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_chars>"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")
            
            """ 112 <ret_chars>	=>	take	( ) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_1"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")
            
            """ 113 <ret_chars>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 114 <ret_chars>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")
            
            """ 115 <ret_chars>	=>	tochars	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_4"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            
            """ 116 <ret_chars>	=>	chars_lit """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_5"]:
            self.parse_token("chars_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_chars>"]) 

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 117 <strict_chars_expr>	=>	<strict_chars_factor>	<strict_chars_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_expr>"]:
            self.strict_chars_factor()
            self.strict_chars_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_chars_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 118 <strict_chars_factor>	=>	<ret_chars> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>"]:
            self.ret_chars()
            
            """ 119 <strict_chars_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_1"]:
            self.id_()
            
            """ 120 <strict_chars_factor>	=>	(	<strict_chars_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_2"]:
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<strict_chars_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 121 <strict_chars_add_tail>	=>	+	<strict_chars_factor>	<strict_chars_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>"]:
            self.parse_token("+")
            self.strict_chars_factor()
            self.strict_chars_add_tail()
            
            """ 122 <strict_chars_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_chars_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 123 <strict_sip_expr>	=>	<strict_sip_term>	<strict_sip_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_expr>"]:
            self.strict_sip_term()
            self.strict_sip_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_sip_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 124 <strict_sip_term>	=>	<strict_sip_factor>	<strict_sip_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_term>"]:
            self.strict_sip_factor()
            self.strict_sip_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_sip_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 125 <strict_sip_factor>	=>	<ret_sip> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>"]:
            self.ret_sip()
            
            """ 126 <strict_sip_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_1"]:
            self.id_()
            
            """ 127 <strict_sip_factor>	=>	(	<strict_sip_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_2"]:
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<strict_sip_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 128 <strict_sip_mult_tail>	=>	*	<strict_sip_factor>	<strict_sip_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()
            
            """ 129 <strict_sip_mult_tail>	=>	/	<strict_sip_factor>	<strict_sip_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()
            
            """ 130 <strict_sip_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_sip_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 131 <strict_sip_add_tail>	=>	+	<strict_sip_term>	<strict_sip_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>"]:
            self.parse_token("+")
            self.strict_sip_term()
            self.strict_sip_add_tail()
            
            """ 132 <strict_sip_add_tail>	=>	-	<strict_sip_term>	<strict_sip_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_term()
            self.strict_sip_add_tail()
            
            """ 133 <strict_sip_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_sip_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_or_table(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 169 <array_or_table>	=>	,	<array_element_id> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_or_table>"]:
            self.parse_token(",")
            self.array_element_id()
            
            """ 170 <array_or_table>	=>	=	<value>	;	<field_assignments> """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_1"]:
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()
            
            """ 171 <array_or_table>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<array_or_table>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def field_assignments(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 172 <field_assignments>	=>	id	=	<value>	;	<field_assignments> """
        if self.tokens[self.pos].type in PREDICT_SET["<field_assignments>"]:
            self.parse_token("id")
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()
            
            """ 173 <field_assignments>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<field_assignments>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<field_assignments>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 263 <flavor_tail>	=>	,	<value>	<flavor_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>"]:
            self.parse_token(",")
            self.value()
            self.flavor_tail()
            
            """ 264 <flavor_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flavor_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def accessor_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 259 <accessor_tail>	=>	<array_accessor> """
        if self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>"]:
            self.array_accessor()
            
            """ 260 <accessor_tail>	=>	<table_accessor> """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_1"]:
            self.table_accessor()
            
            """ 261 <accessor_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<accessor_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_accessor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 258 <array_accessor>	=>	[	<strict_piece_expr>	]	<accessor_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor>"]:
            self.parse_token("[")
            self.strict_piece_expr()
            self.parse_token("]")
            self.accessor_tail()
        else: self.parse_token(PREDICT_SET_M["<array_accessor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_accessor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 262 <table_accessor>	=>	:	id	<accessor_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<table_accessor>"]:
            self.parse_token(":")
            self.parse_token("id")
            self.accessor_tail()
        else: self.parse_token(PREDICT_SET_M["<table_accessor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 265 <piece_inner_dispatch>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge_recurse> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge_recurse()
            
            """ 266 <piece_inner_dispatch>	=>	<id>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>_1"]:
            self.id_()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge_recurse()
            
            """ 267 <piece_inner_dispatch>	=>	(	<piece_inner_dispatch>	<piece_close_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>_2"]:
            self.parse_token("(")
            self.piece_inner_dispatch()
            self.piece_close_recurse()
        else: self.parse_token(PREDICT_SET_M["<piece_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 55 <piece_add_tail>	=>	+	<piece_term>	<piece_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>"]:
            self.parse_token("+")
            self.piece_term()
            self.piece_add_tail()
            
            """ 56 <piece_add_tail>	=>	-	<piece_term>	<piece_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>_1"]:
            self.parse_token("-")
            self.piece_term()
            self.piece_add_tail()
            
            """ 57 <piece_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<piece_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 58 <piece_term>	=>	<piece_factor>	<piece_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_term>"]:
            self.piece_factor()
            self.piece_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 268 <piece_bridge_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<piece_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 269 <piece_close_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<piece_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 59 <piece_rel_gate>	=>	==	<piece_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 60 <piece_rel_gate>	=>	!=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_1"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 61 <piece_rel_gate>	=>	<=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_2"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 62 <piece_rel_gate>	=>	>=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_3"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 63 <piece_rel_gate>	=>	<	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_4"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 64 <piece_rel_gate>	=>	>	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_5"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 65 <piece_rel_gate>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_6"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<piece_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 66 <piece_expr>	=>	<piece_term>	<piece_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_expr>"]:
            self.piece_term()
            self.piece_add_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_logic_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 67 <flag_logic_tail>	=>	and	<must_be_flag> """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>"]:
            self.parse_token("and")
            self.must_be_flag()
            
            """ 68 <flag_logic_tail>	=>	or	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_1"]:
            self.parse_token("or")
            self.must_be_flag()
            
            """ 69 <flag_logic_tail>	=>	==	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_2"]:
            self.parse_token("==")
            self.must_be_flag()
            
            """ 70 <flag_logic_tail>	=>	!=	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_3"]:
            self.parse_token("!=")
            self.must_be_flag()
            
            """ 71 <flag_logic_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_4"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flag_logic_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def must_be_flag(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 72 <must_be_flag>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_trap_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_trap_gate()
            
            """ 73 <must_be_flag>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_trap_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_trap_gate()
            
            """ 74 <must_be_flag>	=>	<ret_chars>	<chars_add_tail>	<chars_trap_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_trap_gate()
            
            """ 75 <must_be_flag>	=>	<ret_flag>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            
            """ 76 <must_be_flag>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
            
            """ 77 <must_be_flag>	=>	(	<paren_dispatch>	<flag_after_paren> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_5"]:
            self.parse_token("(")
            self.paren_dispatch()
            self.flag_after_paren()
            
            """ 78 <must_be_flag>	=>	not	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_6"]:
            self.parse_token("not")
            self.must_be_flag()
        else: self.parse_token(PREDICT_SET_M["<must_be_flag>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 79 <piece_trap_gate>	=>	==	<piece_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 80 <piece_trap_gate>	=>	!=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_1"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 81 <piece_trap_gate>	=>	<=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_2"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 82 <piece_trap_gate>	=>	>=	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_3"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 83 <piece_trap_gate>	=>	<	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_4"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()
            
            """ 84 <piece_trap_gate>	=>	>	<piece_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_5"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 89 <sip_mult_tail>	=>	*	<sip_factor>	<sip_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>"]:
            self.parse_token("*")
            self.sip_factor()
            self.sip_mult_tail()
            
            """ 90 <sip_mult_tail>	=>	/	<sip_factor>	<sip_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>_1"]:
            self.parse_token("/")
            self.sip_factor()
            self.sip_mult_tail()
            
            """ 91 <sip_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<sip_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 92 <sip_factor>	=>	<ret_sip> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_factor>"]:
            self.ret_sip()
            
            """ 93 <sip_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_factor>_1"]:
            self.id_()
            
            """ 94 <sip_factor>	=>	(	<sip_inner_dispatch> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_factor>_2"]:
            self.parse_token("(")
            self.sip_inner_dispatch()

        else: self.parse_token(PREDICT_SET_M["<sip_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 95 <sip_inner_dispatch>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge_recurse> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge_recurse()
            
            """ 96 <sip_inner_dispatch>	=>	<id>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>_1"]:
            self.id_()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge_recurse()
            
            """ 97 <sip_inner_dispatch>	=>	(	<sip_inner_dispatch>	<sip_close_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>_2"]:
            self.parse_token("(")
            self.sip_inner_dispatch()
            self.sip_close_recurse()

        else: self.parse_token(PREDICT_SET_M["<sip_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 98 <sip_add_tail>	=>	+	<sip_term>	<sip_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>"]:
            self.parse_token("+")
            self.sip_term()
            self.sip_add_tail()
            
            """ 99 <sip_add_tail>	=>	-	<sip_term>	<sip_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>_1"]:
            self.parse_token("-")
            self.sip_term()
            self.sip_add_tail()
            
            """ 100 <sip_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<sip_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 101 <sip_term>	=>	<sip_factor>	<sip_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_term>"]:
            self.sip_factor()
            self.sip_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 102 <sip_bridge_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<sip_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 103 <sip_close_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<sip_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 104 <sip_trap_gate>	=>	==	<sip_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()
            
            """ 105 <sip_trap_gate>	=>	!=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_1"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()
            
            """ 106 <sip_trap_gate>	=>	<=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_2"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()
            
            """ 107 <sip_trap_gate>	=>	>=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_3"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()
            
            """ 108 <sip_trap_gate>	=>	<	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_4"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()
            
            """ 109 <sip_trap_gate>	=>	>	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_5"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 110 <sip_expr>	=>	<sip_term>	<sip_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_expr>"]:
            self.sip_term()
            self.sip_add_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 133 <chars_add_tail>	=>	+	<chars_factor>	<chars_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_add_tail>"]:
            self.parse_token("+")
            self.chars_factor()
            self.chars_add_tail()
            
            """ 134 <chars_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_add_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 135 <chars_factor>	=>	<ret_chars> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_factor>"]:
            self.ret_chars()
            
            """ 136 <chars_factor>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_factor>_1"]:
            self.id_()
            
            """ 137 <chars_factor>	=>	(	<chars_inner_dispatch> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_factor>_2"]:
            self.parse_token("(")
            self.chars_inner_dispatch()
        else: self.parse_token(PREDICT_SET_M["<chars_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 138 <chars_inner_dispatch>	=>	<ret_chars>	<chars_add_tail>	<chars_bridge_recurse> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_bridge_recurse()
            
            """ 139 <chars_inner_dispatch>	=>	<id>	<chars_add_tail>	<chars_bridge_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>_1"]:
            self.id_()
            self.chars_add_tail()
            self.chars_bridge_recurse()
            
            """ 140 <chars_inner_dispatch>	=>	(	<chars_inner_dispatch>	<chars_close_recurse> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>_2"]:
            self.parse_token("(")
            self.chars_inner_dispatch()
            self.chars_close_recurse()
        else: self.parse_token(PREDICT_SET_M["<chars_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 142 <chars_bridge_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<chars_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 143 <chars_close_recurse>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<chars_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 144 <chars_trap_gate>	=>	==	<chars_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 145 <chars_trap_gate>	=>	!=	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_1"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 146 <chars_trap_gate>	=>	<=	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_2"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 147 <chars_trap_gate>	=>	>=	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_3"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 148 <chars_trap_gate>	=>	<	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_4"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 149 <chars_trap_gate>	=>	>	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_5"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()
        else: self.parse_token(PREDICT_SET_M["<chars_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 150 <chars_expr>	=>	<chars_factor>	<chars_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_expr>"]:
            self.chars_factor()
            self.chars_add_tail()
        else: self.parse_token(PREDICT_SET_M["<chars_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 174 <univ_mult_tail>	=>	*	<univ_factor>	<univ_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>"]:
            self.parse_token("*")
            self.univ_factor()
            self.univ_mult_tail()
            
            """ 175 <univ_mult_tail>	=>	/	<univ_factor>	<univ_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_1"]:
            self.parse_token("/")
            self.univ_factor()
            self.univ_mult_tail()
            
            """ 176 <univ_mult_tail>	=>	%	<univ_factor>	<univ_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_2"]:
            self.parse_token("%")
            self.univ_factor()
            self.univ_mult_tail()
            
            """ 177 <univ_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_3"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<univ_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 178 <univ_factor>	=>	<id> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_factor>"]:
            self.id_()
            
            """ 179 <univ_factor>	=>	<ret_piece> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_1"]:
            self.ret_piece()
            
            """ 180 <univ_factor>	=>	<ret_sip> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_2"]:
            self.ret_sip()
            
            """ 183 <univ_factor>	=>	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_3"]:
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<univ_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 184 <univ_add_tail>	=>	+	<univ_term>	<univ_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>"]:
            self.parse_token("+")
            self.univ_term()
            self.univ_add_tail()
            
            """ 185 <univ_add_tail>	=>	-	<univ_term>	<univ_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>_1"]:
            self.parse_token("-")
            self.univ_term()
            self.univ_add_tail()
            
            """ 186 <univ_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<univ_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 187 <univ_term>	=>	<univ_factor>	<univ_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_term>"]:
            self.univ_factor()
            self.univ_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<univ_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 188 <univ_rel_gate>	=>	==	<univ_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>"]:
            self.parse_token("==")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 189 <univ_rel_gate>	=>	!=	<univ_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_1"]:
            self.parse_token("!=")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 190 <univ_rel_gate>	=>	<=	<univ_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_2"]:
            self.parse_token("<=")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 191 <univ_rel_gate>	=>	>=	<univ_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_3"]:
            self.parse_token(">=")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 192 <univ_rel_gate>	=>	<	<univ_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_4"]:
            self.parse_token("<")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 193 <univ_rel_gate>	=>	>	<univ_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_5"]:
            self.parse_token(">")
            self.univ_expr()
            self.flag_logic_tail()
            
            """ 194 <univ_rel_gate>	=>	and	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_6"]:
            self.parse_token("and")
            self.must_be_flag()
            
            """ 195 <univ_rel_gate>	=>	or	<must_be_flag> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_7"]:
            self.parse_token("or")
            self.must_be_flag()
            
            """ 196 <univ_rel_gate>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_8"]:
            pass
        
        else: self.parse_token(PREDICT_SET_M["<univ_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 197 <univ_expr>	=>	<univ_term>	<univ_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_expr>"]:
            self.univ_term()
            self.univ_add_tail()
        else: self.parse_token(PREDICT_SET_M["<univ_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 198 <paren_dispatch>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge> """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge()
            
            """ 199 <paren_dispatch>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge()
            
            """ 200 <paren_dispatch>	=>	<ret_chars>	<chars_add_tail>	<chars_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_bridge()
            
            """ 201 <paren_dispatch>	=>	<ret_flag>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 202 <paren_dispatch>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_bridge()
            
            """ 203 <paren_dispatch>	=>	(	<paren_dispatch>	<univ_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_5"]:
            self.parse_token("(")
            self.paren_dispatch()
            self.univ_closure()
            
            """ 204 <paren_dispatch>	=>	not	<must_be_flag>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_6"]:
            self.parse_token("not")
            self.must_be_flag()
            self.flag_closure()
        else: self.parse_token(PREDICT_SET_M["<paren_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 205 <piece_bridge>	=>	)	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>"]:
            self.parse_token(")")
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()
            
            """ 206 <piece_bridge>	=>	==	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_1"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 207 <piece_bridge>	=>	!=	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_2"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 208 <piece_bridge>	=>	<=	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_3"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 209 <piece_bridge>	=>	>=	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_4"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 210 <piece_bridge>	=>	<	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_5"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 211 <piece_bridge>	=>	>	<piece_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_6"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()
        else: self.parse_token(PREDICT_SET_M["<piece_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_closure(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 212 <flag_closure>	=>	)	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_closure>"]:
            self.parse_token(")")
            self.flag_logic_tail()
            
            """ 213 <flag_closure>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_closure>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flag_closure>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 213 <sip_bridge>	=>	)	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>"]:
            self.parse_token(")")
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()
            
            """ 214 <sip_bridge>	=>	==	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_1"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 215 <sip_bridge>	=>	!=	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_2"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 216 <sip_bridge>	=>	<=	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_3"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 217 <sip_bridge>	=>	>=	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_4"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 218 <sip_bridge>	=>	<	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_5"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 219 <sip_bridge>	=>	>	<sip_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_6"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()
        else: self.parse_token(PREDICT_SET_M["<sip_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 220 <sip_rel_gate>	=>	==	<sip_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()

            """ 221 <sip_rel_gate>	=>	!=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_1"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()

            """ 222 <sip_rel_gate>	=>	<=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_2"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()
        
            """ 223 <sip_rel_gate>	=>	>=	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_3"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()
        
            """ 224 <sip_rel_gate>	=>	<	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_4"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()

            """ 225 <sip_rel_gate>	=>	>	<sip_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_5"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()

            """ 226 <sip_rel_gate>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_6"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<sip_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 239 <chars_bridge>	=>	)	<chars_add_tail>	<chars_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>"]:
            self.parse_token(")")
            self.chars_add_tail()
            self.chars_rel_gate()
            
            """ 240 <chars_bridge>	=>	==	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_1"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 241 <chars_bridge>	=>	!=	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_2"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 242 <chars_bridge>	=>	<=	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_3"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 243 <chars_bridge>	=>	>=	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_4"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 244 <chars_bridge>	=>	<	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_5"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 245 <chars_bridge>	=>	>	<chars_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_6"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()
        else: self.parse_token(PREDICT_SET_M["<chars_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 234 <chars_rel_gate>	=>	<=	<chars_expr>	<flag_logic_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 235 <chars_rel_gate>	=>	>=	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_1"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 236 <chars_rel_gate>	=>	<	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_2"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 237 <chars_rel_gate>	=>	>	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_3"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 238 <chars_rel_gate>	=>	==	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_4"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 239 <chars_rel_gate>	=>	!=	<chars_expr>	<flag_logic_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_5"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()
            
            """ 240 <chars_rel_gate>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 241 <univ_bridge>	=>	)	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>"]:
            self.parse_token(")")
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
            
            """ 242 <univ_bridge>	=>	==	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_1"]:
            self.parse_token("==")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 243 <univ_bridge>	=>	!=	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_2"]:
            self.parse_token("!=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 244 <univ_bridge>	=>	<=	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_3"]:
            self.parse_token("<=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 245 <univ_bridge>	=>	>=	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_4"]:
            self.parse_token(">=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
        
            """ 246 <univ_bridge>	=>	<	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_5"]:
            self.parse_token("<")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
            
            """ 247 <univ_bridge>	=>	>	<univ_expr>	<flag_logic_tail>	<flag_closure> """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_6"]:
            self.parse_token(">")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()
        else: self.parse_token(PREDICT_SET_M["<univ_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_closure(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 248 <univ_closure>	=>	)	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_closure>"]:
            self.parse_token(")")
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
        else: self.parse_token(PREDICT_SET_M["<univ_closure>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_after_paren(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 249 <flag_after_paren>	=>	λ """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_after_paren>"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flag_after_paren>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 270 <strict_piece_mult_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            
            """ 271 <strict_piece_mult_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            
            """ 272 <strict_piece_mult_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_2"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            
            """ 273 <strict_piece_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_3"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 274 <strict_piece_add_tail>	=>	+	<strict_piece_term>	<strict_piece_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>"]:
            self.parse_token("+")
            self.strict_piece_term()
            self.strict_piece_add_tail()
            
            """ 275 <strict_piece_add_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_term()
            self.strict_piece_add_tail()
            
            """ 276 <strict_piece_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 277 <piece_id_tail>	=>	,	id	<piece_ingredient_init>	<piece_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()
            
            """ 278 <piece_id_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<piece_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def decl_type(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 279 <decl_type>	=>	<dimensions>	of	<array_declare>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_type>"]:
            self.dimensions()
            self.parse_token("of")
            self.array_declare()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<decl_type>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 280 <dimensions>	=>	[	]	<dimensions_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions>"]:
            self.parse_token("[")
            self.parse_token("]")
            self.dimensions_tail()
        else: self.parse_token(PREDICT_SET_M["<dimensions>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 281 <dimensions_tail>	=>	<dimensions> """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>"]:
            self.dimensions()
            
            """ 282 <dimensions_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<dimensions_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 275 <array_declare>	=>	id	<array_init>	<array_declare_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare>"]:
            self.parse_token("id")
            self.array_init()
            self.array_declare_tail()
        else: self.parse_token(PREDICT_SET_M["<array_declare>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 276 <array_init>	=>	=	<strict_array_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_init>"]:
            self.parse_token("=")
            self.strict_array_expr()
            
            """ 277 <array_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_init>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<array_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 278 <array_declare_tail>	=>	,	<array_declare> """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail>"]:
            self.parse_token(",")
            self.array_declare()
            
            """ 279 <array_declare_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<array_declare_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 280 <chars_decl>    =>  of  <chars_id>"""
        if self.tokens[self.pos].type in PREDICT_SET["<chars_decl>"]:
            self.parse_token("of")
            self.chars_id()
            self.parse_token(";")
            
            """ 281 <chars_decl>    =>  <decl_type>"""
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_decl>_1"]:
            self.decl_type()
        else: self.parse_token(PREDICT_SET_M["<chars_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J


    def chars_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 282 <chars_id>	=>	id	<chars_ingredient_init>	<chars_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id>"]:
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()
        else: self.parse_token(PREDICT_SET_M["<chars_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 283 <chars_ingredient_init>	=>	=	<strict_chars_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>"]:
            self.parse_token("=")
            self.strict_chars_expr()
            
            """ 284 <chars_ingredient_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<chars_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 285 <chars_id_tail>	=>	,	id	<chars_ingredient_init>	<chars_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()
            
            """ 286 <chars_id_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<chars_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 287 <sip_decl>  =>  of  <sip_id> ; """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_decl>"]:
            self.parse_token("of")
            self.sip_id()
            self.parse_token(";")
            
            """ 288 <sip_decl>  =>  decl_type   """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_decl>_1"]:
            self.decl_type()
        else: self.parse_token(PREDICT_SET_M["<sip_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 289 <sip_id>	=>	id	<sip_ingredient_init>	<sip_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id>"]:
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 290 <sip_ingredient_init>	=>	=	<strict_sip_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>"]:
            self.parse_token("=")
            self.strict_sip_expr()
            
            """ 291 <sip_ingredient_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<sip_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 292 <sip_id_tail>	=>	,	id	<sip_ingredient_init>	<sip_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()
            
            """ 293 <sip_id_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<sip_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J
        
        """ 294 <flag_decl> =>  of  <flag_id>   ; """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_decl>"]:
            self.parse_token("of")
            self.flag_id()
            self.parse_token(";")
            
            """ 295 <flag_decl> =>  <decl_type> """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_decl>_1"]:
            self.decl_type()
        else: self.parse_token(PREDICT_SET_M["<flag_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J
        

    def flag_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 296 <flag_id>	=>	id	<flag_ingredient_init>	<flag_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id>"]:
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()
        else: self.parse_token(PREDICT_SET_M["<flag_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 297 <flag_ingredient_init>	=>	=	<strict_flag_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>"]:
            self.parse_token("=")
            self.strict_flag_expr()
            
            """ 298 <flag_ingredient_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flag_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 299 <strict_flag_expr>	=>	<strict_flag_term>	<strict_flag_or_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_expr>"]:
            self.strict_flag_term()
            self.strict_flag_or_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 300 <strict_flag_term>	=>	<strict_flag_equality>	<strict_flag_and_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_term>"]:
            self.strict_flag_equality()
            self.strict_flag_and_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_equality(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 301 <strict_flag_equality>	=>	<strict_flag_factor>	<strict_flag_eq_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_equality>"]:
            self.strict_flag_factor()
            self.strict_flag_eq_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_equality>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 302 <strict_flag_factor>	=>	<ret_flag> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>"]:
            self.ret_flag()
            
            """ 303 <strict_flag_factor>	=>	not	<strict_flag_factor> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_1"]:
            self.parse_token("not")
            self.strict_flag_factor()
            
            """ 304 <strict_flag_factor>	=>	<id>	<strict_id_master_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_2"]:
            self.id_()
            self.strict_id_master_tail()
            
            """ 305 <strict_flag_factor>	=>	(	<strict_flag_paren_entry> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_3"]:
            self.parse_token("(")
            self.strict_flag_paren_entry()
            
            """ 306 <strict_flag_factor>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<strict_piece_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_4"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.strict_piece_gate()
            
            """ 307 <strict_flag_factor>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<strict_sip_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_5"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.strict_sip_gate()
            
            """ 308 <strict_flag_factor>	=>	<ret_chars>	<chars_add_tail>	<strict_chars_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_6"]:
            self.ret_chars()
            self.chars_add_tail()
            self.strict_chars_gate()

        else: self.parse_token(PREDICT_SET_M["<strict_flag_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_id_master_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 309 <strict_id_master_tail>	=>	*	<univ_factor>	<univ_mult_tail>	<univ_add_tail>	<strict_forced_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>"]:
            self.parse_token("*")
            self.univ_factor()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 310 <strict_id_master_tail>	=>	/	<univ_factor>	<univ_mult_tail>	<univ_add_tail>	<strict_forced_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_1"]:
            self.parse_token("/")
            self.univ_factor()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 311 <strict_id_master_tail>	=>	%	<univ_factor>	<univ_mult_tail>	<univ_add_tail>	<strict_forced_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_2"]:
            self.parse_token("%")
            self.univ_factor()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 312 <strict_id_master_tail>	=>	+	<univ_term>	<univ_add_tail>	<strict_forced_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_3"]:
            self.parse_token("+")
            self.univ_term()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 313 <strict_id_master_tail>	=>	-	<univ_term>	<univ_add_tail>	<strict_forced_gate> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_4"]:
            self.parse_token("-")
            self.univ_term()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 314 <strict_id_master_tail>	=>	==	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_5"]:
            self.parse_token("==")
            self.univ_expr()
            
            """ 315 <strict_id_master_tail>	=>	!=	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_6"]:
            self.parse_token("!=")
            self.univ_expr()
            
            """ 316 <strict_id_master_tail>	=>	<=	<comparable_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_7"]:
            self.parse_token("<=")
            self.comparable_expr()
            
            """ 317 <strict_id_master_tail>	=>	>=	<comparable_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_8"]:
            self.parse_token(">=")
            self.comparable_expr()
            
            """ 318 <strict_id_master_tail>	=>	<	<comparable_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_9"]:
            self.parse_token("<")
            self.comparable_expr()
            
            """ 319 <strict_id_master_tail>	=>	>	<comparable_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_10"]:
            self.parse_token(">")
            self.comparable_expr()
            
            """ 320 <strict_id_master_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_id_master_tail>_11"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_id_master_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_forced_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 321 <strict_forced_gate>	=>	==	<univ_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>"]:
            self.parse_token("==")
            self.univ_expr()
            
            """ 322 <strict_forced_gate>	=>	!=	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>_1"]:
            self.parse_token("!=")
            self.univ_expr()
            
            """ 323 <strict_forced_gate>	=>	<=	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>_2"]:
            self.parse_token("<=")
            self.univ_expr()
            
            """ 324 <strict_forced_gate>	=>	>=	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>_3"]:
            self.parse_token(">=")
            self.univ_expr()
            
            """ 325 <strict_forced_gate>	=>	<	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>_4"]:
            self.parse_token("<")
            self.univ_expr()
            
            """ 326 <strict_forced_gate>	=>	>	<univ_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_forced_gate>_5"]:
            self.parse_token(">")
            self.univ_expr()
        else: self.parse_token(PREDICT_SET_M["<strict_forced_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def comparable_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 327 <comparable_expr>	=>	<comparable_term>	<comparable_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<comparable_expr>"]:
            self.comparable_term()
            self.comparable_add_tail()
        else: self.parse_token(PREDICT_SET_M["<comparable_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def comparable_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 328 <comparable_term>	=>	<comparable_factor>	<comparable_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<comparable_term>"]:
            self.comparable_factor()
            self.comparable_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<comparable_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def comparable_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 329 <comparable_factor>	=>	<id> """
        if self.tokens[self.pos].type in PREDICT_SET["<comparable_factor>"]:
            self.id_()
            
            """ 330 <comparable_factor>	=>	<ret_piece> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_factor>_1"]:
            self.ret_piece()
            
            """ 331 <comparable_factor>	=>	<ret_sip> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_factor>_2"]:
            self.ret_sip()
            
            """ 332 <comparable_factor>	=>	<ret_chars> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_factor>_3"]:
            self.ret_chars()
            
            """ 333 <comparable_factor>	=>	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_factor>_4"]:
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<comparable_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def comparable_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 334 <comparable_mult_tail>	=>	*	<comparable_factor>	<comparable_mult_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<comparable_mult_tail>"]:
            self.parse_token("*")
            self.comparable_factor()
            self.comparable_mult_tail()
            
            """ 335 <comparable_mult_tail>	=>	/	<comparable_factor>	<comparable_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_mult_tail>_1"]:
            self.parse_token("/")
            self.comparable_factor()
            self.comparable_mult_tail()
            
            """ 336 <comparable_mult_tail>	=>	%	<comparable_factor>	<comparable_mult_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_mult_tail>_2"]:
            self.parse_token("%")
            self.comparable_factor()
            self.comparable_mult_tail()
            
            """ 337 <comparable_mult_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_mult_tail>_3"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<comparable_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def comparable_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 338 <comparable_add_tail>	=>	+	<comparable_term>	<comparable_add_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<comparable_add_tail>"]:
            self.parse_token("+")
            self.comparable_term()
            self.comparable_add_tail()
            
            """ 339 <comparable_add_tail>	=>	-	<comparable_term>	<comparable_add_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_add_tail>_1"]:
            self.parse_token("-")
            self.comparable_term()
            self.comparable_add_tail()
            
            """ 340 <comparable_add_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<comparable_add_tail>_2"]:
            pass
        
        else: self.parse_token(PREDICT_SET_M["<comparable_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_paren_entry(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 341 <strict_flag_paren_entry>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<strict_paren_piece_bridge> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.strict_paren_piece_bridge()
            
            """ 342 <strict_flag_paren_entry>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<strict_paren_sip_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.strict_paren_sip_bridge()
            
            """ 343 <strict_flag_paren_entry>	=>	<ret_chars>	<chars_add_tail>	<strict_paren_chars_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.strict_paren_chars_bridge()
            
            """ 344 <strict_flag_paren_entry>	=>	<ret_flag>	<flag_logic_tail>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            self.strict_paren_flag_bridge()
            
            """ 345 <strict_flag_paren_entry>	=>	not	<must_be_flag>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_4"]:
            self.parse_token("not")
            self.must_be_flag()
            self.strict_paren_flag_bridge()
            
            """ 346 <strict_flag_paren_entry>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<strict_paren_univ_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_5"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.strict_paren_univ_bridge()
            
            """ 347 <strict_flag_paren_entry>	=>	(	<strict_flag_paren_entry>	<strict_paren_univ_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_paren_entry>_6"]:
            self.parse_token("(")
            self.strict_flag_paren_entry()
            self.strict_paren_univ_bridge()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_paren_entry>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_paren_piece_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 348 <strict_paren_piece_bridge>	=>	)	<piece_mult_tail>	<piece_add_tail>	<strict_piece_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_paren_piece_bridge>"]:
            self.parse_token(")")
            self.piece_mult_tail()
            self.piece_add_tail()
            self.strict_piece_gate()
            
            """ 349 <strict_paren_piece_bridge>	=>	<strict_piece_gate>	<flag_logic_tail>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_paren_piece_bridge>_1"]:
            self.strict_piece_gate()
            self.flag_logic_tail()
            self.strict_paren_flag_bridge()
        else: self.parse_token(PREDICT_SET_M["<strict_paren_piece_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 350 <strict_piece_gate>	=>	==	<piece_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>"]:
            self.parse_token("==")
            self.piece_expr()
            
            """ 351 <strict_piece_gate>	=>	!=	<piece_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>_1"]:
            self.parse_token("!=")
            self.piece_expr()
            
            """ 352 <strict_piece_gate>	=>	<=	<piece_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>_2"]:
            self.parse_token("<=")
            self.piece_expr()
            
            """ 353 <strict_piece_gate>	=>	>=	<piece_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>_3"]:
            self.parse_token(">=")
            self.piece_expr()
            
            """ 354 <strict_piece_gate>	=>	<	<piece_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>_4"]:
            self.parse_token("<")
            self.piece_expr()
            
            """ 355 <strict_piece_gate>	=>	>	<piece_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_gate>_5"]:
            self.parse_token(">")
            self.piece_expr()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_paren_flag_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 356 <strict_paren_flag_bridge>	=>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_paren_flag_bridge>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<strict_paren_flag_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_paren_sip_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 357 <strict_paren_sip_bridge>	=>	)	<sip_mult_tail>	<sip_add_tail>	<strict_sip_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_paren_sip_bridge>"]:
            self.parse_token(")")
            self.sip_mult_tail()
            self.sip_add_tail()
            self.strict_sip_gate()
            
            """ 358 <strict_paren_sip_bridge>	=>	<strict_sip_gate>	<flag_logic_tail>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_paren_sip_bridge>_1"]:
            self.strict_sip_gate()
            self.flag_logic_tail()
            self.strict_paren_flag_bridge()
        else: self.parse_token(PREDICT_SET_M["<strict_paren_sip_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 359 <strict_sip_gate>	=>	==	<sip_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>"]:
            self.parse_token("==")
            self.sip_expr()
            
            """ 360 <strict_sip_gate>	=>	!=	<sip_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>_1"]:
            self.parse_token("!=")
            self.sip_expr()
            
            """ 361 <strict_sip_gate>	=>	<=	<sip_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>_2"]:
            self.parse_token("<=")
            self.sip_expr()
            
            """ 362 <strict_sip_gate>	=>	>=	<sip_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>_3"]:
            self.parse_token(">=")
            self.sip_expr()
            
            """ 363 <strict_sip_gate>	=>	<	<sip_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>_4"]:
            self.parse_token("<")
            self.sip_expr()
            
            """ 364 <strict_sip_gate>	=>	>	<sip_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_gate>_5"]:
            self.parse_token(">")
            self.sip_expr()
        else: self.parse_token(PREDICT_SET_M["<strict_sip_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_paren_chars_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 365 <strict_paren_chars_bridge>	=>	)	<chars_add_tail>	<strict_chars_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_paren_chars_bridge>"]:
            self.parse_token(")")
            self.chars_add_tail()
            self.strict_chars_gate()
            
            """ 366 <strict_paren_chars_bridge>	=>	<strict_chars_gate>	<flag_logic_tail>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_paren_chars_bridge>_1"]:
            self.strict_chars_gate()
            self.flag_logic_tail()
            self.strict_paren_flag_bridge()
        else: self.parse_token(PREDICT_SET_M["<strict_paren_chars_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 367 <strict_chars_gate>	=>	<=	<chars_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>"]:
            self.parse_token("<=")
            self.chars_expr()
            
            """ 368 <strict_chars_gate>	=>	>=	<chars_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>_1"]:
            self.parse_token(">=")
            self.chars_expr()
            
            """ 369 <strict_chars_gate>	=>	<	<chars_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>_2"]:
            self.parse_token("<")
            self.chars_expr()
            
            """ 370 <strict_chars_gate>	=>	>	<chars_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>_3"]:
            self.parse_token(">")
            self.chars_expr()
            
            """ 371 <strict_chars_gate>	=>	==	<chars_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>_4"]:
            self.parse_token("==")
            self.chars_expr()
            
            """ 372 <strict_chars_gate>	=>	!=	<chars_expr> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_gate>_5"]:
            self.parse_token("!=")
            self.chars_expr()
        else: self.parse_token(PREDICT_SET_M["<strict_chars_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_paren_univ_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 373 <strict_paren_univ_bridge>	=>	)	<univ_mult_tail>	<univ_add_tail>	<strict_forced_gate> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_paren_univ_bridge>"]:
            self.parse_token(")")
            self.univ_mult_tail()
            self.univ_add_tail()
            self.strict_forced_gate()
            
            """ 374 <strict_paren_univ_bridge>	=>	<strict_forced_gate>	<flag_logic_tail>	<strict_paren_flag_bridge> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_paren_univ_bridge>_1"]:
            self.strict_forced_gate()
            self.flag_logic_tail()
            self.strict_paren_flag_bridge()
        else: self.parse_token(PREDICT_SET_M["<strict_paren_univ_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_eq_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 375 <strict_flag_eq_tail>	=>	==	<strict_flag_equality> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_eq_tail>"]:
            self.parse_token("==")
            self.strict_flag_equality()
            
            """ 376 <strict_flag_eq_tail>	=>	!=	<strict_flag_equality> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_eq_tail>_1"]:
            self.parse_token("!=")
            self.strict_flag_equality()
            
            """ 377 <strict_flag_eq_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_eq_tail>_2"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_flag_eq_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_and_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 378 <strict_flag_and_tail>	=>	and	<strict_flag_equality>	<strict_flag_and_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>"]:
            self.parse_token("and")
            self.strict_flag_equality()
            self.strict_flag_and_tail()
            
            """ 379 <strict_flag_and_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_flag_and_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_or_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 380 <strict_flag_or_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()
            
            """ 381 <strict_flag_or_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<strict_flag_or_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 382 <flag_id_tail>	=>	,	id	<flag_ingredient_init>	<flag_id_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()
            
            """ 383 <flag_id_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flag_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_prototype(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 384 <table_prototype>	=>	table	of	id	=	[	<required_decl>	]	; """
        if self.tokens[self.pos].type in PREDICT_SET["<table_prototype>"]:
            self.parse_token("table")
            self.parse_token("of")
            self.parse_token("id")
            self.parse_token("=")
            self.parse_token("[")
            self.required_decl()
            self.parse_token("]")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<table_prototype>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def required_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 385 <required_decl>	=>	<decl_head>	;	<required_decl_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl>"]:
            self.decl_head()
            self.parse_token(";")
            self.required_decl_tail()
        else: self.parse_token(PREDICT_SET_M["<required_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def decl_head(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 386 <decl_head>	=>	<primitive_types_dims>	of	id """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_head>"]:
            self.primitive_types_dims()
            self.parse_token("of")
            self.parse_token("id")
        else: self.parse_token(PREDICT_SET_M["<decl_head>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def primitive_types_dims(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 387 <primitive_types_dims>	=>	piece	<dimensions_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>"]:
            self.parse_token("piece")
            self.dimensions_tail()
            
            """ 388 <primitive_types_dims>	=>	sip	<dimensions_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_1"]:
            self.parse_token("sip")
            self.dimensions_tail()
            
            """ 389 <primitive_types_dims>	=>	flag	<dimensions_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_2"]:
            self.parse_token("flag")
            self.dimensions_tail()
            
            """ 390 <primitive_types_dims>	=>	chars	<dimensions_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_3"]:
            self.parse_token("chars")
            self.dimensions_tail()
            
            """ 391 <primitive_types_dims>	=>	id	<dimensions_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_4"]:
            self.parse_token("id")
            self.dimensions_tail()
        else: self.parse_token(PREDICT_SET_M["<primitive_types_dims>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def required_decl_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 392 <required_decl_tail>	=>	<required_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>"]:
            self.required_decl()
            
            """ 393 <required_decl_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<required_decl_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J


    def table_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 394 <table_decl>	=>	of	<table_declare>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<table_decl>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            
            """ 395 <table_decl>	=>	<decl_type> """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_decl>_1"]:
            self.decl_type()
        else: self.parse_token(PREDICT_SET_M["<table_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J


    def table_declare(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 396 <table_declare>	=>	id	<table_init>	<table_declare_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare>"]:
            self.parse_token("id")
            self.table_init()
            self.table_declare_tail()
        else: self.parse_token(PREDICT_SET_M["<table_declare>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 397 <table_init>	=>	=	<strict_table_expr> """
        if self.tokens[self.pos].type in PREDICT_SET["<table_init>"]:
            self.parse_token("=")
            self.strict_table_expr()
            
            """ 398 <table_init>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_init>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<table_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_table_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 399 <strict_table_expr>	=>	[	<field_assignments>	] """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>"]:
            self.parse_token("[")
            self.field_assignments()
            self.parse_token("]")
            
            """ 400 <strict_table_expr>	=>	<id> """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>_1"]:
            self.id_()

        else: self.parse_token(PREDICT_SET_M["<strict_table_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_declare_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 401 <table_declare_tail>	=>	,	<table_declare> """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>"]:
            self.parse_token(",")
            self.table_declare()
            
            """ 402 <table_declare_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<table_declare_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def recipe_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 403 <recipe_decl>	=>	prepare	<serve_type>	(	<spice>	)	<platter>	<recipe_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>"]:
            self.parse_token("prepare")
            self.serve_type()
            self.parse_token("(")
            self.spice()
            self.parse_token(")")
            self.platter()
            self.recipe_decl()
            
            """ 404 <recipe_decl>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<recipe_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def serve_type(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 405 <serve_type>	=>	<decl_head> """
        if self.tokens[self.pos].type in PREDICT_SET["<serve_type>"]:
            self.decl_head()
        else: self.parse_token(PREDICT_SET_M["<serve_type>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 406 <spice>	=>	<decl_head>	<spice_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<spice>"]:
            self.decl_head()
            self.spice_tail()
            
            """ 407 <spice>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<spice>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 408 <spice_tail>	=>	,	<decl_head>	<spice_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<spice_tail>"]:
            self.parse_token(",")
            self.decl_head()
            self.spice_tail()
            
            """ 409 <spice_tail>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice_tail>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<spice_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 410 <platter>	=>	{	<local_decl>	<statements>	} """
        if self.tokens[self.pos].type in PREDICT_SET["<platter>"]:
            self.parse_token("{")
            self.local_decl()
            self.statements()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 411 <local_decl>	=>	piece	<piece_decl>	<local_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl()
            
            """ 412 <local_decl>	=>	chars	<chars_decl>	<local_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl()
            
            """ 413 <local_decl>	=>	sip	<sip_decl>	<local_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl()
            
            """ 414 <local_decl>	=>	flag	<flag_decl>	<local_decl> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl()
            
            """ 415 <local_decl>	=>	id	<local_id_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_4"]:
            self.parse_token("id")
            self.local_id_tail()
            
            """ 416 <local_decl>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_5"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<local_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 417 <local_id_tail>	=>	of	<table_declare>	;	<local_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl()
            
            """ 418 <local_id_tail>	=>	[	<endb_tail> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_1"]:
            self.parse_token("[")
            self.endb_tail()
            
            """ 419 <local_id_tail>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()
            
            """ 420 <local_id_tail>	=>	<assignment_op>	<value>	;	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()
            
            """ 421 <local_id_tail>	=>	<tail1>	;	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements()
        
        else: self.parse_token(PREDICT_SET_M["<local_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endb_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 422 <endb_tail>	=>	]	<dimensions_tail>	of	<array_declare>	;	<local_decl> """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.array_declare()
            self.parse_token(";")
            self.local_decl()
            
            """ 423 <endb_tail>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<]_tail>_1"]:
            self.strict_piece_expr()
            self.parse_token("]")
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()
        else: self.parse_token(PREDICT_SET_M["<]_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def assignment_op(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 424 <assignment_op>	=>	= """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_op>"]:
            self.parse_token("=")
            
            """ 425 <assignment_op>	=>	+= """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_1"]:
            self.parse_token("+=")
            
            """ 426 <assignment_op>	=>	-= """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_2"]:
            self.parse_token("-=")
            
            """ 427 <assignment_op>	=>	*= """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_3"]:
            self.parse_token("*=")
            
            """ 428 <assignment_op>	=>	/= """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_4"]:
            self.parse_token("/=")
            
            """ 429 <assignment_op>	=>	%= """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_5"]:
            self.parse_token("%=")
        else: self.parse_token(PREDICT_SET_M["<assignment_op>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 430 <statements>	=>	<id_statements>	<statements> """
        if self.tokens[self.pos].type in PREDICT_SET["<statements>"]:
            self.id_statements()
            self.statements()
            
            """ 431 <statements>	=>	<built_in_rec_call>	;	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements()
            
            """ 432 <statements>	=>	<conditional_st>	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_2"]:
            self.conditional_st()
            self.statements()
            
            """ 433 <statements>	=>	<looping_st>	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_3"]:
            self.looping_st()
            self.statements()
            
            """ 434 <statements>	=>	<jump_serve>	<statements> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_4"]:
            self.jump_serve()
            self.statements()
            
            """ 435 <statements>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_5"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<statements>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 436 <id_statements>	=>	id	<id_statements_ext>	<statements> """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements()
        else: self.parse_token(PREDICT_SET_M["<id_statements>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_ext(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 437 <id_statements_ext>	=>	<tail1>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>"]:
            self.tail1()
            self.parse_token(";")
            
            """ 438 <id_statements_ext>	=>	<assignment_st> """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>_1"]:
            self.assignment_st()
        else: self.parse_token(PREDICT_SET_M["<id_statements_ext>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def tail1(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 439 <tail1>	=>	<call_tail>	<accessor_tail> """
        if self.tokens[self.pos].type in PREDICT_SET["<tail1>"]:
            self.call_tail()
        else: self.parse_token(PREDICT_SET_M["<tail1>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 440 <call_tail>	=>	(	<flavor>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tail>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<call_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def assignment_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 441 <assignment_st>	=>	<accessor_tail>	<assignment_op>	<value>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_st>"]:
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<assignment_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec_call(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 442 <built_in_rec_call>	=>	<built_in_rec> """
        if self.tokens[self.pos].type in PREDICT_SET["<built-in_rec_call>"]:
            self.built_in_rec()
        else: self.parse_token(PREDICT_SET_M["<built-in_rec_call>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 443 <built_in_rec>	=>	append	(	<strict_array_expr>	,	<value>	) """
        if self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")
            
            """ 444 <built_in_rec>	=>	bill	(	<strict_chars_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_1"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")
            
            """ 445 <built_in_rec>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 446 <built_in_rec>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")
            
            """ 447 <built_in_rec>	=>	fact	(	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_4"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 448 <built_in_rec>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_5"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")
            
            """ 449 <built_in_rec>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_6"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 450 <built_in_rec>	=>	rand	(	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_7"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")
            
            """ 451 <built_in_rec>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_8"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 452 <built_in_rec>	=>	reverse	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_9"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 453 <built_in_rec>	=>	search	(	<strict_array_expr>	,	<value>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_10"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")
            
            """ 454 <built_in_rec>	=>	size	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_11"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 455 <built_in_rec>	=>	sort	(	<strict_array_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_12"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")
            
            """ 456 <built_in_rec>	=>	sqrt	(	<strict_piece_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_13"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")
            
            """ 457 <built_in_rec>	=>	take	(	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_14"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")
            
            """ 458 <built_in_rec>	=>	tochars	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_15"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            
            """ 459 <built_in_rec>	=>	topiece	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_16"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            
            """ 460 <built_in_rec>	=>	tosip	(	<any_expr>	) """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_17"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<built-in_rec>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 461 <conditional_st>	=>	<cond_check> """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st>"]:
            self.cond_check()
            
            """ 462 <conditional_st>	=>	<cond_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st>_1"]:
            self.cond_menu()
        else: self.parse_token(PREDICT_SET_M["<conditional_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 463 <cond_check>	=>	check	(	<strict_flag_expr>	)	<platter>	<alt_clause>	<instead_clause> """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.platter()
            self.alt_clause()
            self.instead_clause()
        else: self.parse_token(PREDICT_SET_M["<cond_check>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def alt_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 464 <alt_clause>	=>	alt	(	<strict_flag_expr>	)	<platter>	<alt_clause> """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.platter()
            self.alt_clause()
            
            """ 465 <alt_clause>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<alt_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 466 <instead_clause>	=>	instead	<platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause>"]:
            self.parse_token("instead")
            self.platter()
            
            """ 467 <instead_clause>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<instead_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 468 <cond_menu>	=>	menu	(	<any_expr>	)	<menu_platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu>"]:
            self.parse_token("menu")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            self.menu_platter()
        else: self.parse_token(PREDICT_SET_M["<cond_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 469 <menu_platter>	=>	{	<choice_clause>	<usual_clause>	} """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_platter>"]:
            self.parse_token("{")
            self.choice_clause()
            self.usual_clause()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 470 <choice_clause>	=>	choice	<choice_val>	:	<statements_menu>	<choice_clause> """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.statements_menu()
            self.choice_clause()
            
            """ 471 <choice_clause>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<choice_clause>"])


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 472 <choice_val>	=>	piece_lit """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_val>"]:
            self.parse_token("piece_lit")
            
            """ 473 <choice_val>	=>	chars_lit """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_val>_1"]:
            self.parse_token("chars_lit")
        
        else: self.parse_token(PREDICT_SET_M["<choice_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 474 <statements_menu>	=>	<id_statements_menu>	<statements_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_menu>"]:
            self.id_statements_menu()
            self.statements_menu()
            
            """ 475 <statements_menu>	=>	<built_in_rec_call>	;	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_menu()
            
            """ 476 <statements_menu>	=>	<conditional_st_menu>	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_2"]:
            self.conditional_st_menu()
            self.statements_menu()
            
            """ 477 <statements_menu>	=>	<looping_st>	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_3"]:
            self.looping_st()
            self.statements_menu()
            
            """ 478 <statements_menu>	=>	<jump_stop>	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_4"]:
            self.jump_stop()
            self.statements_menu()
            
            """ 479 <statements_menu>	=>	<jump_serve>	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_5"]:
            self.jump_serve()
            self.statements_menu()
            
            """ 480 <statements_menu>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<statements_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 481 <id_statements_menu>	=>	id	<id_statements_ext>	<statements_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_menu>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_menu()
        else: self.parse_token(PREDICT_SET_M["<id_statements_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 482 <conditional_st_menu>	=>	<cond_check_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>"]:
            self.cond_check_menu()
            
            """ 483 <conditional_st_menu>	=>	<cond_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>_1"]:
            self.cond_menu()
        else: self.parse_token(PREDICT_SET_M["<conditional_st_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 484 <cond_check_menu>	=>	check	(	<strict_flag_expr>	)	<menu_check_platter>	<alt_clause>	<instead_clause> """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_menu>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.menu_check_platter()
            self.alt_clause()
            self.instead_clause()
        else: self.parse_token(PREDICT_SET_M["<cond_check_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_check_platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 485 <menu_check_platter>	=>	{	<local_decl_menu>	<statements_menu>	} """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_check_platter>"]:
            self.parse_token("{")
            self.local_decl_menu()
            self.statements_menu()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_check_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 486 <local_decl_menu>	=>	piece	<piece_decl>	<local_decl_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_menu()
            
            """ 487 <local_decl_menu>	=>	chars	<chars_decl>	<local_decl_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_menu()
            
            """ 488 <local_decl_menu>	=>	sip	<sip_decl>	<local_decl_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_menu()
            
            """ 489 <local_decl_menu>	=>	flag	<flag_decl>	<local_decl_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_menu()
            
            """ 490 <local_decl_menu>	=>	id	<local_id_tail_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_4"]:
            self.parse_token("id")
            self.local_id_tail_menu()
            
            """ 491 <local_decl_menu>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<local_decl_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 492 <local_id_tail_menu>	=>	of	<table_declare>	;	<local_decl_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_menu()
            
            """ 493 <local_id_tail_menu>	=>	[	<endb_tail_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_1"]:
            self.parse_token("[")
            self.endb_tail_menu()
            
            """ 494 <local_id_tail_menu>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()
            
            """ 495 <local_id_tail_menu>	=>	<assignment_op>	<value>	;	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()
            
            """ 496 <local_id_tail_menu>	=>	<tail1>	;	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_menu()
        else: self.parse_token(PREDICT_SET_M["<local_id_tail_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endb_tail_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 497 <endb_tail_menu>	=>	]	<dimensions_tail>	of	<table_declare>	;	<local_decl_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail_menu>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_menu()
            
            """ 498 <endb_tail_menu>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements_menu> """
        elif self.tokens[self.pos].type in PREDICT_SET["<]_tail_menu>_1"]:
            self.strict_piece_expr()
            self.parse_token("]")
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()
        else: self.parse_token(PREDICT_SET_M["<]_tail_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def looping_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 499 <looping_st>	=>	<loop_pass> """
        if self.tokens[self.pos].type in PREDICT_SET["<looping_st>"]:
            self.loop_pass()
            
            """ 500 <looping_st>	=>	<loop_repeat> """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_1"]:
            self.loop_repeat()
            
            """ 501 <looping_st>	=>	<loop_order> """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_2"]:
            self.loop_order()
        else: self.parse_token(PREDICT_SET_M["<looping_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_pass(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 502 <loop_pass>	=>	pass	(	<initialization>	<update>	<strict_flag_expr>	)	<loop_platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_pass>"]:
            self.parse_token("pass")
            self.parse_token("(")
            self.initialization()
            self.update()
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
        else: self.parse_token(PREDICT_SET_M["<loop_pass>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def initialization(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 503 <initialization>	=>	id	=	<strict_piece_expr>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<initialization>"]:
            self.parse_token("id")
            self.loop_init()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<initialization>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 505 <loop_init> =>  =   <strict_piece_expr>  """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """ 506 <loop_init> =>  =   λ  """
        elif self.tokens[self.pos].type in PREDICT_SET["<loop_init>_1"]:
            pass 
        
        else: self.parse_token(PREDICT_SET_M["<loop_init>"])


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def update(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 504 <update>	=>	id	<accessor_tail> <assignment_op> <strict_piece_expr_upd> ; """
        if self.tokens[self.pos].type in PREDICT_SET["<update>"]:
            self.parse_token("id")
            self.accessor_tail()
            self.assignment_op()
            self.strict_piece_expr_upd()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<update>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 505 <loop_platter>	=>	{	<local_decl_loop>	<statements_loop>	} """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_platter>"]:
            self.parse_token("{")
            self.local_decl_loop()
            self.statements_loop()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<loop_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 506 <local_decl_loop>	=>	piece	<piece_decl>	<local_decl_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_loop()
            
            """ 507 <local_decl_loop>	=>	chars	<chars_decl>	<local_decl_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_loop()
            
            """ 508 <local_decl_loop>	=>	sip	<sip_decl>	<local_decl_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_loop()
            
            """ 509 <local_decl_loop>	=>	flag	<flag_decl>	<local_decl_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_loop()
            
            """ 510 <local_decl_loop>	=>	id	<local_id_tail_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_4"]:
            self.parse_token("id")
            self.local_id_tail_loop()
            
            """ 511 <local_decl_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<local_decl_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 512 <local_id_tail_loop>	=>	of	<table_declare>	;	<local_decl_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_loop()
            
            """ 513 <local_id_tail_loop>	=>	[	<endb_tail_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_1"]:
            self.parse_token("[")
            self.endb_tail_loop()
            
            """ 514 <local_id_tail_loop>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()
            
            """ 515 <local_id_tail_loop>	=>	<assignment_op>	<value>	;	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()
            
            """ 516 <local_id_tail_loop>	=>	<tail1>	;	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_loop()
        else: self.parse_token(PREDICT_SET_M["<local_id_tail_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endb_tail_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 517 <endb_tail_loop>	=>	]	<dimensions_tail>	of	<table_declare>	;	<local_decl_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail_loop>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_loop()
            
            """ 518 <endb_tail_loop>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<]_tail_loop>_1"]:
            self.strict_piece_expr()
            self.parse_token("]")
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()
        else: self.parse_token(PREDICT_SET_M["<]_tail_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 519 <statements_loop>	=>	<id_statements_loop>	<statements_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_loop>"]:
            self.id_statements_loop()
            self.statements_loop()
            
            """ 520 <statements_loop>	=>	<built_in_rec_call>	;	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_loop()
            
            """ 521 <statements_loop>	=>	<conditional_st_loop>	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_2"]:
            self.conditional_st_loop()
            self.statements_loop()
            
            """ 522 <statements_loop>	=>	<looping_st>	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_3"]:
            self.looping_st()
            self.statements_loop()
            
            """ 523 <statements_loop>	=>	<jump_st>	<statements_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_4"]:
            self.jump_st()
            self.statements_loop()
            
            """ 524 <statements_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<statements_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 525 <id_statements_loop>	=>	id	<id_statements_ext>	<statements_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_loop>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_loop()
        else: self.parse_token(PREDICT_SET_M["<id_statements_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 526 <conditional_st_loop>	=>	<cond_check_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>"]:
            self.cond_check_loop()
            
            """ 527 <conditional_st_loop>	=>	<cond_menu_loop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>_1"]:
            self.cond_menu_loop()
        else: self.parse_token(PREDICT_SET_M["<conditional_st_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 528 <cond_check_loop>	=>	check	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>	<instead_clause_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_loop>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
            self.alt_clause_loop()
            self.instead_clause_loop()
        else: self.parse_token(PREDICT_SET_M["<cond_check_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def alt_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 529 <alt_clause_loop>	=>	alt	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
            self.alt_clause_loop()
            
            """ 530 <alt_clause_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<alt_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 531 <instead_clause_loop>	=>	instead	<loop_platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>"]:
            self.parse_token("instead")
            self.loop_platter()
            
            """ 532 <instead_clause_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<instead_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 533 <cond_menu_loop>	=>	menu	(	<any_expr>	)	<menu_loop_platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu_loop>"]:
            self.parse_token("menu")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")
            self.menu_loop_platter()
        else: self.parse_token(PREDICT_SET_M["<cond_menu_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_loop_platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 534 <menu_loop_platter>	=>	{	<choice_clause_loop>	<usual_clause_loop>	} """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_loop_platter>"]:
            self.parse_token("{")
            self.choice_clause_loop()
            self.usual_clause_loop()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_loop_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 535 <choice_clause_loop>	=>	choice	<choice_val>	:	<statements_loop>	<choice_clause_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.statements_loop()
            self.choice_clause_loop()
            
            """ 536 <choice_clause_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<choice_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def usual_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 537 <usual_clause_loop>	=>	usual	:	<statements_loop> """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.statements_loop()
            
            """ 538 <usual_clause_loop>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<usual_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 539 <jump_st>	=>	<jump_next> """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_st>"]:
            self.jump_next()
            
            """ 540 <jump_st>	=>	<jump_stop> """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_1"]:
            self.jump_stop()
            
            """ 541 <jump_st>	=>	<jump_serve> """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_2"]:
            self.jump_serve()
        else: self.parse_token(PREDICT_SET_M["<jump_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_next(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 542 <jump_next>	=>	next	; """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_next>"]:
            self.parse_token("next")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_next>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_stop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 543 <jump_stop>	=>	stop	; """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_stop>"]:
            self.parse_token("stop")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_stop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_serve(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 544 <jump_serve>	=>	serve	<value>	; """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_serve>"]:
            self.parse_token("serve")
            self.value()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_serve>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_repeat(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 545 <loop_repeat>	=>	repeat	(	<strict_flag_expr>	)	<loop_platter> """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_repeat>"]:
            self.parse_token("repeat")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
        else: self.parse_token(PREDICT_SET_M["<loop_repeat>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_order(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 546 <loop_order>	=>	order	<loop_platter>	repeat	(	<strict_flag_expr>	)	; """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_order>"]:
            self.parse_token("order")
            self.loop_platter()
            self.parse_token("repeat")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<loop_order>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def usual_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """ 547 <usual_clause>	=>	usual	:	<statements_menu> """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.statements_menu()
                
            """ 548 <usual_clause>	=>	λ """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause>_1"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<usual_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_expr_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    517 <strict_piece_expr_upd>	=>	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr_upd>"]:
            self.strict_piece_term_upd()
            self.strict_piece_add_tail_upd()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_expr_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_term_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    518 <strict_piece_term_upd>	=>	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term_upd>"]:
            self.strict_piece_factor_upd()
            self.strict_piece_mult_tail_upd()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_term_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_factor_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    519 <strict_piece_factor_upd>	=>	<ret_piece_upd>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>"]:
            self.ret_piece_upd()

            """    520 <strict_piece_factor_upd>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>_1"]:
            self.parse_token("id")
            self.id_tail()

            """    521 <strict_piece_factor_upd>	=>	(	<strict_piece_expr_upd>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>_2"]:
            self.parse_token("(")
            self.strict_piece_expr_upd()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<strict_piece_factor_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_piece_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    522 <ret_piece_upd>	=>	topiece	(	<any_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    523 <ret_piece_upd>	=>	fact	(	<strict_piece_expr_upd>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_1"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr_upd()
            self.parse_token(")")

            """    524 <ret_piece_upd>	=>	pow	(	<strict_piece_expr_upd>	,	<strict_piece_expr_upd>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_2"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr_upd()
            self.parse_token(",")
            self.strict_piece_expr_upd()
            self.parse_token(")")

            """    525 <ret_piece_upd>	=>	piece_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_3"]:
            self.parse_token("piece_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_piece_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_add_tail_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    526 <strict_piece_add_tail_upd>	=>	+	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>"]:
            self.parse_token("+")
            self.strict_piece_term_upd()
            self.strict_piece_add_tail_upd()

            """    527 <strict_piece_add_tail_upd>	=>	-	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>_1"]:
            self.parse_token("-")
            self.strict_piece_term_upd()
            self.strict_piece_add_tail_upd()

            """    528 <strict_piece_add_tail_upd>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_add_tail_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_mult_tail_upd(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    529 <strict_piece_mult_tail_upd>	=>	*	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>"]:
            self.parse_token("*")
            self.strict_piece_factor_upd()
            self.strict_piece_mult_tail_upd()

            """    530 <strict_piece_mult_tail_upd>	=>	/	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_1"]:
            self.parse_token("/")
            self.strict_piece_factor_upd()
            self.strict_piece_mult_tail_upd()

            """    531 <strict_piece_mult_tail_upd>	=>	%	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_2"]:
            self.parse_token("%")
            self.strict_piece_factor_upd()
            self.strict_piece_mult_tail_upd()

            """    532 <strict_piece_mult_tail_upd>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_3"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_mult_tail_upd>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J


if __name__ == "__main__":
    
    filepath = "parser.platter"
    code = run_file(filepath)
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    try:
        parser.parse_program()
        print("No Syntax Error")
    except SyntaxError as e:
        print(str(e))
