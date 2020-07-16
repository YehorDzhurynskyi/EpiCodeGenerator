from epi_code_generator.symbol.symbol import EpiSymbol
from epi_code_generator.symbol.symbol import EpiAttribute
from epi_code_generator.symbol.symbol import EpiVariable

from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import TokenType

from epi_code_generator.idlparser import idlparser_base as idl


class EpiAttributeValidationError(Exception):

    def __init__(self, msg: str, token: Token, err_code: idl.IDLSyntaxErrorCode):

        super().__init__(msg)
        self.token = token
        self.err_code = err_code


__EPI_ATTRIBUTE_CONFLICT_TABLE = {
    TokenType.WriteCallback: [TokenType.ReadOnly],
    TokenType.ReadCallback: [TokenType.WriteOnly],
    TokenType.Virtual: [],
    TokenType.ReadOnly: [TokenType.WriteOnly],
    TokenType.WriteOnly: [TokenType.ReadOnly],
    TokenType.Transient: [],
    TokenType.ExpectMin: [TokenType.ReadOnly, TokenType.ForceMin],
    TokenType.ExpectMax: [TokenType.ReadOnly, TokenType.ForceMax],
    TokenType.ForceMin: [TokenType.ReadOnly, TokenType.ExpectMin],
    TokenType.ForceMax: [TokenType.ReadOnly, TokenType.ExpectMax]
}


def __validate_conflicts(attr: EpiAttribute, target: EpiSymbol):

    for a in target.attrs:

        if a.token.tokentype == attr.token.tokentype:
            raise EpiAttributeValidationError(f'It duplicates {a.token}', attr.token, idl.IDLSyntaxErrorCode.AttributeConflict)

        assert attr.token.tokentype in __EPI_ATTRIBUTE_CONFLICT_TABLE

        if a.token.tokentype in __EPI_ATTRIBUTE_CONFLICT_TABLE[attr.token.tokentype]:
            raise EpiAttributeValidationError(f'It conflicts with {a.token}', attr.token, idl.IDLSyntaxErrorCode.AttributeConflict)


def __validate_parameters_positional(attr: EpiAttribute, positional: list):

    if len(positional) != len(attr.__params_positional):

        msg = f'Number of arguments should be {len(positional)} but were {len(attr.__params_positional)} provided'
        raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)

    for tokenparam, ptypes in zip(attr.__params_positional, positional):

        if tokenparam.tokentype not in ptypes:

            msg = f'{tokenparam.text} positional parameter has a wrong type (the type should be {" or ".join(ptypes)})'
            raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)


def __validate_parameters_named(attr: EpiAttribute, named: dict):

    for name, tokenparam in attr.__params_named:

        if name not in named:

            msg = f'Invalid named parameter {name} was provided'
            raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)

        ptypes = named[name]
        if tokenparam.tokentype not in ptypes:

            msg = f'Invalid named parameter type {tokenparam.tokentype} was provided (but should be {" or ".join(ptypes)})'
            raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidParameters)


def __validate_target(attr: EpiAttribute, target: EpiSymbol, acceptable_targets: list):

    assert isinstance(target, EpiSymbol)

    if not any(isinstance(target, t) for t in acceptable_targets):

        msg = f'An attribute applied to the wrong target (should be applied to: { " or ".join(acceptable_targets) })'
        raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidTarget)


def __validate_target_type(attr: EpiAttribute, target: EpiSymbol, acceptable_targets: list):

    if isinstance(target, EpiVariable):

        if not any(target.tokentype for t in acceptable_targets):

            msg = f'An attribute applied to the wrong target-type (should be applied to: { " or ".join(acceptable_targets) })'
            raise EpiAttributeValidationError(msg, attr.token, idl.IDLSyntaxErrorCode.AttributeInvalidTarget)

    else:
        assert False, 'Unhandled case!'


def __implies(tokentype: TokenType, target: EpiSymbol):

    try:
        target.attr_push(EpiAttribute(tokentype))
    except EpiAttributeValidationError:
        pass


def introduce_WriteCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })
    __validate_parameters_named(attr, {})


def introduce_ReadCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })


def introduce_Virtual(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})

    __implies(TokenType.Transient, target)
    __implies(TokenType.WriteCallback, target)
    __implies(TokenType.ReadCallback, target)


def introduce_ReadOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_WriteOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_Transient(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_ExpectMin(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
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
    __validate_parameters_positional(attr, [TokenType.literals_of(target.token.tokentype)])
    __validate_parameters_named(attr, {})


def introduce_ExpectMax(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
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
    __validate_parameters_positional(attr, [TokenType.literals_of(target.token.tokentype)])
    __validate_parameters_named(attr, {})


def introduce_ForceMin(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
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
    __validate_parameters_positional(attr, [TokenType.literals_of(target.token.tokentype)])
    __validate_parameters_named(attr, {})


def introduce_ForceMax(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(attr, target, [EpiVariable])
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
    __validate_parameters_positional(attr, [TokenType.literals_of(target.token.tokentype)])
    __validate_parameters_named(attr, {})


def __parse_attr(parser: idl.IDLParser) -> EpiAttribute:

    a_t = parser._next()

    attr = EpiAttribute(a_t.tokentype)

    if not parser._test(parser._curr(), [TokenType.OpenBracket]):
        return attr

    has_named_params = False

    parser._next(2)
    while True:

        if parser._test(parser._curr(), [TokenType.CloseBracket]):
            break

        param = parser._next()
        if not parser._test(parser._curr(), [TokenType.Assing]):

            if has_named_params:

                tip = 'Named parameters should come after positional parameters'
                parser._push_error(param, idl.IDLSyntaxErrorCode.AttributeInvalidParameters, tip)

            attr.param_push_positional(param)
        else:

            has_named_params = True
            attr.param_push_named(param.text, parser._next(2))

        if not parser._test(parser._curr().tokentype, [TokenType.Comma]):
            break

        parser._next()

    parser._test(parser._next(), [TokenType.CloseBracket], err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket)

    return attr


def parse_attr_list(parser: idl.IDLParser) -> list:

    attrs = []
    while True:

        t = parser._curr()
        if not parser._test(t, [TokenType.OpenSqBracket]):
            break

        parser._next()
        while True:

            parser._test(parser._curr(), TokenType.attributes(), err_code=idl.IDLSyntaxErrorCode.UnexpectedToken)

            attr = __parse_attr(parser)
            attrs.append(attr)

            if not parser._test(parser._curr(), [TokenType.Comma]):
                break

            parser._next()

        t = parser._next()
        parser._test(t,
                    [TokenType.CloseSqBracket],
                    err_code=idl.IDLSyntaxErrorCode.NoMatchingClosingBracket,
                    tip='Attribute list should be followed by `]`')

    return attrs
