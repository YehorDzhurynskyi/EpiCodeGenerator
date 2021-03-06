from epigen.tokenizer import Token
from epigen.tokenizer import Tokenizer
from epigen.tokenizer import TokenType

from enum import Enum, auto, unique


@unique
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
    DuplicatingSymbol = auto()
    MultiDepthPointer = auto()
    WrongIdentifierContext = auto()

    # TODO: move here incomplete type error checking from linking stage


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
        IDLSyntaxErrorCode.AttributeInvalidTarget: 'An attribute was applied to the wrong target',
        IDLSyntaxErrorCode.DuplicatingSymbol: "The symbol's name duplicates other symbol's name",
        IDLSyntaxErrorCode.MultiDepthPointer: 'Only single-depth pointers are allowed',
        IDLSyntaxErrorCode.WrongIdentifierContext: 'An identifier was used in the wrong context'
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


class IDLParserError(Exception):

    def __init__(self, msg: str, token: Token, err_code: IDLSyntaxErrorCode):

        super().__init__(msg)

        self.token = token
        self.err_code = err_code


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

    def _test(self, token: Token, **kwargs) -> bool:

        expected = None
        unexpected = None

        success = True
        if 'expected' in kwargs:

            expected = kwargs['expected']
            assert isinstance(expected, list)

            success = token is not None and token.tokentype in expected

        if success and 'unexpected' in kwargs:

            unexpected = kwargs['unexpected']
            assert isinstance(unexpected, list)

            success = token is not None and token.tokentype not in unexpected

        if not success:

            if 'err_code' in kwargs:

                err_code = kwargs['err_code']
                assert isinstance(err_code, IDLSyntaxErrorCode)
                tip = f"{kwargs['tip']}. " if 'tip' in kwargs else ''
                assert isinstance(tip, str)
                fatal = kwargs['fatal'] if 'fatal' in kwargs else True
                assert isinstance(fatal, bool)

                if token is not None and expected is not None:

                    token.tokentype_expected.extend(expected)
                    expected = ' or '.join([f'`{exp}`' for exp in token.tokentype_expected])

                    if len(token.tokentype_expected) > 0:
                        tip = f'{tip}{expected} is expected!'

                self._push_error(token, err_code, tip, fatal)

            return False

        return True

    def parse(self) -> (dict, list):

        from epigen.idlparser import idlparser_class as idlclass
        from epigen.idlparser import idlparser_enum as idlenum
        from epigen.idlparser import idlparser_attr as idlattr

        self.syntax_errors = [IDLSyntaxError(t, IDLSyntaxErrorCode.UnknownToken, '') for t in self.tokens if t.tokentype == TokenType.Unknown]
        if len(self.syntax_errors) > 0:
            return {}, self.syntax_errors

        registry = {}

        try:

            while not self._eof():

                attrs = idlattr.parse_attr_list(self)

                t = self._curr()
                self._test(t, expected=list(Tokenizer.BUILTIN_USER_TYPES.values()), err_code=IDLSyntaxErrorCode.MissingTypeDeclaration)

                assert t.tokentype in [TokenType.ClassType, TokenType.EnumType], 'Handle other usertypes'

                if t.tokentype == TokenType.ClassType:
                    sym = idlclass.parse_class(self)

                elif t.tokentype == TokenType.EnumType:
                    sym = idlenum.parse_enum(self)

                if sym.name in registry:

                    tip = f'The symbol `{sym.name}` has already been defined in the current file!'
                    self._push_error(sym.token, IDLSyntaxErrorCode.DuplicatingSymbol, tip, fatal=False)

                try:
                    for attr in attrs:
                        sym.attr_push(attr)

                except IDLParserError as e:
                    self._push_error(e.token, e.err_code, str(e), fatal=False)

                registry[sym.name] = sym

        except IDLParserErrorFatal:
            pass

        if len(self.syntax_errors) > 0:
            registry = {}

        return registry, self.syntax_errors
