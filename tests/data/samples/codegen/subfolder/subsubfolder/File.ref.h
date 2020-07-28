#pragma once

EPI_GENREGION_BEGIN(include)
#include "codegen/subfolder/subsubfolder/File.hxx"
EPI_GENREGION_END(include)

EPI_NAMESPACE_BEGIN()

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
        PID_COUNT = 4
    };

protected:
    epiPtrArray<B> m_BBs;
    epiSize_t m_Size{13};
    B* m_Sibling{nullptr};
    epiFloat* m_NonSibling{nullptr};

EPI_GENREGION_END(B)
};

EPI_NAMESPACE_END()
