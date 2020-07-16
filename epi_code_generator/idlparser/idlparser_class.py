from epi_code_generator.idlparser import idlparser_base as idl

from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol.symbol import EpiClass
from epi_code_generator.symbol.symbol import EpiProperty


def _parse_scope(parser: idl.IDLParser, attrs_inherited: list = []) -> list:

    from epi_code_generator.idlparser import idlparser_property as idlprty
    from epi_code_generator.idlparser import idlparser_attr as idlattr

    parser._test(parser._next(), [TokenType.OpenBrace], err_code=idl.IDLSyntaxErrorCode.NoBodyOnDeclaration)

    scope = []
    while True:

        t = parser._curr()
        attrs_local = idlattr.parse_attr_list(parser)

        attrs_merged = attrs_inherited + attrs_local
        # TODO: check if property isn't reference

        if parser._test(parser._curr(), [TokenType.CloseBrace]):
            break
        elif parser._test(parser._curr(), [TokenType.OpenBrace]):
            scope.append(_parse_scope(parser, attrs_merged))
        else:

            prty = idlprty.parse_property(parser)

            try:
                prty.attrs = attrs_merged
            except idlattr.EpiAttributeValidationError as e:
                parser._push_error(e.token, e.err_code, str(e), fatal=False)

            scope.append(prty)

    t = parser._next()
    parser._test(t,
                [TokenType.CloseBrace],
                err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBrace,
                tip='Expected \'}\'')

    return scope


def parse_class(parser: idl.IDLParser) -> EpiClass:

    assert parser._curr().tokentype == TokenType.ClassType, 'This method should be called on `class` token'

    t = parser._next(2)
    parser._test(t, [TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    clss = EpiClass(t)

    t = parser._curr()
    if parser._test(t, [TokenType.Colon]):

        t = parser._next(2)
        parser._test(t, [TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

        clss.parent = t.text

    def unpack_scope(s):

        for e in s:

            if isinstance(e, EpiProperty):
                clss.properties.append(e)
            elif isinstance(e, list):
                unpack_scope(e)

    scope = _parse_scope(parser)
    unpack_scope(scope)

    t = parser._next()
    parser._test(t,
                [TokenType.Semicolon],
                err_code=idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration,
                tip='`class` type should be followed by `;`')

    return clss
