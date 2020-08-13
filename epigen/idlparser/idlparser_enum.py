from epigen.idlparser import idlparser_base as idl

from epigen.tokenizer import Tokenizer
from epigen.tokenizer import TokenType

from epigen.symbol import EpiEnum
from epigen.symbol import EpiEnumEntry
from epigen.symbol import EpiAttribute


def __parse_enum_entry(parser: idl.IDLParser) -> EpiEnumEntry:

    parser._test(parser._curr(), expected=[TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)
    if not parser._curr().is_declaration_identifier():

        tip = 'An `enum entry` declaration identifier was expected'
        parser._push_error(parser._curr(), idl.IDLSyntaxErrorCode.WrongIdentifierContext, tip, fatal=False)

    t = parser._next()
    entry = EpiEnumEntry(t)

    if parser._test(parser._curr(), expected=[TokenType.Assing]):

        t = parser._next(2)
        if parser._test(t,
                        expected=[TokenType.IntegerLiteral],
                        err_code=idl.IDLSyntaxErrorCode.IncorrectValueAssignment,
                        tip="The assigned value isn't an integer literal",
                        fatal=False):

            entry.tokenvalue = t

    return entry


def __parse_scope(parser: idl.IDLParser, attrs_inherited: list = []) -> list:

    from epigen.idlparser import idlparser_attr as idlattr

    parser._test(parser._next(), expected=[TokenType.OpenBrace], err_code=idl.IDLSyntaxErrorCode.NoBodyOnDeclaration)

    scope = []

    while True:

        attrs_local = idlattr.parse_attr_list(parser)

        attrs_merged = attrs_inherited + attrs_local

        if parser._test(parser._curr(), expected=[TokenType.CloseBrace]):
            break

        elif parser._test(parser._curr(), expected=[TokenType.OpenBrace]):
            scope.append(__parse_scope(parser, attrs_merged))

        else:
            entry = __parse_enum_entry(parser)

            try:

                for attr in attrs_merged:
                    entry.attr_push(attr)

            except idl.IDLParserError as e:
                parser._push_error(e.token, e.err_code, str(e), fatal=False)

            scope.append(entry)

            if not parser._test(parser._curr(), expected=[TokenType.Comma]):
                break

            parser._next()
            parser._test(parser._curr(),
                         unexpected=[TokenType.CloseBrace],
                         err_code=idl.IDLSyntaxErrorCode.UnexpectedToken,
                         fatal=False)

    parser._test(parser._next(),
                expected=[TokenType.CloseBrace],
                unexpected=[TokenType.Comma],
                err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBrace,
                tip='Expected \'}\'')

    return scope


def parse_enum(parser: idl.IDLParser) -> EpiEnum:

    assert parser._curr().tokentype == TokenType.EnumType, 'This method should be called on `enum` token'

    t = parser._next(2)
    parser._test(t, expected=[TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    if not t.is_declaration_identifier():

        tip = 'An `enum` declaration identifier was expected'
        parser._push_error(t, idl.IDLSyntaxErrorCode.WrongIdentifierContext, tip, fatal=False)

    enum = EpiEnum(t)

    t = parser._curr()
    if parser._test(t, expected=[TokenType.Colon]):

        t = parser._next(2)
        parser._test(t, expected=TokenType.integers(), err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

        enum.base = t

    def unpack_scope(s):

        for e in s:

            if isinstance(e, EpiEnumEntry):
                enum.entries.append(e)

            elif isinstance(e, list):
                unpack_scope(e)

    scope = __parse_scope(parser)
    unpack_scope(scope)

    t = parser._next()
    parser._test(t,
                expected=[TokenType.Semicolon],
                err_code=idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration,
                tip='`enum` type should be followed by `;`')

    return enum
