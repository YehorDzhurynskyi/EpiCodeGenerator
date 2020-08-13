from epigen.idlparser import idlparser_base as idl

from epigen.tokenizer import TokenType

from epigen.symbol import EpiClass
from epigen.symbol import EpiProperty
from epigen.symbol import EpiEnum
from epigen.symbol import EpiAttribute


def __parse_scope(parser: idl.IDLParser, attrs_inherited: list = []) -> list:

    from epigen.idlparser import idlparser_property as idlprty
    from epigen.idlparser import idlparser_enum as idlenum
    from epigen.idlparser import idlparser_attr as idlattr

    parser._test(parser._next(), expected=[TokenType.OpenBrace], err_code=idl.IDLSyntaxErrorCode.NoBodyOnDeclaration)

    scope = []
    while True:

        t = parser._curr()
        attrs_local = idlattr.parse_attr_list(parser)

        attrs_merged = attrs_inherited + attrs_local
        # TODO: check if property isn't reference

        if parser._test(parser._curr(), expected=[TokenType.CloseBrace]):
            break

        elif parser._test(parser._curr(), expected=[TokenType.OpenBrace]):
            scope.append(__parse_scope(parser, attrs_merged))

        else:
            try:

                if parser._test(parser._curr(), expected=[TokenType.EnumType]):
                    sym = idlenum.parse_enum(parser)

                else:
                    sym = idlprty.parse_property(parser)

                    # TODO: put it to the other place
                    if sym.form in [EpiProperty.Form.Pointer]:

                        attr = EpiAttribute(TokenType.Transient)
                        attr.is_implied_indirectly = True

                        sym.attr_push(attr)

                for attr in attrs_merged:
                    sym.attr_push(attr)

            except idl.IDLParserError as e:
                parser._push_error(e.token, e.err_code, str(e), fatal=False)

            scope.append(sym)

    t = parser._next()
    parser._test(t,
                expected=[TokenType.CloseBrace],
                err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBrace,
                tip='Expected \'}\'')

    return scope


def parse_class(parser: idl.IDLParser) -> EpiClass:

    assert parser._curr().tokentype == TokenType.ClassType, 'This method should be called on `class` token'

    t = parser._next(2)
    parser._test(t, expected=[TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    if not t.is_declaration_identifier():

        tip = 'A `class` declaration identifier was expected'
        parser._push_error(t, idl.IDLSyntaxErrorCode.WrongIdentifierContext, tip, fatal=False)

    clss = EpiClass(t)

    t = parser._curr()
    if parser._test(t, expected=[TokenType.Colon]):

        t = parser._next(2)
        parser._test(t, expected=[TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

        clss.parent = t.text

    def unpack_scope(scope):

        for sym in scope:

            if isinstance(sym, EpiProperty):
                clss.properties.append(sym)

            elif isinstance(sym, EpiEnum):

                if sym.name in clss.inner:

                    tip = f'The symbol `{sym.name}` has already been defined in the {clss.name} `class` type!'
                    parser._push_error(sym.token, idl.IDLSyntaxErrorCode.DuplicatingSymbol, tip, fatal=False)

                clss.inner[sym.name] = sym

            elif isinstance(sym, list):
                unpack_scope(sym)

            else:
                assert False

    scope = __parse_scope(parser)
    unpack_scope(scope)

    t = parser._next()
    parser._test(t,
                expected=[TokenType.Semicolon],
                err_code=idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration,
                tip='`class` type should be followed by `;`')

    return clss
