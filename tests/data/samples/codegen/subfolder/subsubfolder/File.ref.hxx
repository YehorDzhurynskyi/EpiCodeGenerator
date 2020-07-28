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
inline void SetBBs(const epiPtrArray<B>& value) { m_BBs = value; } \
inline epiSize_t GetSize() const { return m_Size; } \
inline void SetSize(epiSize_t value) { m_Size = value; } \
inline const B* GetSibling() const { return m_Sibling; } \
inline void SetSibling(B* value) { m_Sibling = value; } \
inline const epiFloat* GetNonSibling() const { return m_NonSibling; } \
inline void SetNonSibling(epiFloat* value) { m_NonSibling = value; } \
 \
enum B_PIDXs \
{ \
    PIDX_BBs = 0, \
    PIDX_Size = 1, \
    PIDX_Sibling = 2, \
    PIDX_NonSibling = 3, \
    PIDX_COUNT = 4 \
}; \

