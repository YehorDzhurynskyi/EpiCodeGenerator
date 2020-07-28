#pragma once

EPI_GENREGION_BEGIN(include)
#include "subfolder/Color.hxx"
EPI_GENREGION_END(include)

EPI_NAMESPACE_BEGIN()

class Color : public Object
{
EPI_GENREGION_BEGIN(Color)

EPI_GENHIDDEN_Color()

public:
    constexpr static MetaTypeID TypeID{0xa79767ed};

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
        PID_COUNT = 13
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

EPI_GENREGION_END(Color)
};

EPI_NAMESPACE_END()
