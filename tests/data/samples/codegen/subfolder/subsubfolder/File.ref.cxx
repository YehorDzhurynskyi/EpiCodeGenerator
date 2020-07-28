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

    return MetaClass(std::move(data), epiHashCompileTime(B), epiHashCompileTime(A), sizeof(B), "B");
}

EPI_NAMESPACE_END()
