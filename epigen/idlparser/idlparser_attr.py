from epigen.symbol import EpiSymbol
from epigen.symbol import EpiAttribute
from epigen.symbol import EpiProperty
from epigen.symbol import EpiEnum

from epigen.tokenizer import Token
from epigen.tokenizer import TokenType

from epigen.idlparser import idlparser_base as idl


def __validate_conflicts(attr: EpiAttribute, target: EpiSymbol):

    for a in target.attrs:

        if a.is_implied_indirectly:
            continue

        if a.tokentype == attr.tokentype:
            raise idl.IDLParserError(f'It duplicates {a.tokentype.name}', attr.token, idl.IDLSyntaxErrorCode.AttributeConflict)

        if attr.conflicts(a):
            raise idl.IDLParserError(f'It conflicts with {a.tokentype.name}', attr.token, idl.IDLSyntaxErrorCode.AttributeConflict)


def __validate_parameters_positional(attr: EpiAttribute, positional: list):

    if len(positional) != len(attr.params_positional):

        msg = f'Number of arguments should be {len(positional)} but {len(attr.params_positional)} was provided'
        raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)

    for tokenparam, ptypes in zip(attr.params_positional, positional):

        if tokenparam.tokentype not in ptypes:

            msg = f'{tokenparam.text} positional parameter has a wrong type (the type should be {" or ".join(p.name for p in ptypes)})'
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)


def __validate_parameters_named(attr: EpiAttribute, named: dict):

    for name, tokenparam in attr.params_named.items():

        if name not in named:

            msg = f'Invalid named parameter {name} was provided'
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)

        ptypes = named[name]
        if tokenparam.tokentype not in ptypes:

            msg = f'Invalid named parameter type {tokenparam.tokentype} was provided (but should be {" or ".join(p.name for p in ptypes)})'
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)


def __validate_parameters_named_target_type(attr: EpiAttribute, target: EpiSymbol, named: dict):

    assert isinstance(target, EpiProperty)

    for name in attr.params_named:

        assert name in named, 'check with `__validate_parameters_named` before'

        ptypes = named[name]
        if target.tokentype.tokentype not in ptypes:

            msg = f"An attribute couldn't be applied to the following target={target.tokentype.tokentype.name}"
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)


def __validate_target(attr: EpiAttribute, target: EpiSymbol, acceptable_targets: list):

    assert isinstance(target, EpiSymbol)

    if not any(isinstance(target, t) for t in acceptable_targets):

        msg = f'An attribute applied to the wrong target (should be applied to: { " or ".join([repr(t) for t in acceptable_targets]) })'
        raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidTarget)


def __validate_target_unassigned(attr: EpiAttribute, target: EpiSymbol):

    assert isinstance(target, EpiProperty)

    if target.value_is_assigned():

        msg = f'`{attr.tokentype.name}` attribute target is unassignable'
        raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.IncorrectValueAssignment)


def __validate_target_type(attr: EpiAttribute, target: EpiSymbol, acceptable_targets: list):

    if isinstance(target, EpiProperty):

        if target.tokentype.tokentype not in acceptable_targets:

            msg = f'An attribute applied to the wrong target-type (should be applied to: { " or ".join(t.name for t in acceptable_targets) })'
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidTarget)

    else:
        assert False, 'Unhandled case!'


def __validate_target_form(attr: EpiAttribute, target: EpiSymbol, acceptable_forms: list):

    if isinstance(target, EpiProperty):

        if target.form not in acceptable_forms:

            msg = f'An attribute applied to the wrong target-form (should be applied to: { " or ".join(t.name for t in acceptable_forms) })'
            raise idl.IDLParserError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidTarget)

    else:
        assert False, 'Unhandled case!'


def __validate_target_value_greater_eq(attr: EpiAttribute, target: EpiSymbol, value):

    assert isinstance(target, EpiProperty)

    if target.value_of() < value:

        msg = f"{attr.token} restricts target's value to be >= {value}"
        raise idl.IDLParserError(msg, target.token, idl.IDLSyntaxErrorCode.IncorrectValueAssignment)


def __validate_target_value_less_eq(attr: EpiAttribute, target: EpiSymbol, value):

    assert isinstance(target, EpiProperty)

    if target.value_of() > value:

        msg = f"{attr.token} restricts target's value to be <= {value}"
        raise idl.IDLParserError(msg, target.token, idl.IDLSyntaxErrorCode.IncorrectValueAssignment)


def __implies(tokentype: TokenType, target: EpiSymbol):

    try:
        attr = EpiAttribute(tokentype)
        attr.is_implied_indirectly = True

        target.attr_push(attr)

    except idl.IDLParserError:
        pass


def introduce_DisplayName(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_parameters_positional(attr, [[TokenType.StringLiteral]])


def introduce_WriteCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_target_unassigned(attr, target)
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral],
        'RValueRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })

    types = [TokenType.Identifier, TokenType.ArrayType, TokenType.PtrArrayType]
    types.extend(TokenType.compounds())

    __validate_parameters_named_target_type(attr, target, {
        'SuppressRef': types,
        'RValueRef': types
    })


def introduce_ReadCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })

    types = [TokenType.Identifier, TokenType.ArrayType, TokenType.PtrArrayType]
    types.extend(TokenType.compounds())

    __validate_parameters_named_target_type(attr, target, {
        'SuppressRef': types
    })


def introduce_Virtual(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_target_unassigned(attr, target)
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})

    __implies(TokenType.Transient, target)
    __implies(TokenType.WriteCallback, target)
    __implies(TokenType.ReadCallback, target)


def introduce_ReadOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_WriteOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_Transient(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_Min(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_target_type(attr, target, [TokenType.SingleFloatingType,
                                          TokenType.DoubleFloatingType,
                                          TokenType.Int8Type,
                                          TokenType.Int16Type,
                                          TokenType.Int32Type,
                                          TokenType.Int64Type,
                                          TokenType.UInt8Type,
                                          TokenType.UInt16Type,
                                          TokenType.UInt32Type,
                                          TokenType.UInt64Type,
                                          TokenType.ByteType,
                                          TokenType.SizeTType])
    __validate_target_form(attr, target, [EpiProperty.Form.Plain])
    __validate_parameters_positional(attr, [TokenType.literals_of(target.tokentype.tokentype)])
    __validate_parameters_named(attr, {
        'Force': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })
    __validate_target_value_greater_eq(attr, target, attr.param_positional_at(0).value())


def introduce_Max(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiProperty])
    __validate_target_type(attr, target, [TokenType.SingleFloatingType,
                                          TokenType.DoubleFloatingType,
                                          TokenType.Int8Type,
                                          TokenType.Int16Type,
                                          TokenType.Int32Type,
                                          TokenType.Int64Type,
                                          TokenType.UInt8Type,
                                          TokenType.UInt16Type,
                                          TokenType.UInt32Type,
                                          TokenType.UInt64Type,
                                          TokenType.ByteType,
                                          TokenType.SizeTType])
    __validate_target_form(attr, target, [EpiProperty.Form.Plain])
    __validate_parameters_positional(attr, [TokenType.literals_of(target.tokentype.tokentype)])
    __validate_parameters_named(attr, {
        'Force': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })
    __validate_target_value_less_eq(attr, target, attr.param_positional_at(0).value())


def introduce_FlagMask(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiEnum])

    for e in target.entries:

        incorrect = next((e for v in e.valuetokens if v.tokentype not in [TokenType.Identifier, TokenType.VSlash]), None)
        if incorrect is not None:
            raise idl.IDLParserError(f'Flags could be assigned only with an `identifiers`', incorrect, idl.IDLSyntaxErrorCode.IncorrectValueLiteral)


def __parse_attr(parser: idl.IDLParser) -> EpiAttribute:

    a_t = parser._next()

    attr = EpiAttribute(a_t.tokentype, a_t)

    if not parser._test(parser._curr(), expected=[TokenType.OpenBracket]):
        return attr

    has_named_params = False

    parser._next()
    while True:

        if parser._test(parser._curr(), expected=[TokenType.CloseBracket]):
            break

        param = parser._next()
        if not parser._test(parser._curr(), expected=[TokenType.Assing]):

            if has_named_params:

                tip = 'Named parameters should come after positional parameters'
                parser._push_error(param, idl.IDLSyntaxErrorCode.AttributeInvalidParameters, tip, fatal=False)

            attr.param_positional_push(param)
        else:

            has_named_params = True
            attr.param_named_push(param.text, parser._next(2))

        if not parser._test(parser._curr(), expected=[TokenType.Comma]):
            break

        parser._next()

    parser._test(parser._next(), expected=[TokenType.CloseBracket], err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket)

    return attr


def parse_attr_list(parser: idl.IDLParser) -> list:

    attrs = []
    while True:

        t = parser._curr()
        if not parser._test(t, expected=[TokenType.OpenSqBracket]):
            break

        parser._next()
        while True:

            parser._test(parser._curr(), expected=TokenType.attributes(), err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

            attr = __parse_attr(parser)
            attrs.append(attr)

            if not parser._test(parser._curr(), expected=[TokenType.Comma]):
                break

            parser._next()

        t = parser._next()
        parser._test(t,
                    expected=[TokenType.CloseSqBracket],
                    err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket,
                    tip='Attribute list should be followed by `]`')

    return attrs
