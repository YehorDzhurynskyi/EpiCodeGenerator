import pytest

from epi_code_generator.tokenizer import Tokenizer, TokenType


TOKEN_AVAILABLE = [
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

    def test_token_available(self):

        path = 'tests/data/idl/tokens.epi'

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        for t1, t2 in zip(TOKEN_AVAILABLE, tokens):
            assert t1 == t2.type

    def test_token_empty(self, tmpdir):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write('')

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    @pytest.mark.parametrize('text,expected_type,expected_text', [
        # Identifiers
        ('Name', [TokenType.Identifier], ['Name']),
        ('name', [TokenType.Unknown], ['name']),
        ('1name', [TokenType.Unknown, TokenType.Unknown], ['1', 'name']),
        ('_Name', [TokenType.Unknown, TokenType.Identifier], ['_', 'Name']),
        ('1Name', [TokenType.Unknown, TokenType.Identifier], ['1', 'Name']),
        ('Name AnotherName', [TokenType.Identifier, TokenType.Identifier], ['Name', 'AnotherName']),
        ('NameWithDigits12', [TokenType.Identifier], ['NameWithDigits12']),
        ('12NameWithDigits12', [TokenType.Unknown, TokenType.Identifier], ['12', 'NameWithDigits12']),
        ('NameWith_Underscore', [TokenType.Identifier], ['NameWith_Underscore']),
        ('NameWith_UnderscoreOnEnd_', [TokenType.Identifier], ['NameWith_UnderscoreOnEnd_']),
        ('NameWith12Digits_And_Undersc0reOnEnd_', [TokenType.Identifier], ['NameWith12Digits_And_Undersc0reOnEnd_']),
        ('NameWith12And_Undersc0reDigitsOnEnd_071', [TokenType.Identifier], ['NameWith12And_Undersc0reDigitsOnEnd_071']),
        ('Name 12NameWithDigits12', [TokenType.Identifier, TokenType.Unknown, TokenType.Identifier], ['Name', '12', 'NameWithDigits12']),
        ('   12NameWithDigits12 12 ', [TokenType.Unknown, TokenType.Identifier, TokenType.IntegerLiteral], ['12', 'NameWithDigits12', '12']),

        # Literals Valid
        ("'c'", [TokenType.CharLiteral], ["'c'"]),
        ("L'c'", [TokenType.WCharLiteral], ["L'c'"]),
        ("'\\0'", [TokenType.CharLiteral], ["'\\0'"]),
        ("L'\\0'", [TokenType.WCharLiteral], ["L'\\0'"]),
        ('"string"', [TokenType.StringLiteral], ['"string"']),
        ('L"string"', [TokenType.WStringLiteral], ['L"string"']),
        ('" \\ string\\t "', [TokenType.StringLiteral], ['" \\ string\\t "']),
        ('"  string\\t "', [TokenType.StringLiteral], ['"  string\\t "']),
        ('"  string\\t\\n "', [TokenType.StringLiteral], ['"  string\\t\\n "']),
        ('L"  string \\t \\n "', [TokenType.WStringLiteral], ['L"  string \\t \\n "']),
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
        ('false', [TokenType.FalseLiteral], ['false']),

        # Literals Invalid
        ('42f', [TokenType.Unknown, TokenType.Unknown], ['42', 'f']),
        ('42foo', [TokenType.Unknown, TokenType.Unknown], ['42', 'foo']),
        ("L'", [TokenType.Unknown], ["L'"]),
        ('L"', [TokenType.Unknown], ['L"']),
        ("L'a epiString", [TokenType.Unknown, TokenType.StringType], ["L'a", 'epiString']),
        ("L'a; epiString", [TokenType.Unknown, TokenType.Semicolon, TokenType.StringType], ["L'a", ';', 'epiString']),
        ('L"String epiS32', [TokenType.Unknown], ['L"String epiS32']),
        ('L"String; epiS32', [TokenType.Unknown], ['L"String; epiS32']),
        ('L "String epiS32', [TokenType.Identifier, TokenType.Unknown], ['L', '"String epiS32']),
        ('L "String; epiS32', [TokenType.Identifier, TokenType.Unknown], ['L', '"String; epiS32']),

        # Special symbols
        (';', [TokenType.Semicolon], [';']),
        (';;;;', [TokenType.Semicolon], [';']),
        ('  ; ; ; ; ;  ', [TokenType.Semicolon], [';']),
        ('::', [TokenType.Colon, TokenType.Colon], [':', ':']),
        ('**', [TokenType.Asterisk, TokenType.Asterisk], ['*', '*']),
        ('&&', [TokenType.Ampersand, TokenType.Ampersand], ['&', '&']),
        ('+', [TokenType.Unknown], ['+']),
        ('++', [TokenType.Unknown, TokenType.Unknown], ['+', '+']),
        ('-', [TokenType.Unknown], ['-']),
        ('--', [TokenType.Unknown, TokenType.Unknown], ['-', '-']),
        ('=', [TokenType.Assing], ['=']),
        ('==', [TokenType.Assing, TokenType.Assing], ['=', '=']),
        ("'", [TokenType.Unknown], ["'"]),
        ('"', [TokenType.Unknown], ['"']),
    ])
    def test_token_sequence(self, tmpdir, text, expected_type, expected_text):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write(text)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) > 0

        for exp_type, exp_text, token in zip(expected_type, expected_text, tokens):

            assert exp_type == token.type
            assert exp_text == token.text

        assert tokens[-1].type == TokenType.EOF
