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

#define EPI_GENHIDDEN_Inner() \
public: \
using super = Object; \
 \
static MetaClass EmitMetaClass(); \
 \
const MetaClass& GetMetaClass() const override \
{ \
    super::GetMetaClass(); \
    return ClassRegistry_GetMetaClass<Inner>(); \
} \
 \
epiBool Is(MetaTypeID rhs) const override \
{ \
    return rhs == Inner::TypeID || super::Is(rhs); \
} \
 \
void Serialization(json_t& json) override; \
void Deserialization(const json_t& json) override; \
 \
enum Inner_PIDXs \
{ \
    PIDX_COUNT = 0 \
}; \


#define EPI_GENHIDDEN_B() \
public: \
using super = A; \
 \
static MetaClass EmitMetaClass(); \
 \
const MetaClass& GetMetaClass() const override \
{ \
    super::GetMetaClass(); \
    return ClassRegistry_GetMetaClass<B>(); \
} \
 \
epiBool Is(MetaTypeID rhs) const override \
{ \
    return rhs == B::TypeID || super::Is(rhs); \
} \
 \
void Serialization(json_t& json) override; \
void Deserialization(const json_t& json) override; \
 \
inline const epiPtrArray<B>& GetBBs() const { return m_BBs; } \
inline epiPtrArray<B>& GetBBs() { return m_BBs; } \
inline void SetBBs(const epiPtrArray<B>& value) { m_BBs = value; } \
inline epiSize_t GetSize() const { return m_Size; } \
inline void SetSize(epiSize_t value) { m_Size = value; } \
inline const B* GetSibling() const { return m_Sibling; } \
inline B* GetSibling() { return m_Sibling; } \
inline void SetSibling(B* value) { m_Sibling = value; } \
inline const epiFloat* GetNonSibling() const { return m_NonSibling; } \
inline epiFloat* GetNonSibling() { return m_NonSibling; } \
inline void SetNonSibling(epiFloat* value) { m_NonSibling = value; } \
inline Inner::E GetEnum0() const { return m_Enum0; } \
inline void SetEnum0(Inner::E value) { m_Enum0 = value; } \
inline Inner::E GetEnum1() const { return m_Enum1; } \
inline void SetEnum1(Inner::E value) { m_Enum1 = value; } \
inline E1 GetEnum2() const { return m_Enum2; } \
inline void SetEnum2(E1 value) { m_Enum2 = value; } \
E2 GetEnum3() const { return GetEnum3_Callback(); } \
void SetEnum3(E2 value) { SetEnum3_Callback(value); } \
inline const epiArray<Inner::E>& GetEnums0() const { return m_Enums0; } \
inline epiArray<Inner::E>& GetEnums0() { return m_Enums0; } \
inline void SetEnums0(const epiArray<Inner::E>& value) { m_Enums0 = value; } \
inline const epiArray<E0>& GetEnums1() const { return m_Enums1; } \
inline epiArray<E0>& GetEnums1() { return m_Enums1; } \
inline void SetEnums1(const epiArray<E0>& value) { m_Enums1 = value; } \
 \
enum B_PIDXs \
{ \
    PIDX_BBs = 0, \
    PIDX_Size = 1, \
    PIDX_Sibling = 2, \
    PIDX_NonSibling = 3, \
    PIDX_Enum0 = 4, \
    PIDX_Enum1 = 5, \
    PIDX_Enum2 = 6, \
    PIDX_Enum3 = 7, \
    PIDX_Enums0 = 8, \
    PIDX_Enums1 = 9, \
    PIDX_COUNT = 10 \
}; \
 \
private: \
E2 (B::*GetEnum3_FuncPtr)() const { &B::GetEnum3 }; \
void (B::*SetEnum3_FuncPtr)(E2) { &B::SetEnum3 }; \

