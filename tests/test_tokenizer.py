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
    TokenType.FloatingLiteral,
    TokenType.FloatingLiteral,
    TokenType.FloatingLiteral,
    TokenType.FloatingLiteral,
    TokenType.FloatingLiteral,
    TokenType.FloatingLiteral,
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
    TokenType.FloatingType,
    TokenType.FloatingType,
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

        for t1, t2 in zip(TOKEN_SEQUENCE, tokens):
            assert t1 == t2.type

    @pytest.mark.parametrize('text,expected', [
        ('42', [TokenType.IntegerLiteral]),
        ('+42', [TokenType.IntegerLiteral]),
        ('-42', [TokenType.IntegerLiteral]),
        ('0', [TokenType.IntegerLiteral]),
        ('+0', [TokenType.IntegerLiteral]),
        ('-0', [TokenType.IntegerLiteral])
    ])
    def test_token_literal(self, tmpdir, text, expected):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write(text)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        for t1, t2 in zip(expected, tokens):
            assert t1 == t2.type
