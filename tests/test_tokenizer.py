import pytest

from epi_code_generator.tokenizer import Tokenizer, TokenType


TOKEN_SEQUENCE = [
    TokenType.OpenBrace,
    TokenType.CloseBrace,
    TokenType.OpenAngleBracket,
    TokenType.CloseAngleBracket,
    TokenType.OpenBracket,
    TokenType.CloseBracket,
    TokenType.OpenSqBracket,
    TokenType.CloseSqBracket,
    TokenType.Assing,
    TokenType.Comma,
    TokenType.Asterisk,
    TokenType.Ampersand,
    TokenType.Colon,
    TokenType.Semicolon,
    TokenType.CharLiteral,
    TokenType.WCharLiteral,
    TokenType.StringLiteral,
    TokenType.WStringLiteral,
    TokenType.IntegerLiteral,
    TokenType.IntegerLiteral,
    TokenType.IntegerLiteral,
    TokenType.IntegerLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.SingleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.DoubleFloatingLiteral,
    TokenType.TrueLiteral,
    TokenType.FalseLiteral,
    TokenType.CharType,
    TokenType.WCharType,
    TokenType.BoolType,
    TokenType.ByteType,
    TokenType.SizeTType,
    TokenType.HashTType,
    TokenType.UIntType,
    TokenType.UIntType,
    TokenType.UIntType,
    TokenType.UIntType,
    TokenType.IntType,
    TokenType.IntType,
    TokenType.IntType,
    TokenType.IntType,
    TokenType.StringType,
    TokenType.WStringType,
    TokenType.ArrayType,
    TokenType.PtrArrayType,
    TokenType.SingleFloatingType,
    TokenType.DoubleFloatingType,
    TokenType.Vec2FType,
    TokenType.Vec2DType,
    TokenType.Vec2SType,
    TokenType.Vec2UType,
    TokenType.Vec3FType,
    TokenType.Vec3DType,
    TokenType.Vec3SType,
    TokenType.Vec3UType,
    TokenType.Vec4FType,
    TokenType.Vec4DType,
    TokenType.Vec4SType,
    TokenType.Vec4UType,
    TokenType.Mat2x2FType,
    TokenType.Mat3x3FType,
    TokenType.Mat4x4FType,
    TokenType.Rect2FType,
    TokenType.Rect2DType,
    TokenType.Rect2SType,
    TokenType.Rect2UType,
    TokenType.ClassType,
    TokenType.ReadOnly,
    TokenType.WriteOnly,
    TokenType.Private,
    TokenType.WriteCallback,
    TokenType.ReadCallback,
    TokenType.Virtual,
    TokenType.ExpectMin,
    TokenType.ExpectMax,
    TokenType.ForceMin,
    TokenType.ForceMax,
    TokenType.Transient,
    TokenType.Identifier,
    TokenType.Identifier,
    TokenType.EOF
]


class TestTokenizer:

    def test_token_sequence(self):

        path = 'tests/data/idl/tokens.epi'

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        i = 0
        for t1, t2 in zip(TOKEN_SEQUENCE, tokens):

            t_prev = tokens[i - 1].text if i > 0 else ''
            msg = f'`{t2.text}` (prev token=`{t_prev}`) expected to be <{t1}>, but it`s <{t2.type}>'
            assert t1 == t2.type, msg

            i += 1

    @pytest.mark.parametrize('text,expected_type,expected_text', [
        ("'c'", [TokenType.CharLiteral], ["'c'"]),
        ("L'c'", [TokenType.WCharLiteral], ["L'c'"]),
        ("'\\0'", [TokenType.CharLiteral], ["'\\0'"]),
        ("L'\\0'", [TokenType.WCharLiteral], ["L'\\0'"]),
        ('"string"', [TokenType.StringLiteral], ['"string"']),
        ('L"string"', [TokenType.WStringLiteral], ['L"string"']),
        ('"  string\t\n "', [TokenType.StringLiteral], ['"  string\t\n "']),
        ('L"  string \t \n "', [TokenType.WStringLiteral], ['L"  string \t \n "']),
        ('42', [TokenType.IntegerLiteral], ['42']),
        ('+42', [TokenType.IntegerLiteral], ['+42']),
        ('-42', [TokenType.IntegerLiteral], ['-42']),
        ('0', [TokenType.IntegerLiteral], ['0']),
        ('+0', [TokenType.IntegerLiteral], ['+0']),
        ('-0', [TokenType.IntegerLiteral], ['-0']),
        ('42.0f', [TokenType.SingleFloatingLiteral], ['42.0f']),
        ('+42.0f', [TokenType.SingleFloatingLiteral], ['+42.0f']),
        ('-42.0f', [TokenType.SingleFloatingLiteral], ['-42.0f']),
        ('0.0f', [TokenType.SingleFloatingLiteral], ['0.0f']),
        ('+0.0f', [TokenType.SingleFloatingLiteral], ['+0.0f']),
        ('-0.0f', [TokenType.SingleFloatingLiteral], ['-0.0f']),
        ('4200.000005f', [TokenType.SingleFloatingLiteral], ['4200.000005f']),
        ('+4200.000005f', [TokenType.SingleFloatingLiteral], ['+4200.000005f']),
        ('-4200.000005f', [TokenType.SingleFloatingLiteral], ['-4200.000005f']),
        ('0.00000005f', [TokenType.SingleFloatingLiteral], ['0.00000005f']),
        ('+0.00000005f', [TokenType.SingleFloatingLiteral], ['+0.00000005f']),
        ('-0.00000005f', [TokenType.SingleFloatingLiteral], ['-0.00000005f']),
        ('42.0', [TokenType.DoubleFloatingLiteral], ['42.0']),
        ('+42.0', [TokenType.DoubleFloatingLiteral], ['+42.0']),
        ('-42.0', [TokenType.DoubleFloatingLiteral], ['-42.0']),
        ('0.0', [TokenType.DoubleFloatingLiteral], ['0.0']),
        ('+0.0', [TokenType.DoubleFloatingLiteral], ['+0.0']),
        ('-0.0', [TokenType.DoubleFloatingLiteral], ['-0.0']),
        ('4200.000005', [TokenType.DoubleFloatingLiteral], ['4200.000005']),
        ('+4200.000005', [TokenType.DoubleFloatingLiteral], ['+4200.000005']),
        ('-4200.000005', [TokenType.DoubleFloatingLiteral], ['-4200.000005']),
        ('0.00000005', [TokenType.DoubleFloatingLiteral], ['0.00000005']),
        ('+0.00000005', [TokenType.DoubleFloatingLiteral], ['+0.00000005']),
        ('-0.00000005', [TokenType.DoubleFloatingLiteral], ['-0.00000005']),
        ('true', [TokenType.TrueLiteral], ['true']),
        ('false', [TokenType.FalseLiteral], ['false'])
    ])
    def test_token_literal(self, tmpdir, text, expected_type, expected_text):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write(text)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        i = 0
        for exp_type, exp_text, token in zip(expected_type, expected_text, tokens):

            t_prev = tokens[i - 1].text if i > 0 else ''

            msg = f'`{token.text}` (prev token=`{t_prev}`) expected to be <{exp_type}>, but it`s <{token.type}>'
            assert exp_type == token.type, msg
            assert exp_text == token.text

            i += 1
