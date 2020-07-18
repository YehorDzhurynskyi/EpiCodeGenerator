from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.tokenizer import TokenType

from enum import Enum, auto


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
    AttributeConflict = auto()
    AttributeInvalidParameters = auto()
    AttributeInvalidTarget = auto()


class IDLSyntaxError:

    __SYNTAX_ERROR_MSGS = {
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
        IDLSyntaxErrorCode.AttributeConflict: 'Provided attribute conflicts with the other attribute',
        IDLSyntaxErrorCode.AttributeInvalidParameters: 'Invalid attribute parameters',
        IDLSyntaxErrorCode.AttributeInvalidTarget: 'An attribute was applied to the wrong target'
    }

    def __init__(self, token: Token, err_code: IDLSyntaxErrorCode, tip: str):

        self.__token = token
        self.__err_code = err_code
        self.__err_message = IDLSyntaxError.__SYNTAX_ERROR_MSGS[err_code]
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
        return f'{repr(self.__err_code)}: {repr(self.__token)} {self.__tip}'


class IDLParserErrorFatal(Exception):
    pass


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

    def _push_error(self, token: Token, err_code: IDLSyntaxErrorCode, tip: str='', fatal: bool=True):

        # NOTE: shouldn't be called directly
        assert err_code != IDLSyntaxErrorCode.UnexpectedKeywordUsage and err_code != IDLSyntaxErrorCode.UnexpectedEOF

        if err_code == IDLSyntaxErrorCode.UnexpectedToken:

            err_code = IDLSyntaxErrorCode.UnexpectedToken if token is not None else IDLSyntaxErrorCode.UnexpectedEOF
            if err_code == IDLSyntaxErrorCode.UnexpectedToken:
                err_code = IDLSyntaxErrorCode.UnexpectedKeywordUsage if token.is_keyword() else IDLSyntaxErrorCode.UnexpectedToken

        self.syntax_errors.append(IDLSyntaxError(token, err_code, tip))

        if fatal:
            raise IDLParserErrorFatal()


    def _test(self, token: Token, expected: list, **kwargs) -> bool:

        if token is None or token.tokentype not in expected:

            if 'err_code' in kwargs:

                err_code = kwargs['err_code']
                assert isinstance(err_code, IDLSyntaxErrorCode)
                tip = f"{kwargs['tip']}. " if 'tip' in kwargs else ''
                assert isinstance(tip, str)
                fatal = kwargs['fatal'] if 'fatal' in kwargs else True
                assert isinstance(fatal, bool)

                if token is not None:

                    token.tokentype_expected.extend(expected)
                    expected = ' or '.join([f'`{exp}`' for exp in token.tokentype_expected])

                    if len(token.tokentype_expected) > 0:
                        tip = f'{tip}{expected} is expected!'

                self._push_error(token, err_code, tip, fatal)

            return False

        return True

    def parse(self) -> (dict, list):

        from epi_code_generator.idlparser import idlparser_class as idlclass

        self.syntax_errors = [IDLSyntaxError(t, IDLSyntaxErrorCode.UnknownToken, '') for t in self.tokens if t.tokentype == TokenType.Unknown]
        if len(self.syntax_errors) > 0:
            return {}, self.syntax_errors

        registry = {}

        try:

            while not self._eof():

                t = self._curr()
                self._test(t, list(Tokenizer.BUILTIN_USER_TYPES.values()), err_code=IDLSyntaxErrorCode.MissingTypeDeclaration)

                assert t.tokentype == TokenType.ClassType, 'Handle other usertypes'

                clss = idlclass.parse_class(self)

                registry[clss.name] = clss

        except IDLParserErrorFatal:
            pass

        if len(self.syntax_errors) > 0:
            registry = {}

        return registry, self.syntax_errors
