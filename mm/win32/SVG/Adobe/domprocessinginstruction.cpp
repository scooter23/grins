// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


#include "stdafx.h"
#include "domprocessinginstruction.h"

// Dispatch interfaces referenced by this interface
#include "domnode.h"
#include "domnodelist.h"
#include "domnamednodemap.h"
#include "domdocument.h"


/////////////////////////////////////////////////////////////////////////////
// CDOMProcessingInstruction properties

/////////////////////////////////////////////////////////////////////////////
// CDOMProcessingInstruction operations

CString CDOMProcessingInstruction::GetNodeName()
{
	CString result;
	InvokeHelper(0x2, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

VARIANT CDOMProcessingInstruction::GetNodeValue()
{
	VARIANT result;
	InvokeHelper(0x3, DISPATCH_PROPERTYGET, VT_VARIANT, (void*)&result, NULL);
	return result;
}

void CDOMProcessingInstruction::SetNodeValue(const VARIANT& newValue)
{
	static BYTE parms[] =
		VTS_VARIANT;
	InvokeHelper(0x3, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 &newValue);
}

long CDOMProcessingInstruction::GetNodeType()
{
	long result;
	InvokeHelper(0x4, DISPATCH_PROPERTYGET, VT_I4, (void*)&result, NULL);
	return result;
}

CDOMNode CDOMProcessingInstruction::GetParentNode()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x6, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNodeList CDOMProcessingInstruction::GetChildNodes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x7, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNodeList(pDispatch);
}

CDOMNode CDOMProcessingInstruction::GetFirstChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x8, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::GetLastChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x9, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::GetPreviousSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xa, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::GetNextSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xb, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNamedNodeMap CDOMProcessingInstruction::GetAttributes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xc, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNamedNodeMap(pDispatch);
}

CDOMNode CDOMProcessingInstruction::insertBefore(LPDISPATCH newChild, const VARIANT& refChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_VARIANT;
	InvokeHelper(0xd, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, &refChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::replaceChild(LPDISPATCH newChild, LPDISPATCH oldChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_DISPATCH;
	InvokeHelper(0xe, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, oldChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::removeChild(LPDISPATCH childNode)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0xf, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		childNode);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMProcessingInstruction::appendChild(LPDISPATCH newChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x10, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild);
	return CDOMNode(pDispatch);
}

BOOL CDOMProcessingInstruction::hasChildNodes()
{
	BOOL result;
	InvokeHelper(0x11, DISPATCH_METHOD, VT_BOOL, (void*)&result, NULL);
	return result;
}

CDOMDocument CDOMProcessingInstruction::GetOwnerDocument()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x12, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMDocument(pDispatch);
}

CDOMNode CDOMProcessingInstruction::cloneNode(BOOL deep)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BOOL;
	InvokeHelper(0x13, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		deep);
	return CDOMNode(pDispatch);
}

CString CDOMProcessingInstruction::GetTarget()
{
	CString result;
	InvokeHelper(0xe2, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

CString CDOMProcessingInstruction::GetData()
{
	CString result;
	InvokeHelper(0x0, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

void CDOMProcessingInstruction::SetData(LPCTSTR lpszNewValue)
{
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x0, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 lpszNewValue);
}
