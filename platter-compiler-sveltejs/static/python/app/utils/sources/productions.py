def strict_piece_expr_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    1 <strict_piece_expr_upd>	=>	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr_upd>"]:
        self.strict_piece_term_upd()
        self.strict_piece_add_tail_upd()
    else: self.parse_token(PREDICT_SET_M["<strict_piece_expr_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_term_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    2 <strict_piece_term_upd>	=>	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term_upd>"]:
        self.strict_piece_factor_upd()
        self.strict_piece_mult_tail_upd()
    else: self.parse_token(PREDICT_SET_M["<strict_piece_term_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_factor_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    3 <strict_piece_factor_upd>	=>	<ret_piece_upd>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>"]:
        self.ret_piece_upd()

        """    4 <strict_piece_factor_upd>	=>	id	<id_tail>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>_1"]:
        self.parse_token("id")
        self.id_tail()

        """    5 <strict_piece_factor_upd>	=>	(	<strict_piece_expr_upd>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor_upd>_2"]:
        self.parse_token("(")
        self.strict_piece_expr_upd()
        self.parse_token(")")

    else: self.parse_token(PREDICT_SET_M["<strict_piece_factor_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J

def ret_piece_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    6 <ret_piece_upd>	=>	topiece	(	<any_expr>	)    """
    if self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>"]:
        self.parse_token("topiece")
        self.parse_token("(")
        self.any_expr()
        self.parse_token(")")

        """    7 <ret_piece_upd>	=>	fact	(	<strict_piece_expr_upd>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_1"]:
        self.parse_token("fact")
        self.parse_token("(")
        self.strict_piece_expr_upd()
        self.parse_token(")")

        """    8 <ret_piece_upd>	=>	pow	(	<strict_piece_expr_upd>	,	<strict_piece_expr_upd>	)    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_2"]:
        self.parse_token("pow")
        self.parse_token("(")
        self.strict_piece_expr_upd()
        self.parse_token(",")
        self.strict_piece_expr_upd()
        self.parse_token(")")

        """    9 <ret_piece_upd>	=>	piece_lit    """
    elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece_upd>_3"]:
        self.parse_token("piece_lit")

    else: self.parse_token(PREDICT_SET_M["<ret_piece_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_add_tail_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    10 <strict_piece_add_tail_upd>	=>	+	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>"]:
        self.parse_token("+")
        self.strict_piece_term_upd()
        self.strict_piece_add_tail_upd()

        """    11 <strict_piece_add_tail_upd>	=>	-	<strict_piece_term_upd>	<strict_piece_add_tail_upd>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>_1"]:
        self.parse_token("-")
        self.strict_piece_term_upd()
        self.strict_piece_add_tail_upd()

        """    12 <strict_piece_add_tail_upd>	=>	λ    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail_upd>_2"]:
        self.parse_token("λ")

    else: self.parse_token(PREDICT_SET_M["<strict_piece_add_tail_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J

def strict_piece_mult_tail_upd(self):
    log.info("Enter: " + self.tokens[self.pos].type) # J

    """    13 <strict_piece_mult_tail_upd>	=>	*	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
    if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>"]:
        self.parse_token("*")
        self.strict_piece_factor_upd()
        self.strict_piece_mult_tail_upd()

        """    14 <strict_piece_mult_tail_upd>	=>	/	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_1"]:
        self.parse_token("/")
        self.strict_piece_factor_upd()
        self.strict_piece_mult_tail_upd()

        """    15 <strict_piece_mult_tail_upd>	=>	%	<strict_piece_factor_upd>	<strict_piece_mult_tail_upd>    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_2"]:
        self.parse_token("%")
        self.strict_piece_factor_upd()
        self.strict_piece_mult_tail_upd()

        """    16 <strict_piece_mult_tail_upd>	=>	λ    """
    elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail_upd>_3"]:
        self.parse_token("λ")

    else: self.parse_token(PREDICT_SET_M["<strict_piece_mult_tail_upd>"])

    log.info("Exit: " + self.tokens[self.pos].type) # J
