// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


#include "stdafx.h"
#include "domcomment.h"

// Dispatch interfaces referenced by this interface
#include "DOMNode.h"
#include "DOMNodeList.h"
#include "DOMNamedNodeMap.h"
#include "DOMDocument.h"


/////////////////////////////////////////////////////////////////////////////
// CDOMComment properties

/////////////////////////////////////////////////////////////////////////////
// CDOMComment operations

CString CDOMComment::GetNodeName()
{
	CString result;
	InvokeHelper(0x2, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

VARIANT CDOMComment::GetNodeValue()
{
	VARIANT result;
	InvokeHelper(0x3, DISPATCH_PROPERTYGET, VT_VARIANT, (void*)&result, NULL);
	return result;
}

void CDOMComment::SetNodeValue(const VARIANT& newValue)
{
	static BYTE parms[] =
		VTS_VARIANT;
	InvokeHelper(0x3, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 &newValue);
}

long CDOMComment::GetNodeType()
{
	long result;
	InvokeHelper(0x4, DISPATCH_PROPERTYGET, VT_I4, (void*)&result, NULL);
	return result;
}

CDOMNode CDOMComment::GetParentNode()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x6, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNodeList CDOMComment::GetChildNodes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x7, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNodeList(pDispatch);
}

CDOMNode CDOMComment::GetFirstChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x8, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::GetLastChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x9, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::GetPreviousSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xa, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::GetNextSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xb, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNamedNodeMap CDOMComment::GetAttributes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xc, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNamedNodeMap(pDispatch);
}

CDOMNode CDOMComment::insertBefore(LPDISPATCH newChild, const VARIANT& refChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_VARIANT;
	InvokeHelper(0xd, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, &refChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::replaceChild(LPDISPATCH newChild, LPDISPATCH oldChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_DISPATCH;
	InvokeHelper(0xe, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, oldChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::removeChild(LPDISPATCH childNode)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0xf, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		childNode);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMComment::appendChild(LPDISPATCH newChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x10, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild);
	return CDOMNode(pDispatch);
}

BOOL CDOMComment::hasChildNodes()
{
	BOOL result;
	InvokeHelper(0x11, DISPATCH_METHOD, VT_BOOL, (void*)&result, NULL);
	return result;
}

CDOMDocument CDOMComment::GetOwnerDocument()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x12, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMDocument(pDispatch);
}

CDOMNode CDOMComment::cloneNode(BOOL deep)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BOOL;
	InvokeHelper(0x13, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		deep);
	return CDOMNode(pDispatch);
}

CString CDOMComment::GetData()
{
	CString result;
	InvokeHelper(0x0, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

void CDOMComment::SetData(LPCTSTR lpszNewValue)
{
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x0, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 lpszNewValue);
}

long CDOMComment::GetLength()
{
	long result;
	InvokeHelper(0x82, DISPATCH_PROPERTYGET, VT_I4, (void*)&result, NULL);
	return result;
}

CString CDOMComment::substringData(long offset, long count)
{
	CString result;
	static BYTE parms[] =
		VTS_I4 VTS_I4;
	InvokeHelper(0x83, DISPATCH_METHOD, VT_BSTR, (void*)&result, parms,
		offset, count);
	return result;
}

void CDOMComment::appendData(LPCTSTR data)
{
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x84, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 data);
}

void CDOMComment::insertData(long offset, LPCTSTR data)
{
	static BYTE parms[] =
		VTS_I4 VTS_BSTR;
	InvokeHelper(0x85, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 offset, data);
}

void CDOMComment::deleteData(long offset, long count)
{
	static BYTE parms[] =
		VTS_I4 VTS_I4;
	InvokeHelper(0x86, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 offset, count);
}

void CDOMComment::replaceData(long offset, long count, LPCTSTR data)
{
	static BYTE parms[] =
		VTS_I4 VTS_I4 VTS_BSTR;
	InvokeHelper(0x87, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 offset, count, data);
}
