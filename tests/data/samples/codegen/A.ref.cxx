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
            /* Flags */ {},
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
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiString),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Text), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "VirtualFloats",
            /* PtrRead */ (void*)offsetof(A, GetVirtualFloats_FuncPtr),
            /* PtrWrite */ (void*)nullptr,
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskReadOnly},
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
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
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
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
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
            /* Flags */ {},
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
            /* Flags */ {},
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
            /* Flags */ {},
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
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiU32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Value4), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "NonSiblingVirtual",
            /* PtrRead */ (void*)offsetof(A, GetNonSiblingVirtual_FuncPtr),
            /* PtrWrite */ (void*)offsetof(A, SetNonSiblingVirtual_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(epiFloat)
        );
        data.AddProperty(epiHashCompileTime(NonSiblingVirtual), std::move(m));
    }

    return MetaClass(std::move(data), epiHashCompileTime(A), epiHashCompileTime(Object), sizeof(A), "A");
}

void AA::Serialization(json_t& json)
{
    super::Serialization(json);
}

void AA::Deserialization(const json_t& json)
{
    super::Deserialization(json);
}

MetaClass AA::EmitMetaClass()
{
    MetaClassData data;

    return MetaClass(std::move(data), epiHashCompileTime(AA), epiHashCompileTime(A), sizeof(AA), "AA");
}

EPI_NAMESPACE_END()
