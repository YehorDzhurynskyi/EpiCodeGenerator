from epigen.tokenizer import Tokenizer, TokenType

from epigen.symbol import EpiClass
from epigen.symbol import EpiClassBuilder
from epigen.symbol import EpiProperty
from epigen.symbol import EpiPropertyBuilder
from epigen.symbol import EpiAttribute
from epigen.symbol import EpiAttributeBuilder
from epigen.symbol import EpiEnum
from epigen.symbol import EpiEnumBuilder
from epigen.symbol import EpiEnumEntry
from epigen.symbol import EpiEnumEntryBuilder

from epigen.idlparser import idlparser_base as idl

import pytest


@pytest.mark.order(1)
class TestIDLParser:

    def test_empty(self, tmpdir: str):

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write('')

        tokenizer = Tokenizer(path, path, path)
        tokens = tokenizer.tokenize()

        assert len(tokens) == 0

        parser = idl.IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        assert len(registry_local) == 0 and len(errors_syntax) == 0

    @pytest.mark.parametrize('content,expected_registry,expected_errors', [
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
            'epiFloat Name;',
            {},
            [idl.IDLSyntaxErrorCode.MissingTypeDeclaration]
        ),
        (
            'clas A {}',
            {},
            [idl.IDLSyntaxErrorCode.MissingTypeDeclaration]
        ),
        (
            'class A {}',
            {},
            [idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
        ),
        (
            'class',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class Scope::A : B {};',
            {},
            [idl.IDLSyntaxErrorCode.WrongIdentifierContext]
        ),
        (
            'class A :: B {};',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            'class A :',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A : B',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class A : B {',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            'class A : B {}',
            {},
            [idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
        ),
        (
            'class A : B {;',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            'class A : B };',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            'class A : name {};',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .parent('name')
                        .build()
            },
            []
        ),
        (
            'class A : epiFloat {};',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedKeywordUsage]
        ),
        (
            'class A : Transient {};',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedKeywordUsage]
        ),
        (
            'class A {} : B;',
            {},
            [idl.IDLSyntaxErrorCode.NoSemicolonOnDeclaration]
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
        (
            '''
            class A : B
            {
                epiS32 Name = 42;
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
                                .value('42')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                EpiS32 Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class ClassName : B
            {
                epiS32 Name::Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.WrongIdentifierContext]
        ),
        (
            '''
            class A::ClassName : B
            {
                epiS32 Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.WrongIdentifierContext]
        ),
        (
            '''
            class A::ClassName : B
            {
                epiS32 Name::Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.WrongIdentifierContext] * 2
        ),
        (
            '''
            class A : B
            {
                B::C Name::Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.WrongIdentifierContext]
        ),
        (
            '''
            class A : B
            {
                B::C Name;
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
                                .tokentype_type(TokenType.Identifier, 'B::C')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                B::Nested::C Name;
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
                                .tokentype_type(TokenType.Identifier, 'B::Nested::C')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            enum A
            {
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiS8
            {
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.Int8Type)
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiS8
            {
                Name
            };

            class B : C
            {
                [Transient]
                A a = A::Name;
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.Int8Type)
                        .entry(EpiEnumEntryBuilder().name('Name').build())
                        .build(),
                'B':
                    EpiClassBuilder()
                        .name('B')
                        .parent('C')
                        .property(
                            EpiPropertyBuilder()
                                .name('a')
                                .tokentype_type(TokenType.Identifier, 'A')
                                .value('A::Name')
                                .attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build())
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiS8
            {
                Name
            };

            class B : C
            {
                epiS32 a = A::Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            enum A : epiS8
            {
                Name
            };

            class B : C
            {
                [Transient]
                A a = A;
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.Int8Type)
                        .entry(EpiEnumEntryBuilder().name('Name').build())
                        .build(),
                'B':
                    EpiClassBuilder()
                        .name('B')
                        .parent('C')
                        .property(
                            EpiPropertyBuilder()
                                .name('a')
                                .tokentype_type(TokenType.Identifier, 'A')
                                .value('A')
                                .attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build())
                                .build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiFloat
            {
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedKeywordUsage]
        ),
        (
            '''
            enum A :
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedEOF]
        ),
        (
            '''
            enum A : ;
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            enum A;
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            '''
            enum A : epiS8;
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            '''
            enum A : epiS8 : epiFloat
            {
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoBodyOnDeclaration]
        ),
        (
            '''
            enum A
            {
                Value1,
                Value2,
                Value3,
                Value4,
                Value5,
                Value6
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .entry(EpiEnumEntryBuilder().name('Value5').build())
                        .entry(EpiEnumEntryBuilder().name('Value6').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = 0.0f,
                Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = "textexft",
                Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = EnumName::Value1,
                Value2
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').value([(TokenType.Identifier, 'EnumName::Value1')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = EnumName,
                Value2
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').value([(TokenType.Identifier, 'EnumName')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2 = A
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').value([(TokenType.Identifier, 'A')]).build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2 = A::Value1
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').value([(TokenType.Identifier, 'A::Value1')]).build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = A::Value1 | Value2
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'A::Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'Value2')]).build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = A::Value1 | Value4,
                Value4
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'A::Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'Value4')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = A::Value1 | B::Value1,
                Value4
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'A::Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'B::Value1')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = Value1 | B::Value1 | Value2,
                Value4
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'B::Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'Value2')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = Value1 | B::Value2,
                Value4
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'B::Value2')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = Value1 | B::Value2 |,
                Value4
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = | Value1 | B::Value2,
                Value4
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            [FlagMask]
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = Value1 | B::Value2,
                Value4 = Value2
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.Identifier, 'Value1'), (TokenType.VSlash, '|'), (TokenType.Identifier, 'B::Value2')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').value([(TokenType.Identifier, 'Value2')]).build())
                        .attr(EpiAttributeBuilder().tokentype(TokenType.FlagMask).build())
                        .build()
            },
            []
        ),
        (
            '''
            [FlagMask]
            enum A : epiHash_t
            {
                Value1 = 1,
                Value2 = 0,
                Value3 = Value1 | B::Value2,
                Value4 = Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            [FlagMask]
            enum A : epiHash_t
            {
                Value1,
                Value2,
                Value3 = Value1 | 1,
                Value4 = Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = ,
                Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = =,
                Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment, idl.IDLSyntaxErrorCode.NoMatchingClosingBrace]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1 = ,,
                Value2
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment, idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value2 =
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,

                {
                    Value3,
                    Value4
                }
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                {
                    Value1,
                    Value2
                }

                {
                }

                {
                    Value3,
                    Value4,

                    {
                        Value5
                    }
                }

                Value6,
                Value7 = 124
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').build())
                        .entry(EpiEnumEntryBuilder().name('Value2').build())
                        .entry(EpiEnumEntryBuilder().name('Value3').build())
                        .entry(EpiEnumEntryBuilder().name('Value4').build())
                        .entry(EpiEnumEntryBuilder().name('Value5').build())
                        .entry(EpiEnumEntryBuilder().name('Value6').build())
                        .entry(EpiEnumEntryBuilder().name('Value7').value([(TokenType.IntegerLiteral, '124')]).build())
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,

                {
                    Value3,
                    Value4,
                }
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            class A
            {
                [Virtual]
                enum A : epiHash_t
                {
                    Value1,
                    Value2
                };
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidTarget]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,

                {
                    Value3,
                    Value4
                }

                Value5,
                Value6,
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2,
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            enum A : epiHash_t
            {
                Value1,
                Value2
                Value3,
                Value4,
                Value5
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBrace]
        ),
        (
            '''
            enum A
            {
                Value1 = +0
            };

            class ClassName : B
            {
                enum A : epiHash_t
                {
                    Value1,
                    Value2 = 32,
                    Value3,

                    [DisplayName("Val1")]
                    Value4,

                    Value5
                };

                epiS32 Name1;
                epiString Name2 = "Text";
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .entry(EpiEnumEntryBuilder().name('Value1').value([(TokenType.IntegerLiteral, '+0')]).build())
                        .build(),
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .parent('B')
                        .inner(
                            EpiEnumBuilder()
                                .name('A')
                                .base(TokenType.HashTType)
                                .entry(EpiEnumEntryBuilder().name('Value1').build())
                                .entry(EpiEnumEntryBuilder().name('Value2').value([(TokenType.IntegerLiteral, '32')]).build())
                                .entry(EpiEnumEntryBuilder().name('Value3').build())
                                .entry(EpiEnumEntryBuilder().name('Value4').attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"Val1"').build()).build())
                                .entry(EpiEnumEntryBuilder().name('Value5').build())
                                .build()
                        )
                        .property(
                            EpiPropertyBuilder()
                                .name('Name1')
                                .tokentype_type(TokenType.Int32Type)
                                .build()
                        )
                        .property(
                            EpiPropertyBuilder()
                                .name('Name2')
                                .tokentype_type(TokenType.StringType)
                                .value('"Text"')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            enum A : epiHash_t
            {
                [DisplayName("Value One Two")]
                {
                    Value1 = 1,
                    Value2 = 2
                }

                {
                }

                {
                    [DisplayName("Value Three")]
                    Value3 = -3,
                    Value4 = 512,

                    [DisplayName("Value Four")]
                    {
                        Value5
                    }
                }

                Value6 = 0,
                Value7
            };
            ''',
            {
                'A':
                    EpiEnumBuilder()
                        .name('A')
                        .base(TokenType.HashTType)
                        .entry(EpiEnumEntryBuilder().name('Value1').value([(TokenType.IntegerLiteral, '1')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"Value One Two"').build()).build())
                        .entry(EpiEnumEntryBuilder().name('Value2').value([(TokenType.IntegerLiteral, '2')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"Value One Two"').build()).build())
                        .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.IntegerLiteral, '-3')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"Value Three"').build()).build())
                        .entry(EpiEnumEntryBuilder().name('Value4').value([(TokenType.IntegerLiteral, '512')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value5').attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"Value Four"').build()).build())
                        .entry(EpiEnumEntryBuilder().name('Value6').value([(TokenType.IntegerLiteral, '0')]).build())
                        .entry(EpiEnumEntryBuilder().name('Value7').build())
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                epiS32 Name = 42.0;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiS32 Name = 42.0f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiS32 Name = 42.0.0;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken]
        ),
        (
            '''
            class A : B
            {
                epiDouble Name = 420.05.00;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken]
        ),
        (
            '''
            class A : B
            {
                epiFloat Name = 420.05.00f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken]
        ),
        (
            '''
            class A : B
            {
                epiDouble Name = 420.05.0000.60;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken]
        ),
        (
            '''
            class A : B
            {
                epiFloat Name = 420.05.0000.60f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken]
        ),
        (
            '''
            class A : B
            {
                epiFloat Name = 42.0;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiDouble Name = 42.0f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiFloat Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiDouble Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiChar Name = L'U';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiChar Name = 'U
                ';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken] * 2
        ),
        (
            '''
            class A : B
            {
                epiWChar Name = L'U
                ';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken] * 2
        ),
        (
            '''
            class A : B
            {
                epiWChar Name = 'U';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiChar Name = "U";
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiWChar Name = L"U";
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiString Name = 'text';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken] * 2
        ),
        (
            '''
            class A : B
            {
                epiString Name = "text
                ";
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken] * 2
        ),
        (
            '''
            class A : B
            {
                epiWString Name = L'text';
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnknownToken] * 2
        ),
        (
            '''
            class A : B
            {
                epiString Name = L"text";
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        
        (
            '''
            class A : B
            {
                epiWString Name = "text";
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiArray<epiFloat> Name;
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
                                .tokentype_type(TokenType.ArrayType)
                                .form(EpiProperty.Form.Template)
                                .token_nested(TokenType.SingleFloatingType)
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                epiArray Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.MissingTemplateArguments]
        ),
        (
            '''
            class A : B
            {
                epiArray Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.MissingTemplateArguments, idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                epiArray<epiFloat> Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                epiArray< Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                epiArray<> Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken, idl.IDLSyntaxErrorCode.MissingTemplateArguments]
        ),
        (
            '''
            class A : B
            {
                epiArray<epiFloat Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                epiArray< Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                epiArray<> Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken, idl.IDLSyntaxErrorCode.MissingTemplateArguments, idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                epiArray<epiFloat Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                epiPtrArray<C> Name;
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
                                .tokentype_type(TokenType.PtrArrayType)
                                .form(EpiProperty.Form.Template)
                                .token_nested(TokenType.Identifier, 'C')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                C Name;
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
                                .tokentype_type(TokenType.Identifier, 'C')
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                C Name = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                epiArray<epiFloat> Name18 = 42;
                epiPtrArray<epiFloat> Name19 = 42;
                epiVec2f Name20 = 42;
                epiVec2d Name21 = 42;
                epiVec2s Name22 = 42;
                epiVec2u Name23 = 42;
                epiVec3f Name24 = 42;
                epiVec3d Name25 = 42;
                epiVec3s Name26 = 42;
                epiVec3u Name27 = 42;
                epiVec4f Name28 = 42;
                epiVec4d Name29 = 42;
                epiVec4s Name30 = 42;
                epiVec4u Name31 = 42;
                epiMat2x2f Name32 = 42;
                epiMat3x3f Name33 = 42;
                epiMat4x4f Name34 = 42;
                epiRect2f Name35 = 42;
                epiRect2d Name36 = 42;
                epiRect2s Name37 = 42;
                epiRect2u Name38 = 42;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment] * 21
        ),
        (
            '''
            class A : B
            {
                [Virtual]
                epiFloat Name;
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
                                .attr(EpiAttributeBuilder().tokentype(TokenType.Virtual).build())
                                .tokentype_type(TokenType.SingleFloatingType)
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                [Virtual]
                epiFloat Name = 4.0f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                [Min(5)]
                epiS32 Name = 4;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                [Max(5)]
                epiS32 Name = 6;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                [Min(5)]
                epiS32 Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                [Max(-1)]
                epiS32 Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.IncorrectValueAssignment]
        ),
        (
            '''
            class A : B
            {
                [Max(-1.043)]
                epiFloat Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters]
        ),
        (
            '''
            class A : B
            {
                [Max(-1)]
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidTarget]
        ),
        (
            '''
            class A : B
            {
                [Max(-1)]
                epiS32* Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidTarget]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true)]
                C Name;
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
                                .tokentype_type(TokenType.Identifier, 'C')
                                .attr(
                                    EpiAttributeBuilder()
                                    .tokentype(TokenType.ReadCallback)
                                    .param_named('SuppressRef', TokenType.TrueLiteral, 'true')
                                .build())
                            .build())
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=True)]
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SupressRef=true)]
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters]
        ),
        (
            '''
            class A : B
            {
                [WriteCallback(SuppressRef=false)]
                C Name;
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
                                .tokentype_type(TokenType.Identifier, 'C')
                                .attr(
                                    EpiAttributeBuilder()
                                    .tokentype(TokenType.WriteCallback)
                                    .param_named('SuppressRef', TokenType.FalseLiteral, 'false')
                                .build())
                            .build())
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true)]
                epiFloat Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true) ReadOnly]
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true) ReadOnly
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true), ReadOnly
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.NoMatchingClosingBracket]
        ),
        (
            '''
            class A : B
            {
                [ReadCallback(SuppressRef=true),, ReadOnly]
                C Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.UnexpectedToken]
        ),
        (
            '''
            class A
            {
                [Virtual, ReadCallback(SuppressRef=true)]
                epiMat4x4f Name;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.Mat4x4FType)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadCallback)
                                        .param_named('SuppressRef', TokenType.TrueLiteral, 'true')
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A
            {
                [Virtual, ReadOnly]
                epiFloat Name;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadOnly)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A
            {
                [ReadOnly, Virtual]
                epiFloat Name;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadOnly)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                [Max(5, Force=true)]
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
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Max)
                                        .param_positional(TokenType.IntegerLiteral, '5')
                                        .param_named('Force', TokenType.TrueLiteral, 'true')
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class A : B
            {
                [Max(Force=true, 5)]
                epiS32 Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters]
        ),
        (
            '''
            class A : B
            {
                [Max(Force=true, 5)]
                epiS32 Name = 4.0f;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters, idl.IDLSyntaxErrorCode.IncorrectValueLiteral]
        ),
        (
            '''
            class A : B
            {
                [Max(force=true, 5)]
                epiS32 Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.AttributeInvalidParameters] * 2
        ),
        (
            '''
            class A : B
            {
                [Virtual]
                epiFloat Name;
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
                                .attr(EpiAttributeBuilder().tokentype(TokenType.Virtual).build())
                                .tokentype_type(TokenType.SingleFloatingType)
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                epiFloat Name2;
            };

            class ClassName
            {
                epiFloat Name;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.DuplicatingSymbol]
        ),
        (
            '''
            enum EnumName
            {
                Value1
            };

            enum EnumName
            {
                Value1
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.DuplicatingSymbol]
        ),
        (
            '''
            class ClassName
            {
                epiFloat* Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .form(EpiProperty.Form.Pointer)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                epiFloat * Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .form(EpiProperty.Form.Pointer)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                [Transient]
                epiFloat * Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .form(EpiProperty.Form.Pointer)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                [Virtual, ReadOnly]
                epiS32 Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.Int32Type)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadCallback)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadOnly)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                [ReadOnly, Virtual]
                epiS32 Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.Int32Type)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadOnly)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadCallback)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                [ReadOnly, ReadCallback(SuppressRef=true), Virtual]
                C Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.Identifier, 'C')
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadOnly)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.ReadCallback)
                                        .param_named('SuppressRef', TokenType.TrueLiteral, 'true')
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Virtual)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                epiFloat *Name;
            };
            ''',
            {
                'ClassName':
                    EpiClassBuilder()
                        .name('ClassName')
                        .property(
                            EpiPropertyBuilder()
                                .name('Name')
                                .tokentype_type(TokenType.SingleFloatingType)
                                .form(EpiProperty.Form.Pointer)
                                .attr(
                                    EpiAttributeBuilder()
                                        .tokentype(TokenType.Transient)
                                        .build()
                                )
                                .build()
                        )
                        .build()
            },
            []
        ),
        (
            '''
            class ClassName
            {
                epiFloat** Name1;
                epiFloat* *Name2;
                epiFloat **Name3;
                epiFloat ** Name4;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.MultiDepthPointer] * 4
        ),
        (
            '''
            class ClassName
            {
                epiFloat * * * Name1;
                epiFloat **Name2;
            };
            ''',
            {},
            [idl.IDLSyntaxErrorCode.MultiDepthPointer] * 3
        ),
    ])
    def test_sequence(self, tmpdir: str, content: str, expected_registry: dict, expected_errors: list):

        assert len(expected_registry) * len(expected_errors) == 0 and (len(expected_registry) != 0 or len(expected_errors) != 0)

        path = f'{tmpdir}/test.epi'
        with open(path, 'w') as f:
            f.write(content)

        tokenizer = Tokenizer(path, path, path)
        tokens = tokenizer.tokenize()

        parser = idl.IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        for err, exp_err in zip(errors_syntax, expected_errors):
            assert err.err_code == exp_err

        assert len(errors_syntax) == len(expected_errors), f'{errors_syntax} != {expected_errors}'

        assert list(registry_local.keys()) == list(expected_registry.keys())

        for sym, exp_sym in zip(registry_local.values(), expected_registry.values()):
            assert sym == exp_sym

        assert len(registry_local) == len(expected_registry)

        return registry_local, errors_syntax

    @pytest.mark.parametrize('content,expected_registry,expected_errors', [
        (
            '''
            class A : B
            {
                epiChar Name0;
                epiWChar Name1;
                epiBool Name2;
                epiByte Name3;
                epiSize_t Name4;
                epiHash_t Name5;
                epiU8 Name6;
                epiU16 Name7;
                epiU32 Name8;
                epiU64 Name9;
                epiS8 Name10;
                epiS16 Name11;
                epiS32 Name12;
                epiS64 Name13;
                epiFloat Name14;
                epiDouble Name15;
                epiString Name16;
                epiWString Name17;
                epiArray<MyClassName> Name18;
                epiPtrArray<epiFloat> Name19;
                epiVec2f Name20;
                epiVec2d Name21;
                epiVec2s Name22;
                epiVec2u Name23;
                epiVec3f Name24;
                epiVec3d Name25;
                epiVec3s Name26;
                epiVec3u Name27;
                epiVec4f Name28;
                epiVec4d Name29;
                epiVec4s Name30;
                epiVec4u Name31;
                epiMat2x2f Name32;
                epiMat3x3f Name33;
                epiMat4x4f Name34;
                epiRect2f Name35;
                epiRect2d Name36;
                epiRect2s Name37;
                epiRect2u Name38;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .parent('B')
                        .property(EpiPropertyBuilder().name('Name0').tokentype_type(TokenType.CharType).build())
                        .property(EpiPropertyBuilder().name('Name1').tokentype_type(TokenType.WCharType).build())
                        .property(EpiPropertyBuilder().name('Name2').tokentype_type(TokenType.BoolType).build())
                        .property(EpiPropertyBuilder().name('Name3').tokentype_type(TokenType.ByteType).build())
                        .property(EpiPropertyBuilder().name('Name4').tokentype_type(TokenType.SizeTType).build())
                        .property(EpiPropertyBuilder().name('Name5').tokentype_type(TokenType.HashTType).build())
                        .property(EpiPropertyBuilder().name('Name6').tokentype_type(TokenType.UInt8Type).build())
                        .property(EpiPropertyBuilder().name('Name7').tokentype_type(TokenType.UInt16Type).build())
                        .property(EpiPropertyBuilder().name('Name8').tokentype_type(TokenType.UInt32Type).build())
                        .property(EpiPropertyBuilder().name('Name9').tokentype_type(TokenType.UInt64Type).build())
                        .property(EpiPropertyBuilder().name('Name10').tokentype_type(TokenType.Int8Type).build())
                        .property(EpiPropertyBuilder().name('Name11').tokentype_type(TokenType.Int16Type).build())
                        .property(EpiPropertyBuilder().name('Name12').tokentype_type(TokenType.Int32Type).build())
                        .property(EpiPropertyBuilder().name('Name13').tokentype_type(TokenType.Int64Type).build())
                        .property(EpiPropertyBuilder().name('Name14').tokentype_type(TokenType.SingleFloatingType).build())
                        .property(EpiPropertyBuilder().name('Name15').tokentype_type(TokenType.DoubleFloatingType).build())
                        .property(EpiPropertyBuilder().name('Name16').tokentype_type(TokenType.StringType).build())
                        .property(EpiPropertyBuilder().name('Name17').tokentype_type(TokenType.WStringType).build())
                        .property(EpiPropertyBuilder().name('Name18').tokentype_type(TokenType.ArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.Identifier, 'MyClassName').build())
                        .property(EpiPropertyBuilder().name('Name19').tokentype_type(TokenType.PtrArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.SingleFloatingType).build())
                        .property(EpiPropertyBuilder().name('Name20').tokentype_type(TokenType.Vec2FType).build())
                        .property(EpiPropertyBuilder().name('Name21').tokentype_type(TokenType.Vec2DType).build())
                        .property(EpiPropertyBuilder().name('Name22').tokentype_type(TokenType.Vec2SType).build())
                        .property(EpiPropertyBuilder().name('Name23').tokentype_type(TokenType.Vec2UType).build())
                        .property(EpiPropertyBuilder().name('Name24').tokentype_type(TokenType.Vec3FType).build())
                        .property(EpiPropertyBuilder().name('Name25').tokentype_type(TokenType.Vec3DType).build())
                        .property(EpiPropertyBuilder().name('Name26').tokentype_type(TokenType.Vec3SType).build())
                        .property(EpiPropertyBuilder().name('Name27').tokentype_type(TokenType.Vec3UType).build())
                        .property(EpiPropertyBuilder().name('Name28').tokentype_type(TokenType.Vec4FType).build())
                        .property(EpiPropertyBuilder().name('Name29').tokentype_type(TokenType.Vec4DType).build())
                        .property(EpiPropertyBuilder().name('Name30').tokentype_type(TokenType.Vec4SType).build())
                        .property(EpiPropertyBuilder().name('Name31').tokentype_type(TokenType.Vec4UType).build())
                        .property(EpiPropertyBuilder().name('Name32').tokentype_type(TokenType.Mat2x2FType).build())
                        .property(EpiPropertyBuilder().name('Name33').tokentype_type(TokenType.Mat3x3FType).build())
                        .property(EpiPropertyBuilder().name('Name34').tokentype_type(TokenType.Mat4x4FType).build())
                        .property(EpiPropertyBuilder().name('Name35').tokentype_type(TokenType.Rect2FType).build())
                        .property(EpiPropertyBuilder().name('Name36').tokentype_type(TokenType.Rect2DType).build())
                        .property(EpiPropertyBuilder().name('Name37').tokentype_type(TokenType.Rect2SType).build())
                        .property(EpiPropertyBuilder().name('Name38').tokentype_type(TokenType.Rect2UType).build())
                        .build()
            },
            []
        ),
                (
            '''
            class A : B
            {
                epiChar Name0 = 'E';
                epiWChar Name1 = L'F';
                epiBool Name2 = true;
                epiByte Name3 = 12;
                epiSize_t Name4 = 23;
                epiHash_t Name5 = 42;
                epiU8 Name6 = 1;
                epiU16 Name7 = 2;
                epiU32 Name8 = 3;
                epiU64 Name9 = 4;
                epiS8 Name10 = -2;
                epiS16 Name11 = -5;
                epiS32 Name12 = -2;
                epiS64 Name13 = -1231230;
                epiFloat Name14 = -4.0f;
                epiDouble Name15 = +32.00007;
                epiString Name16 = "TEXT";
                epiWString Name17 = L"QwertY!";
                epiArray<MyClassName> Name18;
                epiPtrArray<epiFloat> Name19;
                epiVec2f Name20;
                epiVec2d Name21;
                epiVec2s Name22;
                epiVec2u Name23;
                epiVec3f Name24;
                epiVec3d Name25;
                epiVec3s Name26;
                epiVec3u Name27;
                epiVec4f Name28;
                epiVec4d Name29;
                epiVec4s Name30;
                epiVec4u Name31;
                epiMat2x2f Name32;
                epiMat3x3f Name33;
                epiMat4x4f Name34;
                epiRect2f Name35;
                epiRect2d Name36;
                epiRect2s Name37;
                epiRect2u Name38;
            };
            ''',
            {
                'A':
                    EpiClassBuilder()
                        .name('A')
                        .parent('B')
                        .property(EpiPropertyBuilder().name('Name0').tokentype_type(TokenType.CharType).value("'E'").build())
                        .property(EpiPropertyBuilder().name('Name1').tokentype_type(TokenType.WCharType).value("L'F'").build())
                        .property(EpiPropertyBuilder().name('Name2').tokentype_type(TokenType.BoolType).value('true', TokenType.TrueLiteral).build())
                        .property(EpiPropertyBuilder().name('Name3').tokentype_type(TokenType.ByteType).value('12').build())
                        .property(EpiPropertyBuilder().name('Name4').tokentype_type(TokenType.SizeTType).value('23').build())
                        .property(EpiPropertyBuilder().name('Name5').tokentype_type(TokenType.HashTType).value('42').build())
                        .property(EpiPropertyBuilder().name('Name6').tokentype_type(TokenType.UInt8Type).value('1').build())
                        .property(EpiPropertyBuilder().name('Name7').tokentype_type(TokenType.UInt16Type).value('2').build())
                        .property(EpiPropertyBuilder().name('Name8').tokentype_type(TokenType.UInt32Type).value('3').build())
                        .property(EpiPropertyBuilder().name('Name9').tokentype_type(TokenType.UInt64Type).value('4').build())
                        .property(EpiPropertyBuilder().name('Name10').tokentype_type(TokenType.Int8Type).value('-2').build())
                        .property(EpiPropertyBuilder().name('Name11').tokentype_type(TokenType.Int16Type).value('-5').build())
                        .property(EpiPropertyBuilder().name('Name12').tokentype_type(TokenType.Int32Type).value('-2').build())
                        .property(EpiPropertyBuilder().name('Name13').tokentype_type(TokenType.Int64Type).value('-1231230').build())
                        .property(EpiPropertyBuilder().name('Name14').tokentype_type(TokenType.SingleFloatingType).value('-4.0f').build())
                        .property(EpiPropertyBuilder().name('Name15').tokentype_type(TokenType.DoubleFloatingType).value('+32.00007').build())
                        .property(EpiPropertyBuilder().name('Name16').tokentype_type(TokenType.StringType).value('"TEXT"').build())
                        .property(EpiPropertyBuilder().name('Name17').tokentype_type(TokenType.WStringType).value('L"QwertY!"').build())
                        .property(EpiPropertyBuilder().name('Name18').tokentype_type(TokenType.ArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.Identifier, 'MyClassName').build())
                        .property(EpiPropertyBuilder().name('Name19').tokentype_type(TokenType.PtrArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.SingleFloatingType).build())
                        .property(EpiPropertyBuilder().name('Name20').tokentype_type(TokenType.Vec2FType).build())
                        .property(EpiPropertyBuilder().name('Name21').tokentype_type(TokenType.Vec2DType).build())
                        .property(EpiPropertyBuilder().name('Name22').tokentype_type(TokenType.Vec2SType).build())
                        .property(EpiPropertyBuilder().name('Name23').tokentype_type(TokenType.Vec2UType).build())
                        .property(EpiPropertyBuilder().name('Name24').tokentype_type(TokenType.Vec3FType).build())
                        .property(EpiPropertyBuilder().name('Name25').tokentype_type(TokenType.Vec3DType).build())
                        .property(EpiPropertyBuilder().name('Name26').tokentype_type(TokenType.Vec3SType).build())
                        .property(EpiPropertyBuilder().name('Name27').tokentype_type(TokenType.Vec3UType).build())
                        .property(EpiPropertyBuilder().name('Name28').tokentype_type(TokenType.Vec4FType).build())
                        .property(EpiPropertyBuilder().name('Name29').tokentype_type(TokenType.Vec4DType).build())
                        .property(EpiPropertyBuilder().name('Name30').tokentype_type(TokenType.Vec4SType).build())
                        .property(EpiPropertyBuilder().name('Name31').tokentype_type(TokenType.Vec4UType).build())
                        .property(EpiPropertyBuilder().name('Name32').tokentype_type(TokenType.Mat2x2FType).build())
                        .property(EpiPropertyBuilder().name('Name33').tokentype_type(TokenType.Mat3x3FType).build())
                        .property(EpiPropertyBuilder().name('Name34').tokentype_type(TokenType.Mat4x4FType).build())
                        .property(EpiPropertyBuilder().name('Name35').tokentype_type(TokenType.Rect2FType).build())
                        .property(EpiPropertyBuilder().name('Name36').tokentype_type(TokenType.Rect2DType).build())
                        .property(EpiPropertyBuilder().name('Name37').tokentype_type(TokenType.Rect2SType).build())
                        .property(EpiPropertyBuilder().name('Name38').tokentype_type(TokenType.Rect2UType).build())
                        .build()
            },
            []
        ),
    ])
    def test_sequence_builtin(self, tmpdir: str, content: str, expected_registry: dict, expected_errors: list):

        registry_local, _ = self.test_sequence(tmpdir, content, expected_registry, expected_errors)

        builtins = [property.tokentype.text for property in list(registry_local.values())[0].properties]
        builtins.sort()

        exp_builtins = list(Tokenizer.builtin_types().keys())
        exp_builtins.sort()

        assert builtins == exp_builtins, 'Some builtin type is missing'

    @pytest.mark.parametrize('content', [
        (
            '''
            enum EnumName
            {
                Value1,
                Value2 = 123,

                [DisplayName("V1")]
                {
                    Value3 = 123,
                    Value4 = 42
                }

                [DisplayName("V2")]
                Value5 = -23
            };

            class ParentClassName
            {
                enum InnerEnumName : epiS32
                {
                    Value1,
                    Value2
                };

                [Transient, WriteOnly]
                {
                    [Max(5, Force=true)]
                    epiS32 A = 1;

                    [Min(-5), Max(5)]
                    {
                        epiS32 B = 1;
                        epiS32 C = -5;
                        epiS32 D = 1;
                    }
                }
            };

            class ClassName : ParentClassName
            {
                epiChar Name0 = 'f';
                epiWChar Name1 = L'F';
                epiBool Name2 = true;
                epiByte Name3;

                [Transient, ReadOnly]
                {
                    epiSize_t Name4;
                    epiHash_t Name5;

                    [Virtual]
                    epiU8 Name6;
                    epiU16 Name7;
                }

                epiU32 Name8 = -1;
                epiU64 Name9;

                [Min(-5)]
                epiS8 Name10;
                epiS16 Name11 = 15;
                epiS32 Name12;
                epiS64* Name13;
                epiFloat Name14;

                epiDouble Name15; # comment
                epiString Name16 = "Hello";
                epiWString Name17;
                epiArray<MyClassName> Name18;
                epiPtrArray<epiFloat> Name19;
                epiVec2f Name20;
                epiVec2d Name_21;

                epiVec2s Name22;
                epiVec2u Name23;
                epiVec3f Name24;
                epiVec3d Name25;
                epiVec3s Name26;
                epiVec3u Name27;
                epiVec4f Name28;
                epiVec4d Name29;
                epiVec4s Name30;
                epiVec4u Name31;
                epiMat2x2f Name32;
                epiMat3x3f Name33;
                epiMat4x4f* Name34;
                epiRect2f Name35;

                [WriteOnly]
                epiRect2d Name36;

                # comment
                # comment

                epiRect2s Name37;
                epiRect2u Name38;
            };
            '''
        ),
        (
            '''
                        enum EnumName {
                Value1, # COMMENT
                # ANOTHER COMMENT

                Value2 =                       123      ,     

                [DisplayName("V1")]
                { Value3 = 123, Value4 = 42 }

                [DisplayName("V2")] Value5 = -23
            };


            class ParentClassName
            {
                enum InnerEnumName : epiS32 { Value1, Value2 };

                [Transient, WriteOnly]
                {
                    [Max(5, Force=true)] { epiS32 A = 1; }

                    [Min(-5)]
                    [Max(5)]
                    {
                        epiS32 B = 1;
                        epiS32 C = -5;
                        epiS32 D = 1;
                    }
                }
            };

            class
            ClassName
                : ParentClassName { # comment
                # comment
                epiChar Name0 = 'f'; epiWChar Name1 = L'F'; epiBool Name2 = true; epiByte Name3;

                [Transient, ReadOnly] { epiSize_t Name4; epiHash_t Name5; [Virtual] epiU8 Name6; epiU16 Name7; }

                epiU32 Name8    =   -1;                  epiU64 Name9;

                [ Min ( -5 ) ]
                epiS8 Name10;
                epiS16 Name11 =    15; epiS32 Name12;
                epiS64 * Name13;
                epiFloat Name14;       

                epiDouble Name15; # comment
                epiString Name16 = "Hello"; epiWString Name17;
                epiArray<MyClassName> Name18;       
                epiPtrArray<epiFloat> Name19;
                epiVec2f Name20;
                epiVec2d Name_21;

                epiVec2s Name22; epiVec2u Name23; epiVec3f Name24; epiVec3d Name25;
                epiVec3s Name26;
                epiVec3u Name27;
                epiVec4f Name28;                         epiVec4d Name29;
                epiVec4s Name30;
                epiVec4u Name31;
                epiMat2x2f Name32;
                epiMat3x3f Name33;
                epiMat4x4f *Name34;
                epiRect2f Name35;
                [WriteOnly] epiRect2d Name36;

                # comment
                # comment

                epiRect2s Name37;
                epiRect2u Name38;
            };
            '''
        ),
    ])
    def test_sequence_formatting(self, tmpdir: str, content: str):

        expected_errors = []
        expected_registry = {
            'EnumName':
                EpiEnumBuilder()
                    .name('EnumName')
                    .entry(EpiEnumEntryBuilder().name('Value1').build())
                    .entry(EpiEnumEntryBuilder().name('Value2').value([(TokenType.IntegerLiteral, '123')]).build())
                    .entry(EpiEnumEntryBuilder().name('Value3').value([(TokenType.IntegerLiteral, '123')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"V1"').build()).build())
                    .entry(EpiEnumEntryBuilder().name('Value4').value([(TokenType.IntegerLiteral, '42')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"V1"').build()).build())
                    .entry(EpiEnumEntryBuilder().name('Value5').value([(TokenType.IntegerLiteral, '-23')]).attr(EpiAttributeBuilder().tokentype(TokenType.DisplayName).param_positional(TokenType.StringLiteral, '"V2"').build()).build())
                    .build(),
            'ParentClassName':
                EpiClassBuilder()
                    .name('ParentClassName')
                    .inner(
                        EpiEnumBuilder()
                            .name('InnerEnumName')
                            .base(TokenType.Int32Type)
                            .entry(EpiEnumEntryBuilder().name('Value1').build())
                            .entry(EpiEnumEntryBuilder().name('Value2').build())
                            .build()
                    )
                    .property(EpiPropertyBuilder().name('A').tokentype_type(TokenType.Int32Type)
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Transient)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.WriteOnly)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Max)
                                .param_positional(TokenType.IntegerLiteral, '5')
                                .param_named('Force', TokenType.TrueLiteral, 'true')
                                .build())
                        .value('1').build())
                    .property(EpiPropertyBuilder().name('B').tokentype_type(TokenType.Int32Type)
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Transient)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.WriteOnly)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Min)
                                .param_positional(TokenType.IntegerLiteral, '-5')
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Max)
                                .param_positional(TokenType.IntegerLiteral, '5')
                                .build())
                        .value('1').build())
                    .property(EpiPropertyBuilder().name('C').tokentype_type(TokenType.Int32Type)
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Transient)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.WriteOnly)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Min)
                                .param_positional(TokenType.IntegerLiteral, '-5')
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Max)
                                .param_positional(TokenType.IntegerLiteral, '5')
                                .build())
                        .value('-5').build())
                    .property(EpiPropertyBuilder().name('D').tokentype_type(TokenType.Int32Type)
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Transient)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.WriteOnly)
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Min)
                                .param_positional(TokenType.IntegerLiteral, '-5')
                                .build())
                        .attr(
                            EpiAttributeBuilder()
                                .tokentype(TokenType.Max)
                                .param_positional(TokenType.IntegerLiteral, '5')
                                .build())
                        .value('1').build())
                    .build(),
            'ClassName':
                EpiClassBuilder()
                    .name('ClassName')
                    .parent('ParentClassName')
                    .property(EpiPropertyBuilder().name('Name0').tokentype_type(TokenType.CharType).value("'f'").build())
                    .property(EpiPropertyBuilder().name('Name1').tokentype_type(TokenType.WCharType).value("L'F'").build())
                    .property(EpiPropertyBuilder().name('Name2').tokentype_type(TokenType.BoolType).value('true', TokenType.TrueLiteral).build())
                    .property(EpiPropertyBuilder().name('Name3').tokentype_type(TokenType.ByteType).build())
                    .property(EpiPropertyBuilder().name('Name4').tokentype_type(TokenType.SizeTType).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).attr(EpiAttributeBuilder().tokentype(TokenType.ReadOnly).build()).build())
                    .property(EpiPropertyBuilder().name('Name5').tokentype_type(TokenType.HashTType).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).attr(EpiAttributeBuilder().tokentype(TokenType.ReadOnly).build()).build())
                    .property(EpiPropertyBuilder().name('Name6').tokentype_type(TokenType.UInt8Type).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).attr(EpiAttributeBuilder().tokentype(TokenType.ReadOnly).build()).attr(EpiAttributeBuilder().tokentype(TokenType.Virtual).build()).build())
                    .property(EpiPropertyBuilder().name('Name7').tokentype_type(TokenType.UInt16Type).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).attr(EpiAttributeBuilder().tokentype(TokenType.ReadOnly).build()).build())
                    .property(EpiPropertyBuilder().name('Name8').tokentype_type(TokenType.UInt32Type).value('-1').build())
                    .property(EpiPropertyBuilder().name('Name9').tokentype_type(TokenType.UInt64Type).build())
                    .property(EpiPropertyBuilder().name('Name10').tokentype_type(TokenType.Int8Type).attr(EpiAttributeBuilder().tokentype(TokenType.Min).param_positional(TokenType.IntegerLiteral, '-5').build()).build())
                    .property(EpiPropertyBuilder().name('Name11').tokentype_type(TokenType.Int16Type).value('15').build())
                    .property(EpiPropertyBuilder().name('Name12').tokentype_type(TokenType.Int32Type).build())
                    .property(EpiPropertyBuilder().name('Name13').tokentype_type(TokenType.Int64Type).form(EpiProperty.Form.Pointer).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).build())
                    .property(EpiPropertyBuilder().name('Name14').tokentype_type(TokenType.SingleFloatingType).build())
                    .property(EpiPropertyBuilder().name('Name15').tokentype_type(TokenType.DoubleFloatingType).build())
                    .property(EpiPropertyBuilder().name('Name16').tokentype_type(TokenType.StringType).value('"Hello"').build())
                    .property(EpiPropertyBuilder().name('Name17').tokentype_type(TokenType.WStringType).build())
                    .property(EpiPropertyBuilder().name('Name18').tokentype_type(TokenType.ArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.Identifier, 'MyClassName').build())
                    .property(EpiPropertyBuilder().name('Name19').tokentype_type(TokenType.PtrArrayType).form(EpiProperty.Form.Template).token_nested(TokenType.SingleFloatingType).build())
                    .property(EpiPropertyBuilder().name('Name20').tokentype_type(TokenType.Vec2FType).build())
                    .property(EpiPropertyBuilder().name('Name_21').tokentype_type(TokenType.Vec2DType).build())
                    .property(EpiPropertyBuilder().name('Name22').tokentype_type(TokenType.Vec2SType).build())
                    .property(EpiPropertyBuilder().name('Name23').tokentype_type(TokenType.Vec2UType).build())
                    .property(EpiPropertyBuilder().name('Name24').tokentype_type(TokenType.Vec3FType).build())
                    .property(EpiPropertyBuilder().name('Name25').tokentype_type(TokenType.Vec3DType).build())
                    .property(EpiPropertyBuilder().name('Name26').tokentype_type(TokenType.Vec3SType).build())
                    .property(EpiPropertyBuilder().name('Name27').tokentype_type(TokenType.Vec3UType).build())
                    .property(EpiPropertyBuilder().name('Name28').tokentype_type(TokenType.Vec4FType).build())
                    .property(EpiPropertyBuilder().name('Name29').tokentype_type(TokenType.Vec4DType).build())
                    .property(EpiPropertyBuilder().name('Name30').tokentype_type(TokenType.Vec4SType).build())
                    .property(EpiPropertyBuilder().name('Name31').tokentype_type(TokenType.Vec4UType).build())
                    .property(EpiPropertyBuilder().name('Name32').tokentype_type(TokenType.Mat2x2FType).build())
                    .property(EpiPropertyBuilder().name('Name33').tokentype_type(TokenType.Mat3x3FType).build())
                    .property(EpiPropertyBuilder().name('Name34').tokentype_type(TokenType.Mat4x4FType).form(EpiProperty.Form.Pointer).attr(EpiAttributeBuilder().tokentype(TokenType.Transient).build()).build())
                    .property(EpiPropertyBuilder().name('Name35').tokentype_type(TokenType.Rect2FType).build())
                    .property(EpiPropertyBuilder().name('Name36').tokentype_type(TokenType.Rect2DType).attr(EpiAttributeBuilder().tokentype(TokenType.WriteOnly).build()).build())
                    .property(EpiPropertyBuilder().name('Name37').tokentype_type(TokenType.Rect2SType).build())
                    .property(EpiPropertyBuilder().name('Name38').tokentype_type(TokenType.Rect2UType).build())
                    .build()
        }

        self.test_sequence(tmpdir, content, expected_registry, expected_errors)

