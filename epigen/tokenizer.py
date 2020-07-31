import os
from enum import Enum, auto, unique


@unique
class TokenType(Enum):

    Unknown = auto()

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
    UInt8Type = auto()
    UInt16Type = auto()
    UInt32Type = auto()
    UInt64Type = auto()
    Int8Type = auto()
    Int16Type = auto()
    Int32Type = auto()
    Int64Type = auto()
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

    Identifier = auto()

    ClassType = auto()
    # StructType = auto()
    # EnumType = auto()
    # InterfaceType = auto()

    # Owner = auto()
    ReadOnly = auto()
    WriteOnly = auto()
    # Private = auto()
    ReadCallback = auto()
    WriteCallback = auto()
    Virtual = auto()
    Min = auto()
    Max = auto()
    # NoDuplicate = auto()
    Transient = auto()
    # AdditionalInterface = auto()
    # SerializationCallback = auto()
    # DllEntry = auto()

    # ConstModifier = auto()

    @staticmethod
    def repr_of(tokentype) -> str:

        for k, v in Tokenizer.keywords().items():

            if v == tokentype:
                return k

        return None

    @staticmethod
    def builtin_types() -> list:
        return list(Tokenizer.builtin_types().values())

    @staticmethod
    def fundamentals() -> list:
        return list(Tokenizer.fundamentals().values())

    @staticmethod
    def compounds() -> list:
        return list(Tokenizer.compounds().values())

    @staticmethod
    def attributes() -> list:
        return \
            list(Tokenizer.BUILTIN_CLSS_ATTRS.values()) + \
            list(Tokenizer.BUILTIN_PRTY_ATTRS.values())

    @staticmethod
    def literals() -> list:
        return [
            TokenType.CharLiteral,
            TokenType.WCharLiteral,
            TokenType.StringLiteral,
            TokenType.WStringLiteral,
            TokenType.IntegerLiteral,
            TokenType.SingleFloatingLiteral,
            TokenType.DoubleFloatingLiteral,
            TokenType.TrueLiteral,
            TokenType.FalseLiteral
        ]

    @staticmethod
    def assignable() -> list:
        return [
            TokenType.BoolType,
            TokenType.ByteType,
            TokenType.Int8Type,
            TokenType.Int16Type,
            TokenType.Int32Type,
            TokenType.Int64Type,
            TokenType.UInt8Type,
            TokenType.UInt16Type,
            TokenType.UInt32Type,
            TokenType.UInt64Type,
            TokenType.SizeTType,
            TokenType.HashTType,
            TokenType.SingleFloatingType,
            TokenType.DoubleFloatingType,
            TokenType.CharType,
            TokenType.WCharType,
            TokenType.StringType,
            TokenType.WStringType
        ]

    @staticmethod
    def literals_of(tokentype) -> list:

        literals = {
            TokenType.BoolType: [TokenType.FalseLiteral, TokenType.TrueLiteral],
            TokenType.ByteType: [TokenType.IntegerLiteral],
            TokenType.Int8Type: [TokenType.IntegerLiteral],
            TokenType.Int16Type: [TokenType.IntegerLiteral],
            TokenType.Int32Type: [TokenType.IntegerLiteral],
            TokenType.Int64Type: [TokenType.IntegerLiteral],
            TokenType.UInt8Type: [TokenType.IntegerLiteral],
            TokenType.UInt16Type: [TokenType.IntegerLiteral],
            TokenType.UInt32Type: [TokenType.IntegerLiteral],
            TokenType.UInt64Type: [TokenType.IntegerLiteral],
            TokenType.SizeTType: [TokenType.IntegerLiteral],
            TokenType.HashTType: [TokenType.IntegerLiteral],
            TokenType.SingleFloatingType: [TokenType.SingleFloatingLiteral],
            TokenType.DoubleFloatingType: [TokenType.DoubleFloatingLiteral],
            TokenType.CharType: [TokenType.CharLiteral],
            TokenType.WCharType: [TokenType.WCharLiteral],
            TokenType.StringType: [TokenType.StringLiteral],
            TokenType.WStringType: [TokenType.WStringLiteral],
        }

        assert len(literals) == len(TokenType.assignable())
        assert tokentype in literals

        return literals[tokentype]


class Token:

    def __init__(self, tokentype, text='???'):

        self.tokentype = tokentype
        self.tokentype_expected = []
        self.text = text
        self.line = None
        self.column = None
        self.relpath = None
        self.modulepath = None

    def __eq__(self, rhs):

        if not isinstance(rhs, Token):
            return False

        return self.tokentype == rhs.tokentype and self.text == rhs.text

    def __str__(self):
        return f'[{self.modulepath}' '(l:{:4d}, c:{:4d})]: '.format(self.line, self.column) + f'"{self.text}" ({self.tokentype})'

    def __repr__(self):
        return f'text={self.text}, tokentype={self.tokentype}'

    def value(self):

        assert self.tokentype in TokenType.literals()

        if self.tokentype in [TokenType.CharLiteral, TokenType.WCharLiteral]:
            return chr(self.text)
        elif self.tokentype in [TokenType.StringLiteral, TokenType.WStringLiteral]:
            return str(self.text)
        elif self.tokentype == TokenType.IntegerLiteral:
            return int(self.text)
        elif self.tokentype == TokenType.SingleFloatingLiteral:
            assert self.text[-1] == 'f'
            return float(self.text[:-1])
        elif self.tokentype == TokenType.DoubleFloatingLiteral:
            return float(self.text)
        elif self.tokentype == TokenType.TrueLiteral:
            return True
        elif self.tokentype == TokenType.FalseLiteral:
            return False
        else:
            assert False, 'Unhandled case!'

    def is_keyword(self) -> bool:
        return self.text in Tokenizer.keywords()

    def is_builtin_type(self) -> bool:
        return self.text in Tokenizer.builtin_types()

    def is_fundamental(self) -> bool:
        return self.text in Tokenizer.fundamentals()

    def is_compound(self) -> bool:
        return self.text in Tokenizer.compounds()

    def is_type(self) -> bool:
        return self.tokentype == TokenType.Identifier or self.is_builtin_type()

    def is_integer(self) -> bool:
        return self.tokentype in [
            TokenType.Int8Type,
            TokenType.Int16Type,
            TokenType.Int32Type,
            TokenType.Int64Type,
            TokenType.UInt8Type,
            TokenType.UInt16Type,
            TokenType.UInt32Type,
            TokenType.UInt64Type,
            TokenType.ByteType,
            TokenType.SizeTType,
            TokenType.HashTType
        ]

    def is_templated(self) -> bool:
        return self.text in Tokenizer.BUILTIN_TEMPLATED_TYPES

    def is_usertype(self) -> bool:
        return self.text in Tokenizer.BUILTIN_USER_TYPES


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

    BUILTIN_FUNDAMENTAL_TYPES = {
        'epiChar': TokenType.CharType,
        'epiWChar': TokenType.WCharType,
        'epiBool': TokenType.BoolType,
        'epiByte': TokenType.ByteType,
        'epiSize_t': TokenType.SizeTType,
        'epiHash_t': TokenType.HashTType,
        'epiU8': TokenType.UInt8Type,
        'epiU16': TokenType.UInt16Type,
        'epiU32': TokenType.UInt32Type,
        'epiU64': TokenType.UInt64Type,
        'epiS8': TokenType.Int8Type,
        'epiS16': TokenType.Int16Type,
        'epiS32': TokenType.Int32Type,
        'epiS64': TokenType.Int64Type,
        'epiFloat': TokenType.SingleFloatingType,
        'epiDouble': TokenType.DoubleFloatingType
    }

    BUILTIN_COMPOUND_TYPES = {
        'epiString': TokenType.StringType,
        'epiWString': TokenType.WStringType,
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

    BUILTIN_TEMPLATED_TYPES = {
        'epiArray': TokenType.ArrayType,
        'epiPtrArray': TokenType.PtrArrayType
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
        # 'Private': TokenType.Private,
        'ReadCallback': TokenType.ReadCallback,
        'WriteCallback': TokenType.WriteCallback,
        'Virtual': TokenType.Virtual,
        'Min': TokenType.Min,
        'Max': TokenType.Max,
        # 'NoDuplicate': TokenType.NoDuplicate,
        'Transient': TokenType.Transient,
        # 'DllEntry': TokenType.DllEntry
        # TBD: 'Hidden': TokenType.Hidden,
        # TBD: 'DisplayName': TokenType.DisplayName,
        # TBD: 'Description': TokenType.Description,
        # TBD: 'EventCallback': TokenType.EventCallback,
        # TBD: 'Category': TokenType.Category,
    }

    def __init__(self, abspath: str, relpath: str, modulepath: str):

        with open(abspath, 'r') as f:
            self.content = f.read()

        self.content_len = len(self.content)
        self.__at = 0
        self.__line = 1
        self.__column = 1
        self.__relpath = relpath
        self.__modulepath = modulepath
        self.tokens = []

    def _ch(self, offset: int = 0) -> chr:
        return self.content[self.at + offset] if self.at + offset < self.content_len else '\0'

    def _substring_until_from(self, start: int) -> str:
        return self.content[start:min(self.at, self.content_len)]

    def _token_create(self, tokentype: TokenType) -> Token:

        token = Token(tokentype)

        token.line = self.__line
        token.column = self.__column
        token.relpath = self.__relpath
        token.modulepath = self.__modulepath

        return token

    @property
    def at(self):
        return self.__at

    @at.setter
    def at(self, at):

        if self._ch() == '\n':

            self.__line += 1
            self.__column = 1

        self.__column += at - self.__at
        self.__at = at

    def tokenize(self):

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

                token = self._token_create(TokenType.Unknown)
                token.text = ch

                self.tokens.append(token)
                self.at += 1

        for token in self.tokens:

            keywords = Tokenizer.keywords()
            if token.text in keywords:
                token.tokentype = keywords[token.text]

        return self.tokens

    def _try_tokenize_special_symbol(self):

        token = None
        for text, tokentype in Tokenizer.SPECIAL_SYMBOL_TOKEN_TYPES.items():

            if self.content.startswith(text, self.at):

                token = self._token_create(tokentype)
                token.text = text

                break

        if not token:
            return False

        self.at += len(token.text)

        if token.tokentype == TokenType.Semicolon and len(self.tokens) > 0 and self.tokens[-1].tokentype == TokenType.Semicolon:
            return True

        self.tokens.append(token)

        return True

    def _tokenize_string_literal(self):

        token = self._token_create(TokenType.Unknown)

        tokentype_suspected = TokenType.StringLiteral
        begin = self.at

        if self._ch() == 'L':

            tokentype_suspected = TokenType.WStringLiteral
            self.at += 1

        self.at += 1

        while self._ch() not in ['"', '\0']:

            if self._ch() == '\\':
                self.at += 1

            self.at += 1

        if self._ch() == '"' and self.__line == token.line:

            token.tokentype = tokentype_suspected
            self.at += 1

        else:
            token.tokentype_expected.append(tokentype_suspected)

        token.text = self._substring_until_from(begin)
        self.tokens.append(token)

    def _tokenize_char_literal(self):

        # TODO: add unicode support (like: '\u8080')
        # (see: https://docs.microsoft.com/en-us/cpp/cpp/string-and-character-literals-cpp?view=vs-2019)

        token = self._token_create(TokenType.Unknown)

        tokentype_suspected = TokenType.CharLiteral
        begin = self.at

        if self._ch() == 'L':

            tokentype_suspected = TokenType.WCharLiteral
            self.at += 1

        self.at += 1

        if self._ch() == '\\':
            self.at += 1

        self.at += 1
        if self._ch() == "'" and self.__line == token.line:

            token.tokentype = tokentype_suspected
            self.at += 1

        else:
            token.tokentype_expected.append(tokentype_suspected)

        token.text = self._substring_until_from(begin)
        self.tokens.append(token)

    def _tokenize_term(self):

        token = self._token_create(TokenType.Unknown)

        tokentype_suspected = TokenType.Identifier
        begin = self.at

        if self._ch().isalpha():
            token.tokentype = TokenType.Identifier
        else:
            token.tokentype_expected.append(tokentype_suspected)

        while self._ch().isalnum() or self._ch() == '_':
            self.at += 1

        token.text = self._substring_until_from(begin)
        self.tokens.append(token)

    def _tokenize_numeric_literal(self):

        token = self._token_create(TokenType.Unknown)

        tokentype_suspected = TokenType.IntegerLiteral
        tokentype_expected = TokenType.IntegerLiteral
        begin = self.at

        if self._ch() == '-' or self._ch() == '+':
            self.at += 1

        while not self._ch().isspace() and self._ch() not in ['\0', ';', ')', ',']:

            if self._ch() == '.' and self._ch(1).isnumeric() and tokentype_suspected == TokenType.IntegerLiteral:

                tokentype_expected = TokenType.DoubleFloatingLiteral
                tokentype_suspected = TokenType.DoubleFloatingLiteral

            elif self._ch() == 'f' and tokentype_suspected == TokenType.DoubleFloatingLiteral:

                tokentype_expected = TokenType.SingleFloatingLiteral
                tokentype_suspected = TokenType.SingleFloatingLiteral

            elif not self._ch().isnumeric() or tokentype_suspected == TokenType.SingleFloatingLiteral:
                tokentype_suspected = TokenType.Unknown

            self.at += 1

        token.tokentype = tokentype_suspected
        if token.tokentype == TokenType.Unknown:
            token.tokentype_expected.append(tokentype_expected)

        token.text = self._substring_until_from(begin)
        self.tokens.append(token)

    @staticmethod
    def keywords() -> dict:
         return {
            **Tokenizer.BUILTIN_FUNDAMENTAL_TYPES,
            **Tokenizer.BUILTIN_COMPOUND_TYPES,
            **Tokenizer.BUILTIN_TEMPLATED_TYPES,
            **Tokenizer.BUILTIN_USER_TYPES,
            **Tokenizer.BUILTIN_PRTY_ATTRS,
            **Tokenizer.BUILTIN_CLSS_ATTRS,
            **Tokenizer.BUILTIN_MODIFIERS,
            **Tokenizer.BUILTIN_VALUES
        }

    @staticmethod
    def builtin_types() -> dict:
        return {
            **Tokenizer.BUILTIN_FUNDAMENTAL_TYPES,
            **Tokenizer.BUILTIN_COMPOUND_TYPES,
            **Tokenizer.BUILTIN_TEMPLATED_TYPES
        }

    @staticmethod
    def fundamentals() -> dict:
        return {
            **Tokenizer.BUILTIN_FUNDAMENTAL_TYPES
        }

    @staticmethod
    def compounds() -> dict:
        return {
            **Tokenizer.BUILTIN_COMPOUND_TYPES
        }


assert len(Tokenizer.keywords().values()) == len(set(Tokenizer.keywords().values())), 'Every builtin keyword should much a single TokenType'
