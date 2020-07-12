import pytest

from epi_code_generator.tokenizer import Tokenizer, TokenType

from epi_code_generator.symbol import EpiClass
from epi_code_generator.symbol import EpiVariable
from epi_code_generator.symbol import EpiClassBuilder
from epi_code_generator.symbol import EpiPropertyBuilder

from epi_code_generator.idlparser.idlparser import IDLParser
from epi_code_generator.idlparser.idlparser import IDLSyntaxErrorCode


class TestIDLParser:

    def test_empty(self, tmpdir: str):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write('')

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) == 0

        parser = IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        assert len(registry_local) == 0 and len(errors_syntax) == 0

    @pytest.mark.parametrize('text,expected_registry,expected_errors', [
        (
            'class A {};',
            {
                'A':
                EpiClassBuilder()
                    .name('A')
                    .build()
            },
            []
        ),
        (
            'class A : B {};',
            {
                'A':
                EpiClassBuilder()
                    .name('A')
                    .parent('B')
                    .build()
            },
            []
        ),
        (
            'clas A {}',
            {},
            [IDLSyntaxErrorCode.MissingTypeDeclaration]
        ),
        (
            'class A {}',
            {},
            [IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
        ),
        (
            'class',
            {},
            [IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A',
            {},
            [IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class A :',
            {},
            [IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A : B',
            {},
            [IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class A : B {',
            {},
            [IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A : B {}',
            {},
            [IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
        ),
        (
            'class A : B {;',
            {},
            [IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            'class A : B };',
            {},
            [IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class A : name {};',
            {},
            [IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            'class A : epiFloat {};',
            {},
            [IDLSyntaxErrorCode.UnexpectedKeywordUsage]
        ),
        (
            'class A : Transient {};',
            {},
            [IDLSyntaxErrorCode.UnexpectedKeywordUsage]
        ),
        (
            'class A {} : B;',
            {},
            [IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
        ),
        (
            '''
            class A : B
            {
                epiS32 Name;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .parent('B')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.Int32Type)
                                .build()
                        )
                        .build()
            },
            []
        ),
    ])
    def test_sequence(self, tmpdir: str, text: str, expected_registry: dict, expected_errors: list):

        assert len(expected_registry) * len(expected_errors) == 0 and (len(expected_registry) != 0 or len(expected_errors) != 0)

        path = f'{tmpdir}/test.epi'
        with open(path, 'w') as f:
            f.write(text)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        parser = IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        assert len(registry_local) == len(expected_registry)
        assert len(errors_syntax) == len(expected_errors)

        assert list(registry_local.keys()) == list(expected_registry.keys())

        for sym, exp_sym in zip(registry_local.values(), expected_registry.values()):
            assert sym == exp_sym

        for err, exp_err in zip(errors_syntax, expected_errors):
            assert err.err_code == exp_err
