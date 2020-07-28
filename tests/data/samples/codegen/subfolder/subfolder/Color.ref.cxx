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

void Color::Serialization(json_t& json)
{
    super::Serialization(json);

    epiSerialize(Color, json);
}

void Color::Deserialization(const json_t& json)
{
    super::Deserialization(json);

    epiDeserialize(Color, json);
}

MetaClass Color::EmitMetaClass()
{
    MetaClassData data;

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Ru",
            /* PtrRead */ (void*)offsetof(Color, GetRu_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetRu_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU8),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Ru), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Gu",
            /* PtrRead */ (void*)offsetof(Color, GetGu_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetGu_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU8),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Gu), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Bu",
            /* PtrRead */ (void*)offsetof(Color, GetBu_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetBu_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU8),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Bu), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Au",
            /* PtrRead */ (void*)offsetof(Color, GetAu_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetAu_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU8),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Au), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Rf",
            /* PtrRead */ (void*)offsetof(Color, GetRf_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetRf_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Rf), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Gf",
            /* PtrRead */ (void*)offsetof(Color, GetGf_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetGf_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Gf), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Bf",
            /* PtrRead */ (void*)offsetof(Color, GetBf_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetBf_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Bf), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Af",
            /* PtrRead */ (void*)offsetof(Color, GetAf_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetAf_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiFloat),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Af), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "RGBA32",
            /* PtrRead */ (void*)offsetof(Color, GetRGBA32_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetRGBA32_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(RGBA32), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "BGRA32",
            /* PtrRead */ (void*)offsetof(Color, GetBGRA32_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetBGRA32_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(BGRA32), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "RGB24",
            /* PtrRead */ (void*)offsetof(Color, GetRGB24_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetRGB24_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(RGB24), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "BGR24",
            /* PtrRead */ (void*)offsetof(Color, GetBGR24_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetBGR24_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiU32),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(BGR24), std::move(m));
    }

    {
        MetaProperty m = epiMetaProperty(
            /* Name */ "Color",
            /* PtrRead */ (void*)offsetof(Color, GetColor_FuncPtr),
            /* PtrWrite */ (void*)offsetof(Color, SetColor_FuncPtr),
            /* Flags */ {MetaProperty::Flags::MaskReadCallback | MetaProperty::Flags::MaskWriteCallback},
            /* typeID */ epiHashCompileTime(epiVec4f),
            /* nestedTypeID */ MetaTypeID_None
        );
        data.AddProperty(epiHashCompileTime(Color), std::move(m));
    }

    return MetaClass(std::move(data), epiHashCompileTime(Color), epiHashCompileTime(Object), sizeof(Color), "Color");
}

EPI_NAMESPACE_END()
