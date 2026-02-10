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

        """    2 <global_decl>	=>	piece	<piece_decl>	<global_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<global_decl>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.global_decl()

            """    3 <global_decl>	=>	chars	<chars_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.global_decl()

            """    4 <global_decl>	=>	sip	<sip_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.global_decl()

            """    5 <global_decl>	=>	flag	<flag_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.global_decl()

            """    6 <global_decl>	=>	<table_prototype>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_4"]:
            self.table_prototype()
            self.global_decl()

            """    7 <global_decl>	=>	id	<table_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_5"]:
            self.parse_token("id")
            self.table_decl()
            self.global_decl()

            """    8 <global_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<global_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    9 <piece_decl>	=>	of	<piece_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_decl>"]:
            self.parse_token("of")
            self.piece_id()
            self.parse_token(";")

            """    10 <piece_decl>	=>	<decl_type>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_decl>_1"]:
            self.decl_type()

        else: self.parse_token(PREDICT_SET_M["<piece_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    11 <piece_id>	=>	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id>"]:
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    12 <piece_ingredient_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """    13 <piece_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<piece_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def any_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    14 <any_expr>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_expr>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()

            """    15 <any_expr>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()

            """    16 <any_expr>	=>	<ret_chars>	<chars_add_tail>	<chars_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_rel_gate()

            """    17 <any_expr>	=>	<ret_flag>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_3"]:
            self.ret_flag()
            self.flag_logic_tail()

            """    18 <any_expr>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_bridge()

            """    19 <any_expr>	=>	(	<paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_5"]:
            self.parse_token("(")
            self.paren_dispatch()

            """    20 <any_expr>	=>	not	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_6"]:
            self.parse_token("not")
            self.must_be_flag()

        else: self.parse_token(PREDICT_SET_M["<any_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    21 <piece_mult_tail>	=>	*	<piece_factor>	<piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>"]:
            self.parse_token("*")
            self.piece_factor()
            self.piece_mult_tail()

            """    22 <piece_mult_tail>	=>	/	<piece_factor>	<piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_1"]:
            self.parse_token("/")
            self.piece_factor()
            self.piece_mult_tail()

            """    23 <piece_mult_tail>	=>	%	<piece_factor>	<piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_2"]:
            self.parse_token("%")
            self.piece_factor()
            self.piece_mult_tail()

            """    24 <piece_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_mult_tail>_3"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<piece_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    25 <piece_factor>	=>	<ret_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_factor>"]:
            self.ret_piece()

            """    26 <piece_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_factor>_1"]:
            self.id_()

            """    27 <piece_factor>	=>	(	<piece_inner_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_factor>_2"]:
            self.parse_token("(")
            self.piece_inner_dispatch()

        else: self.parse_token(PREDICT_SET_M["<piece_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    28 <id>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id>"]:
            self.parse_token("id")
            self.id_tail()
        else: self.parse_token(PREDICT_SET_M["<id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    29 <id_tail>	=>	<call_tailopt>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_tail>"]:
            self.call_tailopt()

            """    30 <id_tail>	=>	<accessor_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_tail>_1"]:
            self.accessor_tail()

        else: self.parse_token(PREDICT_SET_M["<id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tailopt(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    31 <call_tailopt>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")

            """    32 <call_tailopt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<call_tailopt>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    33 <flavor>	=>	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor>"]:
            self.value()
            self.flavor_tail()

            """    34 <flavor>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flavor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def value(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    35 <value>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<value>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()

            """    36 <value>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()

            """    37 <value>	=>	<ret_chars>	<chars_add_tail>	<chars_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_rel_gate()

            """    38 <value>	=>	<ret_flag>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_3"]:
            self.ret_flag()
            self.flag_logic_tail()

            """    39 <value>	=>	(	<paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_4"]:
            self.parse_token("(")
            self.paren_dispatch()

            """    40 <value>	=>	not	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_5"]:
            self.parse_token("not")
            self.must_be_flag()

            """    41 <value>	=>	[	<notation_val>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_6"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")

            """    42 <value>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_7"]:
            self.ret_array()

            """    43 <value>	=>	id	<id_tail>	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_8"]:
            self.parse_token("id")
            self.id_tail()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()

        else: self.parse_token(PREDICT_SET_M["<value>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    44 <piece_add_tail>	=>	+	<piece_term>	<piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>"]:
            self.parse_token("+")
            self.piece_term()
            self.piece_add_tail()

            """    45 <piece_add_tail>	=>	-	<piece_term>	<piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>_1"]:
            self.parse_token("-")
            self.piece_term()
            self.piece_add_tail()

            """    46 <piece_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<piece_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    47 <piece_term>	=>	<piece_factor>	<piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_term>"]:
            self.piece_factor()
            self.piece_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    48 <piece_rel_gate>	=>	==	<piece_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()

            """    49 <piece_rel_gate>	=>	!=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_1"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()

            """    50 <piece_rel_gate>	=>	<=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_2"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()

            """    51 <piece_rel_gate>	=>	>=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_3"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()

            """    52 <piece_rel_gate>	=>	<	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_4"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()

            """    53 <piece_rel_gate>	=>	>	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_5"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()

            """    54 <piece_rel_gate>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_rel_gate>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<piece_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    55 <piece_expr>	=>	<piece_term>	<piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_expr>"]:
            self.piece_term()
            self.piece_add_tail()
        else: self.parse_token(PREDICT_SET_M["<piece_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_logic_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    56 <flag_logic_tail>	=>	and	<must_be_flag>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>"]:
            self.parse_token("and")
            self.must_be_flag()

            """    57 <flag_logic_tail>	=>	or	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_1"]:
            self.parse_token("or")
            self.must_be_flag()

            """    58 <flag_logic_tail>	=>	==	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_2"]:
            self.parse_token("==")
            self.must_be_flag()

            """    59 <flag_logic_tail>	=>	!=	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_3"]:
            self.parse_token("!=")
            self.must_be_flag()

            """    60 <flag_logic_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_logic_tail>_4"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flag_logic_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def must_be_flag(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    61 <must_be_flag>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_trap_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_trap_gate()

            """    62 <must_be_flag>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_trap_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_trap_gate()

            """    63 <must_be_flag>	=>	<ret_chars>	<chars_add_tail>	<chars_trap_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_trap_gate()

            """    64 <must_be_flag>	=>	<ret_flag>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_3"]:
            self.ret_flag()
            self.flag_logic_tail()

            """    65 <must_be_flag>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()

            """    66 <must_be_flag>	=>	(	<paren_dispatch>	<flag_after_paren>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_5"]:
            self.parse_token("(")
            self.paren_dispatch()
            self.flag_after_paren()

            """    67 <must_be_flag>	=>	not	<must_be_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<must_be_flag>_6"]:
            self.parse_token("not")
            self.must_be_flag()

        else: self.parse_token(PREDICT_SET_M["<must_be_flag>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    68 <piece_trap_gate>	=>	==	<piece_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()

            """    69 <piece_trap_gate>	=>	!=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_1"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()

            """    70 <piece_trap_gate>	=>	<=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_2"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()

            """    71 <piece_trap_gate>	=>	>=	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_3"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()

            """    72 <piece_trap_gate>	=>	<	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_4"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()

            """    73 <piece_trap_gate>	=>	>	<piece_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_trap_gate>_5"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()

        else: self.parse_token(PREDICT_SET_M["<piece_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    74 <sip_mult_tail>	=>	*	<sip_factor>	<sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>"]:
            self.parse_token("*")
            self.sip_factor()
            self.sip_mult_tail()

            """    75 <sip_mult_tail>	=>	/	<sip_factor>	<sip_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>_1"]:
            self.parse_token("/")
            self.sip_factor()
            self.sip_mult_tail()

            """    76 <sip_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_mult_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<sip_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    77 <sip_factor>	=>	<ret_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_factor>"]:
            self.ret_sip()

            """    78 <sip_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_factor>_1"]:
            self.id_()

            """    79 <sip_factor>	=>	(	<sip_inner_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_factor>_2"]:
            self.parse_token("(")
            self.sip_inner_dispatch()

        else: self.parse_token(PREDICT_SET_M["<sip_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    80 <sip_inner_dispatch>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge_recurse>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge_recurse()

            """    81 <sip_inner_dispatch>	=>	<id>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>_1"]:
            self.id_()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge_recurse()

            """    82 <sip_inner_dispatch>	=>	(	<sip_inner_dispatch>	<sip_close_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_inner_dispatch>_2"]:
            self.parse_token("(")
            self.sip_inner_dispatch()
            self.sip_close_recurse()

        else: self.parse_token(PREDICT_SET_M["<sip_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    83 <sip_add_tail>	=>	+	<sip_term>	<sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>"]:
            self.parse_token("+")
            self.sip_term()
            self.sip_add_tail()

            """    84 <sip_add_tail>	=>	-	<sip_term>	<sip_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>_1"]:
            self.parse_token("-")
            self.sip_term()
            self.sip_add_tail()

            """    85 <sip_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<sip_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    86 <sip_term>	=>	<sip_factor>	<sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_term>"]:
            self.sip_factor()
            self.sip_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    87 <sip_bridge_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<sip_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    88 <sip_close_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<sip_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    89 <sip_trap_gate>	=>	==	<sip_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()

            """    90 <sip_trap_gate>	=>	!=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_1"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()

            """    91 <sip_trap_gate>	=>	<=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_2"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()

            """    92 <sip_trap_gate>	=>	>=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_3"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()

            """    93 <sip_trap_gate>	=>	<	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_4"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()

            """    94 <sip_trap_gate>	=>	>	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_trap_gate>_5"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()

        else: self.parse_token(PREDICT_SET_M["<sip_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    95 <sip_expr>	=>	<sip_term>	<sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_expr>"]:
            self.sip_term()
            self.sip_add_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    96 <strict_chars_expr>	=>	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_expr>"]:
            self.strict_chars_factor()
            self.strict_chars_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_chars_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    97 <strict_chars_factor>	=>	<ret_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>"]:
            self.ret_chars()

            """    98 <strict_chars_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_1"]:
            self.id_()

            """    99 <strict_chars_factor>	=>	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_2"]:
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<strict_chars_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    100 <strict_chars_add_tail>	=>	+	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>"]:
            self.parse_token("+")
            self.strict_chars_factor()
            self.strict_chars_add_tail()

            """    101 <strict_chars_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_chars_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    102 <strict_sip_expr>	=>	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_expr>"]:
            self.strict_sip_term()
            self.strict_sip_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_sip_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    103 <strict_sip_term>	=>	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_term>"]:
            self.strict_sip_factor()
            self.strict_sip_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_sip_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    104 <strict_sip_mult_tail>	=>	*	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()

            """    105 <strict_sip_mult_tail>	=>	/	<strict_sip_factor>	<strict_sip_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()

            """    106 <strict_sip_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_sip_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    107 <strict_sip_add_tail>	=>	+	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>"]:
            self.parse_token("+")
            self.strict_sip_term()
            self.strict_sip_add_tail()

            """    108 <strict_sip_add_tail>	=>	-	<strict_sip_term>	<strict_sip_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_term()
            self.strict_sip_add_tail()

            """    109 <strict_sip_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_sip_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    110 <chars_add_tail>	=>	+	<chars_factor>	<chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_add_tail>"]:
            self.parse_token("+")
            self.chars_factor()
            self.chars_add_tail()

            """    111 <chars_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_add_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    112 <chars_factor>	=>	<ret_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_factor>"]:
            self.ret_chars()

            """    113 <chars_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_factor>_1"]:
            self.id_()

            """    114 <chars_factor>	=>	(	<chars_inner_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_factor>_2"]:
            self.parse_token("(")
            self.chars_inner_dispatch()

        else: self.parse_token(PREDICT_SET_M["<chars_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    115 <chars_inner_dispatch>	=>	<ret_chars>	<chars_add_tail>	<chars_bridge_recurse>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_bridge_recurse()

            """    116 <chars_inner_dispatch>	=>	<id>	<chars_add_tail>	<chars_bridge_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>_1"]:
            self.id_()
            self.chars_add_tail()
            self.chars_bridge_recurse()

            """    117 <chars_inner_dispatch>	=>	(	<chars_inner_dispatch>	<chars_close_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_inner_dispatch>_2"]:
            self.parse_token("(")
            self.chars_inner_dispatch()
            self.chars_close_recurse()

        else: self.parse_token(PREDICT_SET_M["<chars_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    118 <chars_bridge_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<chars_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    119 <chars_close_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<chars_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_trap_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    120 <chars_trap_gate>	=>	==	<chars_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()

            """    121 <chars_trap_gate>	=>	!=	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_1"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()

            """    122 <chars_trap_gate>	=>	<=	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_2"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()

            """    123 <chars_trap_gate>	=>	>=	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_3"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()

            """    124 <chars_trap_gate>	=>	<	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_4"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()

            """    125 <chars_trap_gate>	=>	>	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_trap_gate>_5"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()

        else: self.parse_token(PREDICT_SET_M["<chars_trap_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    126 <chars_expr>	=>	<chars_factor>	<chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_expr>"]:
            self.chars_factor()
            self.chars_add_tail()
        else: self.parse_token(PREDICT_SET_M["<chars_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_datas_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    127 <strict_datas_expr>	=>	[	<notation_val>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")

            """    128 <strict_datas_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_1"]:
            self.parse_token("id")
            self.id_tail()

            """    129 <strict_datas_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_2"]:
            self.ret_array()

        else: self.parse_token(PREDICT_SET_M["<strict_datas_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def notation_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    130 <notation_val>	=>	<array_element>    """
        if self.tokens[self.pos].type in PREDICT_SET["<notation_val>"]:
            self.array_element()

            """    131 <notation_val>	=>	id	<array_or_table>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_1"]:
            self.parse_token("id")
            self.array_or_table()

            """    132 <notation_val>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<notation_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    133 <array_element>	=>	piece_lit	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element>"]:
            self.parse_token("piece_lit")
            self.element_value_tail()

            """    134 <array_element>	=>	sip_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_1"]:
            self.parse_token("sip_lit")
            self.element_value_tail()

            """    135 <array_element>	=>	flag_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_2"]:
            self.parse_token("flag_lit")
            self.element_value_tail()

            """    136 <array_element>	=>	chars_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_3"]:
            self.parse_token("chars_lit")
            self.element_value_tail()

            """    137 <array_element>	=>	[	<notation_val>	]	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_4"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")
            self.element_value_tail()

        else: self.parse_token(PREDICT_SET_M["<array_element>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_value_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    138 <element_value_tail>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>"]:
            self.parse_token(",")
            self.array_element_id()

            """    139 <element_value_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<element_value_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    140 <array_element_id>	=>	id	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_id>"]:
            self.parse_token("id")
            self.element_value_tail()

            """    141 <array_element_id>	=>	<array_element>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_1"]:
            self.array_element()

            """    142 <array_element_id>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<array_element_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_or_table(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    143 <array_or_table>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_or_table>"]:
            self.parse_token(",")
            self.array_element_id()

            """    144 <array_or_table>	=>	=	<value>	;	<field_assignments>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_1"]:
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()

            """    145 <array_or_table>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<array_or_table>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def field_assignments(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    146 <field_assignments>	=>	id	=	<value>	;	<field_assignments>    """
        if self.tokens[self.pos].type in PREDICT_SET["<field_assignments>"]:
            self.parse_token("id")
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()

            """    147 <field_assignments>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<field_assignments>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<field_assignments>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_array_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    148 <strict_array_expr>	=>	[	<array_element_id>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>"]:
            self.parse_token("[")
            self.array_element_id()
            self.parse_token("]")

            """    149 <strict_array_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_1"]:
            self.parse_token("id")
            self.id_tail()

            """    150 <strict_array_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_2"]:
            self.ret_array()

        else: self.parse_token(PREDICT_SET_M["<strict_array_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    151 <univ_mult_tail>	=>	*	<univ_numeric_factor>	<univ_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>"]:
            self.parse_token("*")
            self.univ_numeric_factor()
            self.univ_mult_tail()

            """    152 <univ_mult_tail>	=>	/	<univ_numeric_factor>	<univ_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_1"]:
            self.parse_token("/")
            self.univ_numeric_factor()
            self.univ_mult_tail()

            """    153 <univ_mult_tail>	=>	%	<univ_numeric_factor>	<univ_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_2"]:
            self.parse_token("%")
            self.univ_numeric_factor()
            self.univ_mult_tail()

            """    154 <univ_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_mult_tail>_3"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<univ_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    155 <univ_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_factor>"]:
            self.id_()

            """    156 <univ_factor>	=>	<ret_piece>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_1"]:
            self.ret_piece()

            """    157 <univ_factor>	=>	<ret_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_2"]:
            self.ret_sip()

            """    158 <univ_factor>	=>	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_factor>_3"]:
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<univ_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    159 <univ_add_tail>	=>	+	<univ_term>	<univ_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>"]:
            self.parse_token("+")
            self.univ_term()
            self.univ_add_tail()

            """    160 <univ_add_tail>	=>	-	<univ_term>	<univ_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>_1"]:
            self.parse_token("-")
            self.univ_term()
            self.univ_add_tail()

            """    161 <univ_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<univ_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    162 <univ_term>	=>	<univ_numeric_factor>	<univ_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_term>"]:
            self.univ_numeric_factor()
            self.univ_mult_tail()

            """    163 <univ_term>	=>	<ret_chars>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_term>_1"]:
            self.ret_chars()

            """    164 <univ_term>	=>	<ret_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_term>_2"]:
            self.ret_flag()

        else: self.parse_token(PREDICT_SET_M["<univ_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    165 <univ_rel_gate>	=>	==	<univ_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>"]:
            self.parse_token("==")
            self.univ_expr()
            self.flag_logic_tail()

            """    166 <univ_rel_gate>	=>	!=	<univ_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_1"]:
            self.parse_token("!=")
            self.univ_expr()
            self.flag_logic_tail()

            """    167 <univ_rel_gate>	=>	<=	<univ_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_2"]:
            self.parse_token("<=")
            self.univ_expr()
            self.flag_logic_tail()

            """    168 <univ_rel_gate>	=>	>=	<univ_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_3"]:
            self.parse_token(">=")
            self.univ_expr()
            self.flag_logic_tail()

            """    169 <univ_rel_gate>	=>	<	<univ_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_4"]:
            self.parse_token("<")
            self.univ_expr()
            self.flag_logic_tail()

            """    170 <univ_rel_gate>	=>	>	<univ_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_5"]:
            self.parse_token(">")
            self.univ_expr()
            self.flag_logic_tail()

            """    171 <univ_rel_gate>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_rel_gate>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<univ_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    172 <univ_expr>	=>	<univ_term>	<univ_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_expr>"]:
            self.univ_term()
            self.univ_add_tail()
        else: self.parse_token(PREDICT_SET_M["<univ_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    173 <paren_dispatch>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge()

            """    174 <paren_dispatch>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge()

            """    175 <paren_dispatch>	=>	<ret_chars>	<chars_add_tail>	<chars_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_2"]:
            self.ret_chars()
            self.chars_add_tail()
            self.chars_bridge()

            """    176 <paren_dispatch>	=>	<ret_flag>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_3"]:
            self.ret_flag()
            self.flag_logic_tail()
            self.flag_closure()

            """    177 <paren_dispatch>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_4"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_bridge()

            """    178 <paren_dispatch>	=>	(	<paren_dispatch>	<univ_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_5"]:
            self.parse_token("(")
            self.paren_dispatch()
            self.univ_closure()

            """    179 <paren_dispatch>	=>	not	<must_be_flag>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch>_6"]:
            self.parse_token("not")
            self.must_be_flag()
            self.flag_closure()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    180 <piece_bridge>	=>	)	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>"]:
            self.parse_token(")")
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()

            """    181 <piece_bridge>	=>	==	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_1"]:
            self.parse_token("==")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    182 <piece_bridge>	=>	!=	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_2"]:
            self.parse_token("!=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    183 <piece_bridge>	=>	<=	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_3"]:
            self.parse_token("<=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    184 <piece_bridge>	=>	>=	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_4"]:
            self.parse_token(">=")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    185 <piece_bridge>	=>	<	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_5"]:
            self.parse_token("<")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    186 <piece_bridge>	=>	>	<piece_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_bridge>_6"]:
            self.parse_token(">")
            self.piece_expr()
            self.flag_logic_tail()
            self.flag_closure()

        else: self.parse_token(PREDICT_SET_M["<piece_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_closure(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    187 <flag_closure>	=>	)	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_closure>"]:
            self.parse_token(")")
            self.flag_logic_tail()
        else: self.parse_token(PREDICT_SET_M["<flag_closure>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    188 <sip_bridge>	=>	)	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>"]:
            self.parse_token(")")
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()

            """    189 <sip_bridge>	=>	==	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_1"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    190 <sip_bridge>	=>	!=	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_2"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    191 <sip_bridge>	=>	<=	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_3"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    192 <sip_bridge>	=>	>=	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_4"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    193 <sip_bridge>	=>	<	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_5"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    194 <sip_bridge>	=>	>	<sip_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_bridge>_6"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()
            self.flag_closure()

        else: self.parse_token(PREDICT_SET_M["<sip_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    195 <sip_rel_gate>	=>	==	<sip_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>"]:
            self.parse_token("==")
            self.sip_expr()
            self.flag_logic_tail()

            """    196 <sip_rel_gate>	=>	!=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_1"]:
            self.parse_token("!=")
            self.sip_expr()
            self.flag_logic_tail()

            """    197 <sip_rel_gate>	=>	<=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_2"]:
            self.parse_token("<=")
            self.sip_expr()
            self.flag_logic_tail()

            """    198 <sip_rel_gate>	=>	>=	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_3"]:
            self.parse_token(">=")
            self.sip_expr()
            self.flag_logic_tail()

            """    199 <sip_rel_gate>	=>	<	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_4"]:
            self.parse_token("<")
            self.sip_expr()
            self.flag_logic_tail()

            """    200 <sip_rel_gate>	=>	>	<sip_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_5"]:
            self.parse_token(">")
            self.sip_expr()
            self.flag_logic_tail()

            """    201 <sip_rel_gate>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_rel_gate>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<sip_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    202 <chars_bridge>	=>	)	<chars_add_tail>	<chars_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>"]:
            self.parse_token(")")
            self.chars_add_tail()
            self.chars_rel_gate()

            """    203 <chars_bridge>	=>	==	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_1"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    204 <chars_bridge>	=>	<=	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_2"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    205 <chars_bridge>	=>	>=	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_3"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    206 <chars_bridge>	=>	<	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_4"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    207 <chars_bridge>	=>	>	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_5"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    208 <chars_bridge>	=>	!=	<chars_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_bridge>_6"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()
            self.flag_closure()

        else: self.parse_token(PREDICT_SET_M["<chars_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_rel_gate(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    209 <chars_rel_gate>	=>	<=	<chars_expr>	<flag_logic_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>"]:
            self.parse_token("<=")
            self.chars_expr()
            self.flag_logic_tail()

            """    210 <chars_rel_gate>	=>	>=	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_1"]:
            self.parse_token(">=")
            self.chars_expr()
            self.flag_logic_tail()

            """    211 <chars_rel_gate>	=>	<	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_2"]:
            self.parse_token("<")
            self.chars_expr()
            self.flag_logic_tail()

            """    212 <chars_rel_gate>	=>	>	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_3"]:
            self.parse_token(">")
            self.chars_expr()
            self.flag_logic_tail()

            """    213 <chars_rel_gate>	=>	==	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_4"]:
            self.parse_token("==")
            self.chars_expr()
            self.flag_logic_tail()

            """    214 <chars_rel_gate>	=>	!=	<chars_expr>	<flag_logic_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_5"]:
            self.parse_token("!=")
            self.chars_expr()
            self.flag_logic_tail()

            """    215 <chars_rel_gate>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_rel_gate>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_rel_gate>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_bridge(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    216 <univ_bridge>	=>	)	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>"]:
            self.parse_token(")")
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()

            """    217 <univ_bridge>	=>	==	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_1"]:
            self.parse_token("==")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    218 <univ_bridge>	=>	!=	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_2"]:
            self.parse_token("!=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    219 <univ_bridge>	=>	<=	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_3"]:
            self.parse_token("<=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    220 <univ_bridge>	=>	>=	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_4"]:
            self.parse_token(">=")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    221 <univ_bridge>	=>	<	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_5"]:
            self.parse_token("<")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

            """    222 <univ_bridge>	=>	>	<univ_expr>	<flag_logic_tail>	<flag_closure>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bridge>_6"]:
            self.parse_token(">")
            self.univ_expr()
            self.flag_logic_tail()
            self.flag_closure()

        else: self.parse_token(PREDICT_SET_M["<univ_bridge>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_closure(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    223 <univ_closure>	=>	)	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_closure>"]:
            self.parse_token(")")
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()
        else: self.parse_token(PREDICT_SET_M["<univ_closure>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_after_paren(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    224 <flag_after_paren>	=>	    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_after_paren>"]:
            pass
        else: self.parse_token(PREDICT_SET_M["<flag_after_paren>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    225 <flavor_tail>	=>	,	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>"]:
            self.parse_token(",")
            self.value()
            self.flavor_tail()

            """    226 <flavor_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flavor_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def accessor_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    227 <accessor_tail>	=>	<array_accessor>    """
        if self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>"]:
            self.array_accessor()

            """    228 <accessor_tail>	=>	<table_accessor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_1"]:
            self.table_accessor()

            """    229 <accessor_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<accessor_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_accessor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    230 <array_accessor>	=>	[	<strict_piece_expr>	]	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor>"]:
            self.parse_token("[")
            self.strict_piece_expr()
            self.parse_token("]")
            self.accessor_tail()
        else: self.parse_token(PREDICT_SET_M["<array_accessor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_accessor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    231 <table_accessor>	=>	:	id	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_accessor>"]:
            self.parse_token(":")
            self.parse_token("id")
            self.accessor_tail()
        else: self.parse_token(PREDICT_SET_M["<table_accessor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_inner_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    232 <piece_inner_dispatch>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge_recurse>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge_recurse()

            """    233 <piece_inner_dispatch>	=>	<id>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>_1"]:
            self.id_()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge_recurse()

            """    234 <piece_inner_dispatch>	=>	(	<piece_inner_dispatch>	<piece_close_recurse>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_inner_dispatch>_2"]:
            self.parse_token("(")
            self.piece_inner_dispatch()
            self.piece_close_recurse()

        else: self.parse_token(PREDICT_SET_M["<piece_inner_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_bridge_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    235 <piece_bridge_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_bridge_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<piece_bridge_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_close_recurse(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    236 <piece_close_recurse>	=>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_close_recurse>"]:
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<piece_close_recurse>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_mult_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    237 <strict_piece_mult_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    238 <strict_piece_mult_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    239 <strict_piece_mult_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_2"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    240 <strict_piece_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_3"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_mult_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_add_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    241 <strict_piece_add_tail>	=>	+	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>"]:
            self.parse_token("+")
            self.strict_piece_term()
            self.strict_piece_add_tail()

            """    242 <strict_piece_add_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_term()
            self.strict_piece_add_tail()

            """    243 <strict_piece_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_piece_add_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    244 <piece_id_tail>	=>	,	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()

            """    245 <piece_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<piece_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def decl_type(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    246 <decl_type>	=>	<dimensions>	of	<array_declare>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_type>"]:
            self.dimensions()
            self.parse_token("of")
            self.array_declare()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<decl_type>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    247 <dimensions>	=>	[	]	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions>"]:
            self.parse_token("[")
            self.parse_token("]")
            self.dimensions_tail()
        else: self.parse_token(PREDICT_SET_M["<dimensions>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    248 <dimensions_tail>	=>	<dimensions>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>"]:
            self.dimensions()

            """    249 <dimensions_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<dimensions_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    250 <array_declare>	=>	id	<array_init>	<array_declare_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare>"]:
            self.parse_token("id")
            self.array_init()
            self.array_declare_tail()
        else: self.parse_token(PREDICT_SET_M["<array_declare>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    251 <array_init>	=>	=	<strict_array_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_init>"]:
            self.parse_token("=")
            self.strict_array_expr()

            """    252 <array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<array_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    253 <array_declare_tail>	=>	,	<array_declare>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail>"]:
            self.parse_token(",")
            self.array_declare()

            """    254 <array_declare_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<array_declare_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    255 <chars_decl>	=>	of	<chars_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_decl>"]:
            self.parse_token("of")
            self.chars_id()
            self.parse_token(";")

            """    256 <chars_decl>	=>	<decl_type>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_decl>_1"]:
            self.decl_type()

        else: self.parse_token(PREDICT_SET_M["<chars_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    257 <chars_id>	=>	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id>"]:
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()
        else: self.parse_token(PREDICT_SET_M["<chars_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    258 <chars_ingredient_init>	=>	=	<strict_chars_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>"]:
            self.parse_token("=")
            self.strict_chars_expr()

            """    259 <chars_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    260 <chars_id_tail>	=>	,	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()

            """    261 <chars_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<chars_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    262 <sip_decl>	=>	of	<sip_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_decl>"]:
            self.parse_token("of")
            self.sip_id()
            self.parse_token(";")

            """    263 <sip_decl>	=>	<decl_type>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_decl>_1"]:
            self.decl_type()

        else: self.parse_token(PREDICT_SET_M["<sip_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    264 <sip_id>	=>	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id>"]:
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()
        else: self.parse_token(PREDICT_SET_M["<sip_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    265 <sip_ingredient_init>	=>	=	<strict_sip_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>"]:
            self.parse_token("=")
            self.strict_sip_expr()

            """    266 <sip_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<sip_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    267 <sip_id_tail>	=>	,	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()

            """    268 <sip_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<sip_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    269 <flag_decl>	=>	of	<flag_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_decl>"]:
            self.parse_token("of")
            self.flag_id()
            self.parse_token(";")

            """    270 <flag_decl>	=>	<decl_type>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_decl>_1"]:
            self.decl_type()

        else: self.parse_token(PREDICT_SET_M["<flag_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_id(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    271 <flag_id>	=>	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id>"]:
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()
        else: self.parse_token(PREDICT_SET_M["<flag_id>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_ingredient_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    272 <flag_ingredient_init>	=>	=	<strict_flag_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>"]:
            self.parse_token("=")
            self.strict_flag_expr()

            """    273 <flag_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flag_ingredient_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    274 <flag_id_tail>	=>	,	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()

            """    275 <flag_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<flag_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_prototype(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    276 <table_prototype>	=>	table	of	id	=	[	<required_decl>	]	;    """
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

        """    277 <required_decl>	=>	<decl_head>	;	<required_decl_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl>"]:
            self.decl_head()
            self.parse_token(";")
            self.required_decl_tail()
        else: self.parse_token(PREDICT_SET_M["<required_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def decl_head(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    278 <decl_head>	=>	<primitive_types_dims>	of	id    """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_head>"]:
            self.primitive_types_dims()
            self.parse_token("of")
            self.parse_token("id")
        else: self.parse_token(PREDICT_SET_M["<decl_head>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def primitive_types_dims(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    279 <primitive_types_dims>	=>	piece	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>"]:
            self.parse_token("piece")
            self.dimensions_tail()

            """    280 <primitive_types_dims>	=>	sip	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_1"]:
            self.parse_token("sip")
            self.dimensions_tail()

            """    281 <primitive_types_dims>	=>	flag	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_2"]:
            self.parse_token("flag")
            self.dimensions_tail()

            """    282 <primitive_types_dims>	=>	chars	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_3"]:
            self.parse_token("chars")
            self.dimensions_tail()

            """    283 <primitive_types_dims>	=>	id	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_4"]:
            self.parse_token("id")
            self.dimensions_tail()

        else: self.parse_token(PREDICT_SET_M["<primitive_types_dims>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def required_decl_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    284 <required_decl_tail>	=>	<required_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>"]:
            self.required_decl()

            """    285 <required_decl_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<required_decl_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    286 <table_decl>	=>	of	<table_declare>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_decl>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")

            """    287 <table_decl>	=>	<decl_type>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_decl>_1"]:
            self.decl_type()

        else: self.parse_token(PREDICT_SET_M["<table_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_declare(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    288 <table_declare>	=>	id	<table_init>	<table_declare_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare>"]:
            self.parse_token("id")
            self.table_init()
            self.table_declare_tail()
        else: self.parse_token(PREDICT_SET_M["<table_declare>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    289 <table_init>	=>	=	<strict_table_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_init>"]:
            self.parse_token("=")
            self.strict_table_expr()

            """    290 <table_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<table_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_table_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    291 <strict_table_expr>	=>	[	<field_assignments>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>"]:
            self.parse_token("[")
            self.field_assignments()
            self.parse_token("]")

            """    292 <strict_table_expr>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>_1"]:
            self.id_()

        else: self.parse_token(PREDICT_SET_M["<strict_table_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_declare_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    293 <table_declare_tail>	=>	,	<table_declare>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>"]:
            self.parse_token(",")
            self.table_declare()

            """    294 <table_declare_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<table_declare_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def recipe_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    295 <recipe_decl>	=>	prepare	<serve_type>	(	<spice>	)	<platter>	<recipe_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>"]:
            self.parse_token("prepare")
            self.serve_type()
            self.parse_token("(")
            self.spice()
            self.parse_token(")")
            self.platter()
            self.recipe_decl()

            """    296 <recipe_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<recipe_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def serve_type(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    297 <serve_type>	=>	<decl_head>    """
        if self.tokens[self.pos].type in PREDICT_SET["<serve_type>"]:
            self.decl_head()
        else: self.parse_token(PREDICT_SET_M["<serve_type>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    298 <spice>	=>	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice>"]:
            self.decl_head()
            self.spice_tail()

            """    299 <spice>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<spice>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    300 <spice_tail>	=>	,	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice_tail>"]:
            self.parse_token(",")
            self.decl_head()
            self.spice_tail()

            """    301 <spice_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<spice_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    302 <platter>	=>	{	<local_decl>	<statements>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<platter>"]:
            self.parse_token("{")
            self.local_decl()
            self.statements()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    303 <local_decl>	=>	piece	<piece_decl>	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl()

            """    304 <local_decl>	=>	chars	<chars_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl()

            """    305 <local_decl>	=>	sip	<sip_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl()

            """    306 <local_decl>	=>	flag	<flag_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl()

            """    307 <local_decl>	=>	id	<local_id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_4"]:
            self.parse_token("id")
            self.local_id_tail()

            """    308 <local_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<local_decl>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    309 <local_id_tail>	=>	of	<table_declare>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl()

            """    310 <local_id_tail>	=>	[	<]_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_1"]:
            self.parse_token("[")
            self.__tail()

            """    311 <local_id_tail>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()

            """    312 <local_id_tail>	=>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()

            """    313 <local_id_tail>	=>	<tail1>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements()

        else: self.parse_token(PREDICT_SET_M["<local_id_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def __tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    314 <]_tail>	=>	]	<dimensions_tail>	of	<array_declare>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.array_declare()
            self.parse_token(";")
            self.local_decl()

            """    315 <]_tail>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements>    """
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

        """    316 <assignment_op>	=>	=    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_op>"]:
            self.parse_token("=")

            """    317 <assignment_op>	=>	+=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_1"]:
            self.parse_token("+=")

            """    318 <assignment_op>	=>	-=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_2"]:
            self.parse_token("-=")

            """    319 <assignment_op>	=>	*=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_3"]:
            self.parse_token("*=")

            """    320 <assignment_op>	=>	/=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_4"]:
            self.parse_token("/=")

            """    321 <assignment_op>	=>	%=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_5"]:
            self.parse_token("%=")

        else: self.parse_token(PREDICT_SET_M["<assignment_op>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    322 <statements>	=>	<id_statements>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements>"]:
            self.id_statements()
            self.statements()

            """    323 <statements>	=>	<built-in_rec_call>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements()

            """    324 <statements>	=>	<conditional_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_2"]:
            self.conditional_st()
            self.statements()

            """    325 <statements>	=>	<looping_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_3"]:
            self.looping_st()
            self.statements()

            """    326 <statements>	=>	<jump_serve>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_4"]:
            self.jump_serve()
            self.statements()

            """    327 <statements>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<statements>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    328 <id_statements>	=>	id	<id_statements_ext>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements()
        else: self.parse_token(PREDICT_SET_M["<id_statements>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_ext(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    329 <id_statements_ext>	=>	<tail1>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>"]:
            self.tail1()
            self.parse_token(";")

            """    330 <id_statements_ext>	=>	<assignment_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>_1"]:
            self.assignment_st()

        else: self.parse_token(PREDICT_SET_M["<id_statements_ext>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def tail1(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    331 <tail1>	=>	<call_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<tail1>"]:
            self.call_tail()
        else: self.parse_token(PREDICT_SET_M["<tail1>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    332 <call_tail>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tail>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")
        else: self.parse_token(PREDICT_SET_M["<call_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def assignment_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    333 <assignment_st>	=>	<accessor_tail>	<assignment_op>	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_st>"]:
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<assignment_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec_call(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    334 <built-in_rec_call>	=>	<built-in_rec>    """
        if self.tokens[self.pos].type in PREDICT_SET["<built-in_rec_call>"]:
            self.built_in_rec()
        else: self.parse_token(PREDICT_SET_M["<built-in_rec_call>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    335 <built-in_rec>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    336 <built-in_rec>	=>	bill	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_1"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

            """    337 <built-in_rec>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    338 <built-in_rec>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")

            """    339 <built-in_rec>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_4"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    340 <built-in_rec>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_5"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")

            """    341 <built-in_rec>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_6"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    342 <built-in_rec>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_7"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")

            """    343 <built-in_rec>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_8"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    344 <built-in_rec>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_9"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    345 <built-in_rec>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_10"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    346 <built-in_rec>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_11"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    347 <built-in_rec>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_12"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    348 <built-in_rec>	=>	sqrt	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_13"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    349 <built-in_rec>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_14"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")

            """    350 <built-in_rec>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_15"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    351 <built-in_rec>	=>	topiece	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_16"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    352 <built-in_rec>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built-in_rec>_17"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<built-in_rec>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    353 <conditional_st>	=>	<cond_check>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st>"]:
            self.cond_check()

            """    354 <conditional_st>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st>_1"]:
            self.cond_menu()

        else: self.parse_token(PREDICT_SET_M["<conditional_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    355 <cond_check>	=>	check	(	<strict_flag_expr>	)	<platter>	<alt_clause>	<instead_clause>    """
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

        """    356 <alt_clause>	=>	alt	(	<strict_flag_expr>	)	<platter>	<alt_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.platter()
            self.alt_clause()

            """    357 <alt_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<alt_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    358 <instead_clause>	=>	instead	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause>"]:
            self.parse_token("instead")
            self.platter()

            """    359 <instead_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<instead_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    360 <cond_menu>	=>	menu	(	<any_expr>	)	<menu_platter>    """
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

        """    361 <menu_platter>	=>	{	<choice_clause>	<usual_clause>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_platter>"]:
            self.parse_token("{")
            self.choice_clause()
            self.usual_clause()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    362 <choice_clause>	=>	choice	<choice_val>	:	<statements_menu>	<choice_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.statements_menu()
            self.choice_clause()

            """    363 <choice_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<choice_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    364 <choice_val>	=>	piece_lit    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_val>"]:
            self.parse_token("piece_lit")

            """    365 <choice_val>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_val>_1"]:
            self.parse_token("chars_lit")

        else: self.parse_token(PREDICT_SET_M["<choice_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    366 <statements_menu>	=>	<id_statements_menu>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_menu>"]:
            self.id_statements_menu()
            self.statements_menu()

            """    367 <statements_menu>	=>	<built-in_rec_call>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_menu()

            """    368 <statements_menu>	=>	<conditional_st_menu>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_2"]:
            self.conditional_st_menu()
            self.statements_menu()

            """    369 <statements_menu>	=>	<looping_st>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_3"]:
            self.looping_st()
            self.statements_menu()

            """    370 <statements_menu>	=>	<jump_stop>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_4"]:
            self.jump_stop()
            self.statements_menu()

            """    371 <statements_menu>	=>	<jump_serve>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_5"]:
            self.jump_serve()
            self.statements_menu()

            """    372 <statements_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_6"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<statements_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    373 <id_statements_menu>	=>	id	<id_statements_ext>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_menu>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_menu()
        else: self.parse_token(PREDICT_SET_M["<id_statements_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    374 <conditional_st_menu>	=>	<cond_check_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>"]:
            self.cond_check_menu()

            """    375 <conditional_st_menu>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>_1"]:
            self.cond_menu()

        else: self.parse_token(PREDICT_SET_M["<conditional_st_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    376 <cond_check_menu>	=>	check	(	<strict_flag_expr>	)	<menu_check_platter>	<alt_clause>	<instead_clause>    """
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

        """    377 <menu_check_platter>	=>	{	<local_decl_menu>	<statements_menu>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_check_platter>"]:
            self.parse_token("{")
            self.local_decl_menu()
            self.statements_menu()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_check_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    378 <local_decl_menu>	=>	piece	<piece_decl>	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_menu()

            """    379 <local_decl_menu>	=>	chars	<chars_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_menu()

            """    380 <local_decl_menu>	=>	sip	<sip_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_menu()

            """    381 <local_decl_menu>	=>	flag	<flag_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_menu()

            """    382 <local_decl_menu>	=>	id	<local_id_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_4"]:
            self.parse_token("id")
            self.local_id_tail_menu()

            """    383 <local_decl_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<local_decl_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    384 <local_id_tail_menu>	=>	of	<table_declare>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_menu()

            """    385 <local_id_tail_menu>	=>	[	<]_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_1"]:
            self.parse_token("[")
            self.__tail_menu()

            """    386 <local_id_tail_menu>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()

            """    387 <local_id_tail_menu>	=>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()

            """    388 <local_id_tail_menu>	=>	<tail1>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_menu()

        else: self.parse_token(PREDICT_SET_M["<local_id_tail_menu>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def __tail_menu(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    389 <]_tail_menu>	=>	]	<dimensions_tail>	of	<table_declare>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail_menu>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_menu()

            """    390 <]_tail_menu>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements_menu>    """
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

        """    391 <looping_st>	=>	<loop_pass>    """
        if self.tokens[self.pos].type in PREDICT_SET["<looping_st>"]:
            self.loop_pass()

            """    392 <looping_st>	=>	<loop_repeat>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_1"]:
            self.loop_repeat()

            """    393 <looping_st>	=>	<loop_order>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_2"]:
            self.loop_order()

        else: self.parse_token(PREDICT_SET_M["<looping_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_pass(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    394 <loop_pass>	=>	pass	(	<initialization>	<update>	<strict_flag_expr>	)	<loop_platter>    """
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

        """    395 <initialization>	=>	id	<loop_init>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<initialization>"]:
            self.parse_token("id")
            self.loop_init()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<initialization>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_init(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    396 <loop_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """    397 <loop_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<loop_init>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<loop_init>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def update(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    398 <update>	=>	id	<accessor_tail>	<assignment_op>	<strict_piece_expr>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<update>"]:
            self.parse_token("id")
            self.accessor_tail()
            self.assignment_op()
            self.strict_piece_expr()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<update>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_platter(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    399 <loop_platter>	=>	{	<local_decl_loop>	<statements_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_platter>"]:
            self.parse_token("{")
            self.local_decl_loop()
            self.statements_loop()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<loop_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    400 <local_decl_loop>	=>	piece	<piece_decl>	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_loop()

            """    401 <local_decl_loop>	=>	chars	<chars_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_loop()

            """    402 <local_decl_loop>	=>	sip	<sip_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_loop()

            """    403 <local_decl_loop>	=>	flag	<flag_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_loop()

            """    404 <local_decl_loop>	=>	id	<local_id_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_4"]:
            self.parse_token("id")
            self.local_id_tail_loop()

            """    405 <local_decl_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<local_decl_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    406 <local_id_tail_loop>	=>	of	<table_declare>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_loop()

            """    407 <local_id_tail_loop>	=>	[	<]_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_1"]:
            self.parse_token("[")
            self.__tail_loop()

            """    408 <local_id_tail_loop>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()

            """    409 <local_id_tail_loop>	=>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()

            """    410 <local_id_tail_loop>	=>	<tail1>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_loop()

        else: self.parse_token(PREDICT_SET_M["<local_id_tail_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def __tail_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    411 <]_tail_loop>	=>	]	<dimensions_tail>	of	<table_declare>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<]_tail_loop>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_loop()

            """    412 <]_tail_loop>	=>	<strict_piece_expr>	]	<accessor_tail>	<assignment_op>	<value>	;	<statements_loop>    """
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

        """    413 <statements_loop>	=>	<id_statements_loop>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_loop>"]:
            self.id_statements_loop()
            self.statements_loop()

            """    414 <statements_loop>	=>	<built-in_rec_call>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_loop()

            """    415 <statements_loop>	=>	<conditional_st_loop>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_2"]:
            self.conditional_st_loop()
            self.statements_loop()

            """    416 <statements_loop>	=>	<looping_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_3"]:
            self.looping_st()
            self.statements_loop()

            """    417 <statements_loop>	=>	<jump_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_4"]:
            self.jump_st()
            self.statements_loop()

            """    418 <statements_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<statements_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    419 <id_statements_loop>	=>	id	<id_statements_ext>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_loop>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_loop()
        else: self.parse_token(PREDICT_SET_M["<id_statements_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    420 <conditional_st_loop>	=>	<cond_check_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>"]:
            self.cond_check_loop()

            """    421 <conditional_st_loop>	=>	<cond_menu_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>_1"]:
            self.cond_menu_loop()

        else: self.parse_token(PREDICT_SET_M["<conditional_st_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    422 <cond_check_loop>	=>	check	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>	<instead_clause_loop>    """
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

        """    423 <alt_clause_loop>	=>	alt	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
            self.alt_clause_loop()

            """    424 <alt_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<alt_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    425 <instead_clause_loop>	=>	instead	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>"]:
            self.parse_token("instead")
            self.loop_platter()

            """    426 <instead_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<instead_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    427 <cond_menu_loop>	=>	menu	(	<any_expr>	)	<menu_loop_platter>    """
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

        """    428 <menu_loop_platter>	=>	{	<choice_clause_loop>	<usual_clause_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_loop_platter>"]:
            self.parse_token("{")
            self.choice_clause_loop()
            self.usual_clause_loop()
            self.parse_token("}")
        else: self.parse_token(PREDICT_SET_M["<menu_loop_platter>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    429 <choice_clause_loop>	=>	choice	<choice_val>	:	<statements_loop>	<choice_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.statements_loop()
            self.choice_clause_loop()

            """    430 <choice_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<choice_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def usual_clause_loop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    431 <usual_clause_loop>	=>	usual	:	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.statements_loop()

            """    432 <usual_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<usual_clause_loop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_st(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    433 <jump_st>	=>	<jump_next>    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_st>"]:
            self.jump_next()

            """    434 <jump_st>	=>	<jump_stop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_1"]:
            self.jump_stop()

            """    435 <jump_st>	=>	<jump_serve>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_2"]:
            self.jump_serve()

        else: self.parse_token(PREDICT_SET_M["<jump_st>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_next(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    436 <jump_next>	=>	next	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_next>"]:
            self.parse_token("next")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_next>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_stop(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    437 <jump_stop>	=>	stop	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_stop>"]:
            self.parse_token("stop")
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_stop>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_serve(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    438 <jump_serve>	=>	serve	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_serve>"]:
            self.parse_token("serve")
            self.value()
            self.parse_token(";")
        else: self.parse_token(PREDICT_SET_M["<jump_serve>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_repeat(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    439 <loop_repeat>	=>	repeat	(	<strict_flag_expr>	)	<loop_platter>    """
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

        """    440 <loop_order>	=>	order	<loop_platter>	repeat	(	<strict_flag_expr>	)	;    """
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

        """    441 <usual_clause>	=>	usual	:	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.statements_menu()

            """    442 <usual_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<usual_clause>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_numeric_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    443 <univ_numeric_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_numeric_factor>"]:
            self.id_()

            """    444 <univ_numeric_factor>	=>	<ret_piece>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_numeric_factor>_1"]:
            self.ret_piece()

            """    445 <univ_numeric_factor>	=>	<ret_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_numeric_factor>_2"]:
            self.ret_sip()

            """    446 <univ_numeric_factor>	=>	(	<numeric_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_numeric_factor>_3"]:
            self.parse_token("(")
            self.numeric_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<univ_numeric_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def numeric_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    447 <numeric_expr>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_rel_gate>    """
        if self.tokens[self.pos].type in PREDICT_SET["<numeric_expr>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_rel_gate()

            """    448 <numeric_expr>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<numeric_expr>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_rel_gate()

            """    449 <numeric_expr>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_rel_gate>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<numeric_expr>_2"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_rel_gate()

            """    450 <numeric_expr>	=>	(	<numeric_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<numeric_expr>_3"]:
            self.parse_token("(")
            self.numeric_paren_dispatch()

        else: self.parse_token(PREDICT_SET_M["<numeric_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def numeric_paren_dispatch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    451 <numeric_paren_dispatch>	=>	<ret_piece>	<piece_mult_tail>	<piece_add_tail>	<piece_bridge>    """
        if self.tokens[self.pos].type in PREDICT_SET["<numeric_paren_dispatch>"]:
            self.ret_piece()
            self.piece_mult_tail()
            self.piece_add_tail()
            self.piece_bridge()

            """    452 <numeric_paren_dispatch>	=>	<ret_sip>	<sip_mult_tail>	<sip_add_tail>	<sip_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<numeric_paren_dispatch>_1"]:
            self.ret_sip()
            self.sip_mult_tail()
            self.sip_add_tail()
            self.sip_bridge()

            """    453 <numeric_paren_dispatch>	=>	<id>	<univ_mult_tail>	<univ_add_tail>	<univ_bridge>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<numeric_paren_dispatch>_2"]:
            self.id_()
            self.univ_mult_tail()
            self.univ_add_tail()
            self.univ_bridge()

        else: self.parse_token(PREDICT_SET_M["<numeric_paren_dispatch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    454 <strict_flag_expr>	=>	<strict_flag_term>	<strict_flag_or_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_expr>"]:
            self.strict_flag_term()
            self.strict_flag_or_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_or_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    455 <strict_flag_or_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    456 <strict_flag_or_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_flag_or_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    457 <strict_flag_term>	=>	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_term>"]:
            self.strict_flag_factor()
            self.strict_flag_and_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_flag_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_and_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    458 <strict_flag_and_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    459 <strict_flag_and_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<strict_flag_and_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    460 <strict_flag_factor>	=>	<id>	<lhs_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>"]:
            self.id_()
            self.lhs_ambig_tail()

            """    461 <strict_flag_factor>	=>	<ret_piece>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_1"]:
            self.ret_piece()
            self.lhs_piece_tail()

            """    462 <strict_flag_factor>	=>	<ret_sip>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_2"]:
            self.ret_sip()
            self.lhs_sip_tail()

            """    463 <strict_flag_factor>	=>	<ret_chars>	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_3"]:
            self.ret_chars()
            self.lhs_str_tail()

            """    464 <strict_flag_factor>	=>	<ret_flag>	<lhs_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_4"]:
            self.ret_flag()
            self.lhs_bool_tail()

            """    465 <strict_flag_factor>	=>	not	<strict_flag_factor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_5"]:
            self.parse_token("not")
            self.strict_flag_factor()

            """    466 <strict_flag_factor>	=>	(	<paren_dispatch_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_6"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()

        else: self.parse_token(PREDICT_SET_M["<strict_flag_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_piece_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    467 <lhs_piece_tail>	=>	+	<strict_piece_factor>	<lhs_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    468 <lhs_piece_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    469 <lhs_piece_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    470 <lhs_piece_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    471 <lhs_piece_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    472 <lhs_piece_tail>	=>	<rel_op>	<strict_piece_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_5"]:
            self.rel_op()
            self.strict_piece_rhs()

        else: self.parse_token(PREDICT_SET_M["<lhs_piece_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_sip_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    473 <lhs_sip_tail>	=>	+	<strict_sip_factor>	<lhs_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    474 <lhs_sip_tail>	=>	-	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    475 <lhs_sip_tail>	=>	*	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    476 <lhs_sip_tail>	=>	/	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    477 <lhs_sip_tail>	=>	%	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_4"]:
            self.parse_token("%")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    478 <lhs_sip_tail>	=>	<rel_op>	<strict_sip_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_5"]:
            self.rel_op()
            self.strict_sip_rhs()

        else: self.parse_token(PREDICT_SET_M["<lhs_sip_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_str_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    479 <lhs_str_tail>	=>	+	<strict_string_factor>	<lhs_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.lhs_str_tail()

            """    480 <lhs_str_tail>	=>	<rel_op>	<strict_string_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>_1"]:
            self.rel_op()
            self.strict_string_rhs()

        else: self.parse_token(PREDICT_SET_M["<lhs_str_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_ambig_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    481 <lhs_ambig_tail>	=>	+	<ambig_calc_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>"]:
            self.parse_token("+")
            self.ambig_calc_branch()

            """    482 <lhs_ambig_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    483 <lhs_ambig_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    484 <lhs_ambig_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    485 <lhs_ambig_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    486 <lhs_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()

            """    487 <lhs_ambig_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_6"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    488 <lhs_ambig_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_7"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    489 <lhs_ambig_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_8"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<lhs_ambig_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ambig_calc_branch(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    490 <ambig_calc_branch>	=>	<id>	<lhs_ambig_tail_no_lambda>    """
        if self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>"]:
            self.id_()
            self.lhs_ambig_tail_no_lambda()

            """    491 <ambig_calc_branch>	=>	<ret_piece>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_1"]:
            self.ret_piece()
            self.lhs_piece_tail()

            """    492 <ambig_calc_branch>	=>	<ret_sip>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_2"]:
            self.ret_sip()
            self.lhs_sip_tail()

            """    493 <ambig_calc_branch>	=>	<ret_chars>	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_3"]:
            self.ret_chars()
            self.lhs_str_tail()

            """    494 <ambig_calc_branch>	=>	(	<paren_dispatch_lhs_no_lambda>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs_no_lambda()

        else: self.parse_token(PREDICT_SET_M["<ambig_calc_branch>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_ambig_tail_no_lambda(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    495 <lhs_ambig_tail_no_lambda>	=>	+	<ambig_calc_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>"]:
            self.parse_token("+")
            self.ambig_calc_branch()

            """    496 <lhs_ambig_tail_no_lambda>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    497 <lhs_ambig_tail_no_lambda>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    498 <lhs_ambig_tail_no_lambda>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    499 <lhs_ambig_tail_no_lambda>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    500 <lhs_ambig_tail_no_lambda>	=>	<rel_op>	<strict_ambig_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()

        else: self.parse_token(PREDICT_SET_M["<lhs_ambig_tail_no_lambda>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    501 <strict_sip_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>"]:
            self.id_()

            """    502 <strict_sip_factor>	=>	<ret_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_1"]:
            self.ret_sip()

            """    503 <strict_sip_factor>	=>	(	<paren_dispatch_val_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_sip()

        else: self.parse_token(PREDICT_SET_M["<strict_sip_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_string_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    504 <strict_string_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>"]:
            self.id_()

            """    505 <strict_string_factor>	=>	<ret_chars>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_1"]:
            self.ret_chars()

            """    506 <strict_string_factor>	=>	(	<paren_dispatch_val_str>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_str()

        else: self.parse_token(PREDICT_SET_M["<strict_string_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_rhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    507 <strict_piece_rhs>	=>	<ret_piece>	<val_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_rhs>"]:
            self.ret_piece()
            self.val_piece_tail()

            """    508 <strict_piece_rhs>	=>	<id>	<val_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_rhs>_1"]:
            self.id_()
            self.val_ambig_tail()

            """    509 <strict_piece_rhs>	=>	(	<paren_dispatch_val_piece>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_rhs>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_piece()
            self.val_piece_tail()

        else: self.parse_token(PREDICT_SET_M["<strict_piece_rhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_rhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    510 <strict_sip_rhs>	=>	<ret_sip>	<val_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_rhs>"]:
            self.ret_sip()
            self.val_sip_tail()

            """    511 <strict_sip_rhs>	=>	<id>	<val_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_rhs>_1"]:
            self.id_()
            self.val_ambig_tail()

            """    512 <strict_sip_rhs>	=>	(	<paren_dispatch_val_sip>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_rhs>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_sip()
            self.val_sip_tail()

        else: self.parse_token(PREDICT_SET_M["<strict_sip_rhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_string_rhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    513 <strict_string_rhs>	=>	<ret_chars>	<val_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_string_rhs>"]:
            self.ret_chars()
            self.val_str_tail()

            """    514 <strict_string_rhs>	=>	<id>	<val_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_rhs>_1"]:
            self.id_()
            self.val_ambig_tail()

            """    515 <strict_string_rhs>	=>	(	<paren_dispatch_val_str>	<val_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_rhs>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_str()
            self.val_str_tail()

        else: self.parse_token(PREDICT_SET_M["<strict_string_rhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_ambig_rhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    516 <strict_ambig_rhs>	=>	<id>	<val_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>"]:
            self.id_()
            self.val_ambig_tail()

            """    517 <strict_ambig_rhs>	=>	<ret_piece>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_1"]:
            self.ret_piece()
            self.val_piece_tail()

            """    518 <strict_ambig_rhs>	=>	<ret_sip>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_2"]:
            self.ret_sip()
            self.val_sip_tail()

            """    519 <strict_ambig_rhs>	=>	<ret_chars>	<val_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_3"]:
            self.ret_chars()
            self.val_str_tail()

            """    520 <strict_ambig_rhs>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

        else: self.parse_token(PREDICT_SET_M["<strict_ambig_rhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    521 <paren_dispatch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    522 <paren_dispatch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    523 <paren_dispatch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    524 <paren_dispatch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    525 <paren_dispatch_lhs>	=>	<ret_flag>	<lhs_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_4"]:
            self.ret_flag()
            self.lhs_bool_tail()
            self.parse_token(")")

            """    526 <paren_dispatch_lhs>	=>	not	<strict_flag_factor>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_5"]:
            self.parse_token("not")
            self.strict_flag_factor()
            self.parse_token(")")

            """    527 <paren_dispatch_lhs>	=>	(	<paren_dispatch_lhs>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_6"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_piece_tail_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    528 <paren_piece_tail_lhs>	=>	+	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    529 <paren_piece_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    530 <paren_piece_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    531 <paren_piece_tail_lhs>	=>	)	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_3"]:
            self.parse_token(")")
            self.lhs_piece_tail()

            """    532 <paren_piece_tail_lhs>	=>	<rel_op>	<strict_piece_rhs>	<lhs_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_4"]:
            self.rel_op()
            self.strict_piece_rhs()
            self.lhs_bool_tail()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<paren_piece_tail_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_sip_tail_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    533 <paren_sip_tail_lhs>	=>	+	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    534 <paren_sip_tail_lhs>	=>	-	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    535 <paren_sip_tail_lhs>	=>	*	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    536 <paren_sip_tail_lhs>	=>	)	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_3"]:
            self.parse_token(")")
            self.lhs_sip_tail()

            """    537 <paren_sip_tail_lhs>	=>	<rel_op>	<strict_sip_rhs>	<lhs_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_4"]:
            self.rel_op()
            self.strict_sip_rhs()
            self.lhs_bool_tail()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<paren_sip_tail_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_tail_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    538 <paren_ambig_tail_lhs>	=>	+	<paren_ambig_branch_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>"]:
            self.parse_token("+")
            self.paren_ambig_branch_lhs()

            """    539 <paren_ambig_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    540 <paren_ambig_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    541 <paren_ambig_tail_lhs>	=>	)	<lhs_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_3"]:
            self.parse_token(")")
            self.lhs_ambig_tail()

            """    542 <paren_ambig_tail_lhs>	=>	<rel_op>	<strict_ambig_rhs>	<lhs_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_4"]:
            self.rel_op()
            self.strict_ambig_rhs()
            self.lhs_bool_tail()
            self.parse_token(")")

            """    543 <paren_ambig_tail_lhs>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_5"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()
            self.parse_token(")")

            """    544 <paren_ambig_tail_lhs>	=>	or	<strict_flag_term>	<strict_flag_or_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_6"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<paren_ambig_tail_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_branch_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    545 <paren_ambig_branch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    546 <paren_ambig_branch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    547 <paren_ambig_branch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    548 <paren_ambig_branch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    549 <paren_ambig_branch_lhs>	=>	(	<paren_dispatch_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()

        else: self.parse_token(PREDICT_SET_M["<paren_ambig_branch_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_str_tail_lhs(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    550 <paren_str_tail_lhs>	=>	+	<strict_string_factor>	<paren_str_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.paren_str_tail_lhs()

            """    551 <paren_str_tail_lhs>	=>	)	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_1"]:
            self.parse_token(")")
            self.lhs_str_tail()

            """    552 <paren_str_tail_lhs>	=>	<rel_op>	<strict_string_rhs>	<lhs_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_2"]:
            self.rel_op()
            self.strict_string_rhs()
            self.lhs_bool_tail()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<paren_str_tail_lhs>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    553 <paren_dispatch_val>	=>	<id>	<paren_ambig_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>"]:
            self.id_()
            self.paren_ambig_tail_val()

            """    554 <paren_dispatch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_1"]:
            self.ret_piece()
            self.paren_piece_tail_val()

            """    555 <paren_dispatch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_2"]:
            self.ret_sip()
            self.paren_sip_tail_val()

            """    556 <paren_dispatch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_3"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    557 <paren_dispatch_val>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_piece_tail_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    558 <paren_piece_tail_val>	=>	+	<strict_piece_factor>	<paren_piece_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    559 <paren_piece_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    560 <paren_piece_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    561 <paren_piece_tail_val>	=>	)	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_3"]:
            self.parse_token(")")
            self.val_piece_tail()

        else: self.parse_token(PREDICT_SET_M["<paren_piece_tail_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_sip_tail_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    562 <paren_sip_tail_val>	=>	+	<strict_sip_factor>	<paren_sip_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    563 <paren_sip_tail_val>	=>	-	<strict_sip_factor>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    564 <paren_sip_tail_val>	=>	*	<strict_sip_factor>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    565 <paren_sip_tail_val>	=>	)	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_3"]:
            self.parse_token(")")
            self.val_sip_tail()

        else: self.parse_token(PREDICT_SET_M["<paren_sip_tail_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_str_tail_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    566 <paren_str_tail_val>	=>	+	<strict_string_factor>	<paren_str_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.paren_str_tail_val()

            """    567 <paren_str_tail_val>	=>	)	<val_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>_1"]:
            self.parse_token(")")
            self.val_str_tail()

        else: self.parse_token(PREDICT_SET_M["<paren_str_tail_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_tail_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    568 <paren_ambig_tail_val>	=>	+	<paren_ambig_branch_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>"]:
            self.parse_token("+")
            self.paren_ambig_branch_val()

            """    569 <paren_ambig_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    570 <paren_ambig_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    571 <paren_ambig_tail_val>	=>	)	<val_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_3"]:
            self.parse_token(")")
            self.val_ambig_tail()

        else: self.parse_token(PREDICT_SET_M["<paren_ambig_tail_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_branch_val(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    572 <paren_ambig_branch_val>	=>	<id>	<paren_ambig_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>"]:
            self.id_()
            self.paren_ambig_tail_val()

            """    573 <paren_ambig_branch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_1"]:
            self.ret_piece()
            self.paren_piece_tail_val()

            """    574 <paren_ambig_branch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_2"]:
            self.ret_sip()
            self.paren_sip_tail_val()

            """    575 <paren_ambig_branch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_3"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    576 <paren_ambig_branch_val>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

        else: self.parse_token(PREDICT_SET_M["<paren_ambig_branch_val>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_piece_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    577 <val_piece_tail>	=>	+	<strict_piece_factor>	<val_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    578 <val_piece_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    579 <val_piece_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    580 <val_piece_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    581 <val_piece_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    582 <val_piece_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<val_piece_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_sip_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    583 <val_sip_tail>	=>	+	<strict_sip_factor>	<val_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    584 <val_sip_tail>	=>	-	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    585 <val_sip_tail>	=>	*	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    586 <val_sip_tail>	=>	/	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    587 <val_sip_tail>	=>	%	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_4"]:
            self.parse_token("%")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    588 <val_sip_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<val_sip_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_str_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    589 <val_str_tail>	=>	+	<strict_string_factor>	<val_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_str_tail>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.val_str_tail()

            """    590 <val_str_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_str_tail>_1"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<val_str_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_ambig_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    591 <val_ambig_tail>	=>	+	<paren_ambig_branch_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>"]:
            self.parse_token("+")
            self.paren_ambig_branch_val()

            """    592 <val_ambig_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    593 <val_ambig_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    594 <val_ambig_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    595 <val_ambig_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    596 <val_ambig_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_5"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<val_ambig_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val_piece(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    597 <paren_dispatch_val_piece>	=>	<id>	<paren_piece_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>"]:
            self.id_()
            self.paren_piece_tail_val()

            """    598 <paren_dispatch_val_piece>	=>	<ret_piece>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>_1"]:
            self.ret_piece()
            self.paren_piece_tail_val()

            """    599 <paren_dispatch_val_piece>	=>	(	<paren_dispatch_val_piece>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_piece()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_val_piece>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val_sip(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    600 <paren_dispatch_val_sip>	=>	<id>	<paren_sip_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>"]:
            self.id_()
            self.paren_sip_tail_val()

            """    601 <paren_dispatch_val_sip>	=>	<ret_sip>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>_1"]:
            self.ret_sip()
            self.paren_sip_tail_val()

            """    602 <paren_dispatch_val_sip>	=>	(	<paren_dispatch_val_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_sip()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_val_sip>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val_str(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    603 <paren_dispatch_val_str>	=>	<id>	<paren_str_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>"]:
            self.id_()
            self.paren_str_tail_val()

            """    604 <paren_dispatch_val_str>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_1"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    605 <paren_dispatch_val_str>	=>	(	<paren_dispatch_val_str>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_str()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_val_str>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_lhs_no_lambda(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    606 <paren_dispatch_lhs_no_lambda>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    607 <paren_dispatch_lhs_no_lambda>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    608 <paren_dispatch_lhs_no_lambda>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    609 <paren_dispatch_lhs_no_lambda>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    610 <paren_dispatch_lhs_no_lambda>	=>	(	<paren_dispatch_lhs_no_lambda>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs_no_lambda()

        else: self.parse_token(PREDICT_SET_M["<paren_dispatch_lhs_no_lambda>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_bool_tail(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    611 <lhs_bool_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    612 <lhs_bool_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>_1"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    613 <lhs_bool_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>_2"]:
            pass

        else: self.parse_token(PREDICT_SET_M["<lhs_bool_tail>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def rel_op(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    614 <rel_op>	=>	==    """
        if self.tokens[self.pos].type in PREDICT_SET["<rel_op>"]:
            self.parse_token("==")

            """    615 <rel_op>	=>	!=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_1"]:
            self.parse_token("!=")

            """    616 <rel_op>	=>	>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_2"]:
            self.parse_token(">")

            """    617 <rel_op>	=>	<    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_3"]:
            self.parse_token("<")

            """    618 <rel_op>	=>	>=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_4"]:
            self.parse_token(">=")

            """    619 <rel_op>	=>	<=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_5"]:
            self.parse_token("<=")

        else: self.parse_token(PREDICT_SET_M["<rel_op>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_expr(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    620 <strict_piece_expr>	=>	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr>"]:
            self.strict_piece_term()
            self.strict_piece_add_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_expr>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_term(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    621 <strict_piece_term>	=>	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term>"]:
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
        else: self.parse_token(PREDICT_SET_M["<strict_piece_term>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_factor(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    622 <strict_piece_factor>	=>	<ret_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>"]:
            self.ret_piece()

            """    623 <strict_piece_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_1"]:
            self.id_()

            """    624 <strict_piece_factor>	=>	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_2"]:
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<strict_piece_factor>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_flag(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    625 <ret_flag>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_flag>"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")

            """    626 <ret_flag>	=>	toflag	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_1"]:
            self.parse_token("toflag")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    627 <ret_flag>	=>	flag_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_2"]:
            self.parse_token("flag_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_flag>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_chars(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    628 <ret_chars>	=>	bill	(	<strict_chars_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_chars>"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

            """    629 <ret_chars>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_1"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")

            """    630 <ret_chars>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    631 <ret_chars>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")

            """    632 <ret_chars>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_4"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    633 <ret_chars>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_5"]:
            self.parse_token("chars_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_chars>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_piece(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    634 <ret_piece>	=>	topiece	(	<any_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_piece>"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    635 <ret_piece>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_1"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    636 <ret_piece>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_2"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    637 <ret_piece>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_3"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    638 <ret_piece>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_4"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    639 <ret_piece>	=>	piece_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_5"]:
            self.parse_token("piece_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_piece>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_sip(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    640 <ret_sip>	=>	sqrt	(	<strict_piece_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_sip>"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    641 <ret_sip>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_1"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")

            """    642 <ret_sip>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_2"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    643 <ret_sip>	=>	sip_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_3"]:
            self.parse_token("sip_lit")

        else: self.parse_token(PREDICT_SET_M["<ret_sip>"])

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_array(self):
        log.info("Enter: " + self.tokens[self.pos].type) # J

        """    644 <ret_array>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_array>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    645 <ret_array>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_1"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    646 <ret_array>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_2"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    647 <ret_array>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_3"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

        else: self.parse_token(PREDICT_SET_M["<ret_array>"])

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
