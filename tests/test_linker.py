from epi_code_generator.tokenizer import Tokenizer, TokenType

from epi_code_generator.symbol import EpiClass
from epi_code_generator.symbol import EpiClassBuilder
from epi_code_generator.symbol import EpiProperty
from epi_code_generator.symbol import EpiPropertyBuilder
from epi_code_generator.symbol import EpiAttribute
from epi_code_generator.symbol import EpiAttributeBuilder

from epi_code_generator.idlparser import idlparser_base as idl
from epi_code_generator.linker import linker as ln

import pytest


class TestIDLParser:


    @pytest.mark.parametrize('contents,expected_errors', [
        (
            ['', '', ''],
            []
        ),
        (
            ['# only comment'],
            []
        ),
        (
            [
                '''
                class ClassName : ParentClassName {};
                ''',
                '''
                class ParentClassName {};
                '''
            ],
            []
        ),
        (
            [
                '''
                class ClassName : ParentClassName {};
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class ClassName : ParentClassName
                {
                    [Virtual]
                    epiS32 Name;

                    epiString Name2;
                };
                ''',
                '''
                class ParentClassName
                {
                    epiS32 Name = 15;

                    epiArray<epiFloat> Name2;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 4
        ),
        (
            [
                '''
                class ClassName
                {
                    epiArray<UnknownClassName> Name2;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class ClassName
                {
                    UnknownClassName1 Name1;
                    UnknownClassName2 Name2;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol, ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class ClassName
                {
                    epiFloat Name2;
                };
                ''',
                '''
                class ClassName
                {
                    epiFloat Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                class ClassName
                {
                    epiArray<ClassName> Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.IncompleteTypeUsage]
        ),
        (
            [
                '''
                class ClassName
                {
                    ClassName Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.IncompleteTypeUsage]
        ),
        (
            [
                '''
                class ClassName
                {
                    ClassName* Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                class ClassName
                {
                    epiPtrArray<ClassName> Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                class PClassName
                {
                    epiS32 Name;
                };

                class ClassName : PClassName
                {
                    epiS32 Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 2
        ),
        (
            [
                '''
                class ParentClassName
                {
                    [Virtual]
                    epiVec2f Name;
                };
                ''',
                '''
                class ClassName : ParentClassName
                {
                    epiS32 Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 2
        ),
        (
            [
                '''
                class AClassName
                {
                    epiS32 Name;
                };

                class PClassName : AClassName
                {
                    epiS32 Name;
                };

                class ClassName : PClassName
                {
                    epiS32 Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 7
        ),
        (
            [
                '''
                class AClassName
                {
                    epiArray<epiFloat> Name;
                };

                class PClassName : AClassName
                {
                    [Min(50)]
                    epiU32 Name = 99;
                };

                class ClassName : PClassName
                {
                    epiString Name = "HLL";
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 7
        ),
        (
            [
                '''
                class ClassName
                {
                    epiS32 Name;
                    epiString Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                class ClassName
                {
                    epiS32 Name;
                    epiString Name;
                    epiRect2f Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 3
        ),
        (
            [
                '''
                class ParentClassName
                {
                    [Virtual]
                    epiVec2f Name;
                };

                class ClassName : ParentClassName
                {
                    epiS32 Name;
                    epiString Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 6
        ),
        (
            [
                '''
                class AClass
                {
                    epiS32 APrty;
                };

                class BClass
                {
                    epiS32 BPrty;
                };
                ''',
                '''
                class AClass
                {
                    epiS32 APrty;
                };

                class ClassName : AClass
                {
                    epiS32 Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                class AClass
                {
                    epiS32 APrty;
                };

                class BClass
                {
                    epiS32 BPrty;
                };
                ''',
                '''
                class AClass
                {
                    epiU32 APrty;
                };
                ''',
                '''
                class ClassName : AClass
                {
                    epiS32 Name;
                    BClass Name2;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                class AClass
                {
                    epiS32 APrty;
                };

                class BClass : AClass
                {
                    epiS32 BPrty;
                };
                ''',
                '''
                class AClass
                {
                    epiU32 APrty;
                };
                ''',
                '''
                class ClassName : AClass
                {
                    epiS32 Name;
                    BClass Name2;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                class ParentClassName
                {
                    [Virtual]
                    epiVec2f Name;
                };
                ''',
                '''
                class ClassName : ParentClassName
                {
                    epiS32 Name;
                    epiString Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol] * 6
        ),
    ])
    def test_sequence(self, tmpdir: str, contents: list, expected_errors: list):

        linker = ln.Linker()
        for i, content in enumerate(contents):
            path = f'{tmpdir}/test{i}.epi'

            with open(path, 'w') as f:
                f.write(content)

            tokenizer = Tokenizer(path, path)
            tokens = tokenizer.tokenize()

            parser = idl.IDLParser(tokens)
            registry_local, errors_syntax = parser.parse()

            assert len(errors_syntax) == 0

            linker.register(registry_local)

        errors_linkage = linker.link()
        assert len(errors_linkage) == len(expected_errors)

        for err, exp_err in zip(errors_linkage, expected_errors):
            assert err.err_code == exp_err