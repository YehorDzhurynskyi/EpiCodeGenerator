from epi_code_generator.idlparser import idlparser_base as idl

from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol.symbol import EpiProperty


def parse_property(parser: idl.IDLParser) -> EpiProperty:

    tokentype_types = [TokenType.Identifier]
    tokentype_types.extend(TokenType.builtin_types())

    parser._test(parser._curr(), tokentype_types, err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    tokentype = parser._next()
    tokens_nested = []
    form = EpiProperty.Form.Plain

    if tokentype is not None and tokentype.is_templated():

        if parser._test(parser._curr(), [TokenType.OpenAngleBracket], err_code=idl.IDLSyntaxErrorCode.MissingTemplateArguments, fatal=False):

            parser._next()

            form = EpiProperty.Form.Template
            if parser._test(parser._curr(), tokentype_types, err_code=idl.IDLSyntaxErrorCode.UnexpectedToken, fatal=False):

                # TODO: parse >1 number of template arguments
                tokens_nested.append(parser._next())

            t = parser._next()
            parser._test(t, [TokenType.CloseAngleBracket], err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket)

            if len(tokens_nested) == 0:
                parser._push_error(t, idl.IDLSyntaxErrorCode.MissingTemplateArguments, fatal=False)

    while True:

        t = parser._curr()
        if parser._test(t, [TokenType.Asterisk]):

            form = EpiProperty.Form.Pointer
            tokentype.text += '*'
            parser._next()

        else:
            break

    t = parser._curr()
    if parser._test(t, [TokenType.Ampersand]):

            assert False
            # form = EpiProperty.Form.Reference
            # parser._next()

    t = parser._next()
    parser._test(t, [TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken, fatal=False)

    prty = EpiProperty(t, tokentype, form)

    if prty.form == EpiProperty.Form.Template:
        prty.tokens_nested = tokens_nested

    # NOTE: if property is virtual an assignment is invalid
    t = parser._next()
    if parser._test(t, [TokenType.Assing]):

        t = parser._next()
        parser._test(t,
                    TokenType.literals(),
                    err_code=idl.IDLSyntaxErrorCode.IncorrectValueAssignment,
                    tip="The assigned value isn't a literal",
                    fatal=False)

        # TODO: add suppress exception
        if prty.tokentype.tokentype == TokenType.Identifier:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Only fundamental types are assingable', fatal=False)
        elif prty.form == EpiProperty.Form.Pointer:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Pointers are unassingable and are set with \'null\' by default', fatal=False)
        elif prty.form == EpiProperty.Form.Template:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Template types are unassingable', fatal=False)
        else:

            if parser._test(prty.tokentype, TokenType.assignable(), err_code=idl.IDLSyntaxErrorCode.IncorrectValueAssignment, fatal=False):
                parser._test(t, TokenType.literals_of(prty.tokentype.tokentype), err_code=idl.IDLSyntaxErrorCode.IncorrectValueLiteral, fatal=False)

            prty.tokenvalue = t

        t = parser._next()

    parser._test(t, [TokenType.Semicolon], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    return prty
