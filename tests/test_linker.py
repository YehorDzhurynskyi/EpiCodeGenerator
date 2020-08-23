from epigen.tokenizer import Tokenizer, TokenType

from epigen.symbol import EpiClass
from epigen.symbol import EpiClassBuilder
from epigen.symbol import EpiProperty
from epigen.symbol import EpiPropertyBuilder
from epigen.symbol import EpiAttribute
from epigen.symbol import EpiAttributeBuilder

from epigen.idlparser import idlparser_base as idl
from epigen.linker import linker as ln

import pytest


@pytest.mark.order(2)
class TestLinker:

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
            [ln.LinkerErrorCode.NoSuchSymbol] * 2
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
                enum EnumName
                {
                    Name
                };
                ''',
                '''
                enum EnumName
                {
                    Name
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
                    enum EnumName
                    {
                        Name,
                        Name
                    };
                };
                '''
            ],
            [ln.LinkerErrorCode.DuplicatingSymbol]
        ),
        (
            [
                '''
                enum EnumClassName
                {
                    Name
                };
                ''',
                '''
                class EnumClassName
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
                enum EnumName
                {
                    Name
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = EnumName::Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                enum EnumName
                {
                    Name
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = EnumName::Name1;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                enum EnumName
                {
                    Name
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = EnumName::Name::1Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                enum EnumName
                {
                    Name
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = EnumName1::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class ParentClassName
                {
                    enum InheritedEnum
                    {
                        InheritedValue0,
                        InheritedValue1
                    };
                };

                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;

                    EnumName Name1 = EnumName::Name;
                };
                ''',
                '''
                class ClassName : ParentClassName
                {
                    Inner::EnumName Name0 = Inner::EnumName::Name;
                    InheritedEnum Name1 = InheritedEnum::InheritedValue0;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;

                    EnumName Name1 = Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = Inner::EnumName::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    Inner::EnumName Name = EnumName::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    Inner::EnumName Name = Inner::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    Inner::EnumName Name = Inner::EnumName;
                };
                '''
            ],
            [ln.LinkerErrorCode.IncorrectValueAssignment]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    enum EnumNameName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    Inner::EnumName Name = Inner::EnumNameName::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.IncorrectValueAssignment]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = EnumName::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol] * 2
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    EnumName Name = Inner::Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.NoSuchSymbol] * 2
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        [DisplayName("Name")]
                        Name
                    };

                    [DisplayName("Hu")]
                    epiFloat Name;
                };
                ''',
                '''
                class ClassName
                {
                    Inner::EnumName Name = Inner::EnumName;
                };
                '''
            ],
            [ln.LinkerErrorCode.IncorrectValueAssignment]
        ),
        (
            [
                '''
                class ClassName
                {
                    enum EnumName { Value0, Value1 };
                    epiArray<EnumName> Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                enum EnumName
                {
                    Value0,
                    Value1
                };
                ''',
                '''
                class ClassName
                {
                    epiArray<EnumName> Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2 = A
                };
                ''',
            ],
            [ln.LinkerErrorCode.IncorrectValueAssignment]
        ),
        (
            [
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2 = A::Value1
                };
                ''',
            ],
            []
        ),
        (
            [
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2,
                    Value3 = A::Value1 | Value2
                };
                ''',
            ],
            []
        ),
        (
            [
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2,
                    Value3 = A::Value1 | Value4,
                    Value4
                };
                ''',
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                enum B
                {
                    Value1
                };
                ''',
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2,
                    Value3 = A::Value1 | B::Value1,
                    Value4
                };
                ''',
            ],
            []
        ),
        (
            [
                '''
                enum B
                {
                    Value1
                };
                ''',
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2,
                    Value3 = Value1 | B::Value1 | Value2,
                    Value4
                };
                ''',
            ],
            []
        ),
        (
            [
                '''
                enum B
                {
                    Value1
                };
                ''',
                '''
                enum A : epiHash_t
                {
                    Value1,
                    Value2,
                    Value3 = Value1 | B::Value2,
                    Value4
                };
                ''',
            ],
            [ln.LinkerErrorCode.NoSuchSymbol]
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        Value0,
                        Value1
                    };

                    epiFloat FloatPrty;
                };
                ''',
                '''
                class ClassName
                {
                    epiArray<Inner::EnumName> Name;
                };
                '''
            ],
            []
        ),
        (
            [
                '''
                class Inner
                {
                    enum EnumName
                    {
                        Value0,
                        Value1
                    };

                    epiFloat FloatPrty;
                };
                ''',
                '''
                class ClassName
                {
                    epiArray<Inner::EnumName::Value0> Name;
                };
                '''
            ],
            [ln.LinkerErrorCode.BadTemplateArgument]
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
                enum EnumName
                {
                    Name,
                    Name
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

            tokenizer = Tokenizer(path, path, path)
            tokens = tokenizer.tokenize()

            parser = idl.IDLParser(tokens)
            registry_local, errors_syntax = parser.parse()

            assert len(errors_syntax) == 0, f'{errors_syntax}'

            linker.register(registry_local)

        errors_linkage = linker.link()

        for err, exp_err in zip(errors_linkage, expected_errors):
            assert err.err_code == exp_err

        assert len(errors_linkage) == len(expected_errors), f'{errors_linkage} != {expected_errors}'
