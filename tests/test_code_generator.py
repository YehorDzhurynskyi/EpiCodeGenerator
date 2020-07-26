from epi_code_generator.tokenizer import Tokenizer

from epi_code_generator.idlparser import idlparser_base as idl
from epi_code_generator.linker import linker as ln
from epi_code_generator.code_generator import code_generator as cgen

import pytest


@pytest.mark.order(3)
class TestCodeGenerator:

    @pytest.mark.parametrize('epi,cxx', [
        (
'''
class A
{
    epiS32 PName;

    [Transient]
    epiString Text = "my text";

    [Virtual, ReadOnly]
    epiArray<epiFloat> VirtualFloats;

    [Virtual]
    epiFloat VirtualFloat;

    [Virtual, ReadCallback(SuppressRef=true)]
    epiMat4x4f ProjMat;

    [Min(0.0)]
    epiDouble Value1 = 3.0;

    [Min(0.0), Max(10.0)]
    epiDouble Value2 = 5.0;

    [Min(0.0), Max(10.0, Force=true)]
    epiDouble Value3 = 2.535;

    [Min(0, Force=true), Max(54, Force=true)]
    epiU32 Value4;
};

class B : A
{
    epiPtrArray<B> BBs;

    epiSize_t Size = 13;

    B* Sibling;
    epiFloat* NonSibling;

    [Virtual]
    epiFloat* NonSiblingVirtual;
};
''',
'''
/*                                                      */
/*  ______       _                                      */
/* |  ____|     (_)                                     */
/* | |__   _ __  _                                      */
/* |  __| | '_ \| |   THIS FILE IS AUTO-GENERATED       */
/* | |____| |_) | |   manual changes won't be saved     */
/* |______| .__/|_|                                     */
/*        | |                                           */
/*        |_|                                           */
/*                                                      */

EPI_NAMESPACE_BEGIN()

void A::Serialization(json_t& json)
{
    super::Serialization(json);

    epiSerialize(PName, json);
    epiSerialize(Value1, json);
    epiSerialize(Value2, json);
    epiSerialize(Value3, json);
    epiSerialize(Value4, json);
}

void A::Deserialization(const json_t& json)
{
    super::Deserialization(json);

    epiDeserialize(PName, json);
    epiDeserialize(Value1, json);
    epiDeserialize(Value2, json);
    epiDeserialize(Value3, json);
    epiDeserialize(Value4, json);
}

MetaClass A::EmitMetaClass()
{
    MetaClassData data;

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "PName",
            /* PtrRead */ (void*)offsetof(A, m_PName),
            /* PtrWrite */ (void*)offsetof(A, m_PName),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiS32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(PName), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Text",
            /* PtrRead */ (void*)offsetof(A, m_Text),
            /* PtrWrite */ (void*)offsetof(A, m_Text),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiString),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Text), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "VirtualFloats",
            /* PtrRead */ (void*)offsetof(A, GetVirtualFloats_FuncPtr),
            /* PtrWrite */ nullptr,
            /* Flags */ {{MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskReadOnly}},
            /* typeID */ epiHashCompileTime(epiArray),
            /* nestedTypeID */ epiHashCompileTime(epiFloat)
        );
        data.AddProperty(epiHashCompileTime(VirtualFloats), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "VirtualFloat",
            /* PtrRead */ (void*)offsetof(A, GetVirtualFloat_FuncPtr),
            /* PtrWrite */ (void*)offsetof(A, SetVirtualFloat_FuncPtr),
            /* Flags */ {{MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback | MetaProperty::Flags::MaskReadOnly}},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(VirtualFloat), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "VirtualFloat",
            /* PtrRead */ (void*)offsetof(A, GetVirtualFloat_FuncPtr),
            /* PtrWrite */ (void*)offsetof(A, SetVirtualFloat_FuncPtr),
            /* Flags */ {{MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback | MetaProperty::Flags::MaskReadOnly}},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(VirtualFloat), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "ProjMat",
            /* PtrRead */ (void*)offsetof(A, GetProjMat_FuncPtr),
            /* PtrWrite */ (void*)offsetof(A, SetProjMat_FuncPtr),
            /* Flags */ {{MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback | MetaProperty::Flags::MaskReadOnly}},
            /* typeID */ epiHashCompileTime(epiMat4x4f),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(ProjMat), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Value1",
            /* PtrRead */ (void*)offsetof(A, m_Value1),
            /* PtrWrite */ (void*)offsetof(A, m_Value1),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiDouble),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Value1), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Value2",
            /* PtrRead */ (void*)offsetof(A, m_Value2),
            /* PtrWrite */ (void*)offsetof(A, m_Value2),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiDouble),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Value2), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Value3",
            /* PtrRead */ (void*)offsetof(A, m_Value3),
            /* PtrWrite */ (void*)offsetof(A, m_Value3),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiDouble),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Value3), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Value4",
            /* PtrRead */ (void*)offsetof(A, m_Value4),
            /* PtrWrite */ (void*)offsetof(A, m_Value4),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiDouble),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Value4), std::move(m));
    }

    return MetaClass(std::move(data), epiHashCompileTime(A), epiHashCompileTime(Object), sizeof(A), "A");
}

void B::Serialization(json_t& json)
{
    super::Serialization(json);

    epiSerialize(BBs, json);
    epiSerialize(Size, json);
}

void B::Deserialization(const json_t& json)
{
    super::Deserialization(json);

    epiDeserialize(BBs, json);
    epiDeserialize(Size, json);
}

MetaClass B::EmitMetaClass()
{
    MetaClassData data;

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "BBs",
            /* PtrRead */ (void*)offsetof(A, m_BBs),
            /* PtrWrite */ (void*)offsetof(A, m_BBs),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiPtrArray),
            /* nestedTypeID */ epiHashCompileTime(B)
        );
        data.AddProperty(epiHashCompileTime(BBs), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Size",
            /* PtrRead */ (void*)offsetof(A, m_Size),
            /* PtrWrite */ (void*)offsetof(A, m_Size),
            /* Flags */ {{}},
            /* typeID */ epiHashCompileTime(epiSize_t),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Size), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Sibling",
            /* PtrRead */ (void*)offsetof(A, m_Sibling),
            /* PtrWrite */ (void*)offsetof(A, m_Sibling),
            /* Flags */ {{}},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(B)
        );
        data.AddProperty(epiHashCompileTime(Sibling), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "NonSibling",
            /* PtrRead */ (void*)offsetof(A, m_NonSibling),
            /* PtrWrite */ (void*)offsetof(A, m_NonSibling),
            /* Flags */ {{}},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(epiFloat)
        );
        data.AddProperty(epiHashCompileTime(NonSibling), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "NonSiblingVirtual",
            /* PtrRead */ (void*)offsetof(A, GetNonSiblingVirtual_FuncPtr),
            /* PtrWrite */ (void*)offsetof(A, SetNonSiblingVirtual_FuncPtr),
            /* Flags */ {{MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback}},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(epiFloat)
        );
        data.AddProperty(epiHashCompileTime(NonSiblingVirtual), std::move(m));
    }

    return MetaClass(std::move(data), epiHashCompileTime(B), epiHashCompileTime(A), sizeof(B), "B");
}

EPI_NAMESPACE_END()

'''
        )
    ])
    def test_sequence(self, tmpdir: str, epi: str, cxx: str):

        linker = ln.Linker()

        basename = f'{tmpdir}/test'
        path = f'{basename}.epi'
        with open(path, 'w') as f:
            f.write(epi)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        parser = idl.IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        assert len(errors_syntax) == 0

        linker.register(registry_local)

        errors_linkage = linker.link()

        assert len(errors_linkage) == 0

        symbols = list(linker.registry.values())
        codegen = cgen.CodeGenerator(symbols, tmpdir, tmpdir, tmpdir)
        errors_codegen = codegen.code_generate()

        assert len(errors_codegen) == 0

        codegen.dump()

        with open(f'{basename}.cxx', 'r') as f:
            assert cxx == f.read()

        #path_hxx = f'{basename}.hxx'
        #path_cpp = f'{basename}.cpp'
        #path_h = f'{basename}.h'


