#if !defined(AFX_DOMIMPLEMENTATION_H__C1150B23_3258_4EA5_9D63_0E24AB15883D__INCLUDED_)
#define AFX_DOMIMPLEMENTATION_H__C1150B23_3258_4EA5_9D63_0E24AB15883D__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.

/////////////////////////////////////////////////////////////////////////////
// CDOMImplementation wrapper class

class CDOMImplementation : public COleDispatchDriver
{
public:
	CDOMImplementation() {}		// Calls COleDispatchDriver default constructor
	CDOMImplementation(LPDISPATCH pDispatch) : COleDispatchDriver(pDispatch) {}
	CDOMImplementation(const CDOMImplementation& dispatchSrc) : COleDispatchDriver(dispatchSrc) {}

// Attributes
public:

// Operations
public:
	BOOL hasFeature(LPCTSTR feature, LPCTSTR version);
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_DOMIMPLEMENTATION_H__C1150B23_3258_4EA5_9D63_0E24AB15883D__INCLUDED_)