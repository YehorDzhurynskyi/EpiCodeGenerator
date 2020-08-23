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

#define EPI_GENHIDDEN_Color() \
public: \
using super = Object; \
 \
static MetaClass EmitMetaClass(); \
 \
const MetaClass& GetMetaClass() const override \
{ \
    super::GetMetaClass(); \
    return ClassRegistry_GetMetaClass<Color>(); \
} \
 \
epiBool Is(MetaTypeID rhs) const override \
{ \
    return rhs == Color::TypeID || super::Is(rhs); \
} \
 \
void Serialization(json_t& json) override; \
void Deserialization(const json_t& json) override; \
 \
epiU8 GetRu() const { return GetRu_Callback(); } \
void SetRu(epiU8 value) { SetRu_Callback(value); } \
epiU8 GetGu() const { return GetGu_Callback(); } \
void SetGu(epiU8 value) { SetGu_Callback(value); } \
epiU8 GetBu() const { return GetBu_Callback(); } \
void SetBu(epiU8 value) { SetBu_Callback(value); } \
epiU8 GetAu() const { return GetAu_Callback(); } \
void SetAu(epiU8 value) { SetAu_Callback(value); } \
epiFloat GetRf() const { return GetRf_Callback(); } \
void SetRf(epiFloat value) { SetRf_Callback(value); } \
epiFloat GetGf() const { return GetGf_Callback(); } \
void SetGf(epiFloat value) { SetGf_Callback(value); } \
epiFloat GetBf() const { return GetBf_Callback(); } \
void SetBf(epiFloat value) { SetBf_Callback(value); } \
epiFloat GetAf() const { return GetAf_Callback(); } \
void SetAf(epiFloat value) { SetAf_Callback(value); } \
epiU32 GetRGBA32() const { return GetRGBA32_Callback(); } \
void SetRGBA32(epiU32 value) { SetRGBA32_Callback(value); } \
epiU32 GetBGRA32() const { return GetBGRA32_Callback(); } \
void SetBGRA32(epiU32 value) { SetBGRA32_Callback(value); } \
epiU32 GetRGB24() const { return GetRGB24_Callback(); } \
void SetRGB24(epiU32 value) { SetRGB24_Callback(value); } \
epiU32 GetBGR24() const { return GetBGR24_Callback(); } \
void SetBGR24(epiU32 value) { SetBGR24_Callback(value); } \
const epiVec4f& GetColor() const { return GetColor_Callback(); } \
void SetColor(const epiVec4f& value) { SetColor_Callback(value); } \
inline EInnerMask GetEnum0() const { return m_Enum0; } \
inline void SetEnum0(EInnerMask value) { m_Enum0 = value; } \
inline EMask GetEnum1() const { return m_Enum1; } \
inline void SetEnum1(EMask value) { m_Enum1 = value; } \
inline EInnerMask GetEnum2() const { return m_Enum2; } \
inline void SetEnum2(EInnerMask value) { m_Enum2 = value; } \
 \
enum Color_PIDXs \
{ \
    PIDX_Ru = 0, \
    PIDX_Gu = 1, \
    PIDX_Bu = 2, \
    PIDX_Au = 3, \
    PIDX_Rf = 4, \
    PIDX_Gf = 5, \
    PIDX_Bf = 6, \
    PIDX_Af = 7, \
    PIDX_RGBA32 = 8, \
    PIDX_BGRA32 = 9, \
    PIDX_RGB24 = 10, \
    PIDX_BGR24 = 11, \
    PIDX_Color = 12, \
    PIDX_Enum0 = 13, \
    PIDX_Enum1 = 14, \
    PIDX_Enum2 = 15, \
    PIDX_COUNT = 16 \
}; \
 \
private: \
epiU8 (Color::*GetRu_FuncPtr)() const { &Color::GetRu }; \
void (Color::*SetRu_FuncPtr)(epiU8) { &Color::SetRu }; \
epiU8 (Color::*GetGu_FuncPtr)() const { &Color::GetGu }; \
void (Color::*SetGu_FuncPtr)(epiU8) { &Color::SetGu }; \
epiU8 (Color::*GetBu_FuncPtr)() const { &Color::GetBu }; \
void (Color::*SetBu_FuncPtr)(epiU8) { &Color::SetBu }; \
epiU8 (Color::*GetAu_FuncPtr)() const { &Color::GetAu }; \
void (Color::*SetAu_FuncPtr)(epiU8) { &Color::SetAu }; \
epiFloat (Color::*GetRf_FuncPtr)() const { &Color::GetRf }; \
void (Color::*SetRf_FuncPtr)(epiFloat) { &Color::SetRf }; \
epiFloat (Color::*GetGf_FuncPtr)() const { &Color::GetGf }; \
void (Color::*SetGf_FuncPtr)(epiFloat) { &Color::SetGf }; \
epiFloat (Color::*GetBf_FuncPtr)() const { &Color::GetBf }; \
void (Color::*SetBf_FuncPtr)(epiFloat) { &Color::SetBf }; \
epiFloat (Color::*GetAf_FuncPtr)() const { &Color::GetAf }; \
void (Color::*SetAf_FuncPtr)(epiFloat) { &Color::SetAf }; \
epiU32 (Color::*GetRGBA32_FuncPtr)() const { &Color::GetRGBA32 }; \
void (Color::*SetRGBA32_FuncPtr)(epiU32) { &Color::SetRGBA32 }; \
epiU32 (Color::*GetBGRA32_FuncPtr)() const { &Color::GetBGRA32 }; \
void (Color::*SetBGRA32_FuncPtr)(epiU32) { &Color::SetBGRA32 }; \
epiU32 (Color::*GetRGB24_FuncPtr)() const { &Color::GetRGB24 }; \
void (Color::*SetRGB24_FuncPtr)(epiU32) { &Color::SetRGB24 }; \
epiU32 (Color::*GetBGR24_FuncPtr)() const { &Color::GetBGR24 }; \
void (Color::*SetBGR24_FuncPtr)(epiU32) { &Color::SetBGR24 }; \
const epiVec4f& (Color::*GetColor_FuncPtr)() const { &Color::GetColor }; \
void (Color::*SetColor_FuncPtr)(const epiVec4f&) { &Color::SetColor }; \

