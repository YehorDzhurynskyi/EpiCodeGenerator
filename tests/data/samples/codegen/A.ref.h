#pragma once

EPI_GENREGION_BEGIN(include)
#include "codegen/A.hxx"
EPI_GENREGION_END(include)

EPI_NAMESPACE_BEGIN()

class A : public Object
{
EPI_GENREGION_BEGIN(A)

EPI_GENHIDDEN_A()

public:
    constexpr static MetaTypeID TypeID{0xd3d99e8b};

    enum A_PIDs
    {
        PID_PName = 0x216436f2,
        PID_Text = 0x9bb908f9,
        PID_VirtualFloats = 0x8da39f42,
        PID_VirtualFloats1 = 0x1b836c94,
        PID_VirtualFloat = 0xa4f8c74a,
        PID_ProjMat = 0xe4669ca8,
        PID_Value1 = 0xa5d9696c,
        PID_Value2 = 0x3cd038d6,
        PID_Value3 = 0x4bd70840,
        PID_Value4 = 0xd5b39de3,
        PID_NonSiblingVirtual = 0x80d41417,
        PID_COUNT = 11
    };

protected:
    const epiArray<epiFloat>& GetVirtualFloats_Callback() const;
    const epiArray<epiFloat>& GetVirtualFloats1_Callback() const;
    epiFloat GetVirtualFloat_Callback() const;
    void SetVirtualFloat_Callback(epiFloat value);
    epiMat4x4f GetProjMat_Callback() const;
    void SetProjMat_Callback(const epiMat4x4f& value);
    const epiFloat* GetNonSiblingVirtual_Callback() const;
    void SetNonSiblingVirtual_Callback(epiFloat* value);

protected:
    epiS32 m_PName{0};
    epiString m_Text{"my text"};
    epiDouble m_Value1{3.0};
    epiDouble m_Value2{5.0};
    epiDouble m_Value3{2.535};
    epiU32 m_Value4{0};

EPI_GENREGION_END(A)
};

class AA : public A
{
EPI_GENREGION_BEGIN(AA)

EPI_GENHIDDEN_AA()

public:
    constexpr static MetaTypeID TypeID{0xa9601dbd};

    enum AA_PIDs
    {
        PID_COUNT = 0
    };

EPI_GENREGION_END(AA)
};

EPI_NAMESPACE_END()
