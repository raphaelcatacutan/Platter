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

def piece_id_tail(self):
    self.appendF(FIRST_SET["<piece_id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    14 <piece_id_tail>	=>	,	id	<piece_ingredient_init>	<piece_id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.piece_ingredient_init()
        self.piece_id_tail()

        """    15 <piece_id_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_decl(self):
    self.appendF(FIRST_SET["<chars_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    16 <chars_decl>	=>	of	<chars_id>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_decl>"]:
        self.parse_token("of")
        self.chars_id()
        self.parse_token(";")

        """    17 <chars_decl>	=>	<chars_array_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_decl>_1"]:
        self.chars_array_decl()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_id(self):
    self.appendF(FIRST_SET["<chars_id>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    18 <chars_id>	=>	id	<chars_ingredient_init>	<chars_id_tail>    """
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

    """    19 <chars_ingredient_init>	=>	=	<strict_chars_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>"]:
        self.parse_token("=")
        self.strict_chars_expr()

        """    20 <chars_ingredient_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_id_tail(self):
    self.appendF(FIRST_SET["<chars_id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    21 <chars_id_tail>	=>	,	id	<chars_ingredient_init>	<chars_id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.chars_ingredient_init()
        self.chars_id_tail()

        """    22 <chars_id_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_decl(self):
    self.appendF(FIRST_SET["<sip_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    23 <sip_decl>	=>	of	<sip_id>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_decl>"]:
        self.parse_token("of")
        self.sip_id()
        self.parse_token(";")

        """    24 <sip_decl>	=>	<sip_array_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_decl>_1"]:
        self.sip_array_decl()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_id(self):
    self.appendF(FIRST_SET["<sip_id>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    25 <sip_id>	=>	id	<sip_ingredient_init>	<sip_id_tail>    """
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

    """    26 <sip_ingredient_init>	=>	=	<strict_sip_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>"]:
        self.parse_token("=")
        self.strict_sip_expr()

        """    27 <sip_ingredient_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_id_tail(self):
    self.appendF(FIRST_SET["<sip_id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    28 <sip_id_tail>	=>	,	id	<sip_ingredient_init>	<sip_id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.sip_ingredient_init()
        self.sip_id_tail()

        """    29 <sip_id_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_decl(self):
    self.appendF(FIRST_SET["<flag_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    30 <flag_decl>	=>	of	<flag_id>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_decl>"]:
        self.parse_token("of")
        self.flag_id()
        self.parse_token(";")

        """    31 <flag_decl>	=>	<flag_array_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_decl>_1"]:
        self.flag_array_decl()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_id(self):
    self.appendF(FIRST_SET["<flag_id>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    32 <flag_id>	=>	id	<flag_ingredient_init>	<flag_id_tail>    """
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

    """    33 <flag_ingredient_init>	=>	=	<strict_flag_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>"]:
        self.parse_token("=")
        self.strict_flag_expr()

        """    34 <flag_ingredient_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_id_tail(self):
    self.appendF(FIRST_SET["<flag_id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    35 <flag_id_tail>	=>	,	id	<flag_ingredient_init>	<flag_id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.flag_ingredient_init()
        self.flag_id_tail()

        """    36 <flag_id_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def piece_array_decl(self):
    self.appendF(FIRST_SET["<piece_array_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    37 <piece_array_decl>	=>	<dimensions>	of	id	<piece_array_init>	<array_declare_tail_piece>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<piece_array_decl>"]:
        self.dimensions()
        self.parse_token("of")
        self.parse_token("id")
        self.piece_array_init()
        self.array_declare_tail_piece()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_array_decl(self):
    self.appendF(FIRST_SET["<sip_array_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    38 <sip_array_decl>	=>	<dimensions>	of	id	<sip_array_init>	<array_declare_tail_sip>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_array_decl>"]:
        self.dimensions()
        self.parse_token("of")
        self.parse_token("id")
        self.sip_array_init()
        self.array_declare_tail_sip()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_array_decl(self):
    self.appendF(FIRST_SET["<chars_array_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    39 <chars_array_decl>	=>	<dimensions>	of	id	<chars_array_init>	<array_declare_tail_chars>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_array_decl>"]:
        self.dimensions()
        self.parse_token("of")
        self.parse_token("id")
        self.chars_array_init()
        self.array_declare_tail_chars()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_array_decl(self):
    self.appendF(FIRST_SET["<flag_array_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    40 <flag_array_decl>	=>	<dimensions>	of	id	<flag_array_init>	<array_declare_tail_flag>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_array_decl>"]:
        self.dimensions()
        self.parse_token("of")
        self.parse_token("id")
        self.flag_array_init()
        self.array_declare_tail_flag()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_array_decl(self):
    self.appendF(FIRST_SET["<table_array_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    41 <table_array_decl>	=>	<dimensions>	of	id	<table_array_init>	<array_declare_tail_table>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_array_decl>"]:
        self.dimensions()
        self.parse_token("of")
        self.parse_token("id")
        self.table_array_init()
        self.array_declare_tail_table()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def piece_array_val(self):
    self.appendF(FIRST_SET["<piece_array_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    42 <piece_array_val>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>"]:
        self.parse_token("id")
        self.id_tail()

        """    43 <piece_array_val>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_1"]:
        self.ret_array()

        """    44 <piece_array_val>	=>	[	<array_element_piece_opt>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_2"]:
        self.parse_token("[")
        self.array_element_piece_opt()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def piece_array_init(self):
    self.appendF(FIRST_SET["<piece_array_init>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    45 <piece_array_init>	=>	=	<piece_array_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>"]:
        self.parse_token("=")
        self.piece_array_val()

        """    46 <piece_array_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_array_val(self):
    self.appendF(FIRST_SET["<sip_array_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    47 <sip_array_val>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>"]:
        self.parse_token("id")
        self.id_tail()

        """    48 <sip_array_val>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_1"]:
        self.ret_array()

        """    49 <sip_array_val>	=>	[	<array_element_sip_opt>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_2"]:
        self.parse_token("[")
        self.array_element_sip_opt()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def sip_array_init(self):
    self.appendF(FIRST_SET["<sip_array_init>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    50 <sip_array_init>	=>	=	<sip_array_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>"]:
        self.parse_token("=")
        self.sip_array_val()

        """    51 <sip_array_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_array_val(self):
    self.appendF(FIRST_SET["<chars_array_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    52 <chars_array_val>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>"]:
        self.parse_token("id")
        self.id_tail()

        """    53 <chars_array_val>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_1"]:
        self.ret_array()

        """    54 <chars_array_val>	=>	[	<array_element_chars_opt>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_2"]:
        self.parse_token("[")
        self.array_element_chars_opt()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def chars_array_init(self):
    self.appendF(FIRST_SET["<chars_array_init>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    55 <chars_array_init>	=>	=	<chars_array_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>"]:
        self.parse_token("=")
        self.chars_array_val()

        """    56 <chars_array_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_array_val(self):
    self.appendF(FIRST_SET["<flag_array_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    57 <flag_array_val>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>"]:
        self.parse_token("id")
        self.id_tail()

        """    58 <flag_array_val>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_1"]:
        self.ret_array()

        """    59 <flag_array_val>	=>	[	<array_element_flag_opt>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_2"]:
        self.parse_token("[")
        self.array_element_flag_opt()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def flag_array_init(self):
    self.appendF(FIRST_SET["<flag_array_init>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    60 <flag_array_init>	=>	=	<flag_array_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>"]:
        self.parse_token("=")
        self.flag_array_val()

        """    61 <flag_array_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_array_val(self):
    self.appendF(FIRST_SET["<table_array_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    62 <table_array_val>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_array_val>"]:
        self.parse_token("id")
        self.id_tail()

        """    63 <table_array_val>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_1"]:
        self.ret_array()

        """    64 <table_array_val>	=>	[	<array_element_table_opt>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_2"]:
        self.parse_token("[")
        self.array_element_table_opt()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_array_init(self):
    self.appendF(FIRST_SET["<table_array_init>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    65 <table_array_init>	=>	=	<table_array_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_array_init>"]:
        self.parse_token("=")
        self.table_array_val()

        """    66 <table_array_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_array_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_declare_tail_piece(self):
    self.appendF(FIRST_SET["<array_declare_tail_piece>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    67 <array_declare_tail_piece>	=>	,	id	<piece_array_init>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_piece>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.piece_array_init()

        """    68 <array_declare_tail_piece>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_piece>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_declare_tail_sip(self):
    self.appendF(FIRST_SET["<array_declare_tail_sip>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    69 <array_declare_tail_sip>	=>	,	id	<sip_array_init>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_sip>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.sip_array_init()

        """    70 <array_declare_tail_sip>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_sip>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_declare_tail_flag(self):
    self.appendF(FIRST_SET["<array_declare_tail_flag>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    71 <array_declare_tail_flag>	=>	,	id	<flag_array_init>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_flag>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.flag_array_init()

        """    72 <array_declare_tail_flag>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_flag>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_declare_tail_chars(self):
    self.appendF(FIRST_SET["<array_declare_tail_chars>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    73 <array_declare_tail_chars>	=>	,	id	<chars_array_init>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_chars>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.chars_array_init()

        """    74 <array_declare_tail_chars>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_chars>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_declare_tail_table(self):
    self.appendF(FIRST_SET["<array_declare_tail_table>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    75 <array_declare_tail_table>	=>	,	id	<table_array_init>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_table>"]:
        self.parse_token(",")
        self.parse_token("id")
        self.table_array_init()

        """    76 <array_declare_tail_table>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_table>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def dimensions(self):
    self.appendF(FIRST_SET["<dimensions>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    77 <dimensions>	=>	[	]	<dimensions_tail>    """
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

    """    78 <dimensions_tail>	=>	<dimensions>    """
    if self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>"]:
        self.dimensions()

        """    79 <dimensions_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def flavor(self):
    self.appendF(FIRST_SET["<flavor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    80 <flavor>	=>	<value>	<flavor_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flavor>"]:
        self.value()
        self.flavor_tail()

        """    81 <flavor>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flavor>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def value(self):
    self.appendF(FIRST_SET["<value>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    82 <value>	=>	<any_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<value>"]:
        self.any_expr()

        """    83 <value>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<value>_1"]:
        self.ret_array()

        """    84 <value>	=>	[	<notation_val>	]    """
    elif self.tokens[self.pos].type in PREDICT_SET["<value>_2"]:
        self.parse_token("[")
        self.notation_val()
        self.parse_token("]")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def notation_val(self):
    self.appendF(FIRST_SET["<notation_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    85 <notation_val>	=>	<array_element>    """
    if self.tokens[self.pos].type in PREDICT_SET["<notation_val>"]:
        self.array_element()

        """    86 <notation_val>	=>	id	<array_or_table>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_1"]:
        self.parse_token("id")
        self.array_or_table()

        """    87 <notation_val>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element(self):
    self.appendF(FIRST_SET["<array_element>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    88 <array_element>	=>	piece_lit	<element_value_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element>"]:
        self.parse_token("piece_lit")
        self.element_value_tail()

        """    89 <array_element>	=>	sip_lit	<element_value_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_1"]:
        self.parse_token("sip_lit")
        self.element_value_tail()

        """    90 <array_element>	=>	flag_lit	<element_value_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_2"]:
        self.parse_token("flag_lit")
        self.element_value_tail()

        """    91 <array_element>	=>	chars_lit	<element_value_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_3"]:
        self.parse_token("chars_lit")
        self.element_value_tail()

        """    92 <array_element>	=>	[	<notation_val>	]	<element_value_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_4"]:
        self.parse_token("[")
        self.notation_val()
        self.parse_token("]")
        self.element_value_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_value_tail(self):
    self.appendF(FIRST_SET["<element_value_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    93 <element_value_tail>	=>	,	<array_element_id>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>"]:
        self.parse_token(",")
        self.array_element_id()

        """    94 <element_value_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_id(self):
    self.appendF(FIRST_SET["<array_element_id>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    95 <array_element_id>	=>	id	<element_value_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_id>"]:
        self.parse_token("id")
        self.element_value_tail()

        """    96 <array_element_id>	=>	<array_element>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_1"]:
        self.array_element()

        """    97 <array_element_id>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_piece(self):
    self.appendF(FIRST_SET["<array_element_piece>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    98 <array_element_piece>	=>	id	<element_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>"]:
        self.parse_token("id")
        self.element_piece_tail()

        """    99 <array_element_piece>	=>	piece_lit	<element_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_1"]:
        self.parse_token("piece_lit")
        self.element_piece_tail()

        """    100 <array_element_piece>	=>	[	<array_element_piece>	]	<element_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_2"]:
        self.parse_token("[")
        self.array_element_piece()
        self.parse_token("]")
        self.element_piece_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_piece_opt(self):
    self.appendF(FIRST_SET["<array_element_piece_opt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    101 <array_element_piece_opt>	=>	<array_element_piece>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>"]:
        self.array_element_piece()

        """    102 <array_element_piece_opt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_piece_tail(self):
    self.appendF(FIRST_SET["<element_piece_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    103 <element_piece_tail>	=>	,	<array_element_piece>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_piece_tail>"]:
        self.parse_token(",")
        self.array_element_piece()

        """    104 <element_piece_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_piece_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_sip(self):
    self.appendF(FIRST_SET["<array_element_sip>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    105 <array_element_sip>	=>	id	<element_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>"]:
        self.parse_token("id")
        self.element_sip_tail()

        """    106 <array_element_sip>	=>	sip_lit	<element_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_1"]:
        self.parse_token("sip_lit")
        self.element_sip_tail()

        """    107 <array_element_sip>	=>	[	<array_element_sip_opt>	]	<element_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_2"]:
        self.parse_token("[")
        self.array_element_sip_opt()
        self.parse_token("]")
        self.element_sip_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_sip_opt(self):
    self.appendF(FIRST_SET["<array_element_sip_opt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    108 <array_element_sip_opt>	=>	<array_element_sip>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>"]:
        self.array_element_sip()

        """    109 <array_element_sip_opt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_sip_tail(self):
    self.appendF(FIRST_SET["<element_sip_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    110 <element_sip_tail>	=>	,	<array_element_sip>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_sip_tail>"]:
        self.parse_token(",")
        self.array_element_sip()

        """    111 <element_sip_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_sip_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_chars(self):
    self.appendF(FIRST_SET["<array_element_chars>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    112 <array_element_chars>	=>	id	<element_chars_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>"]:
        self.parse_token("id")
        self.element_chars_tail()

        """    113 <array_element_chars>	=>	chars_lit	<element_chars_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_1"]:
        self.parse_token("chars_lit")
        self.element_chars_tail()

        """    114 <array_element_chars>	=>	[	<array_element_chars_opt>	]	<element_chars_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_2"]:
        self.parse_token("[")
        self.array_element_chars_opt()
        self.parse_token("]")
        self.element_chars_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_chars_opt(self):
    self.appendF(FIRST_SET["<array_element_chars_opt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    115 <array_element_chars_opt>	=>	<array_element_chars>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>"]:
        self.array_element_chars()

        """    116 <array_element_chars_opt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_chars_tail(self):
    self.appendF(FIRST_SET["<element_chars_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    117 <element_chars_tail>	=>	,	<array_element_chars>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_chars_tail>"]:
        self.parse_token(",")
        self.array_element_chars()

        """    118 <element_chars_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_chars_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_flag(self):
    self.appendF(FIRST_SET["<array_element_flag>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    119 <array_element_flag>	=>	id	<element_flag_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>"]:
        self.parse_token("id")
        self.element_flag_tail()

        """    120 <array_element_flag>	=>	flag_lit	<element_flag_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_1"]:
        self.parse_token("flag_lit")
        self.element_flag_tail()

        """    121 <array_element_flag>	=>	[	<array_element_flag_opt>	]	<element_flag_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_2"]:
        self.parse_token("[")
        self.array_element_flag_opt()
        self.parse_token("]")
        self.element_flag_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_flag_opt(self):
    self.appendF(FIRST_SET["<array_element_flag_opt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    122 <array_element_flag_opt>	=>	<array_element_flag>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>"]:
        self.array_element_flag()

        """    123 <array_element_flag_opt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_flag_tail(self):
    self.appendF(FIRST_SET["<element_flag_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    124 <element_flag_tail>	=>	,	<array_element_id>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_flag_tail>"]:
        self.parse_token(",")
        self.array_element_id()

        """    125 <element_flag_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_flag_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_table(self):
    self.appendF(FIRST_SET["<array_element_table>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    126 <array_element_table>	=>	<strict_table_expr>	<element_table_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_table>"]:
        self.strict_table_expr()
        self.element_table_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_element_table_opt(self):
    self.appendF(FIRST_SET["<array_element_table_opt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    127 <array_element_table_opt>	=>	<array_element_table>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>"]:
        self.array_element_table()

        """    128 <array_element_table_opt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def element_table_tail(self):
    self.appendF(FIRST_SET["<element_table_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    129 <element_table_tail>	=>	,	<array_element_table>    """
    if self.tokens[self.pos].type in PREDICT_SET["<element_table_tail>"]:
        self.parse_token(",")
        self.array_element_table()

        """    130 <element_table_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<element_table_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_or_table(self):
    self.appendF(FIRST_SET["<array_or_table>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    131 <array_or_table>	=>	,	<array_element_id>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_or_table>"]:
        self.parse_token(",")
        self.array_element_id()

        """    132 <array_or_table>	=>	=	<value>	;	<field_assignments>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_1"]:
        self.parse_token("=")
        self.value()
        self.parse_token(";")
        self.field_assignments()

        """    133 <array_or_table>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def field_assignments(self):
    self.appendF(FIRST_SET["<field_assignments>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    134 <field_assignments>	=>	id	=	<value>	;	<field_assignments>    """
    if self.tokens[self.pos].type in PREDICT_SET["<field_assignments>"]:
        self.parse_token("id")
        self.parse_token("=")
        self.value()
        self.parse_token(";")
        self.field_assignments()

        """    135 <field_assignments>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<field_assignments>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def flavor_tail(self):
    self.appendF(FIRST_SET["<flavor_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    136 <flavor_tail>	=>	,	<value>	<flavor_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>"]:
        self.parse_token(",")
        self.value()
        self.flavor_tail()

        """    137 <flavor_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def accessor_tail(self):
    self.appendF(FIRST_SET["<accessor_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    138 <accessor_tail>	=>	<array_accessor>    """
    if self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>"]:
        self.array_accessor()

        """    139 <accessor_tail>	=>	<table_accessor>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_1"]:
        self.table_accessor()

        """    140 <accessor_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_accessor(self):
    self.appendF(FIRST_SET["<array_accessor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    141 <array_accessor>	=>	[	<array_accessor_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_accessor>"]:
        self.parse_token("[")
        self.array_accessor_val()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def array_accessor_val(self):
    self.appendF(FIRST_SET["<array_accessor_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    142 <array_accessor_val>	=>	piece_lit	]	<accessor_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<array_accessor_val>"]:
        self.parse_token("piece_lit")
        self.parse_token("]")
        self.accessor_tail()

        """    143 <array_accessor_val>	=>	id	]	<accessor_tail>    """
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

    """    144 <table_accessor>	=>	:	id	<accessor_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_accessor>"]:
        self.parse_token(":")
        self.parse_token("id")
        self.accessor_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_prototype(self):
    self.appendF(FIRST_SET["<table_prototype>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    145 <table_prototype>	=>	table	of	id	=	[	<required_decl>	]	;    """
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

    """    146 <required_decl>	=>	<decl_head>	;	<required_decl_tail>    """
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

    """    147 <decl_head>	=>	<primitive_types_dims>	of	id    """
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

    """    148 <primitive_types_dims>	=>	piece	<dimensions_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>"]:
        self.parse_token("piece")
        self.dimensions_tail()

        """    149 <primitive_types_dims>	=>	sip	<dimensions_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_1"]:
        self.parse_token("sip")
        self.dimensions_tail()

        """    150 <primitive_types_dims>	=>	flag	<dimensions_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_2"]:
        self.parse_token("flag")
        self.dimensions_tail()

        """    151 <primitive_types_dims>	=>	chars	<dimensions_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_3"]:
        self.parse_token("chars")
        self.dimensions_tail()

        """    152 <primitive_types_dims>	=>	id	<dimensions_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_4"]:
        self.parse_token("id")
        self.dimensions_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def required_decl_tail(self):
    self.appendF(FIRST_SET["<required_decl_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    153 <required_decl_tail>	=>	<required_decl>    """
    if self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>"]:
        self.required_decl()

        """    154 <required_decl_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_decl(self):
    self.appendF(FIRST_SET["<table_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    155 <table_decl>	=>	of	<table_declare>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_decl>"]:
        self.parse_token("of")
        self.table_declare()
        self.parse_token(";")

        """    156 <table_decl>	=>	<table_array_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_decl>_1"]:
        self.table_array_decl()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_declare(self):
    self.appendF(FIRST_SET["<table_declare>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    157 <table_declare>	=>	id	<table_init>	<table_declare_tail>    """
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

    """    158 <table_init>	=>	=	<strict_table_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_init>"]:
        self.parse_token("=")
        self.strict_table_expr()

        """    159 <table_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_table_expr(self):
    self.appendF(FIRST_SET["<strict_table_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    160 <strict_table_expr>	=>	[	<field_assignments>	]    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>"]:
        self.parse_token("[")
        self.field_assignments()
        self.parse_token("]")

        """    161 <strict_table_expr>	=>	<id>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>_1"]:
        self.id_()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def table_declare_tail(self):
    self.appendF(FIRST_SET["<table_declare_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    162 <table_declare_tail>	=>	,	<table_declare>    """
    if self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>"]:
        self.parse_token(",")
        self.table_declare()

        """    163 <table_declare_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def recipe_decl(self):
    self.appendF(FIRST_SET["<recipe_decl>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    164 <recipe_decl>	=>	prepare	<serve_type>	(	<spice>	)	<platter>	<recipe_decl>    """
    if self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>"]:
        self.parse_token("prepare")
        self.serve_type()
        self.parse_token("(")
        self.spice()
        self.parse_token(")")
        self.platter()
        self.recipe_decl()

        """    165 <recipe_decl>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def serve_type(self):
    self.appendF(FIRST_SET["<serve_type>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    166 <serve_type>	=>	<decl_head>    """
    if self.tokens[self.pos].type in PREDICT_SET["<serve_type>"]:
        self.decl_head()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def spice(self):
    self.appendF(FIRST_SET["<spice>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    167 <spice>	=>	<decl_head>	<spice_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<spice>"]:
        self.decl_head()
        self.spice_tail()

        """    168 <spice>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<spice>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def spice_tail(self):
    self.appendF(FIRST_SET["<spice_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    169 <spice_tail>	=>	,	<decl_head>	<spice_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<spice_tail>"]:
        self.parse_token(",")
        self.decl_head()
        self.spice_tail()

        """    170 <spice_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<spice_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def platter(self):
    self.appendF(FIRST_SET["<platter>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    171 <platter>	=>	{	<local_decl>	<statements>	}    """
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

    """    172 <local_decl>	=>	piece	<piece_decl>	<local_decl>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_decl>"]:
        self.parse_token("piece")
        self.piece_decl()
        self.local_decl()

        """    173 <local_decl>	=>	chars	<chars_decl>	<local_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_1"]:
        self.parse_token("chars")
        self.chars_decl()
        self.local_decl()

        """    174 <local_decl>	=>	sip	<sip_decl>	<local_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_2"]:
        self.parse_token("sip")
        self.sip_decl()
        self.local_decl()

        """    175 <local_decl>	=>	flag	<flag_decl>	<local_decl>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_3"]:
        self.parse_token("flag")
        self.flag_decl()
        self.local_decl()

        """    176 <local_decl>	=>	id	<local_id_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_4"]:
        self.parse_token("id")
        self.local_id_tail()

        """    177 <local_decl>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def local_id_tail(self):
    self.appendF(FIRST_SET["<local_id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    178 <local_id_tail>	=>	of	<table_declare>	;	<local_decl>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>"]:
        self.parse_token("of")
        self.table_declare()
        self.parse_token(";")
        self.local_decl()

        """    179 <local_id_tail>	=>	[	<endsb_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_1"]:
        self.parse_token("[")
        self.endsb_tail()

        """    180 <local_id_tail>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_2"]:
        self.table_accessor()
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements()

        """    181 <local_id_tail>	=>	<assignment_op>	<value>	;	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_3"]:
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements()

        """    182 <local_id_tail>	=>	<tail1>	;	<statements>    """
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

    """    183 <endsb_tail>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl>    """
    if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail>"]:
        self.parse_token("]")
        self.dimensions_tail()
        self.parse_token("of")
        self.parse_token("id")
        self.table_array_init()
        self.parse_token(";")
        self.local_decl()

        """    184 <endsb_tail>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements>    """
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

    """    185 <assignment_op>	=>	=    """
    if self.tokens[self.pos].type in PREDICT_SET["<assignment_op>"]:
        self.parse_token("=")

        """    186 <assignment_op>	=>	+=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_1"]:
        self.parse_token("+=")

        """    187 <assignment_op>	=>	-=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_2"]:
        self.parse_token("-=")

        """    188 <assignment_op>	=>	*=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_3"]:
        self.parse_token("*=")

        """    189 <assignment_op>	=>	/=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_4"]:
        self.parse_token("/=")

        """    190 <assignment_op>	=>	%=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_5"]:
        self.parse_token("%=")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def statements(self):
    self.appendF(FIRST_SET["<statements>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    191 <statements>	=>	<id_statements>	<statements>    """
    if self.tokens[self.pos].type in PREDICT_SET["<statements>"]:
        self.id_statements()
        self.statements()

        """    192 <statements>	=>	<built_in_rec_call>	;	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements>_1"]:
        self.built_in_rec_call()
        self.parse_token(";")
        self.statements()

        """    193 <statements>	=>	<conditional_st>	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements>_2"]:
        self.conditional_st()
        self.statements()

        """    194 <statements>	=>	<looping_st>	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements>_3"]:
        self.looping_st()
        self.statements()

        """    195 <statements>	=>	<jump_serve>	<statements>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements>_4"]:
        self.jump_serve()
        self.statements()

        """    196 <statements>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_statements(self):
    self.appendF(FIRST_SET["<id_statements>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    197 <id_statements>	=>	id	<id_statements_ext>	<statements>    """
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

    """    198 <id_statements_ext>	=>	<tail1>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>"]:
        self.tail1()
        self.parse_token(";")

        """    199 <id_statements_ext>	=>	<assignment_st>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>_1"]:
        self.assignment_st()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def tail1(self):
    self.appendF(FIRST_SET["<tail1>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    200 <tail1>	=>	<call_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<tail1>"]:
        self.call_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def call_tail(self):
    self.appendF(FIRST_SET["<call_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    201 <call_tail>	=>	(	<flavor>	)    """
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

    """    202 <assignment_st>	=>	<accessor_tail>	<assignment_op>	<value>	;    """
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

    """    203 <built_in_rec_call>	=>	<built_in_rec>    """
    if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec_call>"]:
        self.built_in_rec()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def built_in_rec(self):
    self.appendF(FIRST_SET["<built_in_rec>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    204 <built_in_rec>	=>	append	(	<strict_array_expr>	,	<value>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>"]:
        self.parse_token("append")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.value()
        self.parse_token(")")

        """    205 <built_in_rec>	=>	bill	(	<strict_chars_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_1"]:
        self.parse_token("bill")
        self.parse_token("(")
        self.strict_chars_expr()
        self.parse_token(")")

        """    206 <built_in_rec>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_2"]:
        self.parse_token("copy")
        self.parse_token("(")
        self.strict_chars_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

        """    207 <built_in_rec>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_3"]:
        self.parse_token("cut")
        self.parse_token("(")
        self.strict_sip_expr()
        self.parse_token(",")
        self.strict_sip_expr()
        self.parse_token(")")

        """    208 <built_in_rec>	=>	fact	(	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_4"]:
        self.parse_token("fact")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(")")

        """    209 <built_in_rec>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_5"]:
        self.parse_token("matches")
        self.parse_token("(")
        self.strict_datas_expr()
        self.parse_token(",")
        self.strict_datas_expr()
        self.parse_token(")")

        """    210 <built_in_rec>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_6"]:
        self.parse_token("pow")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

        """    211 <built_in_rec>	=>	rand	(	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_7"]:
        self.parse_token("rand")
        self.parse_token("(")
        self.parse_token(")")

        """    212 <built_in_rec>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_8"]:
        self.parse_token("remove")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

        """    213 <built_in_rec>	=>	reverse	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_9"]:
        self.parse_token("reverse")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    214 <built_in_rec>	=>	search	(	<strict_array_expr>	,	<value>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_10"]:
        self.parse_token("search")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.value()
        self.parse_token(")")

        """    215 <built_in_rec>	=>	size	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_11"]:
        self.parse_token("size")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    216 <built_in_rec>	=>	sort	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_12"]:
        self.parse_token("sort")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    217 <built_in_rec>	=>	sqrt	(	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_13"]:
        self.parse_token("sqrt")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(")")

        """    218 <built_in_rec>	=>	take	(	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_14"]:
        self.parse_token("take")
        self.parse_token("(")
        self.parse_token(")")

        """    219 <built_in_rec>	=>	tochars	(	<any_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_15"]:
        self.parse_token("tochars")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    220 <built_in_rec>	=>	topiece	(	<any_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_16"]:
        self.parse_token("topiece")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    221 <built_in_rec>	=>	tosip	(	<any_expr>	)    """
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

    """    222 <conditional_st>	=>	<cond_check>    """
    if self.tokens[self.pos].type in PREDICT_SET["<conditional_st>"]:
        self.cond_check()

        """    223 <conditional_st>	=>	<cond_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st>_1"]:
        self.cond_menu()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def cond_check(self):
    self.appendF(FIRST_SET["<cond_check>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    224 <cond_check>	=>	check	(	<strict_flag_expr>	)	<platter>	<alt_clause>	<instead_clause>    """
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

    """    225 <alt_clause>	=>	alt	(	<strict_flag_expr>	)	<platter>	<alt_clause>    """
    if self.tokens[self.pos].type in PREDICT_SET["<alt_clause>"]:
        self.parse_token("alt")
        self.parse_token("(")
        self.strict_flag_expr()
        self.parse_token(")")
        self.platter()
        self.alt_clause()

        """    226 <alt_clause>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def instead_clause(self):
    self.appendF(FIRST_SET["<instead_clause>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    227 <instead_clause>	=>	instead	<platter>    """
    if self.tokens[self.pos].type in PREDICT_SET["<instead_clause>"]:
        self.parse_token("instead")
        self.platter()

        """    228 <instead_clause>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def cond_menu(self):
    self.appendF(FIRST_SET["<cond_menu>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    229 <cond_menu>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_platter>    """
    if self.tokens[self.pos].type in PREDICT_SET["<cond_menu>"]:
        self.parse_token("menu")
        self.parse_token("(")
        self.strict_piece_chars_expr()
        self.parse_token(")")
        self.menu_platter()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def menu_platter(self):
    self.appendF(FIRST_SET["<menu_platter>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    230 <menu_platter>	=>	{	<choice_clause>	<usual_clause>	}    """
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

    """    231 <choice_clause>	=>	choice	<choice_val>	:	<statements_menu>	<choice_clause>    """
    if self.tokens[self.pos].type in PREDICT_SET["<choice_clause>"]:
        self.parse_token("choice")
        self.choice_val()
        self.parse_token(":")
        self.statements_menu()
        self.choice_clause()

        """    232 <choice_clause>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def choice_val(self):
    self.appendF(FIRST_SET["<choice_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    233 <choice_val>	=>	piece_lit    """
    if self.tokens[self.pos].type in PREDICT_SET["<choice_val>"]:
        self.parse_token("piece_lit")

        """    234 <choice_val>	=>	chars_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_val>_1"]:
        self.parse_token("chars_lit")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def statements_menu(self):
    self.appendF(FIRST_SET["<statements_menu>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    235 <statements_menu>	=>	<id_statements_menu>	<statements_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<statements_menu>"]:
        self.id_statements_menu()
        self.statements_menu()

        """    236 <statements_menu>	=>	<built_in_rec_call>	;	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_1"]:
        self.built_in_rec_call()
        self.parse_token(";")
        self.statements_menu()

        """    237 <statements_menu>	=>	<conditional_st_menu>	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_2"]:
        self.conditional_st_menu()
        self.statements_menu()

        """    238 <statements_menu>	=>	<looping_st>	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_3"]:
        self.looping_st()
        self.statements_menu()

        """    239 <statements_menu>	=>	<jump_stop>	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_4"]:
        self.jump_stop()
        self.statements_menu()

        """    240 <statements_menu>	=>	<jump_serve>	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_5"]:
        self.jump_serve()
        self.statements_menu()

        """    241 <statements_menu>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_6"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_statements_menu(self):
    self.appendF(FIRST_SET["<id_statements_menu>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    242 <id_statements_menu>	=>	id	<id_statements_ext>	<statements_menu>    """
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

    """    243 <conditional_st_menu>	=>	<cond_check_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>"]:
        self.cond_check_menu()

        """    244 <conditional_st_menu>	=>	<cond_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>_1"]:
        self.cond_menu()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def cond_check_menu(self):
    self.appendF(FIRST_SET["<cond_check_menu>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    245 <cond_check_menu>	=>	check	(	<strict_flag_expr>	)	<menu_check_platter>	<alt_clause>	<instead_clause>    """
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

    """    246 <menu_check_platter>	=>	{	<local_decl_menu>	<statements_menu>	}    """
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

    """    247 <local_decl_menu>	=>	piece	<piece_decl>	<local_decl_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>"]:
        self.parse_token("piece")
        self.piece_decl()
        self.local_decl_menu()

        """    248 <local_decl_menu>	=>	chars	<chars_decl>	<local_decl_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_1"]:
        self.parse_token("chars")
        self.chars_decl()
        self.local_decl_menu()

        """    249 <local_decl_menu>	=>	sip	<sip_decl>	<local_decl_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_2"]:
        self.parse_token("sip")
        self.sip_decl()
        self.local_decl_menu()

        """    250 <local_decl_menu>	=>	flag	<flag_decl>	<local_decl_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_3"]:
        self.parse_token("flag")
        self.flag_decl()
        self.local_decl_menu()

        """    251 <local_decl_menu>	=>	id	<local_id_tail_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_4"]:
        self.parse_token("id")
        self.local_id_tail_menu()

        """    252 <local_decl_menu>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def local_id_tail_menu(self):
    self.appendF(FIRST_SET["<local_id_tail_menu>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    253 <local_id_tail_menu>	=>	of	<table_declare>	;	<local_decl_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>"]:
        self.parse_token("of")
        self.table_declare()
        self.parse_token(";")
        self.local_decl_menu()

        """    254 <local_id_tail_menu>	=>	[	<endsb_tail_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_1"]:
        self.parse_token("[")
        self.endsb_tail_menu()

        """    255 <local_id_tail_menu>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_2"]:
        self.table_accessor()
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements_menu()

        """    256 <local_id_tail_menu>	=>	<assignment_op>	<value>	;	<statements_menu>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_3"]:
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements_menu()

        """    257 <local_id_tail_menu>	=>	<tail1>	;	<statements_menu>    """
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

    """    258 <endsb_tail_menu>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_menu>"]:
        self.parse_token("]")
        self.dimensions_tail()
        self.parse_token("of")
        self.parse_token("id")
        self.table_array_init()
        self.parse_token(";")
        self.local_decl_menu()

        """    259 <endsb_tail_menu>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_menu>    """
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

    """    260 <looping_st>	=>	<loop_pass>    """
    if self.tokens[self.pos].type in PREDICT_SET["<looping_st>"]:
        self.loop_pass()

        """    261 <looping_st>	=>	<loop_repeat>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_1"]:
        self.loop_repeat()

        """    262 <looping_st>	=>	<loop_order>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_2"]:
        self.loop_order()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def loop_pass(self):
    self.appendF(FIRST_SET["<loop_pass>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    263 <loop_pass>	=>	pass	(	<initialization>	<update>	<strict_flag_expr>	)	<loop_platter>    """
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

    """    264 <initialization>	=>	id	<loop_init>	;    """
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

    """    265 <loop_init>	=>	=	<strict_piece_expr>    """
    if self.tokens[self.pos].type in PREDICT_SET["<loop_init>"]:
        self.parse_token("=")
        self.strict_piece_expr()

        """    266 <loop_init>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<loop_init>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def update(self):
    self.appendF(FIRST_SET["<update>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    267 <update>	=>	id	<accessor_tail>	<assignment_op>	<strict_piece_expr>	;    """
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

    """    268 <loop_platter>	=>	{	<local_decl_loop>	<statements_loop>	}    """
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

    """    269 <local_decl_loop>	=>	piece	<piece_decl>	<local_decl_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>"]:
        self.parse_token("piece")
        self.piece_decl()
        self.local_decl_loop()

        """    270 <local_decl_loop>	=>	chars	<chars_decl>	<local_decl_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_1"]:
        self.parse_token("chars")
        self.chars_decl()
        self.local_decl_loop()

        """    271 <local_decl_loop>	=>	sip	<sip_decl>	<local_decl_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_2"]:
        self.parse_token("sip")
        self.sip_decl()
        self.local_decl_loop()

        """    272 <local_decl_loop>	=>	flag	<flag_decl>	<local_decl_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_3"]:
        self.parse_token("flag")
        self.flag_decl()
        self.local_decl_loop()

        """    273 <local_decl_loop>	=>	id	<local_id_tail_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_4"]:
        self.parse_token("id")
        self.local_id_tail_loop()

        """    274 <local_decl_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def local_id_tail_loop(self):
    self.appendF(FIRST_SET["<local_id_tail_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    275 <local_id_tail_loop>	=>	of	<table_declare>	;	<local_decl_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>"]:
        self.parse_token("of")
        self.table_declare()
        self.parse_token(";")
        self.local_decl_loop()

        """    276 <local_id_tail_loop>	=>	[	<endsb_tail_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_1"]:
        self.parse_token("[")
        self.endsb_tail_loop()

        """    277 <local_id_tail_loop>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_2"]:
        self.table_accessor()
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements_loop()

        """    278 <local_id_tail_loop>	=>	<assignment_op>	<value>	;	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_3"]:
        self.assignment_op()
        self.value()
        self.parse_token(";")
        self.statements_loop()

        """    279 <local_id_tail_loop>	=>	<tail1>	;	<statements_loop>    """
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

    """    280 <endsb_tail_loop>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_loop>"]:
        self.parse_token("]")
        self.dimensions_tail()
        self.parse_token("of")
        self.parse_token("id")
        self.table_array_init()
        self.parse_token(";")
        self.local_decl_loop()

        """    281 <endsb_tail_loop>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_loop>    """
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

    """    282 <statements_loop>	=>	<id_statements_loop>	<statements_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<statements_loop>"]:
        self.id_statements_loop()
        self.statements_loop()

        """    283 <statements_loop>	=>	<built_in_rec_call>	;	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_1"]:
        self.built_in_rec_call()
        self.parse_token(";")
        self.statements_loop()

        """    284 <statements_loop>	=>	<conditional_st_loop>	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_2"]:
        self.conditional_st_loop()
        self.statements_loop()

        """    285 <statements_loop>	=>	<looping_st>	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_3"]:
        self.looping_st()
        self.statements_loop()

        """    286 <statements_loop>	=>	<jump_st>	<statements_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_4"]:
        self.jump_st()
        self.statements_loop()

        """    287 <statements_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_statements_loop(self):
    self.appendF(FIRST_SET["<id_statements_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    288 <id_statements_loop>	=>	id	<id_statements_ext>	<statements_loop>    """
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

    """    289 <conditional_st_loop>	=>	<cond_check_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>"]:
        self.cond_check_loop()

        """    290 <conditional_st_loop>	=>	<cond_menu_loop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>_1"]:
        self.cond_menu_loop()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def cond_check_loop(self):
    self.appendF(FIRST_SET["<cond_check_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    291 <cond_check_loop>	=>	check	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>	<instead_clause_loop>    """
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

    """    292 <alt_clause_loop>	=>	alt	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>"]:
        self.parse_token("alt")
        self.parse_token("(")
        self.strict_flag_expr()
        self.parse_token(")")
        self.loop_platter()
        self.alt_clause_loop()

        """    293 <alt_clause_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def instead_clause_loop(self):
    self.appendF(FIRST_SET["<instead_clause_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    294 <instead_clause_loop>	=>	instead	<loop_platter>    """
    if self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>"]:
        self.parse_token("instead")
        self.loop_platter()

        """    295 <instead_clause_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def cond_menu_loop(self):
    self.appendF(FIRST_SET["<cond_menu_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    296 <cond_menu_loop>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_loop_platter>    """
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

    """    297 <menu_loop_platter>	=>	{	<choice_clause_loop>	<usual_clause_loop>	}    """
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

    """    298 <choice_clause_loop>	=>	choice	<choice_val>	:	<choice_usual_loop_st>	<choice_clause_loop>    """
    if self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>"]:
        self.parse_token("choice")
        self.choice_val()
        self.parse_token(":")
        self.choice_usual_loop_st()
        self.choice_clause_loop()

        """    299 <choice_clause_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def usual_clause_loop(self):
    self.appendF(FIRST_SET["<usual_clause_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    300 <usual_clause_loop>	=>	usual	:	<choice_usual_loop_st>    """
    if self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>"]:
        self.parse_token("usual")
        self.parse_token(":")
        self.choice_usual_loop_st()

        """    301 <usual_clause_loop>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def choice_usual_loop_st(self):
    self.appendF(FIRST_SET["<choice_usual_loop_st>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    302 <choice_usual_loop_st>	=>	<id_statements_choice_usual_loop>	<choice_usual_loop_st>    """
    if self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>"]:
        self.id_statements_choice_usual_loop()
        self.choice_usual_loop_st()

        """    303 <choice_usual_loop_st>	=>	<built_in_rec_call>	;	<choice_usual_loop_st>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_1"]:
        self.built_in_rec_call()
        self.parse_token(";")
        self.choice_usual_loop_st()

        """    304 <choice_usual_loop_st>	=>	<conditional_st_loop>	<choice_usual_loop_st>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_2"]:
        self.conditional_st_loop()
        self.choice_usual_loop_st()

        """    305 <choice_usual_loop_st>	=>	<looping_st>	<choice_usual_loop_st>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_3"]:
        self.looping_st()
        self.choice_usual_loop_st()

        """    306 <choice_usual_loop_st>	=>	<jump_st>	<choice_usual_loop_st>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_4"]:
        self.jump_st()
        self.choice_usual_loop_st()

        """    307 <choice_usual_loop_st>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_statements_choice_usual_loop(self):
    self.appendF(FIRST_SET["<id_statements_choice_usual_loop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    308 <id_statements_choice_usual_loop>	=>	id	<id_statements_ext>	<choice_usual_loop_st>    """
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

    """    309 <jump_st>	=>	<jump_next>    """
    if self.tokens[self.pos].type in PREDICT_SET["<jump_st>"]:
        self.jump_next()

        """    310 <jump_st>	=>	<jump_stop>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_1"]:
        self.jump_stop()

        """    311 <jump_st>	=>	<jump_serve>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_2"]:
        self.jump_serve()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def jump_next(self):
    self.appendF(FIRST_SET["<jump_next>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    312 <jump_next>	=>	next	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<jump_next>"]:
        self.parse_token("next")
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def jump_stop(self):
    self.appendF(FIRST_SET["<jump_stop>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    313 <jump_stop>	=>	stop	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<jump_stop>"]:
        self.parse_token("stop")
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def jump_serve(self):
    self.appendF(FIRST_SET["<jump_serve>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    314 <jump_serve>	=>	serve	<value>	;    """
    if self.tokens[self.pos].type in PREDICT_SET["<jump_serve>"]:
        self.parse_token("serve")
        self.value()
        self.parse_token(";")
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def loop_repeat(self):
    self.appendF(FIRST_SET["<loop_repeat>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    315 <loop_repeat>	=>	repeat	(	<strict_flag_expr>	)	<loop_platter>    """
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

    """    316 <loop_order>	=>	order	<loop_platter>	repeat	(	<strict_flag_expr>	)	;    """
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

    """    317 <usual_clause>	=>	usual	:	<statements_menu>    """
    if self.tokens[self.pos].type in PREDICT_SET["<usual_clause>"]:
        self.parse_token("usual")
        self.parse_token(":")
        self.statements_menu()

        """    318 <usual_clause>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_flag_expr(self):
    self.appendF(FIRST_SET["<strict_flag_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    319 <strict_flag_expr>	=>	<strict_flag_term>	<strict_flag_or_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_expr>"]:
        self.strict_flag_term()
        self.strict_flag_or_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_flag_or_tail(self):
    self.appendF(FIRST_SET["<strict_flag_or_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    320 <strict_flag_or_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>"]:
        self.parse_token("or")
        self.strict_flag_term()
        self.strict_flag_or_tail()

        """    321 <strict_flag_or_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_or_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_flag_term(self):
    self.appendF(FIRST_SET["<strict_flag_term>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    322 <strict_flag_term>	=>	<strict_flag_factor>	<strict_flag_and_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_term>"]:
        self.strict_flag_factor()
        self.strict_flag_and_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_flag_and_tail(self):
    self.appendF(FIRST_SET["<strict_flag_and_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    323 <strict_flag_and_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>"]:
        self.parse_token("and")
        self.strict_flag_factor()
        self.strict_flag_and_tail()

        """    324 <strict_flag_and_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_and_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_flag_factor(self):
    self.appendF(FIRST_SET["<strict_flag_factor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    325 <strict_flag_factor>	=>	<id>	<lhs_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>"]:
        self.id_()
        self.lhs_ambig_tail()

        """    326 <strict_flag_factor>	=>	<ret_piece>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_1"]:
        self.ret_piece()
        self.lhs_piece_tail()

        """    327 <strict_flag_factor>	=>	<ret_sip>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_2"]:
        self.ret_sip()
        self.lhs_sip_tail()

        """    328 <strict_flag_factor>	=>	<ret_chars>	<lhs_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_3"]:
        self.ret_chars()
        self.lhs_str_tail()

        """    329 <strict_flag_factor>	=>	<ret_flag>	<lhs_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_4"]:
        self.ret_flag()
        self.lhs_bool_tail()

        """    330 <strict_flag_factor>	=>	not	<strict_flag_factor>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_5"]:
        self.parse_token("not")
        self.strict_flag_factor()

        """    331 <strict_flag_factor>	=>	(	<paren_dispatch_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_flag_factor>_6"]:
        self.parse_token("(")
        self.paren_dispatch_lhs()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_piece_tail(self):
    self.appendF(FIRST_SET["<lhs_piece_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    332 <lhs_piece_tail>	=>	+	<strict_piece_factor>	<lhs_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>"]:
        self.parse_token("+")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    333 <lhs_piece_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    334 <lhs_piece_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    335 <lhs_piece_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    336 <lhs_piece_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    337 <lhs_piece_tail>	=>	<rel_op>	<strict_piece_expr>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_piece_tail>_5"]:
        self.rel_op()
        self.strict_piece_expr()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_sip_tail(self):
    self.appendF(FIRST_SET["<lhs_sip_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    338 <lhs_sip_tail>	=>	+	<strict_sip_factor>	<lhs_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>"]:
        self.parse_token("+")
        self.strict_sip_factor()
        self.lhs_sip_tail()

        """    339 <lhs_sip_tail>	=>	-	<strict_sip_factor>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_1"]:
        self.parse_token("-")
        self.strict_sip_factor()
        self.lhs_sip_tail()

        """    340 <lhs_sip_tail>	=>	*	<strict_sip_factor>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_2"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.lhs_sip_tail()

        """    341 <lhs_sip_tail>	=>	/	<strict_sip_factor>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_3"]:
        self.parse_token("/")
        self.strict_sip_factor()
        self.lhs_sip_tail()

        """    342 <lhs_sip_tail>	=>	%	<strict_sip_factor>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_4"]:
        self.parse_token("%")
        self.strict_sip_factor()
        self.lhs_sip_tail()

        """    343 <lhs_sip_tail>	=>	<rel_op>	<strict_sip_expr>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_sip_tail>_5"]:
        self.rel_op()
        self.strict_sip_expr()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_str_tail(self):
    self.appendF(FIRST_SET["<lhs_str_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    344 <lhs_str_tail>	=>	+	<strict_string_factor>	<lhs_str_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>"]:
        self.parse_token("+")
        self.strict_string_factor()
        self.lhs_str_tail()

        """    345 <lhs_str_tail>	=>	<rel_op>	<strict_chars_expr>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_str_tail>_1"]:
        self.rel_op()
        self.strict_chars_expr()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_ambig_tail(self):
    self.appendF(FIRST_SET["<lhs_ambig_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    346 <lhs_ambig_tail>	=>	+	<ambig_calc_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>"]:
        self.parse_token("+")
        self.ambig_calc_branch()

        """    347 <lhs_ambig_tail>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    348 <lhs_ambig_tail>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    349 <lhs_ambig_tail>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    350 <lhs_ambig_tail>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    351 <lhs_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_5"]:
        self.rel_op()
        self.strict_ambig_rhs()

        """    352 <lhs_ambig_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_6"]:
        self.parse_token("and")
        self.strict_flag_factor()
        self.strict_flag_and_tail()

        """    353 <lhs_ambig_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_7"]:
        self.parse_token("or")
        self.strict_flag_term()
        self.strict_flag_or_tail()

        """    354 <lhs_ambig_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail>_8"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def ambig_calc_branch(self):
    self.appendF(FIRST_SET["<ambig_calc_branch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    355 <ambig_calc_branch>	=>	<id>	<lhs_ambig_tail_no_lambda>    """
    if self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>"]:
        self.id_()
        self.lhs_ambig_tail_no_lambda()

        """    356 <ambig_calc_branch>	=>	<ret_piece>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_1"]:
        self.ret_piece()
        self.lhs_piece_tail()

        """    357 <ambig_calc_branch>	=>	<ret_sip>	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_2"]:
        self.ret_sip()
        self.lhs_sip_tail()

        """    358 <ambig_calc_branch>	=>	<ret_chars>	<lhs_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_3"]:
        self.ret_chars()
        self.lhs_str_tail()

        """    359 <ambig_calc_branch>	=>	(	<paren_dispatch_lhs_no_lambda>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ambig_calc_branch>_4"]:
        self.parse_token("(")
        self.paren_dispatch_lhs_no_lambda()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_ambig_tail_no_lambda(self):
    self.appendF(FIRST_SET["<lhs_ambig_tail_no_lambda>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    360 <lhs_ambig_tail_no_lambda>	=>	+	<ambig_calc_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>"]:
        self.parse_token("+")
        self.ambig_calc_branch()

        """    361 <lhs_ambig_tail_no_lambda>	=>	-	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    362 <lhs_ambig_tail_no_lambda>	=>	*	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    363 <lhs_ambig_tail_no_lambda>	=>	/	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    364 <lhs_ambig_tail_no_lambda>	=>	%	<strict_piece_factor>	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.lhs_piece_tail()

        """    365 <lhs_ambig_tail_no_lambda>	=>	<rel_op>	<strict_ambig_rhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_ambig_tail_no_lambda>_5"]:
        self.rel_op()
        self.strict_ambig_rhs()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_string_factor(self):
    self.appendF(FIRST_SET["<strict_string_factor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    366 <strict_string_factor>	=>	<id>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>"]:
        self.id_()

        """    367 <strict_string_factor>	=>	<ret_chars>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_1"]:
        self.ret_chars()

        """    368 <strict_string_factor>	=>	(	<paren_dispatch_val_str>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_string_factor>_2"]:
        self.parse_token("(")
        self.paren_dispatch_val_str()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_ambig_rhs(self):
    self.appendF(FIRST_SET["<strict_ambig_rhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    369 <strict_ambig_rhs>	=>	<id>	<val_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>"]:
        self.id_()
        self.val_ambig_tail()

        """    370 <strict_ambig_rhs>	=>	<ret_piece>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_1"]:
        self.ret_piece()
        self.val_piece_tail()

        """    371 <strict_ambig_rhs>	=>	<ret_sip>	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_2"]:
        self.ret_sip()
        self.val_sip_tail()

        """    372 <strict_ambig_rhs>	=>	<ret_chars>	<val_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_3"]:
        self.ret_chars()
        self.val_str_tail()

        """    373 <strict_ambig_rhs>	=>	(	<paren_dispatch_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_ambig_rhs>_4"]:
        self.parse_token("(")
        self.paren_dispatch_val()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_lhs(self):
    self.appendF(FIRST_SET["<paren_dispatch_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    374 <paren_dispatch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>"]:
        self.id_()
        self.paren_ambig_tail_lhs()

        """    375 <paren_dispatch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_1"]:
        self.ret_piece()
        self.paren_piece_tail_lhs()

        """    376 <paren_dispatch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_2"]:
        self.ret_sip()
        self.paren_sip_tail_lhs()

        """    377 <paren_dispatch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_3"]:
        self.ret_chars()
        self.paren_str_tail_lhs()

        """    378 <paren_dispatch_lhs>	=>	<ret_flag>	<lhs_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_4"]:
        self.ret_flag()
        self.lhs_bool_tail()
        self.parse_token(")")

        """    379 <paren_dispatch_lhs>	=>	not	<strict_flag_factor>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_5"]:
        self.parse_token("not")
        self.strict_flag_factor()
        self.parse_token(")")

        """    380 <paren_dispatch_lhs>	=>	(	<paren_dispatch_lhs>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs>_6"]:
        self.parse_token("(")
        self.paren_dispatch_lhs()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_piece_tail_lhs(self):
    self.appendF(FIRST_SET["<paren_piece_tail_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    381 <paren_piece_tail_lhs>	=>	+	<strict_piece_factor>	<paren_piece_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>"]:
        self.parse_token("+")
        self.strict_piece_factor()
        self.paren_piece_tail_lhs()

        """    382 <paren_piece_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.paren_piece_tail_lhs()

        """    383 <paren_piece_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.paren_piece_tail_lhs()

        """    384 <paren_piece_tail_lhs>	=>	)	<lhs_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_3"]:
        self.parse_token(")")
        self.lhs_piece_tail()

        """    385 <paren_piece_tail_lhs>	=>	<rel_op>	<strict_piece_expr>	<lhs_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_lhs>_4"]:
        self.rel_op()
        self.strict_piece_expr()
        self.lhs_bool_tail()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_sip_tail_lhs(self):
    self.appendF(FIRST_SET["<paren_sip_tail_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    386 <paren_sip_tail_lhs>	=>	+	<strict_sip_factor>	<paren_sip_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>"]:
        self.parse_token("+")
        self.strict_sip_factor()
        self.paren_sip_tail_lhs()

        """    387 <paren_sip_tail_lhs>	=>	-	<strict_sip_factor>	<paren_sip_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_1"]:
        self.parse_token("-")
        self.strict_sip_factor()
        self.paren_sip_tail_lhs()

        """    388 <paren_sip_tail_lhs>	=>	*	<strict_sip_factor>	<paren_sip_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_2"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.paren_sip_tail_lhs()

        """    389 <paren_sip_tail_lhs>	=>	)	<lhs_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_3"]:
        self.parse_token(")")
        self.lhs_sip_tail()

        """    390 <paren_sip_tail_lhs>	=>	<rel_op>	<strict_sip_expr>	<lhs_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_lhs>_4"]:
        self.rel_op()
        self.strict_sip_expr()
        self.lhs_bool_tail()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_ambig_tail_lhs(self):
    self.appendF(FIRST_SET["<paren_ambig_tail_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    391 <paren_ambig_tail_lhs>	=>	+	<paren_ambig_branch_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>"]:
        self.parse_token("+")
        self.paren_ambig_branch_lhs()

        """    392 <paren_ambig_tail_lhs>	=>	-	<strict_piece_factor>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.paren_piece_tail_lhs()

        """    393 <paren_ambig_tail_lhs>	=>	*	<strict_piece_factor>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.paren_piece_tail_lhs()

        """    394 <paren_ambig_tail_lhs>	=>	)	<lhs_ambig_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_3"]:
        self.parse_token(")")
        self.lhs_ambig_tail()

        """    395 <paren_ambig_tail_lhs>	=>	<rel_op>	<strict_ambig_rhs>	<lhs_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_4"]:
        self.rel_op()
        self.strict_ambig_rhs()
        self.lhs_bool_tail()
        self.parse_token(")")

        """    396 <paren_ambig_tail_lhs>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_5"]:
        self.parse_token("and")
        self.strict_flag_factor()
        self.strict_flag_and_tail()
        self.parse_token(")")

        """    397 <paren_ambig_tail_lhs>	=>	or	<strict_flag_term>	<strict_flag_or_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_lhs>_6"]:
        self.parse_token("or")
        self.strict_flag_term()
        self.strict_flag_or_tail()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_ambig_branch_lhs(self):
    self.appendF(FIRST_SET["<paren_ambig_branch_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    398 <paren_ambig_branch_lhs>	=>	<id>	<paren_ambig_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>"]:
        self.id_()
        self.paren_ambig_tail_lhs()

        """    399 <paren_ambig_branch_lhs>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_1"]:
        self.ret_piece()
        self.paren_piece_tail_lhs()

        """    400 <paren_ambig_branch_lhs>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_2"]:
        self.ret_sip()
        self.paren_sip_tail_lhs()

        """    401 <paren_ambig_branch_lhs>	=>	<ret_chars>	<paren_str_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_3"]:
        self.ret_chars()
        self.paren_str_tail_lhs()

        """    402 <paren_ambig_branch_lhs>	=>	(	<paren_dispatch_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_lhs>_4"]:
        self.parse_token("(")
        self.paren_dispatch_lhs()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_str_tail_lhs(self):
    self.appendF(FIRST_SET["<paren_str_tail_lhs>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    403 <paren_str_tail_lhs>	=>	+	<strict_string_factor>	<paren_str_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>"]:
        self.parse_token("+")
        self.strict_string_factor()
        self.paren_str_tail_lhs()

        """    404 <paren_str_tail_lhs>	=>	)	<lhs_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_1"]:
        self.parse_token(")")
        self.lhs_str_tail()

        """    405 <paren_str_tail_lhs>	=>	<rel_op>	<strict_chars_expr>	<lhs_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_lhs>_2"]:
        self.rel_op()
        self.strict_chars_expr()
        self.lhs_bool_tail()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_val(self):
    self.appendF(FIRST_SET["<paren_dispatch_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    406 <paren_dispatch_val>	=>	<id>	<paren_ambig_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>"]:
        self.id_()
        self.paren_ambig_tail_val()

        """    407 <paren_dispatch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_1"]:
        self.ret_piece()
        self.paren_piece_tail_val()

        """    408 <paren_dispatch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_2"]:
        self.ret_sip()
        self.paren_sip_tail_val()

        """    409 <paren_dispatch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_3"]:
        self.ret_chars()
        self.paren_str_tail_val()

        """    410 <paren_dispatch_val>	=>	(	<paren_dispatch_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val>_4"]:
        self.parse_token("(")
        self.paren_dispatch_val()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_piece_tail_val(self):
    self.appendF(FIRST_SET["<paren_piece_tail_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    411 <paren_piece_tail_val>	=>	+	<strict_piece_factor>	<paren_piece_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>"]:
        self.parse_token("+")
        self.strict_piece_factor()
        self.paren_piece_tail_val()

        """    412 <paren_piece_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.paren_piece_tail_val()

        """    413 <paren_piece_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.paren_piece_tail_val()

        """    414 <paren_piece_tail_val>	=>	)	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_piece_tail_val>_3"]:
        self.parse_token(")")
        self.val_piece_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_sip_tail_val(self):
    self.appendF(FIRST_SET["<paren_sip_tail_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    415 <paren_sip_tail_val>	=>	+	<strict_sip_factor>	<paren_sip_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>"]:
        self.parse_token("+")
        self.strict_sip_factor()
        self.paren_sip_tail_val()

        """    416 <paren_sip_tail_val>	=>	-	<strict_sip_factor>	<paren_sip_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_1"]:
        self.parse_token("-")
        self.strict_sip_factor()
        self.paren_sip_tail_val()

        """    417 <paren_sip_tail_val>	=>	*	<strict_sip_factor>	<paren_sip_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_2"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.paren_sip_tail_val()

        """    418 <paren_sip_tail_val>	=>	)	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_sip_tail_val>_3"]:
        self.parse_token(")")
        self.val_sip_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_str_tail_val(self):
    self.appendF(FIRST_SET["<paren_str_tail_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    419 <paren_str_tail_val>	=>	+	<strict_string_factor>	<paren_str_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>"]:
        self.parse_token("+")
        self.strict_string_factor()
        self.paren_str_tail_val()

        """    420 <paren_str_tail_val>	=>	)	<val_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_str_tail_val>_1"]:
        self.parse_token(")")
        self.val_str_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_ambig_tail_val(self):
    self.appendF(FIRST_SET["<paren_ambig_tail_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    421 <paren_ambig_tail_val>	=>	+	<paren_ambig_branch_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>"]:
        self.parse_token("+")
        self.paren_ambig_branch_val()

        """    422 <paren_ambig_tail_val>	=>	-	<strict_piece_factor>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.paren_piece_tail_val()

        """    423 <paren_ambig_tail_val>	=>	*	<strict_piece_factor>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.paren_piece_tail_val()

        """    424 <paren_ambig_tail_val>	=>	)	<val_ambig_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_tail_val>_3"]:
        self.parse_token(")")
        self.val_ambig_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_ambig_branch_val(self):
    self.appendF(FIRST_SET["<paren_ambig_branch_val>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    425 <paren_ambig_branch_val>	=>	<id>	<paren_ambig_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>"]:
        self.id_()
        self.paren_ambig_tail_val()

        """    426 <paren_ambig_branch_val>	=>	<ret_piece>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_1"]:
        self.ret_piece()
        self.paren_piece_tail_val()

        """    427 <paren_ambig_branch_val>	=>	<ret_sip>	<paren_sip_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_2"]:
        self.ret_sip()
        self.paren_sip_tail_val()

        """    428 <paren_ambig_branch_val>	=>	<ret_chars>	<paren_str_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_3"]:
        self.ret_chars()
        self.paren_str_tail_val()

        """    429 <paren_ambig_branch_val>	=>	(	<paren_dispatch_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_ambig_branch_val>_4"]:
        self.parse_token("(")
        self.paren_dispatch_val()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def val_piece_tail(self):
    self.appendF(FIRST_SET["<val_piece_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    430 <val_piece_tail>	=>	+	<strict_piece_factor>	<val_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>"]:
        self.parse_token("+")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    431 <val_piece_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    432 <val_piece_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    433 <val_piece_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    434 <val_piece_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    435 <val_piece_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_piece_tail>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def val_sip_tail(self):
    self.appendF(FIRST_SET["<val_sip_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    436 <val_sip_tail>	=>	+	<strict_sip_factor>	<val_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>"]:
        self.parse_token("+")
        self.strict_sip_factor()
        self.val_sip_tail()

        """    437 <val_sip_tail>	=>	-	<strict_sip_factor>	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_1"]:
        self.parse_token("-")
        self.strict_sip_factor()
        self.val_sip_tail()

        """    438 <val_sip_tail>	=>	*	<strict_sip_factor>	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_2"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.val_sip_tail()

        """    439 <val_sip_tail>	=>	/	<strict_sip_factor>	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_3"]:
        self.parse_token("/")
        self.strict_sip_factor()
        self.val_sip_tail()

        """    440 <val_sip_tail>	=>	%	<strict_sip_factor>	<val_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_4"]:
        self.parse_token("%")
        self.strict_sip_factor()
        self.val_sip_tail()

        """    441 <val_sip_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_sip_tail>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def val_str_tail(self):
    self.appendF(FIRST_SET["<val_str_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    442 <val_str_tail>	=>	+	<strict_string_factor>	<val_str_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<val_str_tail>"]:
        self.parse_token("+")
        self.strict_string_factor()
        self.val_str_tail()

        """    443 <val_str_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_str_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def val_ambig_tail(self):
    self.appendF(FIRST_SET["<val_ambig_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    444 <val_ambig_tail>	=>	+	<paren_ambig_branch_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>"]:
        self.parse_token("+")
        self.paren_ambig_branch_val()

        """    445 <val_ambig_tail>	=>	-	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    446 <val_ambig_tail>	=>	*	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    447 <val_ambig_tail>	=>	/	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    448 <val_ambig_tail>	=>	%	<strict_piece_factor>	<val_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.val_piece_tail()

        """    449 <val_ambig_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<val_ambig_tail>_5"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_val_piece(self):
    self.appendF(FIRST_SET["<paren_dispatch_val_piece>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    450 <paren_dispatch_val_piece>	=>	<id>	<paren_piece_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>"]:
        self.id_()
        self.paren_piece_tail_val()

        """    451 <paren_dispatch_val_piece>	=>	<ret_piece>	<paren_piece_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>_1"]:
        self.ret_piece()
        self.paren_piece_tail_val()

        """    452 <paren_dispatch_val_piece>	=>	(	<paren_dispatch_val_piece>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_piece>_2"]:
        self.parse_token("(")
        self.paren_dispatch_val_piece()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_val_sip(self):
    self.appendF(FIRST_SET["<paren_dispatch_val_sip>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    453 <paren_dispatch_val_sip>	=>	<id>	<paren_sip_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>"]:
        self.id_()
        self.paren_sip_tail_val()

        """    454 <paren_dispatch_val_sip>	=>	<ret_sip>	<paren_sip_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>_1"]:
        self.ret_sip()
        self.paren_sip_tail_val()

        """    455 <paren_dispatch_val_sip>	=>	(	<paren_dispatch_val_sip>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_sip>_2"]:
        self.parse_token("(")
        self.paren_dispatch_val_sip()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_val_str(self):
    self.appendF(FIRST_SET["<paren_dispatch_val_str>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    456 <paren_dispatch_val_str>	=>	<id>	<paren_str_tail_val>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>"]:
        self.id_()
        self.paren_str_tail_val()

        """    457 <paren_dispatch_val_str>	=>	<ret_chars>	<paren_str_tail_val>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_1"]:
        self.ret_chars()
        self.paren_str_tail_val()

        """    458 <paren_dispatch_val_str>	=>	(	<paren_dispatch_val_str>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_val_str>_2"]:
        self.parse_token("(")
        self.paren_dispatch_val_str()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def paren_dispatch_lhs_no_lambda(self):
    self.appendF(FIRST_SET["<paren_dispatch_lhs_no_lambda>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    459 <paren_dispatch_lhs_no_lambda>	=>	<id>	<paren_ambig_tail_lhs>    """
    if self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>"]:
        self.id_()
        self.paren_ambig_tail_lhs()

        """    460 <paren_dispatch_lhs_no_lambda>	=>	<ret_piece>	<paren_piece_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_1"]:
        self.ret_piece()
        self.paren_piece_tail_lhs()

        """    461 <paren_dispatch_lhs_no_lambda>	=>	<ret_sip>	<paren_sip_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_2"]:
        self.ret_sip()
        self.paren_sip_tail_lhs()

        """    462 <paren_dispatch_lhs_no_lambda>	=>	<ret_chars>	<paren_str_tail_lhs>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_3"]:
        self.ret_chars()
        self.paren_str_tail_lhs()

        """    463 <paren_dispatch_lhs_no_lambda>	=>	(	<paren_dispatch_lhs_no_lambda>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<paren_dispatch_lhs_no_lambda>_4"]:
        self.parse_token("(")
        self.paren_dispatch_lhs_no_lambda()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def lhs_bool_tail(self):
    self.appendF(FIRST_SET["<lhs_bool_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    464 <lhs_bool_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>"]:
        self.parse_token("and")
        self.strict_flag_factor()
        self.strict_flag_and_tail()

        """    465 <lhs_bool_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>_1"]:
        self.parse_token("or")
        self.strict_flag_term()
        self.strict_flag_or_tail()

        """    466 <lhs_bool_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<lhs_bool_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def rel_op(self):
    self.appendF(FIRST_SET["<rel_op>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    467 <rel_op>	=>	==    """
    if self.tokens[self.pos].type in PREDICT_SET["<rel_op>"]:
        self.parse_token("==")

        """    468 <rel_op>	=>	!=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_1"]:
        self.parse_token("!=")

        """    469 <rel_op>	=>	>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_2"]:
        self.parse_token(">")

        """    470 <rel_op>	=>	<    """
    elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_3"]:
        self.parse_token("<")

        """    471 <rel_op>	=>	>=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_4"]:
        self.parse_token(">=")

        """    472 <rel_op>	=>	<=    """
    elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_5"]:
        self.parse_token("<=")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_chars_expr(self):
    self.appendF(FIRST_SET["<strict_chars_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    473 <strict_chars_expr>	=>	<strict_chars_factor>	<strict_chars_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_expr>"]:
        self.strict_chars_factor()
        self.strict_chars_add_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_chars_factor(self):
    self.appendF(FIRST_SET["<strict_chars_factor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    474 <strict_chars_factor>	=>	<ret_chars>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>"]:
        self.ret_chars()

        """    475 <strict_chars_factor>	=>	<id>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_1"]:
        self.id_()

        """    476 <strict_chars_factor>	=>	(	<strict_chars_expr>	)    """
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

    """    477 <strict_chars_add_tail>	=>	+	<strict_chars_factor>	<strict_chars_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>"]:
        self.parse_token("+")
        self.strict_chars_factor()
        self.strict_chars_add_tail()

        """    478 <strict_chars_add_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_expr(self):
    self.appendF(FIRST_SET["<strict_piece_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    479 <strict_piece_expr>	=>	<strict_piece_term>	<strict_piece_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr>"]:
        self.strict_piece_term()
        self.strict_piece_add_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_term(self):
    self.appendF(FIRST_SET["<strict_piece_term>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    480 <strict_piece_term>	=>	<strict_piece_factor>	<strict_piece_mult_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term>"]:
        self.strict_piece_factor()
        self.strict_piece_mult_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_factor(self):
    self.appendF(FIRST_SET["<strict_piece_factor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    481 <strict_piece_factor>	=>	<ret_piece>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>"]:
        self.ret_piece()

        """    482 <strict_piece_factor>	=>	<id>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_1"]:
        self.id_()

        """    483 <strict_piece_factor>	=>	(	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_2"]:
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_mult_tail(self):
    self.appendF(FIRST_SET["<strict_piece_mult_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    484 <strict_piece_mult_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.strict_piece_mult_tail()

        """    485 <strict_piece_mult_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_1"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.strict_piece_mult_tail()

        """    486 <strict_piece_mult_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_2"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.strict_piece_mult_tail()

        """    487 <strict_piece_mult_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_3"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_add_tail(self):
    self.appendF(FIRST_SET["<strict_piece_add_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    488 <strict_piece_add_tail>	=>	+	<strict_piece_term>	<strict_piece_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>"]:
        self.parse_token("+")
        self.strict_piece_term()
        self.strict_piece_add_tail()

        """    489 <strict_piece_add_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_term()
        self.strict_piece_add_tail()

        """    490 <strict_piece_add_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_sip_expr(self):
    self.appendF(FIRST_SET["<strict_sip_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    491 <strict_sip_expr>	=>	<strict_sip_term>	<strict_sip_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_expr>"]:
        self.strict_sip_term()
        self.strict_sip_add_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_sip_term(self):
    self.appendF(FIRST_SET["<strict_sip_term>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    492 <strict_sip_term>	=>	<strict_sip_factor>	<strict_sip_mult_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_term>"]:
        self.strict_sip_factor()
        self.strict_sip_mult_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_sip_factor(self):
    self.appendF(FIRST_SET["<strict_sip_factor>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    493 <strict_sip_factor>	=>	<id>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>"]:
        self.id_()

        """    494 <strict_sip_factor>	=>	<ret_sip>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_1"]:
        self.ret_sip()

        """    495 <strict_sip_factor>	=>	(	<strict_sip_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_2"]:
        self.parse_token("(")
        self.strict_sip_expr()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_sip_mult_tail(self):
    self.appendF(FIRST_SET["<strict_sip_mult_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    496 <strict_sip_mult_tail>	=>	*	<strict_sip_factor>	<strict_sip_mult_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.strict_sip_mult_tail()

        """    497 <strict_sip_mult_tail>	=>	/	<strict_sip_factor>	<strict_sip_mult_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_1"]:
        self.parse_token("/")
        self.strict_sip_factor()
        self.strict_sip_mult_tail()

        """    498 <strict_sip_mult_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_sip_add_tail(self):
    self.appendF(FIRST_SET["<strict_sip_add_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    499 <strict_sip_add_tail>	=>	+	<strict_sip_term>	<strict_sip_add_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>"]:
        self.parse_token("+")
        self.strict_sip_term()
        self.strict_sip_add_tail()

        """    500 <strict_sip_add_tail>	=>	-	<strict_sip_term>	<strict_sip_add_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_1"]:
        self.parse_token("-")
        self.strict_sip_term()
        self.strict_sip_add_tail()

        """    501 <strict_sip_add_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_flag(self):
    self.appendF(FIRST_SET["<ret_flag>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    502 <ret_flag>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_flag>"]:
        self.parse_token("matches")
        self.parse_token("(")
        self.strict_datas_expr()
        self.parse_token(",")
        self.strict_datas_expr()
        self.parse_token(")")

        """    503 <ret_flag>	=>	toflag	(	<any_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_1"]:
        self.parse_token("toflag")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    504 <ret_flag>	=>	flag_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_2"]:
        self.parse_token("flag_lit")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_chars(self):
    self.appendF(FIRST_SET["<ret_chars>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    505 <ret_chars>	=>	bill	(	<strict_chars_expr>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_chars>"]:
        self.parse_token("bill")
        self.parse_token("(")
        self.strict_chars_expr()
        self.parse_token(")")

        """    506 <ret_chars>	=>	take	(	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_1"]:
        self.parse_token("take")
        self.parse_token("(")
        self.parse_token(")")

        """    507 <ret_chars>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_2"]:
        self.parse_token("copy")
        self.parse_token("(")
        self.strict_chars_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

        """    508 <ret_chars>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_3"]:
        self.parse_token("cut")
        self.parse_token("(")
        self.strict_sip_expr()
        self.parse_token(",")
        self.strict_sip_expr()
        self.parse_token(")")

        """    509 <ret_chars>	=>	tochars	(	<any_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_4"]:
        self.parse_token("tochars")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    510 <ret_chars>	=>	chars_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_5"]:
        self.parse_token("chars_lit")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_piece(self):
    self.appendF(FIRST_SET["<ret_piece>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    511 <ret_piece>	=>	topiece	(	<any_expr>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_piece>"]:
        self.parse_token("topiece")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    512 <ret_piece>	=>	size	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_1"]:
        self.parse_token("size")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    513 <ret_piece>	=>	search	(	<strict_array_expr>	,	<value>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_2"]:
        self.parse_token("search")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.value()
        self.parse_token(")")

        """    514 <ret_piece>	=>	fact	(	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_3"]:
        self.parse_token("fact")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(")")

        """    515 <ret_piece>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_4"]:
        self.parse_token("pow")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

        """    516 <ret_piece>	=>	piece_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_5"]:
        self.parse_token("piece_lit")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_sip(self):
    self.appendF(FIRST_SET["<ret_sip>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    517 <ret_sip>	=>	sqrt	(	<strict_piece_expr>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_sip>"]:
        self.parse_token("sqrt")
        self.parse_token("(")
        self.strict_piece_expr()
        self.parse_token(")")

        """    518 <ret_sip>	=>	rand	(	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_1"]:
        self.parse_token("rand")
        self.parse_token("(")
        self.parse_token(")")

        """    519 <ret_sip>	=>	tosip	(	<any_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_2"]:
        self.parse_token("tosip")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    520 <ret_sip>	=>	sip_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_3"]:
        self.parse_token("sip_lit")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_array(self):
    self.appendF(FIRST_SET["<ret_array>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    521 <ret_array>	=>	append	(	<strict_array_expr>	,	<value>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_array>"]:
        self.parse_token("append")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.value()
        self.parse_token(")")

        """    522 <ret_array>	=>	sort	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_1"]:
        self.parse_token("sort")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    523 <ret_array>	=>	reverse	(	<strict_array_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_2"]:
        self.parse_token("reverse")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(")")

        """    524 <ret_array>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_3"]:
        self.parse_token("remove")
        self.parse_token("(")
        self.strict_array_expr()
        self.parse_token(",")
        self.strict_piece_expr()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_datas_expr(self):
    self.appendF(FIRST_SET["<strict_datas_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    525 <strict_datas_expr>	=>	[	<notation_val>	]    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>"]:
        self.parse_token("[")
        self.notation_val()
        self.parse_token("]")

        """    526 <strict_datas_expr>	=>	id	<id_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_1"]:
        self.parse_token("id")
        self.id_tail()

        """    527 <strict_datas_expr>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_2"]:
        self.ret_array()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_array_expr(self):
    self.appendF(FIRST_SET["<strict_array_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    528 <strict_array_expr>	=>	[	<array_element_id>	]    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>"]:
        self.parse_token("[")
        self.array_element_id()
        self.parse_token("]")

        """    529 <strict_array_expr>	=>	id	<id_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_1"]:
        self.parse_token("id")
        self.id_tail()

        """    530 <strict_array_expr>	=>	<ret_array>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_2"]:
        self.ret_array()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_(self):
    self.appendF(FIRST_SET["<id_>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    531 <id>	=>	id	<id_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<id>"]:
        self.parse_token("id")
        self.id_tail()
    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def id_tail(self):
    self.appendF(FIRST_SET["<id_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    532 <id_tail>	=>	<call_tailopt>    """
    if self.tokens[self.pos].type in PREDICT_SET["<id_tail>"]:
        self.call_tailopt()

        """    533 <id_tail>	=>	<accessor_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<id_tail>_1"]:
        self.accessor_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def call_tailopt(self):
    self.appendF(FIRST_SET["<call_tailopt>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    534 <call_tailopt>	=>	(	<flavor>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>"]:
        self.parse_token("(")
        self.flavor()
        self.parse_token(")")

        """    535 <call_tailopt>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>_1"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def any_expr(self):
    self.appendF(FIRST_SET["<any_expr>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    536 <any_expr>	=>	<id>	<univ_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<any_expr>"]:
        self.id_()
        self.univ_ambig_tail()

        """    537 <any_expr>	=>	<ret_piece>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_1"]:
        self.ret_piece()
        self.univ_piece_tail()

        """    538 <any_expr>	=>	<ret_sip>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_2"]:
        self.ret_sip()
        self.univ_sip_tail()

        """    539 <any_expr>	=>	<ret_chars>	<univ_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_3"]:
        self.ret_chars()
        self.univ_str_tail()

        """    540 <any_expr>	=>	<ret_flag>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_4"]:
        self.ret_flag()
        self.univ_bool_tail()

        """    541 <any_expr>	=>	(	<univ_paren_dispatch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_5"]:
        self.parse_token("(")
        self.univ_paren_dispatch()

        """    542 <any_expr>	=>	not	<strict_flag_expr>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_6"]:
        self.parse_token("not")
        self.strict_flag_expr()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_ambig_tail(self):
    self.appendF(FIRST_SET["<univ_ambig_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    543 <univ_ambig_tail>	=>	+	<univ_ambig_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>"]:
        self.parse_token("+")
        self.univ_ambig_branch()

        """    544 <univ_ambig_tail>	=>	-	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_1"]:
        self.parse_token("-")
        self.univ_ambig_numeric_branch()

        """    545 <univ_ambig_tail>	=>	*	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_2"]:
        self.parse_token("*")
        self.univ_ambig_numeric_branch()

        """    546 <univ_ambig_tail>	=>	/	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_3"]:
        self.parse_token("/")
        self.univ_ambig_numeric_branch()

        """    547 <univ_ambig_tail>	=>	%	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_4"]:
        self.parse_token("%")
        self.univ_ambig_numeric_branch()

        """    548 <univ_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_5"]:
        self.rel_op()
        self.strict_ambig_rhs()
        self.univ_bool_tail()

        """    549 <univ_ambig_tail>	=>	and	<strict_flag_factor>	<strict_flag_and_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_6"]:
        self.parse_token("and")
        self.strict_flag_factor()
        self.strict_flag_and_tail()

        """    550 <univ_ambig_tail>	=>	or	<strict_flag_term>	<strict_flag_or_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_7"]:
        self.parse_token("or")
        self.strict_flag_term()
        self.strict_flag_or_tail()

        """    551 <univ_ambig_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_tail>_8"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_ambig_branch(self):
    self.appendF(FIRST_SET["<univ_ambig_branch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    552 <univ_ambig_branch>	=>	<id>	<univ_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>"]:
        self.id_()
        self.univ_ambig_tail()

        """    553 <univ_ambig_branch>	=>	<ret_piece>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_1"]:
        self.ret_piece()
        self.univ_piece_tail()

        """    554 <univ_ambig_branch>	=>	<ret_sip>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_2"]:
        self.ret_sip()
        self.univ_sip_tail()

        """    555 <univ_ambig_branch>	=>	<ret_chars>	<univ_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_3"]:
        self.ret_chars()
        self.univ_str_tail()

        """    556 <univ_ambig_branch>	=>	(	<univ_paren_dispatch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_branch>_4"]:
        self.parse_token("(")
        self.univ_paren_dispatch()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_ambig_numeric_branch(self):
    self.appendF(FIRST_SET["<univ_ambig_numeric_branch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    557 <univ_ambig_numeric_branch>	=>	<id>	<univ_ambig_numeric_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>"]:
        self.id_()
        self.univ_ambig_numeric_tail()

        """    558 <univ_ambig_numeric_branch>	=>	<ret_piece>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_1"]:
        self.ret_piece()
        self.univ_piece_tail()

        """    559 <univ_ambig_numeric_branch>	=>	<ret_sip>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_2"]:
        self.ret_sip()
        self.univ_sip_tail()

        """    560 <univ_ambig_numeric_branch>	=>	(	<univ_paren_dispatch_numeric>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_branch>_3"]:
        self.parse_token("(")
        self.univ_paren_dispatch_numeric()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_ambig_numeric_tail(self):
    self.appendF(FIRST_SET["<univ_ambig_numeric_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    561 <univ_ambig_numeric_tail>	=>	+	<univ_ambig_numeric_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>"]:
        self.parse_token("+")
        self.univ_ambig_numeric_branch()

        """    562 <univ_ambig_numeric_tail>	=>	-	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_1"]:
        self.parse_token("-")
        self.univ_ambig_numeric_branch()

        """    563 <univ_ambig_numeric_tail>	=>	*	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_2"]:
        self.parse_token("*")
        self.univ_ambig_numeric_branch()

        """    564 <univ_ambig_numeric_tail>	=>	/	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_3"]:
        self.parse_token("/")
        self.univ_ambig_numeric_branch()

        """    565 <univ_ambig_numeric_tail>	=>	%	<univ_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_4"]:
        self.parse_token("%")
        self.univ_ambig_numeric_branch()

        """    566 <univ_ambig_numeric_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_5"]:
        self.rel_op()
        self.strict_ambig_rhs()
        self.univ_bool_tail()

        """    567 <univ_ambig_numeric_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_ambig_numeric_tail>_6"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_piece_tail(self):
    self.appendF(FIRST_SET["<univ_piece_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    568 <univ_piece_tail>	=>	+	<strict_piece_expr>	<univ_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>"]:
        self.parse_token("+")
        self.strict_piece_expr()
        self.univ_piece_tail()

        """    569 <univ_piece_tail>	=>	-	<strict_piece_expr>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_expr()
        self.univ_piece_tail()

        """    570 <univ_piece_tail>	=>	*	<strict_piece_expr>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_expr()
        self.univ_piece_tail()

        """    571 <univ_piece_tail>	=>	/	<strict_piece_expr>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_expr()
        self.univ_piece_tail()

        """    572 <univ_piece_tail>	=>	%	<strict_piece_expr>	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_expr()
        self.univ_piece_tail()

        """    573 <univ_piece_tail>	=>	<rel_op>	<strict_piece_expr>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_5"]:
        self.rel_op()
        self.strict_piece_expr()
        self.univ_bool_tail()

        """    574 <univ_piece_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_piece_tail>_6"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_sip_tail(self):
    self.appendF(FIRST_SET["<univ_sip_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    575 <univ_sip_tail>	=>	+	<strict_sip_expr>	<univ_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>"]:
        self.parse_token("+")
        self.strict_sip_expr()
        self.univ_sip_tail()

        """    576 <univ_sip_tail>	=>	-	<strict_sip_expr>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_1"]:
        self.parse_token("-")
        self.strict_sip_expr()
        self.univ_sip_tail()

        """    577 <univ_sip_tail>	=>	*	<strict_sip_expr>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_2"]:
        self.parse_token("*")
        self.strict_sip_expr()
        self.univ_sip_tail()

        """    578 <univ_sip_tail>	=>	/	<strict_sip_expr>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_3"]:
        self.parse_token("/")
        self.strict_sip_expr()
        self.univ_sip_tail()

        """    579 <univ_sip_tail>	=>	%	<strict_sip_expr>	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_4"]:
        self.parse_token("%")
        self.strict_sip_expr()
        self.univ_sip_tail()

        """    580 <univ_sip_tail>	=>	<rel_op>	<strict_sip_expr>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_5"]:
        self.rel_op()
        self.strict_sip_expr()
        self.univ_bool_tail()

        """    581 <univ_sip_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_sip_tail>_6"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_str_tail(self):
    self.appendF(FIRST_SET["<univ_str_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    582 <univ_str_tail>	=>	+	<strict_chars_expr>	<univ_str_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_str_tail>"]:
        self.parse_token("+")
        self.strict_chars_expr()
        self.univ_str_tail()

        """    583 <univ_str_tail>	=>	<rel_op>	<strict_piece_expr>	<univ_bool_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_str_tail>_1"]:
        self.rel_op()
        self.strict_piece_expr()
        self.univ_bool_tail()

        """    584 <univ_str_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_str_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_bool_tail(self):
    self.appendF(FIRST_SET["<univ_bool_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    585 <univ_bool_tail>	=>	and	<strict_flag_expr>	<strict_flag_and_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_bool_tail>"]:
        self.parse_token("and")
        self.strict_flag_expr()
        self.strict_flag_and_tail()

        """    586 <univ_bool_tail>	=>	or	<strict_flag_expr>	<strict_flag_or_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_bool_tail>_1"]:
        self.parse_token("or")
        self.strict_flag_expr()
        self.strict_flag_or_tail()

        """    587 <univ_bool_tail>	=>	    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_bool_tail>_2"]:
        pass


    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_dispatch(self):
    self.appendF(FIRST_SET["<univ_paren_dispatch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    588 <univ_paren_dispatch>	=>	<id>	<univ_paren_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>"]:
        self.id_()
        self.univ_paren_ambig_tail()

        """    589 <univ_paren_dispatch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_1"]:
        self.ret_piece()
        self.univ_paren_piece_tail()

        """    590 <univ_paren_dispatch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_2"]:
        self.ret_sip()
        self.univ_paren_sip_tail()

        """    591 <univ_paren_dispatch>	=>	<ret_chars>	<univ_paren_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_3"]:
        self.ret_chars()
        self.univ_paren_str_tail()

        """    592 <univ_paren_dispatch>	=>	<ret_flag>	<univ_bool_tail>	)	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_4"]:
        self.ret_flag()
        self.univ_bool_tail()
        self.parse_token(")")
        self.parse_token(")")

        """    593 <univ_paren_dispatch>	=>	not	<strict_flag_factor>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_5"]:
        self.parse_token("not")
        self.strict_flag_factor()
        self.parse_token(")")

        """    594 <univ_paren_dispatch>	=>	(	<univ_paren_dispatch>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch>_6"]:
        self.parse_token("(")
        self.univ_paren_dispatch()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_dispatch_numeric(self):
    self.appendF(FIRST_SET["<univ_paren_dispatch_numeric>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    595 <univ_paren_dispatch_numeric>	=>	<id>	<univ_paren_ambig_numeric_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>"]:
        self.id_()
        self.univ_paren_ambig_numeric_tail()

        """    596 <univ_paren_dispatch_numeric>	=>	<ret_piece>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_1"]:
        self.ret_piece()
        self.univ_paren_piece_tail()

        """    597 <univ_paren_dispatch_numeric>	=>	<ret_sip>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_2"]:
        self.ret_sip()
        self.univ_paren_sip_tail()

        """    598 <univ_paren_dispatch_numeric>	=>	(	<univ_paren_dispatch_numeric>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_numeric>_3"]:
        self.parse_token("(")
        self.univ_paren_dispatch_numeric()
        self.parse_token(")")

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_dispatch_piece(self):
    self.appendF(FIRST_SET["<univ_paren_dispatch_piece>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    599 <univ_paren_dispatch_piece>	=>	<id>	<univ_paren_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_piece>"]:
        self.id_()
        self.univ_paren_piece_tail()

        """    600 <univ_paren_dispatch_piece>	=>	<ret_piece>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_piece>_1"]:
        self.ret_piece()
        self.univ_paren_piece_tail()

        """    601 <univ_paren_dispatch_piece>	=>	(	<univ_paren_dispatch_piece>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_piece>_2"]:
        self.parse_token("(")
        self.univ_paren_dispatch_piece()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_dispatch_sip(self):
    self.appendF(FIRST_SET["<univ_paren_dispatch_sip>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    602 <univ_paren_dispatch_sip>	=>	<id>	<univ_paren_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_sip>"]:
        self.id_()
        self.univ_paren_sip_tail()

        """    603 <univ_paren_dispatch_sip>	=>	<ret_sip>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_sip>_1"]:
        self.ret_sip()
        self.univ_paren_sip_tail()

        """    604 <univ_paren_dispatch_sip>	=>	(	<univ_paren_dispatch_sip>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_sip>_2"]:
        self.parse_token("(")
        self.univ_paren_dispatch_sip()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_dispatch_str(self):
    self.appendF(FIRST_SET["<univ_paren_dispatch_str>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    605 <univ_paren_dispatch_str>	=>	<id>	<univ_paren_str_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_str>"]:
        self.id_()
        self.univ_paren_str_tail()

        """    606 <univ_paren_dispatch_str>	=>	<ret_chars>	<univ_paren_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_str>_1"]:
        self.ret_chars()
        self.univ_paren_str_tail()

        """    607 <univ_paren_dispatch_str>	=>	(	<univ_paren_dispatch_str>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_dispatch_str>_2"]:
        self.parse_token("(")
        self.univ_paren_dispatch_str()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_ambig_tail(self):
    self.appendF(FIRST_SET["<univ_paren_ambig_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    608 <univ_paren_ambig_tail>	=>	+	<univ_paren_ambig_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>"]:
        self.parse_token("+")
        self.univ_paren_ambig_branch()

        """    609 <univ_paren_ambig_tail>	=>	-	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_1"]:
        self.parse_token("-")
        self.univ_paren_ambig_numeric_branch()

        """    610 <univ_paren_ambig_tail>	=>	*	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_2"]:
        self.parse_token("*")
        self.univ_paren_ambig_numeric_branch()

        """    611 <univ_paren_ambig_tail>	=>	/	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_3"]:
        self.parse_token("/")
        self.univ_paren_ambig_numeric_branch()

        """    612 <univ_paren_ambig_tail>	=>	%	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_4"]:
        self.parse_token("%")
        self.univ_paren_ambig_numeric_branch()

        """    613 <univ_paren_ambig_tail>	=>	<rel_op>	<strict_ambig_rhs>	<univ_bool_tail>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_5"]:
        self.rel_op()
        self.strict_ambig_rhs()
        self.univ_bool_tail()
        self.parse_token(")")

        """    614 <univ_paren_ambig_tail>	=>	)	<univ_ambig_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_tail>_6"]:
        self.parse_token(")")
        self.univ_ambig_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_ambig_branch(self):
    self.appendF(FIRST_SET["<univ_paren_ambig_branch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    615 <univ_paren_ambig_branch>	=>	<id>	<univ_paren_ambig_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>"]:
        self.id_()
        self.univ_paren_ambig_tail()

        """    616 <univ_paren_ambig_branch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_1"]:
        self.ret_piece()
        self.univ_paren_piece_tail()

        """    617 <univ_paren_ambig_branch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_2"]:
        self.ret_sip()
        self.univ_paren_sip_tail()

        """    618 <univ_paren_ambig_branch>	=>	<ret_chars>	<univ_paren_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_3"]:
        self.ret_chars()
        self.univ_paren_str_tail()

        """    619 <univ_paren_ambig_branch>	=>	(	<univ_paren_dispatch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_branch>_4"]:
        self.parse_token("(")
        self.univ_paren_dispatch()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_ambig_numeric_tail(self):
    self.appendF(FIRST_SET["<univ_paren_ambig_numeric_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    620 <univ_paren_ambig_numeric_tail>	=>	+	<univ_paren_ambig_numeric_branch>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>"]:
        self.parse_token("+")
        self.univ_paren_ambig_numeric_branch()

        """    621 <univ_paren_ambig_numeric_tail>	=>	-	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_1"]:
        self.parse_token("-")
        self.univ_paren_ambig_numeric_branch()

        """    622 <univ_paren_ambig_numeric_tail>	=>	*	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_2"]:
        self.parse_token("*")
        self.univ_paren_ambig_numeric_branch()

        """    623 <univ_paren_ambig_numeric_tail>	=>	/	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_3"]:
        self.parse_token("/")
        self.univ_paren_ambig_numeric_branch()

        """    624 <univ_paren_ambig_numeric_tail>	=>	%	<univ_paren_ambig_numeric_branch>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_4"]:
        self.parse_token("%")
        self.univ_paren_ambig_numeric_branch()

        """    625 <univ_paren_ambig_numeric_tail>	=>	)	<univ_ambig_numeric_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_tail>_5"]:
        self.parse_token(")")
        self.univ_ambig_numeric_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_ambig_numeric_branch(self):
    self.appendF(FIRST_SET["<univ_paren_ambig_numeric_branch>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    626 <univ_paren_ambig_numeric_branch>	=>	<id>	<univ_paren_ambig_numeric_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>"]:
        self.id_()
        self.univ_paren_ambig_numeric_tail()

        """    627 <univ_paren_ambig_numeric_branch>	=>	<ret_piece>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_1"]:
        self.ret_piece()
        self.univ_paren_piece_tail()

        """    628 <univ_paren_ambig_numeric_branch>	=>	<ret_sip>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_2"]:
        self.ret_sip()
        self.univ_paren_sip_tail()

        """    629 <univ_paren_ambig_numeric_branch>	=>	(	<univ_paren_dispatch_numeric>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_ambig_numeric_branch>_3"]:
        self.parse_token("(")
        self.univ_paren_dispatch_numeric()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_piece_tail(self):
    self.appendF(FIRST_SET["<univ_paren_piece_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    630 <univ_paren_piece_tail>	=>	+	<strict_piece_factor>	<univ_paren_piece_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>"]:
        self.parse_token("+")
        self.strict_piece_factor()
        self.univ_paren_piece_tail()

        """    631 <univ_paren_piece_tail>	=>	-	<strict_piece_factor>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_1"]:
        self.parse_token("-")
        self.strict_piece_factor()
        self.univ_paren_piece_tail()

        """    632 <univ_paren_piece_tail>	=>	*	<strict_piece_factor>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_2"]:
        self.parse_token("*")
        self.strict_piece_factor()
        self.univ_paren_piece_tail()

        """    633 <univ_paren_piece_tail>	=>	/	<strict_piece_factor>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_3"]:
        self.parse_token("/")
        self.strict_piece_factor()
        self.univ_paren_piece_tail()

        """    634 <univ_paren_piece_tail>	=>	%	<strict_piece_factor>	<univ_paren_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_4"]:
        self.parse_token("%")
        self.strict_piece_factor()
        self.univ_paren_piece_tail()

        """    635 <univ_paren_piece_tail>	=>	)	<univ_piece_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_piece_tail>_5"]:
        self.parse_token(")")
        self.univ_piece_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_sip_tail(self):
    self.appendF(FIRST_SET["<univ_paren_sip_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    636 <univ_paren_sip_tail>	=>	+	<strict_sip_factor>	<univ_paren_sip_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>"]:
        self.parse_token("+")
        self.strict_sip_factor()
        self.univ_paren_sip_tail()

        """    637 <univ_paren_sip_tail>	=>	-	<strict_sip_factor>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_1"]:
        self.parse_token("-")
        self.strict_sip_factor()
        self.univ_paren_sip_tail()

        """    638 <univ_paren_sip_tail>	=>	*	<strict_sip_factor>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_2"]:
        self.parse_token("*")
        self.strict_sip_factor()
        self.univ_paren_sip_tail()

        """    639 <univ_paren_sip_tail>	=>	/	<strict_sip_factor>	<univ_paren_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_3"]:
        self.parse_token("/")
        self.strict_sip_factor()
        self.univ_paren_sip_tail()

        """    640 <univ_paren_sip_tail>	=>	)	<univ_sip_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_sip_tail>_4"]:
        self.parse_token(")")
        self.univ_sip_tail()

    else: self.parse_token(self.error_arr)

    log.info("Exit: " + self.tokens[self.pos].type) # J

def univ_paren_str_tail(self):
    self.appendF(FIRST_SET["<univ_paren_str_tail>"])
    log.info("Enter: " + self.tokens[self.pos].type)
    log.info("STACK: " + str(self.error_arr))

    """    641 <univ_paren_str_tail>	=>	+	<strict_string_factor>	<univ_paren_str_tail>    """
    if self.tokens[self.pos].type in PREDICT_SET["<univ_paren_str_tail>"]:
        self.parse_token("+")
        self.strict_string_factor()
        self.univ_paren_str_tail()

        """    642 <univ_paren_str_tail>	=>	)	<univ_str_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<univ_paren_str_tail>_1"]:
        self.parse_token(")")
        self.univ_str_tail()

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
    elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_5"]:
        pass


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
