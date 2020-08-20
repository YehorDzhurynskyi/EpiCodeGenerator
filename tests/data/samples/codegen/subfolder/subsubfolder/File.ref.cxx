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

void Inner::Serialization(json_t& json)
{
    super::Serialization(json);
}

void Inner::Deserialization(const json_t& json)
{
    super::Deserialization(json);
}

MetaClass Inner::EmitMetaClass()
{
    MetaClassData data;

    return MetaClass(std::move(data), epiHashCompileTime(Inner), epiHashCompileTime(Object), sizeof(Inner), "Inner");
}

void B::Serialization(json_t& json)
{
    super::Serialization(json);

    epiSerialize(BBs, json);
    epiSerialize(Size, json);
    epiSerialize(Enum0, json);
    epiSerialize(Enum1, json);
    epiSerialize(Enums0, json);
    epiSerialize(Enums1, json);
}

void B::Deserialization(const json_t& json)
{
    super::Deserialization(json);

    epiDeserialize(BBs, json);
    epiDeserialize(Size, json);
    epiDeserialize(Enum0, json);
    epiDeserialize(Enum1, json);
    epiDeserialize(Enums0, json);
    epiDeserialize(Enums1, json);
}

MetaClass B::EmitMetaClass()
{
    MetaClassData data;

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "BBs",
            /* PtrRead */ (void*)offsetof(B, m_BBs),
            /* PtrWrite */ (void*)offsetof(B, m_BBs),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiPtrArray),
            /* nestedTypeID */ epiHashCompileTime(B)
        );
        data.AddProperty(epiHashCompileTime(BBs), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Size",
            /* PtrRead */ (void*)offsetof(B, m_Size),
            /* PtrWrite */ (void*)offsetof(B, m_Size),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiSize_t),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Size), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Sibling",
            /* PtrRead */ (void*)offsetof(B, m_Sibling),
            /* PtrWrite */ (void*)offsetof(B, m_Sibling),
            /* Flags */ {},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(B)
        );
        data.AddProperty(epiHashCompileTime(Sibling), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "NonSibling",
            /* PtrRead */ (void*)offsetof(B, m_NonSibling),
            /* PtrWrite */ (void*)offsetof(B, m_NonSibling),
            /* Flags */ {},
            /* typeID */ MetaTypeID_Ptr,
            /* nestedTypeID */ epiHashCompileTime(epiFloat)
        );
        data.AddProperty(epiHashCompileTime(NonSibling), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Enum0",
            /* PtrRead */ (void*)offsetof(B, m_Enum0),
            /* PtrWrite */ (void*)offsetof(B, m_Enum0),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(Inner::E),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Enum0), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Enum1",
            /* PtrRead */ (void*)offsetof(B, m_Enum1),
            /* PtrWrite */ (void*)offsetof(B, m_Enum1),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(Inner::E),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Enum1), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Enum2",
            /* PtrRead */ (void*)offsetof(B, GetEnum2_FuncPtr),
            /* PtrWrite */ (void*)offsetof(B, SetEnum2_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(E1),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Enum2), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Enums0",
            /* PtrRead */ (void*)offsetof(B, m_Enums0),
            /* PtrWrite */ (void*)offsetof(B, m_Enums0),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiArray),
            /* nestedTypeID */ epiHashCompileTime(Inner::E)
        );
        data.AddProperty(epiHashCompileTime(Enums0), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Enums1",
            /* PtrRead */ (void*)offsetof(B, m_Enums1),
            /* PtrWrite */ (void*)offsetof(B, m_Enums1),
            /* Flags */ {},
            /* typeID */ epiHashCompileTime(epiArray),
            /* nestedTypeID */ epiHashCompileTime(E0)
        );
        data.AddProperty(epiHashCompileTime(Enums1), std::move(m));
    }

    return MetaClass(std::move(data), epiHashCompileTime(B), epiHashCompileTime(A), sizeof(B), "B");
}

EPI_NAMESPACE_END()
