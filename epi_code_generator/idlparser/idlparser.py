from enum import Enum, auto

from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol import EpiAttributeInvalidListError
from epi_code_generator.symbol import EpiAttribute
from epi_code_generator.symbol import EpiVariable
from epi_code_generator.symbol import EpiClass


class IDLSyntaxErrorCode(Enum):

    NoMatchingClosingBrace = auto()
    NoMatchingOpeningBrace = auto()
    NoMatchingClosingBracket = auto()
    NoSemicolonOnDeclaration = auto()
    NoBodyOnDeclaration = auto()
    MissingTypeDeclaration = auto()
    UnexpectedToken = auto()
    UnexpectedKeywordUsage = auto()
    UnexpectedEOF = auto()
    IncorrectValueLiteral = auto()
    InvalidArgumentsNumber = auto()
    InvalidAttribute = auto()


SYNTAX_ERROR_MSGS = {
    IDLSyntaxErrorCode.NoMatchingClosingBrace: 'No matching closing brace for',
    IDLSyntaxErrorCode.NoMatchingClosingBracket: 'No matching closing bracket for',
    IDLSyntaxErrorCode.NoSemicolonOnDeclaration: 'No `;` on the end of the declaration',
    IDLSyntaxErrorCode.NoBodyOnDeclaration: 'The body of type declaration is absent',
    IDLSyntaxErrorCode.MissingTypeDeclaration: 'Missing an user type declaration',
    IDLSyntaxErrorCode.UnexpectedToken: 'Unexpected token',
    IDLSyntaxErrorCode.UnexpectedKeywordUsage: 'Unexpected keyword usage',
    IDLSyntaxErrorCode.UnexpectedEOF: 'Unexpected end of file',
    IDLSyntaxErrorCode.IncorrectValueLiteral: 'Incorrect value literal',
    IDLSyntaxErrorCode.InvalidArgumentsNumber: 'Invalid number of arguments',
    IDLSyntaxErrorCode.InvalidAttribute: 'Invalid attribute'
}


class IDLSyntaxError:

    def __init__(self, token, err_code, tip = ''):

        self.token = token
        self.err_code = err_code
        self.err_message = SYNTAX_ERROR_MSGS[err_code]
        self.tip = tip

    def __str__(self):

        token = str(self.token) if self.token is not None else 'EOF'
        s = f'Syntax error {token}: {self.err_message}'
        if len(self.tip) != 0:
            s = f'{s} ({self.tip})'

        return s

class IDLParser:

    def __init__(self, tokens):

        self.tokens = tokens
        self.__at = 0
        self.syntax_errors = []

    def _eof(self):
        return self.__at >= len(self.tokens)

    def _curr(self):
        return self.tokens[self.__at] if not self._eof() else None

    def _next(self, offset: int = 1):

        self.__at += offset - 1
        curr = self._curr()
        self.__at += 1

        return curr

    def _test(self, token: Token, tokentype: TokenType) -> bool:
        return token is not None and token.type == tokentype

    def parse(self) -> (dict, list):

        registry = {}
        while not self._eof():

            t = self._curr()
            if t.text not in Tokenizer.BUILTIN_USER_TYPES:

                err_msg = f'Expected an usertype: {",".join(Tokenizer.BUILTIN_USER_TYPES.keys())}'
                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.MissingTypeDeclaration, err_msg))
                break

            if not t.type == TokenType.ClassType:
                assert False, 'Handle other usertypes'

            clss = self._parse_class()
            if clss is None:
                registry = {}
                break

            registry[clss.name] = clss

        return registry, self.syntax_errors

    def _parse_class(self) -> EpiClass:

        assert self._curr().type == TokenType.ClassType, 'This method should be called on `class` token'

        t = self._next(2)
        if not self._test(t, TokenType.Identifier):

            self._error_push_unexpected_token(t, 'Expected an \'<identifier>\'')
            return None

        clss = EpiClass(t)

        t = self._curr()
        if self._test(t, TokenType.Colon):

            t = self._next(2)
            if not self._test(t, TokenType.Identifier):

                self._error_push_unexpected_token(t, 'Expected an \'<identifier>\'')
                return None

            clss.parent = t.text

        def unpack_scope(s):

            for e in s:

                if isinstance(e, EpiVariable):
                    clss.properties.append(e)
                elif isinstance(e, list):
                    unpack_scope(e)

        scope = self._parse_scope()
        if scope is None:
            return None

        unpack_scope(scope)

        t = self._next()
        if not self._test(t, TokenType.Semicolon):

            err_msg = '`class` type should be followed by `;`'
            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoSemicolonOnDeclaration, err_msg))
            return None

        return clss

    def _parse_scope(self, attrs_inherited: list = []) -> list:

        t = self._next()
        if not self._test(t, TokenType.OpenBrace):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoBodyOnDeclaration, 'Expected \'{\''))
            return None

        scope = []
        while True:

            t = self._curr()
            attrs_local = self._parse_attr_list()
            if attrs_local is None:
                return None

            attrs_merged = attrs_inherited + attrs_local
            # TODO: check if property isn't reference

            if self._test(self._curr(), TokenType.CloseBrace):
                break
            elif self._test(self._curr(), TokenType.OpenBrace):
                scope.append(self._parse_scope(attrs_merged))
            else:

                var = self._parse_variable()
                if var is None:
                    return None

                try:
                    var.attrs = attrs_merged
                except EpiAttributeInvalidListError as e:

                    self.syntax_errors.append(var.tokentype, IDLSyntaxErrorCode.InvalidAttribute, str(e))
                    return None

                scope.append(var)

        t = self._next()
        if not self._test(t, TokenType.CloseBrace):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBrace, 'Expected \'}\''))
            return None

        return scope

    def _parse_attr_list(self) -> list:

        attrs = []
        while True:

            t = self._curr()
            if not self._test(t, TokenType.OpenSqBracket):
                break

            self._next()
            while True:

                if self._curr() is None or self._curr().text not in Tokenizer.BUILTIN_PRTY_ATTRS.keys() | Tokenizer.BUILTIN_CLSS_ATTRS.keys():

                    self._error_push_unexpected_token(self._curr(), 'Expected an attribute')
                    return None

                attr = self._parse_attr()
                if attr is None:
                    return None

                attrs.append(attr)

                if not self._test(self._curr(), TokenType.Comma):
                    break

                self._next()

            t = self._next()
            if not self._test(t, TokenType.CloseSqBracket):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket, 'Expected \']\''))
                return None

        return attrs

    def _parse_attr(self) -> EpiAttribute:

        a_t = self._next()

        assert a_t is not None, "EOF check should be done on caller side"

        attr = EpiAttribute(a_t.type)

        lbound, rbound = EpiAttribute.RANGES[a_t.type]
        if rbound == 0:
            return attr

        if lbound == 0 and not self._test(self._curr(), TokenType.OpenBracket):
            return attr

        self._next()
        for i in range(rbound):

            if self._test(self._curr(), TokenType.CloseBracket):
                break

            attr.params.append(self._next())

            if not self._test(self._curr().type, TokenType.Comma):
                break

            self._next()

        if i > rbound:

            tip = f'Maximum number of args is {rbound} but {i} provided'
            self.syntax_errors.append(IDLSyntaxError(a_t, IDLSyntaxErrorCode.InvalidArgumentsNumber, tip))
            return None

        t = self._next()
        if not self._test(t, TokenType.CloseBracket):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket, 'Expected \')\''))
            return None

        if i < lbound:

            tip = f'Minimum number of args is {lbound} but {i} provided'
            self.syntax_errors.append(IDLSyntaxError(a_t, IDLSyntaxErrorCode.InvalidArgumentsNumber, tip))
            return None

        return attr

    def _parse_variable(self) -> EpiVariable:

        if not self._is_next_type():

            self._error_push_unexpected_token(self._curr())
            return None

        tokentype = self._next()
        form = EpiVariable.Form.Plain

        if self._test(self._curr(), TokenType.OpenAngleBracket):

            self._next()
            form = EpiVariable.Form.Array
            if not self._is_next_type():

                self._error_push_unexpected_token(self._curr(), 'Expected a <typename>')
                return None

            nestedtokentype = self._next()

            t = self._next()
            if not self._test(t, TokenType.CloseAngleBracket):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket, 'Expected \'>\''))
                return None

        while True:

            t = self._curr()
            if self._test(t, TokenType.Asterisk):

                form = EpiVariable.Form.Pointer
                tokentype.text += '*'
                self._next()

            else:
                break

        t = self._curr()
        if self._test(t, TokenType.Ampersand):

                assert False
                # form = EpiVariable.Form.Reference
                # self._next()

        t = self._next()
        if not self._test(t, TokenType.Identifier):

            self._error_push_unexpected_token(t, 'Expected an <identifier>')
            return None

        var = EpiVariable(t, tokentype, form)

        if var.form == EpiVariable.Form.Array:
            var.nestedtokentype = nestedtokentype

        # NOTE: if property is virtual an assignment is invalid
        t = self._next()
        if self._test(t, TokenType.Assing):

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
            t = self._next()
            if t is None:
                return None

            if var.tokentype.type == TokenType.Identifier:

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueLiteral, 'Only fundamental types are assingable'))
                return None

            if var.form == EpiVariable.Form.Pointer:

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueLiteral, 'Pointers are unassingable and are set with \'null\' by default'))
                return None

            if var.form == EpiVariable.Form.Array:

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueLiteral, 'Arrays are unassingable'))
                return None

            assert var.form == EpiVariable.Form.Plain, 'Add error message for a new Form'

            if t.type not in literals[var.tokentype.type]:

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueLiteral))
                return None

            var.value = t.text

            t = self._next()

        if not self._test(t, TokenType.Semicolon):

            self._error_push_unexpected_token(t, 'Expected \';\'')
            return None

        return var

    def _is_next_type(self):

        t = self._curr()
        return t is not None and (t.text in (
            Tokenizer.BUILTIN_PRIMITIVE_TYPES.keys() |
            Tokenizer.BUILTIN_COMPOUND_TYPES.keys()
        ) or t.type == TokenType.Identifier)

    def _is_next_variable(self):

        # NOTE: could be a method
        t = self._curr()
        return  t is not None and ( \
            t.type == TokenType.Identifier or \
            t.text in Tokenizer.BUILTIN_PRIMITIVE_TYPES or \
            t.text in Tokenizer.BUILTIN_COMPOUND_TYPES or \
            t.text in Tokenizer.BUILTIN_MODIFIERS \
        )

    def _error_push_unexpected_token(self, t, tip = ''):

        if t is None:
            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedEOF, tip))
        elif t.is_keyword():
            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedKeywordUsage, tip))
        else:
            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedToken, tip))
