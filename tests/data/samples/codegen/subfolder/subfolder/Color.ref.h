#pragma once

EPI_GENREGION_BEGIN(include)
#include "subfolder/Color.hxx"
EPI_GENREGION_END(include)

EPI_NAMESPACE_BEGIN()

enum EMask
{
EPI_GENREGION_BEGIN(EMask)
    EMask_Value0 = (1 << 1),
    EMask_Value1 = (1 << 2),
    EMask_Value2 = (1 << 3),
    EMask_Value3 = (1 << 4),
    EMask_Value012 = EMask_Value0 | EMask_Value1 | EMask_Value2,
    EMask_Value4 = (1 << 5)
EPI_GENREGION_END(EMask)
};

class Color : public Object
{
EPI_GENREGION_BEGIN(Color)

public:
    enum EInnerMask
    {
    EPI_GENREGION_BEGIN(Color::EInnerMask)
        Color_EInnerMask_Value0 = (1 << 1),
        Color_EInnerMask_Value1 = (1 << 2),
        Color_EInnerMask_Value2 = (1 << 3),
        Color_EInnerMask_Value3 = (1 << 4),
        Color_EInnerMask_Value012 = Color_EInnerMask_Value0 | Color_EInnerMask_Value1 | Color_EInnerMask_Value2,
        Color_EInnerMask_Value4 = (1 << 5)
    EPI_GENREGION_END(Color::EInnerMask)
    };

EPI_GENHIDDEN_Color()

public:
    constexpr static epiMetaTypeID TypeID{0xa79767ed};

    enum Color_PIDs
    {
        PID_Ru = 0xe93ba89a,
        PID_Gu = 0xde8e4e8e,
        PID_Bu = 0xa3f9bacb,
        PID_Au = 0x88d4e908,
        PID_Rf = 0x6d85e944,
        PID_Gf = 0x5a300f50,
        PID_Bf = 0x2747fb15,
        PID_Af = 0xc6aa8d6,
        PID_RGBA32 = 0x66aecff7,
        PID_BGRA32 = 0x35619af3,
        PID_RGB24 = 0x3de8f258,
        PID_BGR24 = 0x412ec6aa,
        PID_Color = 0xa79767ed,
        PID_Enum0 = 0x29782fe9,
        PID_Enum1 = 0x5e7f1f7f,
        PID_Enum2 = 0xc7764ec5,
        PID_COUNT = 16
    };

protected:
    epiU8 GetRu_Callback() const;
    void SetRu_Callback(epiU8 value);
    epiU8 GetGu_Callback() const;
    void SetGu_Callback(epiU8 value);
    epiU8 GetBu_Callback() const;
    void SetBu_Callback(epiU8 value);
    epiU8 GetAu_Callback() const;
    void SetAu_Callback(epiU8 value);
    epiFloat GetRf_Callback() const;
    void SetRf_Callback(epiFloat value);
    epiFloat GetGf_Callback() const;
    void SetGf_Callback(epiFloat value);
    epiFloat GetBf_Callback() const;
    void SetBf_Callback(epiFloat value);
    epiFloat GetAf_Callback() const;
    void SetAf_Callback(epiFloat value);
    epiU32 GetRGBA32_Callback() const;
    void SetRGBA32_Callback(epiU32 value);
    epiU32 GetBGRA32_Callback() const;
    void SetBGRA32_Callback(epiU32 value);
    epiU32 GetRGB24_Callback() const;
    void SetRGB24_Callback(epiU32 value);
    epiU32 GetBGR24_Callback() const;
    void SetBGR24_Callback(epiU32 value);
    const epiVec4f& GetColor_Callback() const;
    void SetColor_Callback(const epiVec4f& value);

protected:
    epiVec4f m_Color;
    EInnerMask m_Enum0{Color_EInnerMask_Value012};
    EMask m_Enum1{EMask_Value4};
    EInnerMask m_Enum2{Color_EInnerMask_Value012};

EPI_GENREGION_END(Color)
};

EPI_NAMESPACE_END()
