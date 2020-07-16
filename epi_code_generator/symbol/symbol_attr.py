from epi_code_generator.symbol.symbol import EpiSymbol
from epi_code_generator.symbol.symbol import EpiAttribute
from epi_code_generator.symbol.symbol import EpiAttributeValidationError
from epi_code_generator.symbol.symbol import EpiVariable

from epi_code_generator.tokenizer import TokenType


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

        if a.tokentype == attr.tokentype:
            raise EpiAttributeValidationError(f'It duplicates {a.tokentype}')

        assert attr.tokentype in __EPI_ATTRIBUTE_CONFLICT_TABLE

        if a.tokentype in __EPI_ATTRIBUTE_CONFLICT_TABLE[attr.tokentype]:
            raise EpiAttributeValidationError(f'It conflicts with {a.tokentype}')


def __validate_parameters_positional(attr: EpiAttribute, positional: list):

    if len(positional) != len(attr.__params_positional):

        msg = f'Number of arguments should be {len(positional)} but were {len(attr.__params_positional)} provided'
        raise EpiAttributeValidationError(msg)

    for tokenparam, ptypes in zip(attr.__params_positional, positional):

        if tokenparam.tokentype not in ptypes:

            msg = f'{tokenparam.text} positional parameter has a wrong type (the type should be {" or ".join(ptypes)})'
            raise EpiAttributeValidationError(msg)


def __validate_parameters_named(attr: EpiAttribute, named: dict):

    for name, tokenparam in attr.__params_named:

        if name not in named:

            msg = f'Invalid named parameter {name} was provided'
            raise EpiAttributeValidationError(msg)

        ptypes = named[name]
        if tokenparam.tokentype not in ptypes:

            msg = f'Invalid named parameter type {tokenparam.tokentype} was provided (but should be {" or ".join(ptypes)})'
            raise EpiAttributeValidationError(msg)


def __validate_target(target: EpiSymbol, acceptable_targets: list):

    assert isinstance(target, EpiSymbol)

    if not any(isinstance(target, t) for t in acceptable_targets):

        msg = f'An attribute applied to the wrong target (should be applied to: { " or ".join(acceptable_targets) })'
        raise EpiAttributeValidationError(msg)


def __validate_target_type(target: EpiSymbol, acceptable_targets: list):

    if isinstance(target, EpiVariable):

        if not any(target.tokentype for t in acceptable_targets):

            msg = f'An attribute applied to the wrong target-type (should be applied to: { " or ".join(acceptable_targets) })'
            raise EpiAttributeValidationError(msg)

    else:
        assert False, 'Unhandled case!'


def __implies(tokentype: TokenType, target: EpiSymbol):

    try:
        target.attr_push(EpiAttribute(tokentype))
    except EpiAttributeValidationError:
        pass


def introduce_WriteCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })
    __validate_parameters_named(attr, {})


def introduce_ReadCallback(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {
        'SuppressRef': [TokenType.TrueLiteral, TokenType.FalseLiteral]
    })


def introduce_Virtual(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})

    __implies(TokenType.Transient, target)
    __implies(TokenType.WriteCallback, target)
    __implies(TokenType.ReadCallback, target)


def introduce_ReadOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_WriteOnly(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_Transient(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_parameters_positional(attr, [])
    __validate_parameters_named(attr, {})


def introduce_ExpectMin(attr: EpiAttribute, target: EpiSymbol):

    __validate_conflicts(attr, target)
    __validate_target(target, [EpiVariable])
    __validate_target_type(target, [TokenType.SingleFloatingType,
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
    __validate_target(target, [EpiVariable])
    __validate_target_type(target, [TokenType.SingleFloatingType,
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
    __validate_target(target, [EpiVariable])
    __validate_target_type(target, [TokenType.SingleFloatingType,
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
    __validate_target(target, [EpiVariable])
    __validate_target_type(target, [TokenType.SingleFloatingType,
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
