import os
from enum import Enum, auto


class TokenType(Enum):

    Unknown = auto()

    EOF = auto()

    OpenBrace = auto()
    CloseBrace = auto()
    OpenAngleBracket = auto()
    CloseAngleBracket = auto()
    OpenBracket = auto()
    CloseBracket = auto()
    OpenSqBracket = auto()
    CloseSqBracket = auto()
    Assing = auto()
    Comma = auto()
    Asterisk = auto()
    Ampersand = auto()
    Colon = auto()
    # DoubleColon = auto()
    Semicolon = auto()

    CharLiteral = auto()
    WCharLiteral = auto()
    StringLiteral = auto()
    WStringLiteral = auto()
    IntegerLiteral = auto()
    SingleFloatingLiteral = auto()
    DoubleFloatingLiteral = auto()
    TrueLiteral = auto()
    FalseLiteral = auto()

    CharType = auto()
    WCharType = auto()
    BoolType = auto()
    ByteType = auto()
    SizeTType = auto()
    HashTType = auto()
    UIntType = auto()
    IntType = auto()
    StringType = auto()
    WStringType = auto()
    ArrayType = auto()
    PtrArrayType = auto()
    SingleFloatingType = auto()
    DoubleFloatingType = auto()
    Vec2FType = auto()
    Vec2DType = auto()
    Vec2SType = auto()
    Vec2UType = auto()
    Vec3FType = auto()
    Vec3DType = auto()
    Vec3SType = auto()
    Vec3UType = auto()
    Vec4FType = auto()
    Vec4DType = auto()
    Vec4SType = auto()
    Vec4UType = auto()
    Mat2x2FType = auto()
    Mat3x3FType = auto()
    Mat4x4FType = auto()
    Rect2FType = auto()
    Rect2DType = auto()
    Rect2SType = auto()
    Rect2UType = auto()

    ClassType = auto()
    # StructType = auto()
    # EnumType = auto()
    # InterfaceType = auto()

    # Owner = auto()
    ReadOnly = auto()
    WriteOnly = auto()
    Private = auto()
    WriteCallback = auto()
    ReadCallback = auto()
    Virtual = auto()
    ExpectMin = auto()
    ExpectMax = auto()
    ForceMin = auto()
    ForceMax = auto()
    # NoDuplicate = auto()
    Transient = auto()
    # AdditionalInterface = auto()
    # SerializationCallback = auto()
    # DllEntry = auto()

    # ConstModifier = auto()

    Identifier = auto()


class Token:

    def __init__(self, type, line, column, filepath, text='???'):

        self.type = type
        self.text = text
        self.line = line
        self.column = column
        self.filepath = filepath

    def __str__(self):
        return f'[{self.filepath}' '(l:{:4d}, c:{:4d})]: '.format(self.line, self.column) + f'"{self.text}" ({self.type})'


class Tokenizer:

    SPECIAL_SYMBOL_TOKEN_TYPES = {
        '{': TokenType.OpenBrace,
        '}': TokenType.CloseBrace,
        '<': TokenType.OpenAngleBracket,
        '>': TokenType.CloseAngleBracket,
        '(': TokenType.OpenBracket,
        ')': TokenType.CloseBracket,
        '[': TokenType.OpenSqBracket,
        ']': TokenType.CloseSqBracket,
        '=': TokenType.Assing,
        '*': TokenType.Asterisk,
        '&': TokenType.Ampersand,
        ',': TokenType.Comma,
        # '::': TokenType.DoubleColon,
        ':': TokenType.Colon,
        ';': TokenType.Semicolon
    }

    BUILTIN_VALUES = {
        'true': TokenType.TrueLiteral,
        'false': TokenType.FalseLiteral
    }

    BUILTIN_MODIFIERS = {
        # 'const': TokenType.ConstModifier
    }

    BUILTIN_PRIMITIVE_TYPES = {
        'epiChar': TokenType.CharType,
        'epiWChar': TokenType.WCharType,
        'epiBool': TokenType.BoolType,
        'epiByte': TokenType.ByteType,
        'epiSize_t': TokenType.SizeTType,
        'epiHash_t': TokenType.HashTType,
        'epiU8': TokenType.UIntType,
        'epiU16': TokenType.UIntType,
        'epiU32': TokenType.UIntType,
        'epiU64': TokenType.UIntType,
        'epiS8': TokenType.IntType,
        'epiS16': TokenType.IntType,
        'epiS32': TokenType.IntType,
        'epiS64': TokenType.IntType,
        'epiFloat': TokenType.SingleFloatingType,
        'epiDouble': TokenType.DoubleFloatingType
    }

    BUILTIN_COMPOUND_TYPES = {
        'epiString': TokenType.StringType,
        'epiWString': TokenType.WStringType,
        'epiArray': TokenType.ArrayType,
        'epiPtrArray': TokenType.PtrArrayType,
        'epiVec2f': TokenType.Vec2FType,
        'epiVec2d': TokenType.Vec2DType,
        'epiVec2s': TokenType.Vec2SType,
        'epiVec2u': TokenType.Vec2UType,
        'epiVec3f': TokenType.Vec3FType,
        'epiVec3d': TokenType.Vec3DType,
        'epiVec3s': TokenType.Vec3SType,
        'epiVec3u': TokenType.Vec3UType,
        'epiVec4f': TokenType.Vec4FType,
        'epiVec4d': TokenType.Vec4DType,
        'epiVec4s': TokenType.Vec4SType,
        'epiVec4u': TokenType.Vec4UType,
        'epiMat2x2f': TokenType.Mat2x2FType,
        'epiMat3x3f': TokenType.Mat3x3FType,
        'epiMat4x4f': TokenType.Mat4x4FType,
        'epiRect2f': TokenType.Rect2FType,
        'epiRect2d': TokenType.Rect2DType,
        'epiRect2s': TokenType.Rect2SType,
        'epiRect2u': TokenType.Rect2UType
    }

    BUILTIN_USER_TYPES = {
        'class': TokenType.ClassType,
        # 'struct': TokenType.StructType,
        # 'enum': TokenType.EnumType,
        # 'interface': TokenType.InterfaceType
    }

    BUILTIN_CLSS_ATTRS = {
        # 'AdditionalInterface': TokenType.AdditionalInterface,
        # 'SerializationCallback': TokenType.SerializationCallback,
        # 'DllEntry': TokenType.DllEntry
    }

    BUILTIN_PRTY_ATTRS = {
        # 'Owner': TokenType.Owner,
        'ReadOnly': TokenType.ReadOnly,
        'WriteOnly': TokenType.WriteOnly,
        'Private': TokenType.Private,
        'WriteCallback': TokenType.WriteCallback,
        'ReadCallback': TokenType.ReadCallback,
        'Virtual': TokenType.Virtual,
        'ExpectMin': TokenType.ExpectMin,
        'ExpectMax': TokenType.ExpectMax,
        'ForceMin': TokenType.ForceMin,
        'ForceMax': TokenType.ForceMax,
        # 'NoDuplicate': TokenType.NoDuplicate,
        'Transient': TokenType.Transient,
        # 'DllEntry': TokenType.DllEntry
        # TBD: 'Hidden': TokenType.Hidden,
        # TBD: 'DisplayName': TokenType.DisplayName,
        # TBD: 'Description': TokenType.Description,
        # TBD: 'EventCallback': TokenType.EventCallback,
        # TBD: 'Category': TokenType.Category,
    }

    def __init__(self, abspath: str, relpath: str):

        with open(abspath, 'r') as f:
            self.content = f.read()

        self.content_len = len(self.content)
        self.__at = 0
        self.line = 1
        self.column = 1
        self.filepath = relpath
        self.tokens = []

    def _ch(self, offset: int = 0) -> chr:
        return self.content[self.at + offset] if self.at + offset < self.content_len else '\0'

    def _substring_until_at(self, start: int) -> str:
        return self.content[start:min(self.at, self.content_len)]

    @property
    def at(self):
        return self.__at

    @at.setter
    def at(self, at):

        if self._ch() == '\n':

            self.line += 1
            self.column = 1

        self.column += at - self.__at
        self.__at = at

    @staticmethod
    def is_keyword(type):
        return type in\
            Tokenizer.BUILTIN_PRIMITIVE_TYPES.keys() |\
            Tokenizer.BUILTIN_COMPOUND_TYPES.keys() |\
            Tokenizer.BUILTIN_USER_TYPES.keys() |\
            Tokenizer.BUILTIN_PRTY_ATTRS.keys() |\
            Tokenizer.BUILTIN_CLSS_ATTRS.keys() |\
            Tokenizer.BUILTIN_MODIFIERS.keys() |\
            Tokenizer.BUILTIN_VALUES.keys()

    def tokenize(self):

        try:

            while self.at < self.content_len:

                ch = self._ch()

                if ch.isspace():
                    self.at += 1
                elif ch == '#':

                    while self._ch() not in ['\n', '\0']:
                        self.at += 1

                elif ch == '\'' or (ch == 'L' and self._ch(1) == '\''):
                    self._tokenize_char_literal()
                elif ch == '"' or (ch == 'L' and self._ch(1) == '"'):
                    self._tokenize_string_literal()
                elif self._try_tokenize_special_symbol():
                    pass
                elif ch.isnumeric() or ((ch == '-' or ch == '+') and self._ch(1).isnumeric()):
                    self._tokenize_numeric_literal()
                elif ch.isalpha():
                    self._tokenize_term()
                else:
                    self.tokens.append(Token(TokenType.Unknown, self.line, self.column, self.filepath, ch))
                    self.at += 1

        except IndexError:
            pass
        else:
            self.tokens.append(Token(TokenType.EOF, self.line, self.column, self.filepath, 'EOF'))

        for token in self.tokens:

            if token.text in Tokenizer.BUILTIN_PRIMITIVE_TYPES:
                token.type = Tokenizer.BUILTIN_PRIMITIVE_TYPES[token.text]
            elif token.text in Tokenizer.BUILTIN_COMPOUND_TYPES:
                token.type = Tokenizer.BUILTIN_COMPOUND_TYPES[token.text]
            elif token.text in Tokenizer.BUILTIN_USER_TYPES:
                token.type = Tokenizer.BUILTIN_USER_TYPES[token.text]
            elif token.text in Tokenizer.BUILTIN_PRTY_ATTRS:
                token.type = Tokenizer.BUILTIN_PRTY_ATTRS[token.text]
            elif token.text in Tokenizer.BUILTIN_CLSS_ATTRS:
                token.type = Tokenizer.BUILTIN_CLSS_ATTRS[token.text]
            elif token.text in Tokenizer.BUILTIN_MODIFIERS:
                token.type = Tokenizer.BUILTIN_MODIFIERS[token.text]
            elif token.text in Tokenizer.BUILTIN_VALUES:
                token.type = Tokenizer.BUILTIN_VALUES[token.text]

        return self.tokens

    def _try_tokenize_special_symbol(self):

        token = None
        for text, type in Tokenizer.SPECIAL_SYMBOL_TOKEN_TYPES.items():

            if self.content.startswith(text, self.at):

                token = Token(type, self.line, self.column, self.filepath, text)
                break

        if not token:
            return False

        self.at += len(token.text)

        if token.type == TokenType.Semicolon and len(self.tokens) > 0 and self.tokens[-1].type == TokenType.Semicolon:
            return False

        self.tokens.append(token)

        return True

    def _tokenize_string_literal(self):

        token = Token(TokenType.Unknown, self.line, self.column, self.filepath)
        suspected_type = TokenType.StringLiteral
        begin = self.at
        if self._ch() == 'L':

            suspected_type = TokenType.WStringLiteral
            self.at += 1

        self.at += 1

        while self._ch() not in ['"', '\0']:

            if self._ch() == '\\':
                self.at += 1

            self.at += 1

        if self._ch() == '"' and self.line == token.line:

            token.type = suspected_type
            self.at += 1

        token.text = self._substring_until_at(begin)
        self.tokens.append(token)

    def _tokenize_char_literal(self):

        # TODO: add unicode support (like: '\u8080')
        # (see: https://docs.microsoft.com/en-us/cpp/cpp/string-and-character-literals-cpp?view=vs-2019)

        token = Token(TokenType.Unknown, self.line, self.column, self.filepath)
        suspected_type = TokenType.CharLiteral
        begin = self.at
        if self._ch() == 'L':

            suspected_type = TokenType.WCharLiteral
            self.at += 1

        self.at += 1

        if self._ch() == '\\':
            self.at += 1

        self.at += 1
        if self._ch() == "'":

            token.type = suspected_type
            self.at += 1

        token.text = self._substring_until_at(begin)
        self.tokens.append(token)

    def _tokenize_term(self):

        token = Token(TokenType.Unknown, self.line, self.column, self.filepath)
        begin = self.at

        if self._ch().isalpha() and self._ch().isupper():
            token.type = TokenType.Identifier

        while self._ch().isalnum() or self._ch() == '_':
            self.at += 1

        token.text = self._substring_until_at(begin)
        self.tokens.append(token)

    def _tokenize_numeric_literal(self):

        token = Token(TokenType.Unknown, self.line, self.column, self.filepath)
        suspected_type = TokenType.IntegerLiteral
        begin = self.at

        if self._ch() == '-' or self._ch() == '+':
            self.at += 1

        while self._ch().isnumeric():

            self.at += 1
            if self._ch() == '.':

                self.at += 1

                if self._ch().isnumeric() and suspected_type == TokenType.IntegerLiteral:
                    suspected_type = TokenType.DoubleFloatingLiteral
                else:
                    suspected_type = TokenType.Unknown

        if self._ch() == 'f' and suspected_type == TokenType.DoubleFloatingLiteral:

            suspected_type = TokenType.SingleFloatingLiteral
            self.at += 1

        if self._ch().isspace() or self._ch() in ['\0', ';']:
            token.type = suspected_type

        token.text = self._substring_until_at(begin)
        self.tokens.append(token)
