from app.lexer.lexer import Lexer
from app.lexer.token import Token
from app.parser.error_handler import ErrorHandler
from app.parser.predict_set import PREDICT_SET
from app.parser.first_set import FIRST_SET
from app.utils.FileHandler import run_file
import logging as log

# To disable logs, set level=log.CRITICAL. 
# To enable logs, set level=log.DEBUG
log.basicConfig(level=log.DEBUG, format='%(levelname)s: <%(funcName)s> | %(message)s') # J

class Parser():
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")] # filter out ws and comments
        self.error_arr = [] # err
        if not self.tokens: 
            raise ErrorHandler("EOF", None, PREDICT_SET["<program>"])
        
        # Add EOF token at the end to prevent index out of range errors
        last_token = self.tokens[-1]
        self.tokens.append(Token("EOF", "EOF", last_token.line, last_token.col))
        
        self.pos = 0
    
    def parse_token(self, tok):
        """Parse and consume a specific token type"""
        if self.pos >= len(self.tokens):
            raise ErrorHandler("EOF", None, tok)    
        
        if self.tokens[self.pos].type == tok: 
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: MATCH!") # J
            
            self.pos += 1
            self.error_arr.clear() # err
            
        else:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: INVALID!\n") # J
            
            if tok != self.error_arr:
                if isinstance(tok, list):
                    self.error_arr.extend([t for t in tok if t not in self.error_arr])
                else:
                    if tok not in self.error_arr: # check membership
                        self.error_arr.append(tok)
            
            log.info("STACK: " + str(self.error_arr) + "\n") # J
            
            # Remove duplicates while preserving order 
            self.error_arr = list(dict.fromkeys(self.error_arr))
            raise ErrorHandler("Unexpected_err", self.tokens[self.pos], self.error_arr) # filtered_tok if filtered_tok else tok

    def appendF(self, first_set):
        first_set = [t for t in first_set if not (t=="λ")]
        self.error_arr.extend(first_set)

    def parse_program(self):
        self.appendF(FIRST_SET["<program>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    1 <program>	=>	<global_decl>	<recipe_decl>	start	(	)	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<program>"]:
            self.global_decl()
            self.recipe_decl()
            self.parse_token("start")
            self.parse_token("(")
            self.parse_token(")")
            self.platter()
        else: self.parse_token(self.error_arr)
        
        # Ensure we've consumed all tokens (should be at EOF token now)
        if self.pos < len(self.tokens) and self.tokens[self.pos].type != "EOF":
            raise ErrorHandler("ExpectedEOF_err", self.tokens[self.pos], None)

        log.info("Exit: " + self.tokens[self.pos].type) # J













    def global_decl(self):
        self.appendF(FIRST_SET["<global_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

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


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_decl(self):
        self.appendF(FIRST_SET["<piece_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    9 <piece_decl>	=>	of	<piece_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_decl>"]:
            self.parse_token("of")
            self.piece_id()
            self.parse_token(";")

            """    10 <piece_decl>	=>	<piece_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_decl>_1"]:
            self.piece_array_decl()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id(self):
        self.appendF(FIRST_SET["<piece_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    11 <piece_id>	=>	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id>"]:
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_ingredient_init(self):
        self.appendF(FIRST_SET["<piece_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    12 <piece_ingredient_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """    13 <piece_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_expr(self):
        self.appendF(FIRST_SET["<strict_piece_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    14 <strict_piece_expr>	=>	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr>"]:
            self.strict_piece_term()
            self.strict_piece_add_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_term(self):
        self.appendF(FIRST_SET["<strict_piece_term>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    15 <strict_piece_term>	=>	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term>"]:
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_factor(self):
        self.appendF(FIRST_SET["<strict_piece_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    16 <strict_piece_factor>	=>	<ret_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>"]:
            self.ret_piece()

            """    17 <strict_piece_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_1"]:
            self.id_()

            """    18 <strict_piece_factor>	=>	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_2"]:
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_piece(self):
        self.appendF(FIRST_SET["<ret_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    19 <ret_piece>	=>	topiece	(	<any_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_piece>"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    20 <ret_piece>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_1"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    21 <ret_piece>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_2"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    22 <ret_piece>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_3"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    23 <ret_piece>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_4"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    24 <ret_piece>	=>	piece_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_5"]:
            self.parse_token("piece_lit")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def any_expr(self):
        self.appendF(FIRST_SET["<any_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    25 <any_expr>	=>	<id>	<univ_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_expr>"]:
            self.id_()
            self.univ_ambig_tail()

            """    26 <any_expr>	=>	<ret_piece>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_1"]:
            self.ret_piece()
            self.univ_piece_tail()

            """    27 <any_expr>	=>	<ret_sip>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_2"]:
            self.ret_sip()
            self.univ_sip_tail()

            """    28 <any_expr>	=>	<ret_chars>	<univ_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_3"]:
            self.ret_chars()
            self.univ_str_tail()

            """    29 <any_expr>	=>	<ret_flag>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_4"]:
            self.ret_flag()
            self.univ_bool_tail()

            """    30 <any_expr>	=>	(	<univ_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_5"]:
            self.parse_token("(")
            self.univ_paren_dispatch()

            """    31 <any_expr>	=>	not	<strict_flag_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_6"]:
            self.parse_token("not")
            self.strict_flag_expr()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_(self):
        self.appendF(FIRST_SET["<id_>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    32 <id>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["id_"]:
            self.parse_token("id")
            self.id_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_tail(self):
        self.appendF(FIRST_SET["<id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    33 <id_tail>	=>	<call_tailopt>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_tail>"]:
            self.call_tailopt()

            """    34 <id_tail>	=>	<accessor_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_tail>_1"]:
            self.accessor_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tailopt(self):
        self.appendF(FIRST_SET["<call_tailopt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    35 <call_tailopt>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")

            """    36 <call_tailopt>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor(self):
        self.appendF(FIRST_SET["<flavor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    37 <flavor>	=>	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor>"]:
            self.value()
            self.flavor_tail()

            """    38 <flavor>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def value(self):
        self.appendF(FIRST_SET["<value>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    39 <value>	=>	<any_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<value>"]:
            self.any_expr()

            """    40 <value>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_1"]:
            self.ret_array()

            """    41 <value>	=>	[	<notation_val>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_2"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_array(self):
        self.appendF(FIRST_SET["<ret_array>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    42 <ret_array>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_array>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    43 <ret_array>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_1"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    44 <ret_array>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_2"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    45 <ret_array>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_3"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_array_expr(self):
        self.appendF(FIRST_SET["<strict_array_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    46 <strict_array_expr>	=>	[	<array_element_id>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>"]:
            self.parse_token("[")
            self.array_element_id()
            self.parse_token("]")

            """    47 <strict_array_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_1"]:
            self.parse_token("id")
            self.id_tail()

            """    48 <strict_array_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_2"]:
            self.ret_array()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_id(self):
        self.appendF(FIRST_SET["<array_element_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    49 <array_element_id>	=>	id	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_id>"]:
            self.parse_token("id")
            self.element_value_tail()

            """    50 <array_element_id>	=>	<array_element>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_1"]:
            self.array_element()

            """    51 <array_element_id>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_2"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_value_tail(self):
        self.appendF(FIRST_SET["<element_value_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    52 <element_value_tail>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>"]:
            self.parse_token(",")
            self.array_element_id()

            """    53 <element_value_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element(self):
        self.appendF(FIRST_SET["<array_element>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    54 <array_element>	=>	piece_lit	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element>"]:
            self.parse_token("piece_lit")
            self.element_value_tail()

            """    55 <array_element>	=>	sip_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_1"]:
            self.parse_token("sip_lit")
            self.element_value_tail()

            """    56 <array_element>	=>	flag_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_2"]:
            self.parse_token("flag_lit")
            self.element_value_tail()

            """    57 <array_element>	=>	chars_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_3"]:
            self.parse_token("chars_lit")
            self.element_value_tail()

            """    58 <array_element>	=>	[	<notation_val>	]	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_4"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")
            self.element_value_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def notation_val(self):
        self.appendF(FIRST_SET["<notation_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    59 <notation_val>	=>	<array_element>    """
        if self.tokens[self.pos].type in PREDICT_SET["<notation_val>"]:
            self.array_element()

            """    60 <notation_val>	=>	id	<array_or_table>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_1"]:
            self.parse_token("id")
            self.array_or_table()

            """    61 <notation_val>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_2"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_or_table(self):
        self.appendF(FIRST_SET["<array_or_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    62 <array_or_table>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_or_table>"]:
            self.parse_token(",")
            self.array_element_id()

            """    63 <array_or_table>	=>	=	<value>	;	<field_assignments>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_1"]:
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()

            """    64 <array_or_table>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_2"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def field_assignments(self):
        self.appendF(FIRST_SET["<field_assignments>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    65 <field_assignments>	=>	id	=	<value>	;	<field_assignments>    """
        if self.tokens[self.pos].type in PREDICT_SET["<field_assignments>"]:
            self.parse_token("id")
            self.parse_token("=")
            self.value()
            self.parse_token(";")
            self.field_assignments()

            """    66 <field_assignments>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<field_assignments>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flavor_tail(self):
        self.appendF(FIRST_SET["<flavor_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    67 <flavor_tail>	=>	,	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>"]:
            self.parse_token(",")
            self.value()
            self.flavor_tail()

            """    68 <flavor_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def accessor_tail(self):
        self.appendF(FIRST_SET["<accessor_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    69 <accessor_tail>	=>	<array_accessor>    """
        if self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>"]:
            self.array_accessor()

            """    70 <accessor_tail>	=>	<table_accessor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_1"]:
            self.table_accessor()

            """    71 <accessor_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_accessor(self):
        self.appendF(FIRST_SET["<array_accessor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    72 <array_accessor>	=>	[	<array_accessor_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor>"]:
            self.parse_token("[")
            self.array_accessor_val()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_accessor_val(self):
        self.appendF(FIRST_SET["<array_accessor_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    73 <array_accessor_val>	=>	piece_lit	]	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor_val>"]:
            self.parse_token("piece_lit")
            self.parse_token("]")
            self.accessor_tail()

            """    74 <array_accessor_val>	=>	id	]	<accessor_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_accessor_val>_1"]:
            self.parse_token("id")
            self.parse_token("]")
            self.accessor_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_accessor(self):
        self.appendF(FIRST_SET["<table_accessor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    75 <table_accessor>	=>	:	id	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_accessor>"]:
            self.parse_token(":")
            self.parse_token("id")
            self.accessor_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_ambig_tail(self):
        self.appendF(FIRST_SET["<univ_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    76 <univ_ambig_tail>	=>	+	<univ_ambig_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>"]:
            self.parse_token("+")
            self.univ_ambig_branch()

            """    77 <univ_ambig_tail>	=>	-	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_1"]:
            self.parse_token("-")
            self.univ_ambig_numeric_branch()

            """    78 <univ_ambig_tail>	=>	*	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_2"]:
            self.parse_token("*")
            self.univ_ambig_numeric_branch()

            """    79 <univ_ambig_tail>	=>	/	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_3"]:
            self.parse_token("/")
            self.univ_ambig_numeric_branch()

            """    80 <univ_ambig_tail>	=>	%	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_4"]:
            self.parse_token("%")
            self.univ_ambig_numeric_branch()

            """    81 <univ_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()
            self.univ_bool_tail()

            """    82 <univ_ambig_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_6"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    83 <univ_ambig_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_7"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    84 <univ_ambig_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_ambig_branch(self):
        self.appendF(FIRST_SET["<univ_ambig_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    85 <univ_ambig_branch>	=>	<id>	<univ_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>"]:
            self.id_()
            self.univ_ambig_tail()

            """    86 <univ_ambig_branch>	=>	<ret_piece>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_1"]:
            self.ret_piece()
            self.univ_piece_tail()

            """    87 <univ_ambig_branch>	=>	<ret_sip>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_2"]:
            self.ret_sip()
            self.univ_sip_tail()

            """    88 <univ_ambig_branch>	=>	<ret_chars>	<univ_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_3"]:
            self.ret_chars()
            self.univ_str_tail()

            """    89 <univ_ambig_branch>	=>	(	<univ_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_4"]:
            self.parse_token("(")
            self.univ_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_piece_tail(self):
        self.appendF(FIRST_SET["<univ_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    90 <univ_piece_tail>	=>	+	<strict_piece_expr>	<univ_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_expr()
            self.univ_piece_tail()

            """    91 <univ_piece_tail>	=>	-	<strict_piece_expr>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_expr()
            self.univ_piece_tail()

            """    92 <univ_piece_tail>	=>	*	<strict_piece_expr>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_expr()
            self.univ_piece_tail()

            """    93 <univ_piece_tail>	=>	/	<strict_piece_expr>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_expr()
            self.univ_piece_tail()

            """    94 <univ_piece_tail>	=>	%	<strict_piece_expr>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_expr()
            self.univ_piece_tail()

            """    95 <univ_piece_tail>	=>	<rel_op>	<strict_piece_expr>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_5"]:
            self.rel_op()
            self.strict_piece_expr()
            self.univ_bool_tail()

            """    96 <univ_piece_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def rel_op(self):
        self.appendF(FIRST_SET["<rel_op>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    97 <rel_op>	=>	==    """
        if self.tokens[self.pos].type in PREDICT_SET["<rel_op>"]:
            self.parse_token("==")

            """    98 <rel_op>	=>	!=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_1"]:
            self.parse_token("!=")

            """    99 <rel_op>	=>	>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_2"]:
            self.parse_token(">")

            """    100 <rel_op>	=>	<    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_3"]:
            self.parse_token("<")

            """    101 <rel_op>	=>	>=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_4"]:
            self.parse_token(">=")

            """    102 <rel_op>	=>	<=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_5"]:
            self.parse_token("<=")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_bool_tail(self):
        self.appendF(FIRST_SET["<univ_bool_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    103 <univ_bool_tail>	=>	and	<strict_flag_expr>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_bool_tail>"]:
            self.parse_token("and")
            self.strict_flag_expr()
            self.strict_flag_and_tail()

            """    104 <univ_bool_tail>	=>	or	<strict_flag_expr>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_bool_tail>_1"]:
            self.parse_token("or")
            self.strict_flag_expr()
            self.strict_flag_or_tail()

            """    105 <univ_bool_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_expr(self):
        self.appendF(FIRST_SET["<strict_flag_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    106 <strict_flag_expr>	=>	<strict_flag_term>	<strict_flag_or_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_expr>"]:
            self.strict_flag_term()
            self.strict_flag_or_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_term(self):
        self.appendF(FIRST_SET["<strict_flag_term>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    107 <strict_flag_term>	=>	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_term>"]:
            self.strict_flag_factor()
            self.strict_flag_and_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_factor(self):
        self.appendF(FIRST_SET["<strict_flag_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    108 <strict_flag_factor>	=>	<id>	<lhs_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>"]:
            self.id_()
            self.lhs_ambig_tail()

            """    109 <strict_flag_factor>	=>	<ret_piece>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_1"]:
            self.ret_piece()
            self.lhs_piece_tail()

            """    110 <strict_flag_factor>	=>	<ret_sip>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_2"]:
            self.ret_sip()
            self.lhs_sip_tail()

            """    111 <strict_flag_factor>	=>	<ret_chars>	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_3"]:
            self.ret_chars()
            self.lhs_str_tail()

            """    112 <strict_flag_factor>	=>	<ret_flag>	<lhs_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_4"]:
            self.ret_flag()
            self.lhs_bool_tail()

            """    113 <strict_flag_factor>	=>	not	<strict_flag_factor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_5"]:
            self.parse_token("not")
            self.strict_flag_factor()

            """    114 <strict_flag_factor>	=>	(	<paren_dispatch_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_6"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_ambig_tail(self):
        self.appendF(FIRST_SET["<lhs_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    115 <lhs_ambig_tail>	=>	+	<ambig_calc_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>"]:
            self.parse_token("+")
            self.ambig_calc_branch()

            """    116 <lhs_ambig_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    117 <lhs_ambig_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    118 <lhs_ambig_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    119 <lhs_ambig_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    120 <lhs_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()

            """    121 <lhs_ambig_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_6"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    122 <lhs_ambig_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_7"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    123 <lhs_ambig_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ambig_calc_branch(self):
        self.appendF(FIRST_SET["<ambig_calc_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    124 <ambig_calc_branch>	=>	<id>	<lhs_ambig_tail_no_lambda>    """
        if self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>"]:
            self.id_()
            self.lhs_ambig_tail_no_lambda()

            """    125 <ambig_calc_branch>	=>	<ret_piece>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_1"]:
            self.ret_piece()
            self.lhs_piece_tail()

            """    126 <ambig_calc_branch>	=>	<ret_sip>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_2"]:
            self.ret_sip()
            self.lhs_sip_tail()

            """    127 <ambig_calc_branch>	=>	<ret_chars>	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_3"]:
            self.ret_chars()
            self.lhs_str_tail()

            """    128 <ambig_calc_branch>	=>	(	<paren_dispatch_lhs_no_lambda>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs_no_lambda()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_ambig_tail_no_lambda(self):
        self.appendF(FIRST_SET["<lhs_ambig_tail_no_lambda>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    129 <lhs_ambig_tail_no_lambda>	=>	+	<ambig_calc_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>"]:
            self.parse_token("+")
            self.ambig_calc_branch()

            """    130 <lhs_ambig_tail_no_lambda>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    131 <lhs_ambig_tail_no_lambda>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    132 <lhs_ambig_tail_no_lambda>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    133 <lhs_ambig_tail_no_lambda>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    134 <lhs_ambig_tail_no_lambda>	=>	<rel_op>	<strict_ambig_rhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_piece_tail(self):
        self.appendF(FIRST_SET["<lhs_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    135 <lhs_piece_tail>	=>	+	<strict_piece_factor>	<lhs_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    136 <lhs_piece_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    137 <lhs_piece_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    138 <lhs_piece_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    139 <lhs_piece_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.lhs_piece_tail()

            """    140 <lhs_piece_tail>	=>	<rel_op>	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_5"]:
            self.rel_op()
            self.strict_piece_expr()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_ambig_rhs(self):
        self.appendF(FIRST_SET["<strict_ambig_rhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    141 <strict_ambig_rhs>	=>	<id>	<val_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>"]:
            self.id_()
            self.val_ambig_tail()

            """    142 <strict_ambig_rhs>	=>	<ret_piece>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_1"]:
            self.ret_piece()
            self.val_piece_tail()

            """    143 <strict_ambig_rhs>	=>	<ret_sip>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_2"]:
            self.ret_sip()
            self.val_sip_tail()

            """    144 <strict_ambig_rhs>	=>	<ret_chars>	<val_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_3"]:
            self.ret_chars()
            self.val_str_tail()

            """    145 <strict_ambig_rhs>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

            """     <strict_ambig_rhs>	=>	<ret_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_5"]:
            self.ret_flag()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_ambig_tail(self):
        self.appendF(FIRST_SET["<val_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    147 <val_ambig_tail>	=>	+	<paren_ambig_branch_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>"]:
            self.parse_token("+")
            self.paren_ambig_branch_val()

            """    148 <val_ambig_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    149 <val_ambig_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    150 <val_ambig_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    151 <val_ambig_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    152 <val_ambig_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_branch_val(self):
        self.appendF(FIRST_SET["<paren_ambig_branch_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    153 <paren_ambig_branch_val>	=>	<id>	<paren_ambig_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>"]:
            self.id_()
            self.paren_ambig_tail_val()

            """    154 <paren_ambig_branch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_1"]:
            self.ret_piece()
            self.paren_piece_tail_val()

            """    155 <paren_ambig_branch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_2"]:
            self.ret_sip()
            self.paren_sip_tail_val()

            """    156 <paren_ambig_branch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_3"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    157 <paren_ambig_branch_val>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_tail_val(self):
        self.appendF(FIRST_SET["<paren_ambig_tail_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    158 <paren_ambig_tail_val>	=>	+	<paren_ambig_branch_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>"]:
            self.parse_token("+")
            self.paren_ambig_branch_val()

            """    159 <paren_ambig_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    160 <paren_ambig_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    161 <paren_ambig_tail_val>	=>	/	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    162 <paren_ambig_tail_val>	=>	%	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    163 <paren_ambig_tail_val>	=>	)	<val_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_5"]:
            self.parse_token(")")
            self.val_ambig_tail()

            """    164 <paren_ambig_tail_val>	=>	<lhs_flag_comp_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_6"]:
            self.lhs_flag_comp_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_piece_tail_val(self):
        self.appendF(FIRST_SET["<paren_piece_tail_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    165 <paren_piece_tail_val>	=>	+	<strict_piece_factor>	<paren_piece_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    166 <paren_piece_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    167 <paren_piece_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    168 <paren_piece_tail_val>	=>	/	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    169 <paren_piece_tail_val>	=>	%	<strict_piece_factor>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.paren_piece_tail_val()

            """    170 <paren_piece_tail_val>	=>	)	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_5"]:
            self.parse_token(")")
            self.val_piece_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_piece_tail(self):
        self.appendF(FIRST_SET["<val_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    171 <val_piece_tail>	=>	+	<strict_piece_factor>	<val_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    172 <val_piece_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    173 <val_piece_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    174 <val_piece_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    175 <val_piece_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.val_piece_tail()

            """    176 <val_piece_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_flag_comp_tail(self):
        self.appendF(FIRST_SET["<lhs_flag_comp_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    177 <lhs_flag_comp_tail>	=>	<rel_op>	<strict_flag_factor>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_flag_comp_tail>"]:
            self.rel_op()
            self.strict_flag_factor()

            """    178 <lhs_flag_comp_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_sip(self):
        self.appendF(FIRST_SET["<ret_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    179 <ret_sip>	=>	sqrt	(	<strict_piece_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_sip>"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    180 <ret_sip>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_1"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")

            """    181 <ret_sip>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_2"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    182 <ret_sip>	=>	sip_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_3"]:
            self.parse_token("sip_lit")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_sip_tail_val(self):
        self.appendF(FIRST_SET["<paren_sip_tail_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    183 <paren_sip_tail_val>	=>	+	<strict_sip_factor>	<paren_sip_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    184 <paren_sip_tail_val>	=>	-	<strict_sip_factor>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    185 <paren_sip_tail_val>	=>	*	<strict_sip_factor>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    186 <paren_sip_tail_val>	=>	/	<strict_sip_factor>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.paren_sip_tail_val()

            """    187 <paren_sip_tail_val>	=>	)	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_4"]:
            self.parse_token(")")
            self.val_sip_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_factor(self):
        self.appendF(FIRST_SET["<strict_sip_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    188 <strict_sip_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>"]:
            self.id_()

            """    189 <strict_sip_factor>	=>	<ret_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_1"]:
            self.ret_sip()

            """    190 <strict_sip_factor>	=>	(	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_2"]:
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_expr(self):
        self.appendF(FIRST_SET["<strict_sip_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    191 <strict_sip_expr>	=>	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_expr>"]:
            self.strict_sip_term()
            self.strict_sip_add_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_term(self):
        self.appendF(FIRST_SET["<strict_sip_term>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    192 <strict_sip_term>	=>	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_term>"]:
            self.strict_sip_factor()
            self.strict_sip_mult_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_mult_tail(self):
        self.appendF(FIRST_SET["<strict_sip_mult_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    193 <strict_sip_mult_tail>	=>	*	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()

            """    194 <strict_sip_mult_tail>	=>	/	<strict_sip_factor>	<strict_sip_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.strict_sip_mult_tail()

            """    195 <strict_sip_mult_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_sip_add_tail(self):
        self.appendF(FIRST_SET["<strict_sip_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    196 <strict_sip_add_tail>	=>	+	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>"]:
            self.parse_token("+")
            self.strict_sip_term()
            self.strict_sip_add_tail()

            """    197 <strict_sip_add_tail>	=>	-	<strict_sip_term>	<strict_sip_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_term()
            self.strict_sip_add_tail()

            """    198 <strict_sip_add_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_sip_tail(self):
        self.appendF(FIRST_SET["<val_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    199 <val_sip_tail>	=>	+	<strict_sip_factor>	<val_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    200 <val_sip_tail>	=>	-	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    201 <val_sip_tail>	=>	*	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    202 <val_sip_tail>	=>	/	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    203 <val_sip_tail>	=>	%	<strict_sip_factor>	<val_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_4"]:
            self.parse_token("%")
            self.strict_sip_factor()
            self.val_sip_tail()

            """    204 <val_sip_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_chars(self):
        self.appendF(FIRST_SET["<ret_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    205 <ret_chars>	=>	bill	(	<strict_chars_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_chars>"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

            """    206 <ret_chars>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_1"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")

            """    207 <ret_chars>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    208 <ret_chars>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")

            """    209 <ret_chars>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_4"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    210 <ret_chars>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_5"]:
            self.parse_token("chars_lit")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_expr(self):
        self.appendF(FIRST_SET["<strict_chars_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    211 <strict_chars_expr>	=>	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_expr>"]:
            self.strict_chars_factor()
            self.strict_chars_add_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_factor(self):
        self.appendF(FIRST_SET["<strict_chars_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    212 <strict_chars_factor>	=>	<ret_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>"]:
            self.ret_chars()

            """    213 <strict_chars_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_1"]:
            self.id_()

            """    214 <strict_chars_factor>	=>	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_2"]:
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_chars_add_tail(self):
        self.appendF(FIRST_SET["<strict_chars_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    215 <strict_chars_add_tail>	=>	+	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>"]:
            self.parse_token("+")
            self.strict_chars_factor()
            self.strict_chars_add_tail()

            """    216 <strict_chars_add_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_str_tail_val(self):
        self.appendF(FIRST_SET["<paren_str_tail_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    217 <paren_str_tail_val>	=>	+	<strict_string_factor>	<paren_str_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.paren_str_tail_val()

            """    218 <paren_str_tail_val>	=>	)	<val_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>_1"]:
            self.parse_token(")")
            self.val_str_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_string_factor(self):
        self.appendF(FIRST_SET["<strict_string_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    219 <strict_string_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>"]:
            self.id_()

            """    220 <strict_string_factor>	=>	<ret_chars>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_1"]:
            self.ret_chars()

            """    221 <strict_string_factor>	=>	(	<paren_dispatch_val_str>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_str()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val_str(self):
        self.appendF(FIRST_SET["<paren_dispatch_val_str>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    222 <paren_dispatch_val_str>	=>	<id>	<paren_str_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>"]:
            self.id_()
            self.paren_str_tail_val()

            """    223 <paren_dispatch_val_str>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_1"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    224 <paren_dispatch_val_str>	=>	(	<paren_dispatch_val_str>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_2"]:
            self.parse_token("(")
            self.paren_dispatch_val_str()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def val_str_tail(self):
        self.appendF(FIRST_SET["<val_str_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    225 <val_str_tail>	=>	+	<strict_string_factor>	<val_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<val_str_tail>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.val_str_tail()

            """    226 <val_str_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_val(self):
        self.appendF(FIRST_SET["<paren_dispatch_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    227 <paren_dispatch_val>	=>	<id>	<paren_ambig_tail_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>"]:
            self.id_()
            self.paren_ambig_tail_val()

            """    228 <paren_dispatch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_1"]:
            self.ret_piece()
            self.paren_piece_tail_val()

            """    229 <paren_dispatch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_2"]:
            self.ret_sip()
            self.paren_sip_tail_val()

            """    230 <paren_dispatch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_3"]:
            self.ret_chars()
            self.paren_str_tail_val()

            """    231 <paren_dispatch_val>	=>	(	<paren_dispatch_val>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_4"]:
            self.parse_token("(")
            self.paren_dispatch_val()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def ret_flag(self):
        self.appendF(FIRST_SET["<ret_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    232 <ret_flag>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_flag>"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")

            """    233 <ret_flag>	=>	toflag	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_1"]:
            self.parse_token("toflag")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    234 <ret_flag>	=>	flag_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_2"]:
            self.parse_token("flag_lit")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_datas_expr(self):
        self.appendF(FIRST_SET["<strict_datas_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    235 <strict_datas_expr>	=>	[	<notation_val>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>"]:
            self.parse_token("[")
            self.notation_val()
            self.parse_token("]")

            """    236 <strict_datas_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_1"]:
            self.parse_token("id")
            self.id_tail()

            """    237 <strict_datas_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_2"]:
            self.ret_array()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_sip_tail(self):
        self.appendF(FIRST_SET["<lhs_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    238 <lhs_sip_tail>	=>	+	<strict_sip_factor>	<lhs_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    239 <lhs_sip_tail>	=>	-	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    240 <lhs_sip_tail>	=>	*	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    241 <lhs_sip_tail>	=>	/	<strict_sip_factor>	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.lhs_sip_tail()

            """    242 <lhs_sip_tail>	=>	<rel_op>	<strict_sip_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_4"]:
            self.rel_op()
            self.strict_sip_expr()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_str_tail(self):
        self.appendF(FIRST_SET["<lhs_str_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    243 <lhs_str_tail>	=>	+	<strict_string_factor>	<lhs_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.lhs_str_tail()

            """    244 <lhs_str_tail>	=>	<rel_op>	<strict_chars_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>_1"]:
            self.rel_op()
            self.strict_chars_expr()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_lhs_no_lambda(self):
        self.appendF(FIRST_SET["<paren_dispatch_lhs_no_lambda>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    245 <paren_dispatch_lhs_no_lambda>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    246 <paren_dispatch_lhs_no_lambda>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    247 <paren_dispatch_lhs_no_lambda>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    248 <paren_dispatch_lhs_no_lambda>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    249 <paren_dispatch_lhs_no_lambda>	=>	(	<paren_dispatch_lhs_no_lambda>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs_no_lambda()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_tail_lhs(self):
        self.appendF(FIRST_SET["<paren_ambig_tail_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    250 <paren_ambig_tail_lhs>	=>	+	<paren_ambig_branch_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>"]:
            self.parse_token("+")
            self.paren_ambig_branch_lhs()

            """    251 <paren_ambig_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    252 <paren_ambig_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    253 <paren_ambig_tail_lhs>	=>	/	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    254 <paren_ambig_tail_lhs>	=>	%	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    255 <paren_ambig_tail_lhs>	=>	)	<lhs_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_5"]:
            self.parse_token(")")
            self.lhs_ambig_tail()

            """    256 <paren_ambig_tail_lhs>	=>	<rel_op>	<strict_ambig_rhs>	<lhs_bool_tail>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_6"]:
            self.rel_op()
            self.strict_ambig_rhs()
            self.lhs_bool_tail()
            self.paren_ambig_tail_lhs()

            """    257 <paren_ambig_tail_lhs>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>	)	<lhs_flag_comp_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_7"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()
            self.parse_token(")")
            self.lhs_flag_comp_tail()

            """    258 <paren_ambig_tail_lhs>	=>	or	<strict_flag_term>	<strict_flag_or_tail>	)	<lhs_flag_comp_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_8"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()
            self.parse_token(")")
            self.lhs_flag_comp_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_ambig_branch_lhs(self):
        self.appendF(FIRST_SET["<paren_ambig_branch_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    259 <paren_ambig_branch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    260 <paren_ambig_branch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    261 <paren_ambig_branch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    262 <paren_ambig_branch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    263 <paren_ambig_branch_lhs>	=>	(	<paren_dispatch_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_4"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_piece_tail_lhs(self):
        self.appendF(FIRST_SET["<paren_piece_tail_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    264 <paren_piece_tail_lhs>	=>	+	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    265 <paren_piece_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    266 <paren_piece_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    267 <paren_piece_tail_lhs>	=>	/	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    268 <paren_piece_tail_lhs>	=>	%	<strict_piece_factor>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.paren_piece_tail_lhs()

            """    269 <paren_piece_tail_lhs>	=>	)	<lhs_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_5"]:
            self.parse_token(")")
            self.lhs_piece_tail()

            """    270 <paren_piece_tail_lhs>	=>	<rel_op>	<strict_piece_expr>	<lhs_bool_tail>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_6"]:
            self.rel_op()
            self.strict_piece_expr()
            self.lhs_bool_tail()
            self.paren_ambig_tail_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def lhs_bool_tail(self):
        self.appendF(FIRST_SET["<lhs_bool_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    271 <lhs_bool_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    272 <lhs_bool_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>_1"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    273 <lhs_bool_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_and_tail(self):
        self.appendF(FIRST_SET["<strict_flag_and_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    274 <strict_flag_and_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>"]:
            self.parse_token("and")
            self.strict_flag_factor()
            self.strict_flag_and_tail()

            """    275 <strict_flag_and_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_flag_or_tail(self):
        self.appendF(FIRST_SET["<strict_flag_or_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    276 <strict_flag_or_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>"]:
            self.parse_token("or")
            self.strict_flag_term()
            self.strict_flag_or_tail()

            """    277 <strict_flag_or_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_sip_tail_lhs(self):
        self.appendF(FIRST_SET["<paren_sip_tail_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    278 <paren_sip_tail_lhs>	=>	+	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    279 <paren_sip_tail_lhs>	=>	-	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    280 <paren_sip_tail_lhs>	=>	*	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    281 <paren_sip_tail_lhs>	=>	/	<strict_sip_factor>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.paren_sip_tail_lhs()

            """    282 <paren_sip_tail_lhs>	=>	)	<lhs_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_4"]:
            self.parse_token(")")
            self.lhs_sip_tail()

            """    283 <paren_sip_tail_lhs>	=>	<rel_op>	<strict_sip_expr>	<lhs_bool_tail>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_5"]:
            self.rel_op()
            self.strict_sip_expr()
            self.lhs_bool_tail()
            self.paren_ambig_tail_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_str_tail_lhs(self):
        self.appendF(FIRST_SET["<paren_str_tail_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    284 <paren_str_tail_lhs>	=>	+	<strict_string_factor>	<paren_str_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.paren_str_tail_lhs()

            """    285 <paren_str_tail_lhs>	=>	)	<lhs_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_1"]:
            self.parse_token(")")
            self.lhs_str_tail()

            """    286 <paren_str_tail_lhs>	=>	<rel_op>	<strict_chars_expr>	<lhs_bool_tail>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_2"]:
            self.rel_op()
            self.strict_chars_expr()
            self.lhs_bool_tail()
            self.paren_ambig_tail_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def paren_dispatch_lhs(self):
        self.appendF(FIRST_SET["<paren_dispatch_lhs>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    287 <paren_dispatch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
        if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>"]:
            self.id_()
            self.paren_ambig_tail_lhs()

            """    288 <paren_dispatch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_1"]:
            self.ret_piece()
            self.paren_piece_tail_lhs()

            """    289 <paren_dispatch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_2"]:
            self.ret_sip()
            self.paren_sip_tail_lhs()

            """    290 <paren_dispatch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_3"]:
            self.ret_chars()
            self.paren_str_tail_lhs()

            """    291 <paren_dispatch_lhs>	=>	<ret_flag>	<lhs_bool_tail>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_4"]:
            self.ret_flag()
            self.lhs_bool_tail()
            self.paren_ambig_tail_lhs()

            """    292 <paren_dispatch_lhs>	=>	not	<strict_flag_factor>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_5"]:
            self.parse_token("not")
            self.strict_flag_factor()
            self.paren_ambig_tail_lhs()

            """    293 <paren_dispatch_lhs>	=>	(	<paren_dispatch_lhs>	<paren_ambig_tail_lhs>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_6"]:
            self.parse_token("(")
            self.paren_dispatch_lhs()
            self.paren_ambig_tail_lhs()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_sip_tail(self):
        self.appendF(FIRST_SET["<univ_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    294 <univ_sip_tail>	=>	+	<strict_sip_expr>	<univ_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_expr()
            self.univ_sip_tail()

            """    295 <univ_sip_tail>	=>	-	<strict_sip_expr>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_expr()
            self.univ_sip_tail()

            """    296 <univ_sip_tail>	=>	*	<strict_sip_expr>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_expr()
            self.univ_sip_tail()

            """    297 <univ_sip_tail>	=>	/	<strict_sip_expr>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_expr()
            self.univ_sip_tail()

            """    298 <univ_sip_tail>	=>	%	<strict_sip_expr>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_4"]:
            self.parse_token("%")
            self.strict_sip_expr()
            self.univ_sip_tail()

            """    299 <univ_sip_tail>	=>	<rel_op>	<strict_sip_expr>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_5"]:
            self.rel_op()
            self.strict_sip_expr()
            self.univ_bool_tail()

            """    300 <univ_sip_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_str_tail(self):
        self.appendF(FIRST_SET["<univ_str_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    301 <univ_str_tail>	=>	+	<strict_chars_expr>	<univ_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_str_tail>"]:
            self.parse_token("+")
            self.strict_chars_expr()
            self.univ_str_tail()

            """    302 <univ_str_tail>	=>	<rel_op>	<strict_piece_expr>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_str_tail>_1"]:
            self.rel_op()
            self.strict_piece_expr()
            self.univ_bool_tail()

            """    303 <univ_str_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_dispatch(self):
        self.appendF(FIRST_SET["<univ_paren_dispatch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    304 <univ_paren_dispatch>	=>	<id>	<univ_paren_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>"]:
            self.id_()
            self.univ_paren_ambig_tail()

            """    305 <univ_paren_dispatch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_1"]:
            self.ret_piece()
            self.univ_paren_piece_tail()

            """    306 <univ_paren_dispatch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_2"]:
            self.ret_sip()
            self.univ_paren_sip_tail()

            """    307 <univ_paren_dispatch>	=>	<ret_chars>	<univ_paren_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_3"]:
            self.ret_chars()
            self.univ_paren_str_tail()

            """    308 <univ_paren_dispatch>	=>	<ret_flag>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_4"]:
            self.ret_flag()
            self.univ_bool_tail()

            """    309 <univ_paren_dispatch>	=>	not	<strict_flag_factor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_5"]:
            self.parse_token("not")
            self.strict_flag_factor()

            """    310 <univ_paren_dispatch>	=>	(	<univ_paren_dispatch>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_6"]:
            self.parse_token("(")
            self.univ_paren_dispatch()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_ambig_tail(self):
        self.appendF(FIRST_SET["<univ_paren_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    311 <univ_paren_ambig_tail>	=>	+	<univ_paren_ambig_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>"]:
            self.parse_token("+")
            self.univ_paren_ambig_branch()

            """    312 <univ_paren_ambig_tail>	=>	-	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_1"]:
            self.parse_token("-")
            self.univ_paren_ambig_numeric_branch()

            """    313 <univ_paren_ambig_tail>	=>	*	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_2"]:
            self.parse_token("*")
            self.univ_paren_ambig_numeric_branch()

            """    314 <univ_paren_ambig_tail>	=>	/	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_3"]:
            self.parse_token("/")
            self.univ_paren_ambig_numeric_branch()

            """    315 <univ_paren_ambig_tail>	=>	%	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_4"]:
            self.parse_token("%")
            self.univ_paren_ambig_numeric_branch()

            """    316 <univ_paren_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()
            self.univ_bool_tail()
            self.parse_token(")")

            """    317 <univ_paren_ambig_tail>	=>	)	<univ_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_6"]:
            self.parse_token(")")
            self.univ_ambig_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_ambig_branch(self):
        self.appendF(FIRST_SET["<univ_paren_ambig_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    318 <univ_paren_ambig_branch>	=>	<id>	<univ_paren_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>"]:
            self.id_()
            self.univ_paren_ambig_tail()

            """    319 <univ_paren_ambig_branch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_1"]:
            self.ret_piece()
            self.univ_paren_piece_tail()

            """    320 <univ_paren_ambig_branch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_2"]:
            self.ret_sip()
            self.univ_paren_sip_tail()

            """    321 <univ_paren_ambig_branch>	=>	<ret_chars>	<univ_paren_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_3"]:
            self.ret_chars()
            self.univ_paren_str_tail()

            """    322 <univ_paren_ambig_branch>	=>	(	<univ_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_4"]:
            self.parse_token("(")
            self.univ_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_piece_tail(self):
        self.appendF(FIRST_SET["<univ_paren_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    323 <univ_paren_piece_tail>	=>	+	<strict_piece_factor>	<univ_paren_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.univ_paren_piece_tail()

            """    324 <univ_paren_piece_tail>	=>	-	<strict_piece_factor>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.univ_paren_piece_tail()

            """    325 <univ_paren_piece_tail>	=>	*	<strict_piece_factor>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.univ_paren_piece_tail()

            """    326 <univ_paren_piece_tail>	=>	/	<strict_piece_factor>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.univ_paren_piece_tail()

            """    327 <univ_paren_piece_tail>	=>	%	<strict_piece_factor>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.univ_paren_piece_tail()

            """    328 <univ_paren_piece_tail>	=>	)	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_5"]:
            self.parse_token(")")
            self.univ_piece_tail()

            """    329 <univ_paren_piece_tail>	=>	<rel_op>	<strict_piece_expr>	<univ_bool_tail>	)	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_6"]:
            self.rel_op()
            self.strict_piece_expr()
            self.univ_bool_tail()
            self.parse_token(")")
            self.univ_bool_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_sip_tail(self):
        self.appendF(FIRST_SET["<univ_paren_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    330 <univ_paren_sip_tail>	=>	+	<strict_sip_factor>	<univ_paren_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>"]:
            self.parse_token("+")
            self.strict_sip_factor()
            self.univ_paren_sip_tail()

            """    331 <univ_paren_sip_tail>	=>	-	<strict_sip_factor>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_1"]:
            self.parse_token("-")
            self.strict_sip_factor()
            self.univ_paren_sip_tail()

            """    332 <univ_paren_sip_tail>	=>	*	<strict_sip_factor>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_2"]:
            self.parse_token("*")
            self.strict_sip_factor()
            self.univ_paren_sip_tail()

            """    333 <univ_paren_sip_tail>	=>	/	<strict_sip_factor>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_3"]:
            self.parse_token("/")
            self.strict_sip_factor()
            self.univ_paren_sip_tail()

            """    334 <univ_paren_sip_tail>	=>	)	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_4"]:
            self.parse_token(")")
            self.univ_sip_tail()

            """    335 <univ_paren_sip_tail>	=>	<rel_op>	<strict_sip_expr>	<univ_bool_tail>	)	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_5"]:
            self.rel_op()
            self.strict_sip_expr()
            self.univ_bool_tail()
            self.parse_token(")")
            self.univ_bool_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_str_tail(self):
        self.appendF(FIRST_SET["<univ_paren_str_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    336 <univ_paren_str_tail>	=>	+	<strict_string_factor>	<univ_paren_str_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_str_tail>"]:
            self.parse_token("+")
            self.strict_string_factor()
            self.univ_paren_str_tail()

            """    337 <univ_paren_str_tail>	=>	)	<univ_str_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_str_tail>_1"]:
            self.parse_token(")")
            self.univ_str_tail()

            """    338 <univ_paren_str_tail>	=>	<rel_op>	<strict_chars_expr>	<univ_bool_tail>	)	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_str_tail>_2"]:
            self.rel_op()
            self.strict_chars_expr()
            self.univ_bool_tail()
            self.parse_token(")")
            self.univ_bool_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_ambig_numeric_branch(self):
        self.appendF(FIRST_SET["<univ_paren_ambig_numeric_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    339 <univ_paren_ambig_numeric_branch>	=>	<id>	<univ_paren_ambig_numeric_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>"]:
            self.id_()
            self.univ_paren_ambig_numeric_tail()

            """    340 <univ_paren_ambig_numeric_branch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_1"]:
            self.ret_piece()
            self.univ_paren_piece_tail()

            """    341 <univ_paren_ambig_numeric_branch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_2"]:
            self.ret_sip()
            self.univ_paren_sip_tail()

            """    342 <univ_paren_ambig_numeric_branch>	=>	(	<univ_paren_dispatch_numeric>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_3"]:
            self.parse_token("(")
            self.univ_paren_dispatch_numeric()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_ambig_numeric_tail(self):
        self.appendF(FIRST_SET["<univ_paren_ambig_numeric_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    343 <univ_paren_ambig_numeric_tail>	=>	+	<univ_paren_ambig_numeric_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>"]:
            self.parse_token("+")
            self.univ_paren_ambig_numeric_branch()

            """    344 <univ_paren_ambig_numeric_tail>	=>	-	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_1"]:
            self.parse_token("-")
            self.univ_paren_ambig_numeric_branch()

            """    345 <univ_paren_ambig_numeric_tail>	=>	*	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_2"]:
            self.parse_token("*")
            self.univ_paren_ambig_numeric_branch()

            """    346 <univ_paren_ambig_numeric_tail>	=>	/	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_3"]:
            self.parse_token("/")
            self.univ_paren_ambig_numeric_branch()

            """    347 <univ_paren_ambig_numeric_tail>	=>	%	<univ_paren_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_4"]:
            self.parse_token("%")
            self.univ_paren_ambig_numeric_branch()

            """    348 <univ_paren_ambig_numeric_tail>	=>	)	<univ_ambig_numeric_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_5"]:
            self.parse_token(")")
            self.univ_ambig_numeric_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_ambig_numeric_tail(self):
        self.appendF(FIRST_SET["<univ_ambig_numeric_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    349 <univ_ambig_numeric_tail>	=>	+	<univ_ambig_numeric_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>"]:
            self.parse_token("+")
            self.univ_ambig_numeric_branch()

            """    350 <univ_ambig_numeric_tail>	=>	-	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_1"]:
            self.parse_token("-")
            self.univ_ambig_numeric_branch()

            """    351 <univ_ambig_numeric_tail>	=>	*	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_2"]:
            self.parse_token("*")
            self.univ_ambig_numeric_branch()

            """    352 <univ_ambig_numeric_tail>	=>	/	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_3"]:
            self.parse_token("/")
            self.univ_ambig_numeric_branch()

            """    353 <univ_ambig_numeric_tail>	=>	%	<univ_ambig_numeric_branch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_4"]:
            self.parse_token("%")
            self.univ_ambig_numeric_branch()

            """    354 <univ_ambig_numeric_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_5"]:
            self.rel_op()
            self.strict_ambig_rhs()
            self.univ_bool_tail()

            """    355 <univ_ambig_numeric_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_ambig_numeric_branch(self):
        self.appendF(FIRST_SET["<univ_ambig_numeric_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    356 <univ_ambig_numeric_branch>	=>	<id>	<univ_ambig_numeric_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>"]:
            self.id_()
            self.univ_ambig_numeric_tail()

            """    357 <univ_ambig_numeric_branch>	=>	<ret_piece>	<univ_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_1"]:
            self.ret_piece()
            self.univ_piece_tail()

            """    358 <univ_ambig_numeric_branch>	=>	<ret_sip>	<univ_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_2"]:
            self.ret_sip()
            self.univ_sip_tail()

            """    359 <univ_ambig_numeric_branch>	=>	(	<univ_paren_dispatch_numeric>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_3"]:
            self.parse_token("(")
            self.univ_paren_dispatch_numeric()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def univ_paren_dispatch_numeric(self):
        self.appendF(FIRST_SET["<univ_paren_dispatch_numeric>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    360 <univ_paren_dispatch_numeric>	=>	<id>	<univ_paren_ambig_numeric_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>"]:
            self.id_()
            self.univ_paren_ambig_numeric_tail()

            """    361 <univ_paren_dispatch_numeric>	=>	<ret_piece>	<univ_paren_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_1"]:
            self.ret_piece()
            self.univ_paren_piece_tail()

            """    362 <univ_paren_dispatch_numeric>	=>	<ret_sip>	<univ_paren_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_2"]:
            self.ret_sip()
            self.univ_paren_sip_tail()

            """    363 <univ_paren_dispatch_numeric>	=>	(	<univ_paren_dispatch_numeric>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_3"]:
            self.parse_token("(")
            self.univ_paren_dispatch_numeric()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_mult_tail(self):
        self.appendF(FIRST_SET["<strict_piece_mult_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    364 <strict_piece_mult_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    365 <strict_piece_mult_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_1"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    366 <strict_piece_mult_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_2"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()

            """    367 <strict_piece_mult_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_add_tail(self):
        self.appendF(FIRST_SET["<strict_piece_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    368 <strict_piece_add_tail>	=>	+	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>"]:
            self.parse_token("+")
            self.strict_piece_term()
            self.strict_piece_add_tail()

            """    369 <strict_piece_add_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_term()
            self.strict_piece_add_tail()

            """    370 <strict_piece_add_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_id_tail(self):
        self.appendF(FIRST_SET["<piece_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    371 <piece_id_tail>	=>	,	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.piece_ingredient_init()
            self.piece_id_tail()

            """    372 <piece_id_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_array_decl(self):
        self.appendF(FIRST_SET["<piece_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    373 <piece_array_decl>	=>	<dimensions>	of	id	<piece_array_init>	<array_declare_tail_piece>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_decl>"]:
            self.dimensions()
            self.parse_token("of")
            self.parse_token("id")
            self.piece_array_init()
            self.array_declare_tail_piece()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions(self):
        self.appendF(FIRST_SET["<dimensions>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    374 <dimensions>	=>	[	]	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions>"]:
            self.parse_token("[")
            self.parse_token("]")
            self.dimensions_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def dimensions_tail(self):
        self.appendF(FIRST_SET["<dimensions_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    375 <dimensions_tail>	=>	<dimensions>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>"]:
            self.dimensions()

            """    376 <dimensions_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_array_init(self):
        self.appendF(FIRST_SET["<piece_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    377 <piece_array_init>	=>	=	<piece_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>"]:
            self.parse_token("=")
            self.piece_array_val()

            """    378 <piece_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def piece_array_val(self):
        self.appendF(FIRST_SET["<piece_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    379 <piece_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>"]:
            self.parse_token("id")
            self.id_tail()

            """    380 <piece_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_1"]:
            self.ret_array()

            """    381 <piece_array_val>	=>	[	<array_element_piece_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_2"]:
            self.parse_token("[")
            self.array_element_piece_opt()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_piece_opt(self):
        self.appendF(FIRST_SET["<array_element_piece_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    382 <array_element_piece_opt>	=>	<array_element_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>"]:
            self.array_element_piece()

            """    383 <array_element_piece_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_piece(self):
        self.appendF(FIRST_SET["<array_element_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    384 <array_element_piece>	=>	id	<element_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>"]:
            self.parse_token("id")
            self.element_piece_tail()

            """    385 <array_element_piece>	=>	piece_lit	<element_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_1"]:
            self.parse_token("piece_lit")
            self.element_piece_tail()

            """    386 <array_element_piece>	=>	[	<array_element_piece>	]	<element_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_2"]:
            self.parse_token("[")
            self.array_element_piece()
            self.parse_token("]")
            self.element_piece_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_piece_tail(self):
        self.appendF(FIRST_SET["<element_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    387 <element_piece_tail>	=>	,	<array_element_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_piece_tail>"]:
            self.parse_token(",")
            self.array_element_piece()

            """    388 <element_piece_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail_piece(self):
        self.appendF(FIRST_SET["<array_declare_tail_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    389 <array_declare_tail_piece>	=>	,	id	<piece_array_init>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_piece>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.piece_array_init()

            """    390 <array_declare_tail_piece>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_decl(self):
        self.appendF(FIRST_SET["<chars_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    391 <chars_decl>	=>	of	<chars_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_decl>"]:
            self.parse_token("of")
            self.chars_id()
            self.parse_token(";")

            """    392 <chars_decl>	=>	<chars_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_decl>_1"]:
            self.chars_array_decl()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_id(self):
        self.appendF(FIRST_SET["<chars_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    393 <chars_id>	=>	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id>"]:
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_ingredient_init(self):
        self.appendF(FIRST_SET["<chars_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    394 <chars_ingredient_init>	=>	=	<strict_chars_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>"]:
            self.parse_token("=")
            self.strict_chars_expr()

            """    395 <chars_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_id_tail(self):
        self.appendF(FIRST_SET["<chars_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    396 <chars_id_tail>	=>	,	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.chars_ingredient_init()
            self.chars_id_tail()

            """    397 <chars_id_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_array_decl(self):
        self.appendF(FIRST_SET["<chars_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    398 <chars_array_decl>	=>	<dimensions>	of	id	<chars_array_init>	<array_declare_tail_chars>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_decl>"]:
            self.dimensions()
            self.parse_token("of")
            self.parse_token("id")
            self.chars_array_init()
            self.array_declare_tail_chars()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_array_init(self):
        self.appendF(FIRST_SET["<chars_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    399 <chars_array_init>	=>	=	<chars_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>"]:
            self.parse_token("=")
            self.chars_array_val()

            """    400 <chars_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def chars_array_val(self):
        self.appendF(FIRST_SET["<chars_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    401 <chars_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>"]:
            self.parse_token("id")
            self.id_tail()

            """    402 <chars_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_1"]:
            self.ret_array()

            """    403 <chars_array_val>	=>	[	<array_element_chars_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_2"]:
            self.parse_token("[")
            self.array_element_chars_opt()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_chars_opt(self):
        self.appendF(FIRST_SET["<array_element_chars_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    404 <array_element_chars_opt>	=>	<array_element_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>"]:
            self.array_element_chars()

            """    405 <array_element_chars_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_chars(self):
        self.appendF(FIRST_SET["<array_element_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    406 <array_element_chars>	=>	id	<element_chars_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>"]:
            self.parse_token("id")
            self.element_chars_tail()

            """    407 <array_element_chars>	=>	chars_lit	<element_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_1"]:
            self.parse_token("chars_lit")
            self.element_chars_tail()

            """    408 <array_element_chars>	=>	[	<array_element_chars_opt>	]	<element_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_2"]:
            self.parse_token("[")
            self.array_element_chars_opt()
            self.parse_token("]")
            self.element_chars_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_chars_tail(self):
        self.appendF(FIRST_SET["<element_chars_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    409 <element_chars_tail>	=>	,	<array_element_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_chars_tail>"]:
            self.parse_token(",")
            self.array_element_chars()

            """    410 <element_chars_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail_chars(self):
        self.appendF(FIRST_SET["<array_declare_tail_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    411 <array_declare_tail_chars>	=>	,	id	<chars_array_init>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_chars>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.chars_array_init()

            """    412 <array_declare_tail_chars>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_decl(self):
        self.appendF(FIRST_SET["<sip_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    413 <sip_decl>	=>	of	<sip_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_decl>"]:
            self.parse_token("of")
            self.sip_id()
            self.parse_token(";")

            """    414 <sip_decl>	=>	<sip_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_decl>_1"]:
            self.sip_array_decl()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id(self):
        self.appendF(FIRST_SET["<sip_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    415 <sip_id>	=>	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id>"]:
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_ingredient_init(self):
        self.appendF(FIRST_SET["<sip_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    416 <sip_ingredient_init>	=>	=	<strict_sip_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>"]:
            self.parse_token("=")
            self.strict_sip_expr()

            """    417 <sip_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_id_tail(self):
        self.appendF(FIRST_SET["<sip_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    418 <sip_id_tail>	=>	,	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.sip_ingredient_init()
            self.sip_id_tail()

            """    419 <sip_id_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_array_decl(self):
        self.appendF(FIRST_SET["<sip_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    420 <sip_array_decl>	=>	<dimensions>	of	id	<sip_array_init>	<array_declare_tail_sip>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_decl>"]:
            self.dimensions()
            self.parse_token("of")
            self.parse_token("id")
            self.sip_array_init()
            self.array_declare_tail_sip()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_array_init(self):
        self.appendF(FIRST_SET["<sip_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    421 <sip_array_init>	=>	=	<sip_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>"]:
            self.parse_token("=")
            self.sip_array_val()

            """    422 <sip_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def sip_array_val(self):
        self.appendF(FIRST_SET["<sip_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    423 <sip_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>"]:
            self.parse_token("id")
            self.id_tail()

            """    424 <sip_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_1"]:
            self.ret_array()

            """    425 <sip_array_val>	=>	[	<array_element_sip_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_2"]:
            self.parse_token("[")
            self.array_element_sip_opt()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_sip_opt(self):
        self.appendF(FIRST_SET["<array_element_sip_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    426 <array_element_sip_opt>	=>	<array_element_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>"]:
            self.array_element_sip()

            """    427 <array_element_sip_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_sip(self):
        self.appendF(FIRST_SET["<array_element_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    428 <array_element_sip>	=>	id	<element_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>"]:
            self.parse_token("id")
            self.element_sip_tail()

            """    429 <array_element_sip>	=>	sip_lit	<element_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_1"]:
            self.parse_token("sip_lit")
            self.element_sip_tail()

            """    430 <array_element_sip>	=>	[	<array_element_sip_opt>	]	<element_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_2"]:
            self.parse_token("[")
            self.array_element_sip_opt()
            self.parse_token("]")
            self.element_sip_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_sip_tail(self):
        self.appendF(FIRST_SET["<element_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    431 <element_sip_tail>	=>	,	<array_element_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_sip_tail>"]:
            self.parse_token(",")
            self.array_element_sip()

            """    432 <element_sip_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail_sip(self):
        self.appendF(FIRST_SET["<array_declare_tail_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    433 <array_declare_tail_sip>	=>	,	id	<sip_array_init>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_sip>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.sip_array_init()

            """    434 <array_declare_tail_sip>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_decl(self):
        self.appendF(FIRST_SET["<flag_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    435 <flag_decl>	=>	of	<flag_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_decl>"]:
            self.parse_token("of")
            self.flag_id()
            self.parse_token(";")

            """    436 <flag_decl>	=>	<flag_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_decl>_1"]:
            self.flag_array_decl()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_id(self):
        self.appendF(FIRST_SET["<flag_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    437 <flag_id>	=>	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id>"]:
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_ingredient_init(self):
        self.appendF(FIRST_SET["<flag_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    438 <flag_ingredient_init>	=>	=	<strict_flag_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>"]:
            self.parse_token("=")
            self.strict_flag_expr()

            """    439 <flag_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_id_tail(self):
        self.appendF(FIRST_SET["<flag_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    440 <flag_id_tail>	=>	,	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.flag_ingredient_init()
            self.flag_id_tail()

            """    441 <flag_id_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_array_decl(self):
        self.appendF(FIRST_SET["<flag_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    442 <flag_array_decl>	=>	<dimensions>	of	id	<flag_array_init>	<array_declare_tail_flag>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_decl>"]:
            self.dimensions()
            self.parse_token("of")
            self.parse_token("id")
            self.flag_array_init()
            self.array_declare_tail_flag()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_array_init(self):
        self.appendF(FIRST_SET["<flag_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    443 <flag_array_init>	=>	=	<flag_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>"]:
            self.parse_token("=")
            self.flag_array_val()

            """    444 <flag_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def flag_array_val(self):
        self.appendF(FIRST_SET["<flag_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    445 <flag_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>"]:
            self.parse_token("id")
            self.id_tail()

            """    446 <flag_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_1"]:
            self.ret_array()

            """    447 <flag_array_val>	=>	[	<array_element_flag_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_2"]:
            self.parse_token("[")
            self.array_element_flag_opt()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_flag_opt(self):
        self.appendF(FIRST_SET["<array_element_flag_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    448 <array_element_flag_opt>	=>	<array_element_flag>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>"]:
            self.array_element_flag()

            """    449 <array_element_flag_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_flag(self):
        self.appendF(FIRST_SET["<array_element_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    450 <array_element_flag>	=>	id	<element_flag_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>"]:
            self.parse_token("id")
            self.element_flag_tail()

            """    451 <array_element_flag>	=>	flag_lit	<element_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_1"]:
            self.parse_token("flag_lit")
            self.element_flag_tail()

            """    452 <array_element_flag>	=>	[	<array_element_flag_opt>	]	<element_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_2"]:
            self.parse_token("[")
            self.array_element_flag_opt()
            self.parse_token("]")
            self.element_flag_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_flag_tail(self):
        self.appendF(FIRST_SET["<element_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    453 <element_flag_tail>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_flag_tail>"]:
            self.parse_token(",")
            self.array_element_id()

            """    454 <element_flag_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail_flag(self):
        self.appendF(FIRST_SET["<array_declare_tail_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    455 <array_declare_tail_flag>	=>	,	id	<flag_array_init>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_flag>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.flag_array_init()

            """    456 <array_declare_tail_flag>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_prototype(self):
        self.appendF(FIRST_SET["<table_prototype>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    457 <table_prototype>	=>	table	of	id	=	[	<required_decl>	]	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_prototype>"]:
            self.parse_token("table")
            self.parse_token("of")
            self.parse_token("id")
            self.parse_token("=")
            self.parse_token("[")
            self.required_decl()
            self.parse_token("]")
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def required_decl(self):
        self.appendF(FIRST_SET["<required_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    458 <required_decl>	=>	<decl_head>	;	<required_decl_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl>"]:
            self.decl_head()
            self.parse_token(";")
            self.required_decl_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def decl_head(self):
        self.appendF(FIRST_SET["<decl_head>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    459 <decl_head>	=>	<primitive_types_dims>	of	id    """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_head>"]:
            self.primitive_types_dims()
            self.parse_token("of")
            self.parse_token("id")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def primitive_types_dims(self):
        self.appendF(FIRST_SET["<primitive_types_dims>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    460 <primitive_types_dims>	=>	piece	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>"]:
            self.parse_token("piece")
            self.dimensions_tail()

            """    461 <primitive_types_dims>	=>	sip	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_1"]:
            self.parse_token("sip")
            self.dimensions_tail()

            """    462 <primitive_types_dims>	=>	flag	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_2"]:
            self.parse_token("flag")
            self.dimensions_tail()

            """    463 <primitive_types_dims>	=>	chars	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_3"]:
            self.parse_token("chars")
            self.dimensions_tail()

            """    464 <primitive_types_dims>	=>	id	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_4"]:
            self.parse_token("id")
            self.dimensions_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def required_decl_tail(self):
        self.appendF(FIRST_SET["<required_decl_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    465 <required_decl_tail>	=>	<required_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>"]:
            self.required_decl()

            """    466 <required_decl_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_decl(self):
        self.appendF(FIRST_SET["<table_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    467 <table_decl>	=>	of	<table_declare>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_decl>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")

            """    468 <table_decl>	=>	<table_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_decl>_1"]:
            self.table_array_decl()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_declare(self):
        self.appendF(FIRST_SET["<table_declare>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    469 <table_declare>	=>	id	<table_init>	<table_declare_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare>"]:
            self.parse_token("id")
            self.table_init()
            self.table_declare_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_init(self):
        self.appendF(FIRST_SET["<table_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    470 <table_init>	=>	=	<strict_table_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_init>"]:
            self.parse_token("=")
            self.strict_table_expr()

            """    471 <table_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_table_expr(self):
        self.appendF(FIRST_SET["<strict_table_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    472 <strict_table_expr>	=>	[	<field_assignments>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>"]:
            self.parse_token("[")
            self.field_assignments()
            self.parse_token("]")

            """    473 <strict_table_expr>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>_1"]:
            self.id_()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_declare_tail(self):
        self.appendF(FIRST_SET["<table_declare_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    474 <table_declare_tail>	=>	,	<table_declare>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>"]:
            self.parse_token(",")
            self.table_declare()

            """    475 <table_declare_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_array_decl(self):
        self.appendF(FIRST_SET["<table_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    476 <table_array_decl>	=>	<dimensions>	of	id	<table_array_init>	<array_declare_tail_table>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_decl>"]:
            self.dimensions()
            self.parse_token("of")
            self.parse_token("id")
            self.table_array_init()
            self.array_declare_tail_table()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_array_init(self):
        self.appendF(FIRST_SET["<table_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    477 <table_array_init>	=>	=	<table_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_init>"]:
            self.parse_token("=")
            self.table_array_val()

            """    478 <table_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def table_array_val(self):
        self.appendF(FIRST_SET["<table_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    479 <table_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_val>"]:
            self.parse_token("id")
            self.id_tail()

            """    480 <table_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_1"]:
            self.ret_array()

            """    481 <table_array_val>	=>	[	<array_element_table_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_2"]:
            self.parse_token("[")
            self.array_element_table_opt()
            self.parse_token("]")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_table_opt(self):
        self.appendF(FIRST_SET["<array_element_table_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    482 <array_element_table_opt>	=>	<array_element_table>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>"]:
            self.array_element_table()

            """    483 <array_element_table_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_element_table(self):
        self.appendF(FIRST_SET["<array_element_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    484 <array_element_table>	=>	<strict_table_expr>	<element_table_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_table>"]:
            self.strict_table_expr()
            self.element_table_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def element_table_tail(self):
        self.appendF(FIRST_SET["<element_table_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    485 <element_table_tail>	=>	,	<array_element_table>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_table_tail>"]:
            self.parse_token(",")
            self.array_element_table()

            """    486 <element_table_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def array_declare_tail_table(self):
        self.appendF(FIRST_SET["<array_declare_tail_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    487 <array_declare_tail_table>	=>	,	id	<table_array_init>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_table>"]:
            self.parse_token(",")
            self.parse_token("id")
            self.table_array_init()

            """    488 <array_declare_tail_table>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def recipe_decl(self):
        self.appendF(FIRST_SET["<recipe_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    489 <recipe_decl>	=>	prepare	<serve_type>	(	<spice>	)	<platter>	<recipe_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>"]:
            self.parse_token("prepare")
            self.serve_type()
            self.parse_token("(")
            self.spice()
            self.parse_token(")")
            self.platter()
            self.recipe_decl()

            """    490 <recipe_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def serve_type(self):
        self.appendF(FIRST_SET["<serve_type>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    491 <serve_type>	=>	<decl_head>    """
        if self.tokens[self.pos].type in PREDICT_SET["<serve_type>"]:
            self.decl_head()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice(self):
        self.appendF(FIRST_SET["<spice>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    492 <spice>	=>	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice>"]:
            self.decl_head()
            self.spice_tail()

            """    493 <spice>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def spice_tail(self):
        self.appendF(FIRST_SET["<spice_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    494 <spice_tail>	=>	,	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice_tail>"]:
            self.parse_token(",")
            self.decl_head()
            self.spice_tail()

            """    495 <spice_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def platter(self):
        self.appendF(FIRST_SET["<platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    496 <platter>	=>	{	<local_decl>	<statements>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<platter>"]:
            self.parse_token("{")
            self.local_decl()
            self.statements()
            self.parse_token("}")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl(self):
        self.appendF(FIRST_SET["<local_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    497 <local_decl>	=>	piece	<piece_decl>	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl()

            """    498 <local_decl>	=>	chars	<chars_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl()

            """    499 <local_decl>	=>	sip	<sip_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl()

            """    500 <local_decl>	=>	flag	<flag_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl()

            """    501 <local_decl>	=>	id	<local_id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_4"]:
            self.parse_token("id")
            self.local_id_tail()

            """    502 <local_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail(self):
        self.appendF(FIRST_SET["<local_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    503 <local_id_tail>	=>	of	<table_declare>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl()

            """    504 <local_id_tail>	=>	[	<endsb_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_1"]:
            self.parse_token("[")
            self.endsb_tail()

            """    505 <local_id_tail>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()

            """    506 <local_id_tail>	=>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()

            """    507 <local_id_tail>	=>	<tail1>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endsb_tail(self):
        self.appendF(FIRST_SET["<endsb_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    508 <endsb_tail>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.parse_token("id")
            self.table_array_init()
            self.parse_token(";")
            self.local_decl()

            """    509 <endsb_tail>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail>_1"]:
            self.array_accessor_val()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def assignment_op(self):
        self.appendF(FIRST_SET["<assignment_op>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    510 <assignment_op>	=>	=    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_op>"]:
            self.parse_token("=")

            """    511 <assignment_op>	=>	+=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_1"]:
            self.parse_token("+=")

            """    512 <assignment_op>	=>	-=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_2"]:
            self.parse_token("-=")

            """    513 <assignment_op>	=>	*=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_3"]:
            self.parse_token("*=")

            """    514 <assignment_op>	=>	/=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_4"]:
            self.parse_token("/=")

            """    515 <assignment_op>	=>	%=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_5"]:
            self.parse_token("%=")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements(self):
        self.appendF(FIRST_SET["<statements>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    516 <statements>	=>	<id_statements>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements>"]:
            self.id_statements()
            self.statements()

            """    517 <statements>	=>	<built_in_rec_call>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements()

            """    518 <statements>	=>	<conditional_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_2"]:
            self.conditional_st()
            self.statements()

            """    519 <statements>	=>	<looping_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_3"]:
            self.looping_st()
            self.statements()

            """    520 <statements>	=>	<jump_serve>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_4"]:
            self.jump_serve()
            self.statements()

            """    521 <statements>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements(self):
        self.appendF(FIRST_SET["<id_statements>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    522 <id_statements>	=>	id	<id_statements_ext>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_ext(self):
        self.appendF(FIRST_SET["<id_statements_ext>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    523 <id_statements_ext>	=>	<tail1>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>"]:
            self.tail1()
            self.parse_token(";")

            """    524 <id_statements_ext>	=>	<assignment_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>_1"]:
            self.assignment_st()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def tail1(self):
        self.appendF(FIRST_SET["<tail1>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    525 <tail1>	=>	<call_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<tail1>"]:
            self.call_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def call_tail(self):
        self.appendF(FIRST_SET["<call_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    526 <call_tail>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tail>"]:
            self.parse_token("(")
            self.flavor()
            self.parse_token(")")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def assignment_st(self):
        self.appendF(FIRST_SET["<assignment_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    527 <assignment_st>	=>	<accessor_tail>	<assignment_op>	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_st>"]:
            self.accessor_tail()
            self.assignment_op()
            self.value()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec_call(self):
        self.appendF(FIRST_SET["<built_in_rec_call>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    528 <built_in_rec_call>	=>	<built_in_rec>    """
        if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec_call>"]:
            self.built_in_rec()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def built_in_rec(self):
        self.appendF(FIRST_SET["<built_in_rec>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    529 <built_in_rec>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>"]:
            self.parse_token("append")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    530 <built_in_rec>	=>	bill	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_1"]:
            self.parse_token("bill")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(")")

            """    531 <built_in_rec>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_2"]:
            self.parse_token("copy")
            self.parse_token("(")
            self.strict_chars_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    532 <built_in_rec>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_3"]:
            self.parse_token("cut")
            self.parse_token("(")
            self.strict_sip_expr()
            self.parse_token(",")
            self.strict_sip_expr()
            self.parse_token(")")

            """    533 <built_in_rec>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_4"]:
            self.parse_token("fact")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    534 <built_in_rec>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_5"]:
            self.parse_token("matches")
            self.parse_token("(")
            self.strict_datas_expr()
            self.parse_token(",")
            self.strict_datas_expr()
            self.parse_token(")")

            """    535 <built_in_rec>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_6"]:
            self.parse_token("pow")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    536 <built_in_rec>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_7"]:
            self.parse_token("rand")
            self.parse_token("(")
            self.parse_token(")")

            """    537 <built_in_rec>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_8"]:
            self.parse_token("remove")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.strict_piece_expr()
            self.parse_token(")")

            """    538 <built_in_rec>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_9"]:
            self.parse_token("reverse")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    539 <built_in_rec>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_10"]:
            self.parse_token("search")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(",")
            self.value()
            self.parse_token(")")

            """    540 <built_in_rec>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_11"]:
            self.parse_token("size")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    541 <built_in_rec>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_12"]:
            self.parse_token("sort")
            self.parse_token("(")
            self.strict_array_expr()
            self.parse_token(")")

            """    542 <built_in_rec>	=>	sqrt	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_13"]:
            self.parse_token("sqrt")
            self.parse_token("(")
            self.strict_piece_expr()
            self.parse_token(")")

            """    543 <built_in_rec>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_14"]:
            self.parse_token("take")
            self.parse_token("(")
            self.parse_token(")")

            """    544 <built_in_rec>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_15"]:
            self.parse_token("tochars")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    545 <built_in_rec>	=>	topiece	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_16"]:
            self.parse_token("topiece")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

            """    546 <built_in_rec>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_17"]:
            self.parse_token("tosip")
            self.parse_token("(")
            self.any_expr()
            self.parse_token(")")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st(self):
        self.appendF(FIRST_SET["<conditional_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    547 <conditional_st>	=>	<cond_check>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st>"]:
            self.cond_check()

            """    548 <conditional_st>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st>_1"]:
            self.cond_menu()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check(self):
        self.appendF(FIRST_SET["<cond_check>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    549 <cond_check>	=>	check	(	<strict_flag_expr>	)	<platter>	<alt_clause>	<instead_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.platter()
            self.alt_clause()
            self.instead_clause()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def alt_clause(self):
        self.appendF(FIRST_SET["<alt_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    550 <alt_clause>	=>	alt	(	<strict_flag_expr>	)	<platter>	<alt_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.platter()
            self.alt_clause()

            """    551 <alt_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause(self):
        self.appendF(FIRST_SET["<instead_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    552 <instead_clause>	=>	instead	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause>"]:
            self.parse_token("instead")
            self.platter()

            """    553 <instead_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu(self):
        self.appendF(FIRST_SET["<cond_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    554 <cond_menu>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu>"]:
            self.parse_token("menu")
            self.parse_token("(")
            self.strict_piece_chars_expr()
            self.parse_token(")")
            self.menu_platter()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def strict_piece_chars_expr(self):
        self.appendF(FIRST_SET["<strict_piece_chars_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    666 <strict_piece_chars_expr>	=>	<id>	<pc_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>"]:
            self.id_()
            self.pc_ambig_tail()

            """    667 <strict_piece_chars_expr>	=>	<ret_piece>	<pc_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_1"]:
            self.ret_piece()
            self.pc_piece_tail()

            """    668 <strict_piece_chars_expr>	=>	<ret_chars>	<pc_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_2"]:
            self.ret_chars()
            self.pc_chars_tail()

            """    669 <strict_piece_chars_expr>	=>	(	<pc_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_3"]:
            self.parse_token("(")
            self.pc_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_ambig_tail(self):
        self.appendF(FIRST_SET["<pc_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    672 <pc_ambig_tail>	=>	+	<pc_ambig_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>"]:
            self.parse_token("+")
            self.pc_ambig_branch()

            """    673 <pc_ambig_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_1"]:
            self.parse_token("-")
            self.strict_piece_term()
            self.strict_piece_add_tail()

            """    674 <pc_ambig_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            self.strict_piece_add_tail()

            """    675 <pc_ambig_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            self.strict_piece_add_tail()

            """    676 <pc_ambig_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.strict_piece_mult_tail()
            self.strict_piece_add_tail()

            """    677 <pc_ambig_tail>	=>	    """



        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_ambig_branch(self):
        self.appendF(FIRST_SET["<pc_ambig_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    678 <pc_ambig_branch>	=>	<id>	<pc_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_branch>"]:
            self.id_()
            self.pc_ambig_tail()

            """    679 <pc_ambig_branch>	=>	<ret_piece>	<pc_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_branch>_1"]:
            self.ret_piece()
            self.pc_piece_tail()

            """    680 <pc_ambig_branch>	=>	<ret_chars>	<pc_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_branch>_2"]:
            self.ret_chars()
            self.pc_chars_tail()

            """    681 <pc_ambig_branch>	=>	(	<pc_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_branch>_3"]:
            self.parse_token("(")
            self.pc_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_piece_tail(self):
        self.appendF(FIRST_SET["<pc_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    670 <pc_piece_tail>	=>	<strict_piece_mult_tail>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_piece_tail>"]:
            self.strict_piece_mult_tail()
            self.strict_piece_add_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_chars_tail(self):
        self.appendF(FIRST_SET["<pc_chars_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    671 <pc_chars_tail>	=>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_chars_tail>"]:
            self.strict_chars_add_tail()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_paren_dispatch(self):
        self.appendF(FIRST_SET["<pc_paren_dispatch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    682 <pc_paren_dispatch>	=>	<id>	<pc_paren_ambig_tail_inner>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_paren_dispatch>"]:
            self.id_()
            self.pc_paren_ambig_tail_inner()

            """    683 <pc_paren_dispatch>	=>	<ret_piece>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_dispatch>_1"]:
            self.ret_piece()
            self.pc_paren_piece_tail_inner()

            """    684 <pc_paren_dispatch>	=>	<ret_chars>	<pc_paren_chars_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_dispatch>_2"]:
            self.ret_chars()
            self.pc_paren_chars_tail_inner()

            """    685 <pc_paren_dispatch>	=>	(	<pc_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_dispatch>_3"]:
            self.parse_token("(")
            self.pc_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_paren_ambig_tail_inner(self):
        self.appendF(FIRST_SET["<pc_paren_ambig_tail_inner>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    694 <pc_paren_ambig_tail_inner>	=>	+	<pc_paren_ambig_branch>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>"]:
            self.parse_token("+")
            self.pc_paren_ambig_branch()

            """    695 <pc_paren_ambig_tail_inner>	=>	-	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    696 <pc_paren_ambig_tail_inner>	=>	*	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    697 <pc_paren_ambig_tail_inner>	=>	/	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    698 <pc_paren_ambig_tail_inner>	=>	%	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    699 <pc_paren_ambig_tail_inner>	=>	)	<pc_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_tail_inner>_5"]:
            self.parse_token(")")
            self.pc_ambig_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_paren_ambig_branch(self):
        self.appendF(FIRST_SET["<pc_paren_ambig_branch>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    700 <pc_paren_ambig_branch>	=>	<id>	<pc_paren_ambig_tail_inner>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_branch>"]:
            self.id_()
            self.pc_paren_ambig_tail_inner()

            """    701 <pc_paren_ambig_branch>	=>	<ret_piece>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_branch>_1"]:
            self.ret_piece()
            self.pc_paren_piece_tail_inner()

            """    702 <pc_paren_ambig_branch>	=>	<ret_chars>	<pc_paren_chars_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_branch>_2"]:
            self.ret_chars()
            self.pc_paren_chars_tail_inner()

            """    703 <pc_paren_ambig_branch>	=>	(	<pc_paren_dispatch>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_ambig_branch>_3"]:
            self.parse_token("(")
            self.pc_paren_dispatch()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_paren_piece_tail_inner(self):
        self.appendF(FIRST_SET["<pc_paren_piece_tail_inner>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    686 <pc_paren_piece_tail_inner>	=>	+	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>"]:
            self.parse_token("+")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    687 <pc_paren_piece_tail_inner>	=>	-	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>_1"]:
            self.parse_token("-")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    688 <pc_paren_piece_tail_inner>	=>	*	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>_2"]:
            self.parse_token("*")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    689 <pc_paren_piece_tail_inner>	=>	/	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>_3"]:
            self.parse_token("/")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    690 <pc_paren_piece_tail_inner>	=>	%	<strict_piece_factor>	<pc_paren_piece_tail_inner>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>_4"]:
            self.parse_token("%")
            self.strict_piece_factor()
            self.pc_paren_piece_tail_inner()

            """    691 <pc_paren_piece_tail_inner>	=>	)	<pc_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_piece_tail_inner>_5"]:
            self.parse_token(")")
            self.pc_piece_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def pc_paren_chars_tail_inner(self):
        self.appendF(FIRST_SET["<pc_paren_chars_tail_inner>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    692 <pc_paren_chars_tail_inner>	=>	+	<strict_chars_factor>	<pc_paren_chars_tail_inner>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_paren_chars_tail_inner>"]:
            self.parse_token("+")
            self.strict_chars_factor()
            self.pc_paren_chars_tail_inner()

            """    693 <pc_paren_chars_tail_inner>	=>	)	<pc_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_paren_chars_tail_inner>_1"]:
            self.parse_token(")")
            self.pc_chars_tail()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_platter(self):
        self.appendF(FIRST_SET["<menu_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    593 <menu_platter>	=>	{	<choice_clause>	<usual_clause>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_platter>"]:
            self.parse_token("{")
            self.choice_clause()
            self.usual_clause()
            self.parse_token("}")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause(self):
        self.appendF(FIRST_SET["<choice_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    594 <choice_clause>	=>	choice	<choice_val>	:	<statements_menu>	<choice_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.statements_menu()
            self.choice_clause()

            """    595 <choice_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_val(self):
        self.appendF(FIRST_SET["<choice_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    596 <choice_val>	=>	piece_lit    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_val>"]:
            self.parse_token("piece_lit")

            """    597 <choice_val>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_val>_1"]:
            self.parse_token("chars_lit")

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements_menu(self):
        self.appendF(FIRST_SET["<statements_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    598 <statements_menu>	=>	<id_statements_menu>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_menu>"]:
            self.id_statements_menu()
            self.statements_menu()

            """    599 <statements_menu>	=>	<built_in_rec_call>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_menu()

            """    600 <statements_menu>	=>	<conditional_st_menu>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_2"]:
            self.conditional_st_menu()
            self.statements_menu()

            """    601 <statements_menu>	=>	<looping_st>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_3"]:
            self.looping_st()
            self.statements_menu()

            """    602 <statements_menu>	=>	<jump_stop>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_4"]:
            self.jump_stop()
            self.statements_menu()

            """    603 <statements_menu>	=>	<jump_serve>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_5"]:
            self.jump_serve()
            self.statements_menu()

            """    604 <statements_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_6"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_menu(self):
        self.appendF(FIRST_SET["<id_statements_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    605 <id_statements_menu>	=>	id	<id_statements_ext>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_menu>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_menu()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_menu(self):
        self.appendF(FIRST_SET["<conditional_st_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    606 <conditional_st_menu>	=>	<cond_check_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>"]:
            self.cond_check_menu()

            """    607 <conditional_st_menu>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>_1"]:
            self.cond_menu()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_menu(self):
        self.appendF(FIRST_SET["<cond_check_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    608 <cond_check_menu>	=>	check	(	<strict_flag_expr>	)	<menu_check_platter>	<alt_clause>	<instead_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_menu>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.menu_check_platter()
            self.alt_clause()
            self.instead_clause()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_check_platter(self):
        self.appendF(FIRST_SET["<menu_check_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    609 <menu_check_platter>	=>	{	<local_decl_menu>	<statements_menu>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_check_platter>"]:
            self.parse_token("{")
            self.local_decl_menu()
            self.statements_menu()
            self.parse_token("}")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_menu(self):
        self.appendF(FIRST_SET["<local_decl_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    610 <local_decl_menu>	=>	piece	<piece_decl>	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_menu()

            """    611 <local_decl_menu>	=>	chars	<chars_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_menu()

            """    612 <local_decl_menu>	=>	sip	<sip_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_menu()

            """    613 <local_decl_menu>	=>	flag	<flag_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_menu()

            """    614 <local_decl_menu>	=>	id	<local_id_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_4"]:
            self.parse_token("id")
            self.local_id_tail_menu()

            """    615 <local_decl_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_menu(self):
        self.appendF(FIRST_SET["<local_id_tail_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    616 <local_id_tail_menu>	=>	of	<table_declare>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_menu()

            """    617 <local_id_tail_menu>	=>	[	<endsb_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_1"]:
            self.parse_token("[")
            self.endsb_tail_menu()

            """    618 <local_id_tail_menu>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()

            """    619 <local_id_tail_menu>	=>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()

            """    620 <local_id_tail_menu>	=>	<tail1>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_menu()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endsb_tail_menu(self):
        self.appendF(FIRST_SET["<endsb_tail_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    621 <endsb_tail_menu>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_menu>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.parse_token("id")
            self.table_array_init()
            self.parse_token(";")
            self.local_decl_menu()

            """    622 <endsb_tail_menu>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_menu>_1"]:
            self.array_accessor_val()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_menu()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def looping_st(self):
        self.appendF(FIRST_SET["<looping_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    623 <looping_st>	=>	<loop_pass>    """
        if self.tokens[self.pos].type in PREDICT_SET["<looping_st>"]:
            self.loop_pass()

            """    624 <looping_st>	=>	<loop_repeat>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_1"]:
            self.loop_repeat()

            """    625 <looping_st>	=>	<loop_order>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_2"]:
            self.loop_order()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_pass(self):
        self.appendF(FIRST_SET["<loop_pass>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    626 <loop_pass>	=>	pass	(	<initialization>	<update>	<strict_flag_expr>	)	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_pass>"]:
            self.parse_token("pass")
            self.parse_token("(")
            self.initialization()
            self.update()
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def initialization(self):
        self.appendF(FIRST_SET["<initialization>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    627 <initialization>	=>	id	<loop_init>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<initialization>"]:
            self.parse_token("id")
            self.loop_init()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_init(self):
        self.appendF(FIRST_SET["<loop_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    628 <loop_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_init>"]:
            self.parse_token("=")
            self.strict_piece_expr()

            """    629 <loop_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<loop_init>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def update(self):
        self.appendF(FIRST_SET["<update>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    630 <update>	=>	id	<accessor_tail>	<assignment_op>	<strict_piece_expr>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<update>"]:
            self.parse_token("id")
            self.accessor_tail()
            self.assignment_op()
            self.strict_piece_expr()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_platter(self):
        self.appendF(FIRST_SET["<loop_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    631 <loop_platter>	=>	{	<local_decl_loop>	<statements_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_platter>"]:
            self.parse_token("{")
            self.local_decl_loop()
            self.statements_loop()
            self.parse_token("}")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_decl_loop(self):
        self.appendF(FIRST_SET["<local_decl_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    632 <local_decl_loop>	=>	piece	<piece_decl>	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>"]:
            self.parse_token("piece")
            self.piece_decl()
            self.local_decl_loop()

            """    633 <local_decl_loop>	=>	chars	<chars_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_1"]:
            self.parse_token("chars")
            self.chars_decl()
            self.local_decl_loop()

            """    634 <local_decl_loop>	=>	sip	<sip_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_2"]:
            self.parse_token("sip")
            self.sip_decl()
            self.local_decl_loop()

            """    635 <local_decl_loop>	=>	flag	<flag_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_3"]:
            self.parse_token("flag")
            self.flag_decl()
            self.local_decl_loop()

            """    636 <local_decl_loop>	=>	id	<local_id_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_4"]:
            self.parse_token("id")
            self.local_id_tail_loop()

            """    637 <local_decl_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def local_id_tail_loop(self):
        self.appendF(FIRST_SET["<local_id_tail_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    638 <local_id_tail_loop>	=>	of	<table_declare>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>"]:
            self.parse_token("of")
            self.table_declare()
            self.parse_token(";")
            self.local_decl_loop()

            """    639 <local_id_tail_loop>	=>	[	<endsb_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_1"]:
            self.parse_token("[")
            self.endsb_tail_loop()

            """    640 <local_id_tail_loop>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_2"]:
            self.table_accessor()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()

            """    641 <local_id_tail_loop>	=>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_3"]:
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()

            """    642 <local_id_tail_loop>	=>	<tail1>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_4"]:
            self.tail1()
            self.parse_token(";")
            self.statements_loop()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def endsb_tail_loop(self):
        self.appendF(FIRST_SET["<endsb_tail_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    643 <endsb_tail_loop>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_loop>"]:
            self.parse_token("]")
            self.dimensions_tail()
            self.parse_token("of")
            self.parse_token("id")
            self.table_array_init()
            self.parse_token(";")
            self.local_decl_loop()

            """    644 <endsb_tail_loop>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_loop>_1"]:
            self.array_accessor_val()
            self.assignment_op()
            self.value()
            self.parse_token(";")
            self.statements_loop()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def statements_loop(self):
        self.appendF(FIRST_SET["<statements_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    645 <statements_loop>	=>	<id_statements_loop>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_loop>"]:
            self.id_statements_loop()
            self.statements_loop()

            """    646 <statements_loop>	=>	<built_in_rec_call>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.statements_loop()

            """    647 <statements_loop>	=>	<conditional_st_loop>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_2"]:
            self.conditional_st_loop()
            self.statements_loop()

            """    648 <statements_loop>	=>	<looping_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_3"]:
            self.looping_st()
            self.statements_loop()

            """    649 <statements_loop>	=>	<jump_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_4"]:
            self.jump_st()
            self.statements_loop()

            """    650 <statements_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_loop(self):
        self.appendF(FIRST_SET["<id_statements_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    651 <id_statements_loop>	=>	id	<id_statements_ext>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_loop>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.statements_loop()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def conditional_st_loop(self):
        self.appendF(FIRST_SET["<conditional_st_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    652 <conditional_st_loop>	=>	<cond_check_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>"]:
            self.cond_check_loop()

            """    653 <conditional_st_loop>	=>	<cond_menu_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>_1"]:
            self.cond_menu_loop()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_check_loop(self):
        self.appendF(FIRST_SET["<cond_check_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    654 <cond_check_loop>	=>	check	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>	<instead_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_loop>"]:
            self.parse_token("check")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
            self.alt_clause_loop()
            self.instead_clause_loop()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def alt_clause_loop(self):
        self.appendF(FIRST_SET["<alt_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    655 <alt_clause_loop>	=>	alt	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>"]:
            self.parse_token("alt")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
            self.alt_clause_loop()

            """    656 <alt_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def instead_clause_loop(self):
        self.appendF(FIRST_SET["<instead_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    657 <instead_clause_loop>	=>	instead	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>"]:
            self.parse_token("instead")
            self.loop_platter()

            """    658 <instead_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def cond_menu_loop(self):
        self.appendF(FIRST_SET["<cond_menu_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    659 <cond_menu_loop>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu_loop>"]:
            self.parse_token("menu")
            self.parse_token("(")
            self.strict_piece_chars_expr()
            self.parse_token(")")
            self.menu_loop_platter()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def menu_loop_platter(self):
        self.appendF(FIRST_SET["<menu_loop_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    660 <menu_loop_platter>	=>	{	<choice_clause_loop>	<usual_clause_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_loop_platter>"]:
            self.parse_token("{")
            self.choice_clause_loop()
            self.usual_clause_loop()
            self.parse_token("}")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_clause_loop(self):
        self.appendF(FIRST_SET["<choice_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    661 <choice_clause_loop>	=>	choice	<choice_val>	:	<choice_usual_loop_st>	<choice_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>"]:
            self.parse_token("choice")
            self.choice_val()
            self.parse_token(":")
            self.choice_usual_loop_st()
            self.choice_clause_loop()

            """    662 <choice_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def choice_usual_loop_st(self):
        self.appendF(FIRST_SET["<choice_usual_loop_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    663 <choice_usual_loop_st>	=>	<id_statements_choice_usual_loop>	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>"]:
            self.id_statements_choice_usual_loop()
            self.choice_usual_loop_st()

            """    664 <choice_usual_loop_st>	=>	<built_in_rec_call>	;	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_1"]:
            self.built_in_rec_call()
            self.parse_token(";")
            self.choice_usual_loop_st()

            """    665 <choice_usual_loop_st>	=>	<conditional_st_loop>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_2"]:
            self.conditional_st_loop()
            self.choice_usual_loop_st()

            """    666 <choice_usual_loop_st>	=>	<looping_st>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_3"]:
            self.looping_st()
            self.choice_usual_loop_st()

            """    667 <choice_usual_loop_st>	=>	<jump_st>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_4"]:
            self.jump_st()
            self.choice_usual_loop_st()

            """    668 <choice_usual_loop_st>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_5"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def id_statements_choice_usual_loop(self):
        self.appendF(FIRST_SET["<id_statements_choice_usual_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    669 <id_statements_choice_usual_loop>	=>	id	<id_statements_ext>	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_choice_usual_loop>"]:
            self.parse_token("id")
            self.id_statements_ext()
            self.choice_usual_loop_st()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_st(self):
        self.appendF(FIRST_SET["<jump_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    670 <jump_st>	=>	<jump_next>    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_st>"]:
            self.jump_next()

            """    671 <jump_st>	=>	<jump_stop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_1"]:
            self.jump_stop()

            """    672 <jump_st>	=>	<jump_serve>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_2"]:
            self.jump_serve()

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_next(self):
        self.appendF(FIRST_SET["<jump_next>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    673 <jump_next>	=>	next	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_next>"]:
            self.parse_token("next")
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_stop(self):
        self.appendF(FIRST_SET["<jump_stop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    674 <jump_stop>	=>	stop	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_stop>"]:
            self.parse_token("stop")
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def jump_serve(self):
        self.appendF(FIRST_SET["<jump_serve>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    675 <jump_serve>	=>	serve	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_serve>"]:
            self.parse_token("serve")
            self.value()
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def usual_clause_loop(self):
        self.appendF(FIRST_SET["<usual_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    676 <usual_clause_loop>	=>	usual	:	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.choice_usual_loop_st()

            """    677 <usual_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_repeat(self):
        self.appendF(FIRST_SET["<loop_repeat>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    678 <loop_repeat>	=>	repeat	(	<strict_flag_expr>	)	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_repeat>"]:
            self.parse_token("repeat")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.loop_platter()
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def loop_order(self):
        self.appendF(FIRST_SET["<loop_order>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    679 <loop_order>	=>	order	<loop_platter>	repeat	(	<strict_flag_expr>	)	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_order>"]:
            self.parse_token("order")
            self.loop_platter()
            self.parse_token("repeat")
            self.parse_token("(")
            self.strict_flag_expr()
            self.parse_token(")")
            self.parse_token(";")
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type) # J

    def usual_clause(self):
        self.appendF(FIRST_SET["<usual_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    680 <usual_clause>	=>	usual	:	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause>"]:
            self.parse_token("usual")
            self.parse_token(":")
            self.statements_menu()

            """    681 <usual_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause>_1"]:
            pass


        log.info("Exit: " + self.tokens[self.pos].type) # J
