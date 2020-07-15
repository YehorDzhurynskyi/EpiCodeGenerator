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
    MissingTemplateArguments = auto()
    UnknownToken = auto()
    UnexpectedToken = auto()
    UnexpectedKeywordUsage = auto()
    UnexpectedEOF = auto()
    IncorrectValueLiteral = auto()
    IncorrectValueAssignment = auto()
    InvalidArgumentsNumber = auto()
    InvalidAttribute = auto()


SYNTAX_ERROR_MSGS = {
    IDLSyntaxErrorCode.NoMatchingClosingBrace: 'No matching closing brace for',
    IDLSyntaxErrorCode.NoMatchingClosingBracket: 'No matching closing bracket for',
    IDLSyntaxErrorCode.NoSemicolonOnDeclaration: 'No `;` on the end of the declaration',
    IDLSyntaxErrorCode.NoBodyOnDeclaration: 'The body of type declaration is absent',
    IDLSyntaxErrorCode.MissingTypeDeclaration: 'Missing an user type declaration',
    IDLSyntaxErrorCode.MissingTemplateArguments: 'Template type should have template argument list',
    IDLSyntaxErrorCode.UnknownToken: 'Unknown token (the token is unrecognized)',
    IDLSyntaxErrorCode.UnexpectedToken: 'Unexpected token (the token is recognized, but used in the wrong context)',
    IDLSyntaxErrorCode.UnexpectedKeywordUsage: 'Unexpected keyword usage',
    IDLSyntaxErrorCode.UnexpectedEOF: 'Unexpected end of file',
    IDLSyntaxErrorCode.IncorrectValueLiteral: 'Incorrect value literal',
    IDLSyntaxErrorCode.IncorrectValueAssignment: 'Incorrect value assignment',
    IDLSyntaxErrorCode.InvalidArgumentsNumber: 'Invalid number of arguments',
    IDLSyntaxErrorCode.InvalidAttribute: 'Invalid attribute'
}


class IDLSyntaxError:

    def __init__(self, token, err_code, tip = ''):

        if token is not None:

            expected = ' or '.join([f'`{exp}`' for exp in token.tokentype_expected])
            if len(token.tokentype_expected) > 0:
                tip = f'{expected} is expected! {tip}'

            if err_code == IDLSyntaxErrorCode.UnexpectedToken and token.is_keyword():
                err_code = IDLSyntaxErrorCode.UnexpectedKeywordUsage

        elif err_code == IDLSyntaxErrorCode.UnexpectedToken:
            err_code = IDLSyntaxErrorCode.UnexpectedEOF

        self.__token = token
        self.__err_code = err_code
        self.__err_message = SYNTAX_ERROR_MSGS[err_code]
        self.__tip = tip

    @property
    def err_code(self):
        return self.__err_code

    def __str__(self):

        token = str(self.__token) if self.__token is not None else 'EOF'
        s = f'Syntax error {token}: {self.__err_message}'
        if len(self.__tip) != 0:
            s = f'{s} ({self.__tip})'

        return s

    def __repr__(self):
        return f'{repr(self.__err_code)}: {self.__token} {self.__tip}'


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

        # TODO: throw EOF

        self.__at += offset - 1
        curr = self._curr()
        self.__at += 1

        return curr

    def _test(self, token: Token, expected: list, required: bool = True) -> bool:

        # TODO: throw some exception on fail if `required` is True, and silencly return False otherwise
        # Perform here: `self.syntax_errors.append(IDLSyntaxError(token, IDLSyntaxErrorCode.?))`

        if token is None or token.tokentype not in expected:

            if token is not None and required:
                token.tokentype_expected.extend(expected)

            return False

        return True

    def parse(self) -> (dict, list):

        self.syntax_errors = [IDLSyntaxError(t, IDLSyntaxErrorCode.UnknownToken) for t in self.tokens if t.tokentype == TokenType.Unknown]
        if len(self.syntax_errors) > 0:
            return {}, self.syntax_errors

        registry = {}
        while not self._eof():

            t = self._curr()
            if not self._test(t, list(Tokenizer.BUILTIN_USER_TYPES.values())):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.MissingTypeDeclaration))
                break

            assert t.tokentype == TokenType.ClassType, 'Handle other usertypes'

            clss = self._parse_class()
            if clss is None:
                break

            registry[clss.name] = clss

        if len(self.syntax_errors) > 0:
            registry = {}

        return registry, self.syntax_errors

    def _parse_class(self) -> EpiClass:

        assert self._curr().tokentype == TokenType.ClassType, 'This method should be called on `class` token'

        t = self._next(2)
        if not self._test(t, [TokenType.Identifier]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedToken))
            return None

        clss = EpiClass(t)

        t = self._curr()
        if self._test(t, [TokenType.Colon], required=False):

            t = self._next(2)
            if not self._test(t, [TokenType.Identifier]):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedToken))
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
        if not self._test(t, [TokenType.Semicolon]):

            tip = '`class` type should be followed by `;`'
            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoSemicolonOnDeclaration, tip))
            return None

        return clss

    def _parse_scope(self, attrs_inherited: list = []) -> list:

        t = self._next()
        if not self._test(t, [TokenType.OpenBrace]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoBodyOnDeclaration))
            return None

        scope = []
        while True:

            t = self._curr()
            attrs_local = self._parse_attr_list(list(Tokenizer.BUILTIN_PRTY_ATTRS.values()))
            if attrs_local is None:
                return None

            attrs_merged = attrs_inherited + attrs_local
            # TODO: check if property isn't reference

            if self._test(self._curr(), [TokenType.CloseBrace], required=False):
                break
            elif self._test(self._curr(), [TokenType.OpenBrace], required=False):
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
        if not self._test(t, [TokenType.CloseBrace]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBrace, 'Expected \'}\''))
            return None

        return scope

    def _parse_attr_list(self, attr_whitelist: list) -> list:

        attrs = []
        while True:

            t = self._curr()
            if not self._test(t, [TokenType.OpenSqBracket]):
                break

            self._next()
            while True:

                if not self._test(self._curr(), attr_whitelist):

                    self.syntax_errors.append(IDLSyntaxError(self._curr(), IDLSyntaxErrorCode.UnexpectedToken))
                    return None

                attr = self._parse_attr()
                if attr is None:
                    return None

                attrs.append(attr)

                if not self._test(self._curr(), [TokenType.Comma], required=False):
                    break

                self._next()

            t = self._next()
            if not self._test(t, [TokenType.CloseSqBracket]):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket))
                return None

        return attrs

    def _parse_attr(self) -> EpiAttribute:

        a_t = self._next()

        assert a_t is not None, "EOF check should be done on caller side"

        attr = EpiAttribute(a_t.tokentype)

        lbound, rbound = EpiAttribute.RANGES[a_t.tokentype]
        if rbound == 0:
            return attr

        if lbound == 0 and not self._test(self._curr(), [TokenType.OpenBracket], required=False):
            return attr

        self._next()
        for i in range(rbound):

            if self._test(self._curr(), [TokenType.CloseBracket], required=False):
                break

            attr.params.append(self._next())

            if not self._test(self._curr().tokentype, [TokenType.Comma], required=False):
                break

            self._next()

        if i > rbound:

            tip = f'Maximum number of args is {rbound} but {i} provided'
            self.syntax_errors.append(IDLSyntaxError(a_t, IDLSyntaxErrorCode.InvalidArgumentsNumber, tip))
            return None

        t = self._next()
        if not self._test(t, [TokenType.CloseBracket]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket))
            return None

        if i < lbound:

            tip = f'Minimum number of args is {lbound} but {i} provided'
            self.syntax_errors.append(IDLSyntaxError(a_t, IDLSyntaxErrorCode.InvalidArgumentsNumber, tip))
            return None

        return attr

    def _parse_variable(self) -> EpiVariable:

        tokentype_types = [TokenType.Identifier]
        tokentype_types.extend(list(Tokenizer.fundamentals().values()))

        if not self._test(self._curr(), tokentype_types):

            self.syntax_errors.append(IDLSyntaxError(self._curr(), IDLSyntaxErrorCode.UnexpectedToken))
            return None

        tokentype = self._next()
        tokentype_nested = []
        form = EpiVariable.Form.Plain

        if tokentype is not None and tokentype.is_templated():

            if not self._test(self._next(), [TokenType.OpenAngleBracket]):

                self.syntax_errors.append(IDLSyntaxError(tokentype, IDLSyntaxErrorCode.MissingTemplateArguments))
                return None

            form = EpiVariable.Form.Template
            if not self._test(self._curr(), tokentype_types):

                self.syntax_errors.append(IDLSyntaxError(self._curr(), IDLSyntaxErrorCode.UnexpectedToken))
                return None

            # TODO: parse >1 number of template arguments
            tokentype_nested.append(self._next())

            t = self._next()
            if not self._test(t, [TokenType.CloseAngleBracket]):

                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.NoMatchingClosingBracket))
                return None

        while True:

            t = self._curr()
            if self._test(t, [TokenType.Asterisk], required=False):

                form = EpiVariable.Form.Pointer
                tokentype.text += '*'
                self._next()

            else:
                break

        t = self._curr()
        if self._test(t, [TokenType.Ampersand], required=False):

                assert False
                # form = EpiVariable.Form.Reference
                # self._next()

        t = self._next()
        if not self._test(t, [TokenType.Identifier]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedToken))
            return None

        var = EpiVariable(t, tokentype, form)

        if var.form == EpiVariable.Form.Template:
            var.tokentype_nested = tokentype_nested

        # NOTE: if property is virtual an assignment is invalid
        t = self._next()
        if self._test(t, [TokenType.Assing], required=False):

            t = self._next()
            if t is None:
                return None

            if var.tokentype.tokentype == TokenType.Identifier:
                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueAssignment, 'Only fundamental types are assingable'))
            elif var.form == EpiVariable.Form.Pointer:
                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueAssignment, 'Pointers are unassingable and are set with \'null\' by default'))
            elif var.form == EpiVariable.Form.Template:
                self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueAssignment, 'Template types are unassingable'))
            else:

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

                if not self._test(var.tokentype, list(literals.keys())):
                    self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueAssignment))
                elif not self._test(t, literals[var.tokentype.tokentype]):
                    self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.IncorrectValueLiteral))

                var.value = t.text

            t = self._next()

        if not self._test(t, [TokenType.Semicolon]):

            self.syntax_errors.append(IDLSyntaxError(t, IDLSyntaxErrorCode.UnexpectedToken))
            return None

        return var
