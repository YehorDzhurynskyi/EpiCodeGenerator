from epigen.idlparser import idlparser_base as idl

from epigen.tokenizer import TokenType

from epigen.symbol import EpiProperty


def parse_property(parser: idl.IDLParser) -> EpiProperty:

    tokentype_types = [TokenType.Identifier]
    tokentype_types.extend(TokenType.builtin_types())

    parser._test(parser._curr(), expected=tokentype_types, err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    tokentype = parser._next()
    tokens_nested = []
    form = EpiProperty.Form.Plain

    if tokentype is not None and tokentype.is_templated():

        if parser._test(parser._curr(), expected=[TokenType.OpenAngleBracket], err_code=idl.IDLSyntaxErrorCode.MissingTemplateArguments, fatal=False):

            parser._next()

            form = EpiProperty.Form.Template
            if parser._test(parser._curr(), expected=tokentype_types, err_code=idl.IDLSyntaxErrorCode.UnexpectedToken, fatal=False):

                # TODO: parse >1 number of template arguments
                tokens_nested.append(parser._next())

            t = parser._next()
            parser._test(t, expected=[TokenType.CloseAngleBracket], err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket)

            if len(tokens_nested) == 0:
                parser._push_error(t, idl.IDLSyntaxErrorCode.MissingTemplateArguments, fatal=False)

    if parser._test(parser._curr(), expected=[TokenType.Asterisk]):

        form = EpiProperty.Form.Pointer
        parser._next()

    while not parser._test(parser._curr(), unexpected=[TokenType.Asterisk], err_code=idl.IDLSyntaxErrorCode.MultiDepthPointer, fatal=False):
        parser._next()

    t = parser._curr()
    if parser._test(t, expected=[TokenType.Ampersand]):
            assert False

    t = parser._next()
    parser._test(t, expected=[TokenType.Identifier], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken, fatal=False)

    prty = EpiProperty(t, tokentype, form)

    if prty.form == EpiProperty.Form.Template:
        prty.tokens_nested = tokens_nested

    t = parser._next()
    if parser._test(t, expected=[TokenType.Assing]):

        t = parser._next()
        parser._test(t,
                    expected=TokenType.literals(),
                    err_code=idl.IDLSyntaxErrorCode.IncorrectValueAssignment,
                    tip="The assigned value isn't a literal",
                    fatal=False)

        if prty.tokentype.tokentype == TokenType.Identifier:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Only fundamental types are assingable', fatal=False)
        elif prty.form == EpiProperty.Form.Pointer:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Pointers are unassingable and are set with \'null\' by default', fatal=False)
        elif prty.form == EpiProperty.Form.Template:
            parser._push_error(t, idl.IDLSyntaxErrorCode.IncorrectValueAssignment, 'Template types are unassingable', fatal=False)
        else:

            if parser._test(prty.tokentype, expected=TokenType.assignable(), err_code=idl.IDLSyntaxErrorCode.IncorrectValueAssignment, fatal=False):
                parser._test(t, expected=TokenType.literals_of(prty.tokentype.tokentype), err_code=idl.IDLSyntaxErrorCode.IncorrectValueLiteral, fatal=False)

            prty.tokenvalue = t

        t = parser._next()

    parser._test(t, expected=[TokenType.Semicolon], err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

    return prty