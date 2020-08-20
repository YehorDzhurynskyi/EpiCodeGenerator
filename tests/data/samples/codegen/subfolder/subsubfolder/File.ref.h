#pragma once

EPI_GENREGION_BEGIN(include)
#include "codegen/subfolder/subsubfolder/File.hxx"
EPI_GENREGION_END(include)

EPI_NAMESPACE_BEGIN()

class Inner : public Object
{
EPI_GENREGION_BEGIN(Inner)

EPI_GENHIDDEN_Inner()

public:
    constexpr static MetaTypeID TypeID{0xacf024cd};

    enum Inner_PIDs
    {
        PID_COUNT = 0
    };

EPI_GENREGION_END(Inner)
};

class B : public A
{
EPI_GENREGION_BEGIN(B)

EPI_GENHIDDEN_B()

public:
    constexpr static MetaTypeID TypeID{0x4ad0cf31};

    enum B_PIDs
    {
        PID_BBs = 0x871c8dbd,
        PID_Size = 0x57f28b54,
        PID_Sibling = 0x5d065c2d,
        PID_NonSibling = 0xe52820ca,
        PID_Enum0 = 0x29782fe9,
        PID_Enum1 = 0x5e7f1f7f,
        PID_Enum2 = 0xc7764ec5,
        PID_Enums0 = 0xf670e114,
        PID_Enums1 = 0x8177d182,
        PID_COUNT = 9
    };

protected:
    E1 GetEnum2_Callback() const;
    void SetEnum2_Callback(E1 value);

protected:
    epiPtrArray<B> m_BBs;
    epiSize_t m_Size{13};
    B* m_Sibling{nullptr};
    epiFloat* m_NonSibling{nullptr};
    Inner::E m_Enum0;
    Inner::E m_Enum1{Inner::E::Value1};
    epiArray<Inner::E> m_Enums0;
    epiArray<E0> m_Enums1;

EPI_GENREGION_END(B)
};

EPI_NAMESPACE_END()
