import pytest

from epigen.tokenizer import Tokenizer, TokenType


@pytest.mark.order(0)
class TestTokenizer:

    def test_empty(self, tmpdir: str):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write('')

        tokenizer = Tokenizer(path, path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) == 0

    @pytest.mark.parametrize('text,expected_type,expected_text', [
        # Identifiers
        ('Name', [TokenType.Identifier], ['Name']),
        ('name', [TokenType.Identifier], ['name']),
        ('1name', [TokenType.Unknown], ['1name']),
        ('_Name', [TokenType.Unknown, TokenType.Identifier], ['_', 'Name']),
        ('1Name', [TokenType.Unknown], ['1Name']),
        ('Name AnotherName', [TokenType.Identifier, TokenType.Identifier], ['Name', 'AnotherName']),
        ('NameWithDigits12', [TokenType.Identifier], ['NameWithDigits12']),
        ('12NameWithDigits12', [TokenType.Unknown], ['12NameWithDigits12']),
        ('NameWith_Underscore', [TokenType.Identifier], ['NameWith_Underscore']),
        ('NameWith_UnderscoreOnEnd_', [TokenType.Identifier], ['NameWith_UnderscoreOnEnd_']),
        ('NameWith12Digits_And_Undersc0reOnEnd_', [TokenType.Identifier], ['NameWith12Digits_And_Undersc0reOnEnd_']),
        ('NameWith12And_Undersc0reDigitsOnEnd_071', [TokenType.Identifier], ['NameWith12And_Undersc0reDigitsOnEnd_071']),
        ('Name 12NameWithDigits12', [TokenType.Identifier, TokenType.Unknown], ['Name', '12NameWithDigits12']),
        ('   12NameWithDigits12  12 ', [TokenType.Unknown, TokenType.IntegerLiteral], ['12NameWithDigits12', '12']),

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
        ('+0042.0', [TokenType.DoubleFloatingLiteral], ['+0042.0']),
        ('-0042.0', [TokenType.DoubleFloatingLiteral], ['-0042.0']),
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
        ('42f', [TokenType.Unknown], ['42f']),
        ('42.0ff', [TokenType.Unknown], ['42.0ff']),
        ('42foo', [TokenType.Unknown], ['42foo']),
        ('420.05.00f;', [TokenType.Unknown, TokenType.Semicolon], ['420.05.00f', ';']),
        ('420.05.00;', [TokenType.Unknown, TokenType.Semicolon], ['420.05.00', ';']),
        ('420.0500;', [TokenType.DoubleFloatingLiteral, TokenType.Semicolon], ['420.0500', ';']),
        ('420.0500', [TokenType.DoubleFloatingLiteral], ['420.0500']),
        ('420.0500f;', [TokenType.SingleFloatingLiteral, TokenType.Semicolon], ['420.0500f', ';']),
        ('420.0500f', [TokenType.SingleFloatingLiteral], ['420.0500f']),
        ("L'", [TokenType.Unknown], ["L'"]),
        ('L"', [TokenType.Unknown], ['L"']),
        ("L'a epiString", [TokenType.Unknown, TokenType.StringType], ["L'a", 'epiString']),
        ("L'a; epiString", [TokenType.Unknown, TokenType.Semicolon, TokenType.StringType], ["L'a", ';', 'epiString']),
        ('L"String epiS32', [TokenType.Unknown], ['L"String epiS32']),
        ('L"String; epiS32', [TokenType.Unknown], ['L"String; epiS32']),
        ('L "String epiS32', [TokenType.Identifier, TokenType.Unknown], ['L', '"String epiS32']),
        ('L "String; epiS32', [TokenType.Identifier, TokenType.Unknown], ['L', '"String; epiS32']),

        ('.52', [TokenType.Unknown, TokenType.IntegerLiteral], ['.', '52']),
        ('42.', [TokenType.Unknown], ['42.']),
        ('42.f', [TokenType.Unknown], ['42.f']),
        ('42.0f0', [TokenType.Unknown], ['42.0f0']),
        ('+42.', [TokenType.Unknown], ['+42.']),
        ('-42.', [TokenType.Unknown], ['-42.']),
        ('--0', [TokenType.Unknown, TokenType.IntegerLiteral], ['-', '-0']),
        ('++0', [TokenType.Unknown, TokenType.IntegerLiteral], ['+', '+0']),
        ('42.0000.005', [TokenType.Unknown], ['42.0000.005']),
        ('+42.000.005', [TokenType.Unknown], ['+42.000.005']),
        ('-42.000.005', [TokenType.Unknown], ['-42.000.005']),

        # Comments
        ('# COMMENT epiS32; ;;; "As well as this is a comment"', [], []),
        (' epiS32 Name   =   42  ;   # COMMENT epiS32; ;;; "As well as this is a comment"', [TokenType.Int32Type, TokenType.Identifier, TokenType.Assing, TokenType.IntegerLiteral, TokenType.Semicolon], ['epiS32', 'Name', '=', '42', ';']),

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
        ('epiFloat* Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', 'Name']),
        ('epiFloat * Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', 'Name']),
        ('epiFloat *Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', 'Name']),
        ('epiFloat** Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', '*', 'Name']),
        ('epiFloat* *Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', '*', 'Name']),
        ('epiFloat **Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', '*', 'Name']),
        ('epiFloat ** Name', [TokenType.SingleFloatingType, TokenType.Asterisk, TokenType.Asterisk, TokenType.Identifier], ['epiFloat', '*', '*', 'Name']),
        ('[Min(5, Force=true)] epiS32 Name = 6;',
            [
                TokenType.OpenSqBracket,
                TokenType.Min,
                TokenType.OpenBracket,
                TokenType.IntegerLiteral,
                TokenType.Comma,
                TokenType.Identifier,
                TokenType.Assing,
                TokenType.TrueLiteral,
                TokenType.CloseBracket,
                TokenType.CloseSqBracket,
                TokenType.Int32Type,
                TokenType.Identifier,
                TokenType.Assing,
                TokenType.IntegerLiteral,
                TokenType.Semicolon
            ],
            [
                '[',
                'Min',
                '(',
                '5',
                ',',
                'Force',
                '=',
                'true',
                ')',
                ']',
                'epiS32',
                'Name',
                '=',
                '6',
                ';'
            ]),
    ])
    def test_sequence(self, tmpdir: str, text: str, expected_type: list, expected_text: list):

        assert len(expected_type) == len(expected_text)

        path = f'{tmpdir}/test.epi'
        with open(path, 'w') as f:
            f.write(text)

        tokenizer = Tokenizer(path, path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) == len(expected_text)

        for exp_type, exp_text, token in zip(expected_type, expected_text, tokens):

            assert exp_type == token.tokentype
            assert exp_text == token.text
