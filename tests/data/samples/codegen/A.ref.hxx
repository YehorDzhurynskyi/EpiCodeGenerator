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

#define EPI_GENHIDDEN_A() \
public: \
using super = Object; \
 \
static MetaClass EmitMetaClass(); \
 \
const MetaClass& GetMetaClass() const override \
{ \
    super::GetMetaClass(); \
    return ClassRegistry_GetMetaClass<A>(); \
} \
 \
epiBool Is(MetaTypeID rhs) const override \
{ \
    return rhs == A::TypeID || super::Is(rhs); \
} \
 \
void Serialization(json_t& json) override; \
void Deserialization(const json_t& json) override; \
 \
inline epiS32 GetPName() const { return m_PName; } \
inline void SetPName(epiS32 value) { m_PName = value; } \
inline const epiString& GetText() const { return m_Text; } \
inline void SetText(const epiString& value) { m_Text = value; } \
const epiArray<epiFloat>& GetVirtualFloats() const { return GetVirtualFloats_Callback(); } \
epiFloat GetVirtualFloat() const { return GetVirtualFloat_Callback(); } \
void SetVirtualFloat(epiFloat value) { SetVirtualFloat_Callback(value); } \
epiMat4x4f GetProjMat() const { return GetProjMat_Callback(); } \
void SetProjMat(const epiMat4x4f& value) { SetProjMat_Callback(value); } \
inline epiDouble GetValue1() const { return m_Value1; } \
void SetValue1(epiDouble value) { epiExpected(value >= 0.0); m_Value1 = value; } \
inline epiDouble GetValue2() const { return m_Value2; } \
void SetValue2(epiDouble value) { epiExpected(value >= 0.0); epiExpected(value <= 10.0); m_Value2 = value; } \
inline epiDouble GetValue3() const { return m_Value3; } \
void SetValue3(epiDouble value) { epiExpected(value >= 0.0); value = std::min(value, 10.0); m_Value3 = value; } \
inline epiU32 GetValue4() const { return m_Value4; } \
void SetValue4(epiU32 value) { value = std::max(value, 0); value = std::min(value, 54); m_Value4 = value; } \
const epiFloat* GetNonSiblingVirtual() const { return GetNonSiblingVirtual_Callback(); } \
void SetNonSiblingVirtual(epiFloat* value) { SetNonSiblingVirtual_Callback(value); } \
 \
enum A_PIDXs \
{ \
    PIDX_PName = 0, \
    PIDX_Text = 1, \
    PIDX_VirtualFloats = 2, \
    PIDX_VirtualFloat = 3, \
    PIDX_ProjMat = 4, \
    PIDX_Value1 = 5, \
    PIDX_Value2 = 6, \
    PIDX_Value3 = 7, \
    PIDX_Value4 = 8, \
    PIDX_NonSiblingVirtual = 9, \
    PIDX_COUNT = 10 \
}; \
 \
private: \
const epiArray<epiFloat>& (A::*GetVirtualFloats_FuncPtr)() const { &A::GetVirtualFloats }; \
epiFloat (A::*GetVirtualFloat_FuncPtr)() const { &A::GetVirtualFloat }; \
void (A::*SetVirtualFloat_FuncPtr)(epiFloat) { &A::SetVirtualFloat }; \
epiMat4x4f (A::*GetProjMat_FuncPtr)() const { &A::GetProjMat }; \
void (A::*SetProjMat_FuncPtr)(const epiMat4x4f&) { &A::SetProjMat }; \
const epiFloat* (A::*GetNonSiblingVirtual_FuncPtr)() const { &A::GetNonSiblingVirtual }; \
void (A::*SetNonSiblingVirtual_FuncPtr)(epiFloat*) { &A::SetNonSiblingVirtual }; \


#define EPI_GENHIDDEN_AA() \
public: \
using super = A; \
 \
static MetaClass EmitMetaClass(); \
 \
const MetaClass& GetMetaClass() const override \
{ \
    super::GetMetaClass(); \
    return ClassRegistry_GetMetaClass<AA>(); \
} \
 \
epiBool Is(MetaTypeID rhs) const override \
{ \
    return rhs == AA::TypeID || super::Is(rhs); \
} \
 \
void Serialization(json_t& json) override; \
void Deserialization(const json_t& json) override; \
 \
enum AA_PIDXs \
{ \
    PIDX_COUNT = 0 \
}; \

