from app.lexer.token import Token
from app.lexer.protocol import LexerProtocol


class LexerKeywords(LexerProtocol):
    # --- 'a' ---
    def s1(self):
        self.advance()
        if self.current == "l": return self.s2()
        if self.current == "n": return self.s5()
        if self.current == "p": return self.s8()
        self.restore()
        return None

    def s2(self):  # al
        self.advance()
        if self.current == "t": return self.s3()
        self.restore()
        return None

    def s3(self):  # alt (Accepting State 4)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s4()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s4(self):
        return Token("alt", self.get_lexeme(), self.start_line, self.start_col)

    def s5(self):  # an
        self.advance()
        if self.current == "d": return self.s6()
        self.restore()
        return None

    def s6(self):  # and (Accepting State 7)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s7()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s7(self):
        return Token("and", self.get_lexeme(), self.start_line, self.start_col)

    def s8(self):  # ap
        self.advance()
        if self.current == "p": return self.s9()
        self.restore()
        return None

    def s9(self):  # app
        self.advance()
        if self.current == "e": return self.s10()
        self.restore()
        return None

    def s10(self):  # appe
        self.advance()
        if self.current == "n": return self.s11()
        self.restore()
        return None

    def s11(self):  # appen
        self.advance()
        if self.current == "d": return self.s12()
        self.restore()
        return None

    def s12(self):  # append (Accepting State 13)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s13()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s13(self):
        return Token("append", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'b' ---
    def s14(self):  # b
        self.advance()
        if self.current == "i": return self.s15()
        self.restore()
        return None

    def s15(self):  # bi
        self.advance()
        if self.current == "l": return self.s16()
        self.restore()
        return None

    def s16(self):  # bil
        self.advance()
        if self.current == "l": return self.s17()
        self.restore()
        return None

    def s17(self):  # bill (Accepting State 18)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s18()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s18(self):
        return Token("bill", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'c' ---
    def s19(self):  # c
        self.advance()
        if self.current == "h": return self.s20()
        if self.current == "o": return self.s34()
        if self.current == "u": return self.s38()
        self.restore()
        return None

    def s20(self):  # ch
        self.advance()
        if self.current == "a": return self.s21()
        if self.current == "e": return self.s25()
        if self.current == "o": return self.s29()
        self.restore()
        return None

    def s21(self):  # cha
        self.advance()
        if self.current == "r": return self.s22()
        self.restore()
        return None

    def s22(self):  # char
        self.advance()
        if self.current == "s": return self.s23()
        self.restore()
        return None

    def s23(self):  # chars (Accepting State 24)
        self.advance()
        if self._match_delimiter(self.dtype_dlm): return self.s24()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s24(self):
        return Token("chars", self.get_lexeme(), self.start_line, self.start_col)

    def s25(self):  # che
        self.advance()
        if self.current == "c": return self.s26()
        self.restore()
        return None

    def s26(self):  # chec
        self.advance()
        if self.current == "k": return self.s27()
        self.restore()
        return None

    def s27(self):  # check (Accepting State 28)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s28()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s28(self):
        return Token("check", self.get_lexeme(), self.start_line, self.start_col)

    def s29(self):  # cho
        self.advance()
        if self.current == "i": return self.s30()
        if self.current == "p": return self.s34()  # 'copy' starts with 'c-o-p'
        self.restore()
        return None

    def s30(self):  # choi
        self.advance()
        if self.current == "c": return self.s31()
        self.restore()
        return None

    def s31(self):  # choic
        self.advance()
        if self.current == "e": return self.s32()
        self.restore()
        return None

    def s32(self):  # choice (Accepting State 33)
        self.advance()
        if self._match_delimiter(self.whitespace): return self.s33()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s33(self):
        return Token("choice", self.get_lexeme(), self.start_line, self.start_col)

    def s34(self):  # cop
        self.advance()
        if self.current == "p": return self.s35()
        self.restore()
        return None

    def s35(self):  # copy (Accepting State 37)
        self.advance()
        if self.current == "y": return self.s36()
        self.restore()
        return None

    def s36(self):  # copy (Accepting State 37)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s37()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s37(self):  # copy (Accepting State 37)
        return Token("copy", self.get_lexeme(), self.start_line, self.start_col)

    def s38(self):  # cu
        self.advance()
        if self.current == "t": return self.s39()
        self.restore()
        return None

    def s39(self):  # cut (Accepting State 40)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s40()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s40(self):
        return Token("cut", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'd' ---
    def s41(self):  # d
        self.advance()
        if self.current == "o": return self.s42()
        self.restore()
        return None

    def s42(self):  # do
        self.advance()
        if self.current == "w": return self.s43()
        self.restore()
        return None

    def s43(self):  # dow
        self.advance()
        if self.current == "n": return self.s44()
        self.restore()
        return None

    def s44(self):  # down (Accepting State 45)
        self.advance()
        if self._match_delimiter(self.flag_dlm): return self.s45()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s45(self):
        return Token("flag_lit", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'f' ---
    def s46(self):  # f
        self.advance()
        if self.current == "a": return self.s47()
        if self.current == "l": return self.s51()
        self.restore()
        return None

    def s47(self):  # fa
        self.advance()
        if self.current == "c": return self.s48()
        self.restore()
        return None

    def s48(self):  # fac
        self.advance()
        if self.current == "t": return self.s49()
        self.restore()
        return None

    def s49(self):  # fact (Accepting State 50)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s50()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s50(self):
        return Token("fact", self.get_lexeme(), self.start_line, self.start_col)

    def s51(self):  # fl
        self.advance()
        if self.current == "a": return self.s52()
        self.restore()
        return None

    def s52(self):  # fla
        self.advance()
        if self.current == "g": return self.s53()
        self.restore()
        return None

    def s53(self):  # flag (Accepting State 54)
        self.advance()
        if self._match_delimiter(self.dtype_dlm): return self.s54()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s54(self):
        return Token("flag", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'i' ---
    def s55(self):  # i
        self.advance()
        if self.current == "n": return self.s56()
        self.restore()
        return None

    def s56(self):  # in
        self.advance()
        if self.current == "s": return self.s57()
        self.restore()
        return None

    def s57(self):  # ins
        self.advance()
        if self.current == "t": return self.s58()
        self.restore()
        return None

    def s58(self):  # inst
        self.advance()
        if self.current == "e": return self.s59()
        self.restore()
        return None

    def s59(self):  # inste
        self.advance()
        if self.current == "a": return self.s60()
        self.restore()
        return None

    def s60(self):  # instea
        self.advance()
        if self.current == "d": return self.s61()
        self.restore()
        return None

    def s61(self):  # instead (Accepting State 62)
        self.advance()
        if self._match_delimiter(self.curly_dlm): return self.s62()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s62(self):
        return Token("instead", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'm' ---
    def s63(self):  # m
        self.advance()
        if self.current == "a": return self.s64()
        if self.current == "e": return self.s71()
        self.restore()
        return None

    def s64(self):  # ma
        self.advance()
        if self.current == "t": return self.s65()
        self.restore()
        return None

    def s65(self):  # mat
        self.advance()
        if self.current == "c": return self.s66()
        self.restore()
        return None

    def s66(self):  # matc
        self.advance()
        if self.current == "h": return self.s67()
        self.restore()
        return None

    def s67(self):  # match
        self.advance()
        if self.current == "e": return self.s68()
        self.restore()
        return None

    def s68(self):  # matche
        self.advance()
        if self.current == "s": return self.s69()
        self.restore()
        return None

    def s69(self):  # matches (Accepting State 70)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s70()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s70(self):
        return Token("matches", self.get_lexeme(), self.start_line, self.start_col)

    def s71(self):  # me
        self.advance()
        if self.current == "n": return self.s72()
        self.restore()
        return None

    def s72(self):  # men
        self.advance()
        if self.current == "u": return self.s73()
        self.restore()
        return None

    def s73(self):  # menu (Accepting State 74)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s74()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s74(self):
        return Token("menu", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'n' ---
    def s75(self):  # n
        self.advance()
        if self.current == "e": return self.s76()
        if self.current == "o": return self.s80()
        self.restore()
        return None

    def s76(self):  # ne
        self.advance()
        if self.current == "x": return self.s77()
        self.restore()
        return None

    def s77(self):  # nex
        self.advance()
        if self.current == "t": return self.s78()
        self.restore()
        return None

    def s78(self):  # next (Accepting State 79)
        self.advance()
        if self._match_delimiter(self.term_dlm): return self.s79()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s79(self):
        return Token("next", self.get_lexeme(), self.start_line, self.start_col)

    def s80(self):  # no
        self.advance()
        if self.current == "t": return self.s81()
        self.restore()
        return None

    def s81(self):  # not (Accepting State 82)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s82()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s82(self):
        return Token("not", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'o' ---
    def s83(self):  # o
        self.advance()
        if self.current == "f": return self.s84()
        if self.current == "r": return self.s86()
        self.restore()
        return None

    def s84(self):  # of (Accepting State 85)
        self.advance()
        if self._match_delimiter(self.whitespace): return self.s85()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s85(self):
        return Token("of", self.get_lexeme(), self.start_line, self.start_col)

    def s86(self):  # or (Accepting State 87)
        self.advance()
        if self.current == "d": return self.s88()
        if self._match_delimiter(self.paren_dlm): return self.s87()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s87(self):
        return Token("or", self.get_lexeme(), self.start_line, self.start_col)

    def s88(self):  # ord
        self.advance()
        if self.current == "e": return self.s89()
        self.restore()
        return None

    def s89(self):  # orde
        self.advance()
        if self.current == "r": return self.s90()
        self.restore()
        return None

    def s90(self):  # order (Accepting State 91)
        self.advance()
        if self._match_delimiter(self.curly_dlm): return self.s91()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s91(self):
        return Token("order", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'p' ---
    def s92(self):  # p
        self.advance()
        if self.current == "a": return self.s93()
        if self.current == "i": return self.s97()
        if self.current == "o": return self.s102()
        if self.current == "r": return self.s105()
        self.restore()
        return None

    def s93(self):  # pa
        self.advance()
        if self.current == "s": return self.s94()
        self.restore()
        return None

    def s94(self):  # pas
        self.advance()
        if self.current == "s": return self.s95()
        self.restore()
        return None

    def s95(self):  # pass (Accepting State 96)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s96()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s96(self):
        return Token("pass", self.get_lexeme(), self.start_line, self.start_col)

    def s97(self):  # pi
        self.advance()
        if self.current == "e": return self.s98()
        self.restore()
        return None

    def s98(self):  # pie
        self.advance()
        if self.current == "c": return self.s99()
        self.restore()
        return None

    def s99(self):  # piec
        self.advance()
        if self.current == "e": return self.s100()
        self.restore()
        return None

    def s100(self):  # piece (Accepting State 101)
        self.advance()
        if self._match_delimiter(self.dtype_dlm): return self.s101()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s101(self):
        return Token("piece", self.get_lexeme(), self.start_line, self.start_col)

    def s102(self):  # po
        self.advance()
        if self.current == "w": return self.s103()
        self.restore()
        return None

    def s103(self):  # pow (Accepting State 104)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s104()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s104(self):
        return Token("pow", self.get_lexeme(), self.start_line, self.start_col)

    def s105(self):  # pr
        self.advance()
        if self.current == "e": return self.s106()
        self.restore()
        return None

    def s106(self):  # pre
        self.advance()
        if self.current == "p": return self.s107()
        self.restore()
        return None

    def s107(self):  # prep
        self.advance()
        if self.current == "a": return self.s108()
        self.restore()
        return None

    def s108(self):  # prepa
        self.advance()
        if self.current == "r": return self.s109()
        self.restore()
        return None

    def s109(self):  # prepar
        self.advance()
        if self.current == "e": return self.s110()
        self.restore()
        return None

    def s110(self):  # prepare (Accepting State 111)
        self.advance()
        if self._match_delimiter(self.whitespace): return self.s111()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s111(self):
        return Token("prepare", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'r' ---
    def s112(self):  # r
        self.advance()
        if self.current == "a": return self.s113()
        if self.current == "e": return self.s117()
        self.restore()
        return None

    def s113(self):  # ra
        self.advance()
        if self.current == "n": return self.s114()
        self.restore()
        return None

    def s114(self):  # ran
        self.advance()
        if self.current == "d": return self.s115()
        self.restore()
        return None

    def s115(self):  # rand (Accepting State 116)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s116()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s116(self):
        return Token("rand", self.get_lexeme(), self.start_line, self.start_col)

    def s117(self):  # re
        self.advance()
        if self.current == "m": return self.s118()
        if self.current == "p": return self.s123()
        if self.current == "v": return self.s128()
        self.restore()
        return None

    def s118(self):  # rem
        self.advance()
        if self.current == "o": return self.s119()
        self.restore()
        return None

    def s119(self):  # remo
        self.advance()
        if self.current == "v": return self.s120()
        self.restore()
        return None

    def s120(self):  # remov
        self.advance()
        if self.current == "e": return self.s121()
        self.restore()
        return None

    def s121(self):  # remove (Accepting State 122)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s122()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s122(self):
        return Token("remove", self.get_lexeme(), self.start_line, self.start_col)

    def s123(self):  # rep
        self.advance()
        if self.current == "e": return self.s124()
        self.restore()
        return None

    def s124(self):  # repe
        self.advance()
        if self.current == "a": return self.s125()
        self.restore()
        return None

    def s125(self):  # repea
        self.advance()
        if self.current == "t": return self.s126()
        self.restore()
        return None

    def s126(self):  # repeat (Accepting State 127)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s127()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s127(self):
        return Token("repeat", self.get_lexeme(), self.start_line, self.start_col)

    def s128(self):  # rev
        self.advance()
        if self.current == "e": return self.s129()
        self.restore()
        return None

    def s129(self):  # reve
        self.advance()
        if self.current == "r": return self.s130()
        self.restore()
        return None

    def s130(self):  # rever
        self.advance()
        if self.current == "s": return self.s131()
        self.restore()
        return None

    def s131(self):  # revers
        self.advance()
        if self.current == "e": return self.s132()
        self.restore()
        return None

    def s132(self):  # reverse (Accepting State 133)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s133()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s133(self):
        return Token("reverse", self.get_lexeme(), self.start_line, self.start_col)

    # --- 's' ---
    def s134(self):  # s
        self.advance()
        if self.current == "e": return self.s135()
        if self.current == "i": return self.s145()
        if self.current == "o": return self.s151()
        if self.current == "q": return self.s155()
        if self.current == "t": return self.s159()
        self.restore()
        return None

    def s135(self):  # se
        self.advance()
        if self.current == "a": return self.s136()
        if self.current == "r": return self.s141()
        self.restore()
        return None

    def s136(self):  # sea
        self.advance()
        if self.current == "r": return self.s137()
        self.restore()
        return None

    def s137(self):  # sear
        self.advance()
        if self.current == "c": return self.s138()
        self.restore()
        return None

    def s138(self):  # searc
        self.advance()
        if self.current == "h": return self.s139()
        self.restore()
        return None

    def s139(self):  # search (Accepting State 140)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s140()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s140(self):
        return Token("search", self.get_lexeme(), self.start_line, self.start_col)

    def s141(self):  # ser
        self.advance()
        if self.current == "v": return self.s142()
        self.restore()
        return None

    def s142(self):  # serv
        self.advance()
        if self.current == "e": return self.s143()
        self.restore()
        return None

    def s143(self):  # serve (Accepting State 144)
        self.advance()
        if self._match_delimiter(self.whitespace): return self.s144()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s144(self):
        return Token("serve", self.get_lexeme(), self.start_line, self.start_col)

    def s145(self):  # si
        self.advance()
        if self.current == "p": return self.s146()
        if self.current == "z": return self.s148()
        self.restore()
        return None

    def s146(self):  # sip (Accepting State 147)
        self.advance()
        if self._match_delimiter(self.dtype_dlm): return self.s147()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s147(self):
        return Token("sip", self.get_lexeme(), self.start_line, self.start_col)

    def s148(self):  # siz
        self.advance()
        if self.current == "e": return self.s149()
        self.restore()
        return None

    def s149(self):  # size (Accepting State 150)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s150()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s150(self):
        return Token("size", self.get_lexeme(), self.start_line, self.start_col)

    def s151(self):  # so
        self.advance()
        if self.current == "r": return self.s152()
        self.restore()
        return None

    def s152(self):  # sor
        self.advance()
        if self.current == "t": return self.s153()
        self.restore()
        return None

    def s153(self):  # sort (Accepting State 154)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s154()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s154(self):
        return Token("sort", self.get_lexeme(), self.start_line, self.start_col)

    def s155(self):  # sq
        self.advance()
        if self.current == "r": return self.s156()
        self.restore()
        return None

    def s156(self):  # sqr
        self.advance()
        if self.current == "t": return self.s157()
        self.restore()
        return None

    def s157(self):  # sqrt (Accepting State 158)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s158()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s158(self):
        return Token("sqrt", self.get_lexeme(), self.start_line, self.start_col)

    def s159(self):  # st
        self.advance()
        if self.current == "a": return self.s160()
        if self.current == "o": return self.s164()
        self.restore()
        return None

    def s160(self):  # sta
        self.advance()
        if self.current == "r": return self.s161()
        self.restore()
        return None

    def s161(self):  # star
        self.advance()
        if self.current == "t": return self.s162()
        self.restore()
        return None

    def s162(self):  # start (Accepting State 163)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s163()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s163(self):
        return Token("start", self.get_lexeme(), self.start_line, self.start_col)

    def s164(self):  # sto
        self.advance()
        if self.current == "p": return self.s165()
        self.restore()
        return None

    def s165(self):  # stop (Accepting State 166)
        self.advance()
        if self._match_delimiter(self.term_dlm): return self.s166()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s166(self):
        return Token("stop", self.get_lexeme(), self.start_line, self.start_col)

    # --- 't' ---
    def s167(self):  # t
        self.advance()
        if self.current == "a": return self.s168()
        if self.current == "o": return self.s176()
        self.restore()
        return None

    def s168(self):  # ta
        self.advance()
        if self.current == "b": return self.s169()
        if self.current == "k": return self.s173()
        self.restore()
        return None

    def s169(self):  # tab
        self.advance()
        if self.current == "l": return self.s170()
        self.restore()
        return None

    def s170(self):  # tabl
        self.advance()
        if self.current == "e": return self.s171()
        self.restore()
        return None

    def s171(self):  # table (Accepting State 172)
        self.advance()
        if self._match_delimiter(self.whitespace): return self.s172()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s172(self):
        return Token("table", self.get_lexeme(), self.start_line, self.start_col)

    def s173(self):  # tak
        self.advance()
        if self.current == "e": return self.s174()
        self.restore()
        return None

    def s174(self):  # take (Accepting State 175)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s175()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s175(self):
        return Token("take", self.get_lexeme(), self.start_line, self.start_col)

    def s176(self):  # to
        self.advance()
        if self.current == "c": return self.s177()
        if self.current == "p": return self.s183()
        if self.current == "s": return self.s189()
        self.restore()
        return None

    def s177(self):  # toc
        self.advance()
        if self.current == "h": return self.s178()
        self.restore()
        return None

    def s178(self):  # toch
        self.advance()
        if self.current == "a": return self.s179()
        self.restore()
        return None

    def s179(self):  # tocha
        self.advance()
        if self.current == "r": return self.s180()
        self.restore()
        return None

    def s180(self):  # tochar
        self.advance()
        if self.current == "s": return self.s181()
        self.restore()
        return None

    def s181(self):  # tochars (Accepting State 182)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s182()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s182(self):
        return Token("tochars", self.get_lexeme(), self.start_line, self.start_col)

    def s183(self):  # top
        self.advance()
        if self.current == "i": return self.s184()
        self.restore()
        return None

    def s184(self):  # topi
        self.advance()
        if self.current == "e": return self.s185()
        self.restore()
        return None

    def s185(self):  # topie
        self.advance()
        if self.current == "c": return self.s186()
        self.restore()
        return None

    def s186(self):  # topiec
        self.advance()
        if self.current == "e": return self.s187()
        self.restore()
        return None

    def s187(self):  # topiece (Accepting State 188)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s188()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s188(self):
        return Token("topiece", self.get_lexeme(), self.start_line, self.start_col)

    def s189(self):  # tos
        self.advance()
        if self.current == "i": return self.s190()
        self.restore()
        return None

    def s190(self):  # tosi
        self.advance()
        if self.current == "p": return self.s191()
        self.restore()
        return None

    def s191(self):  # tosip (Accepting State 192)
        self.advance()
        if self._match_delimiter(self.paren_dlm): return self.s192()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s192(self):
        return Token("tosip", self.get_lexeme(), self.start_line, self.start_col)

    # --- 'u' ---
    def s193(self):  # u
        self.advance()
        if self.current == "p": return self.s194()
        if self.current == "s": return self.s196()
        self.restore()
        return None

    def s194(self):  # up (Accepting State 195)
        self.advance()
        if self._match_delimiter(self.flag_dlm): return self.s195()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s195(self):
        return Token("flag_lit", self.get_lexeme(), self.start_line, self.start_col)

    def s196(self):  # us
        self.advance()
        if self.current == "u": return self.s197()
        self.restore()
        return None

    def s197(self):  # usu
        self.advance()
        if self.current == "a": return self.s198()
        self.restore()
        return None

    def s198(self):  # usua
        self.advance()
        if self.current == "l": return self.s199()
        self.restore()
        return None

    def s199(self):  # usual (Accepting State 200)
        self.advance()
        if self._match_delimiter(self.colon_dlm): return self.s200()
        elif self.current not in self.id_chars:
            tok = Token(Token.InvalidLexemeReserved, self.get_lexeme(), self.start_line, self.start_col)
            return tok
        self.restore()
        return None

    def s200(self):
        return Token("usual", self.get_lexeme(), self.start_line, self.start_col)
