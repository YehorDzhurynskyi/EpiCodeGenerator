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
