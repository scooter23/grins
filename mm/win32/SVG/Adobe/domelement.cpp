// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


#include "stdafx.h"
#include "domelement.h"

// Dispatch interfaces referenced by this interface
#include "domnode.h"
#include "domnodelist.h"
#include "DOMNamedNodeMap.h"
#include "DOMDocument.h"
#include "DOMAttribute.h"


/////////////////////////////////////////////////////////////////////////////
// CDOMElement properties

/////////////////////////////////////////////////////////////////////////////
// CDOMElement operations

CString CDOMElement::GetNodeName()
{
	CString result;
	InvokeHelper(0x2, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

VARIANT CDOMElement::GetNodeValue()
{
	VARIANT result;
	InvokeHelper(0x3, DISPATCH_PROPERTYGET, VT_VARIANT, (void*)&result, NULL);
	return result;
}

void CDOMElement::SetNodeValue(const VARIANT& newValue)
{
	static BYTE parms[] =
		VTS_VARIANT;
	InvokeHelper(0x3, DISPATCH_PROPERTYPUT, VT_EMPTY, NULL, parms,
		 &newValue);
}

long CDOMElement::GetNodeType()
{
	long result;
	InvokeHelper(0x4, DISPATCH_PROPERTYGET, VT_I4, (void*)&result, NULL);
	return result;
}

CDOMNode CDOMElement::GetParentNode()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x6, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNodeList CDOMElement::GetChildNodes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x7, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNodeList(pDispatch);
}

CDOMNode CDOMElement::GetFirstChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x8, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::GetLastChild()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x9, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::GetPreviousSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xa, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::GetNextSibling()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xb, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNode(pDispatch);
}

CDOMNamedNodeMap CDOMElement::GetAttributes()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0xc, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMNamedNodeMap(pDispatch);
}

CDOMNode CDOMElement::insertBefore(LPDISPATCH newChild, const VARIANT& refChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_VARIANT;
	InvokeHelper(0xd, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, &refChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::replaceChild(LPDISPATCH newChild, LPDISPATCH oldChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH VTS_DISPATCH;
	InvokeHelper(0xe, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild, oldChild);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::removeChild(LPDISPATCH childNode)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0xf, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		childNode);
	return CDOMNode(pDispatch);
}

CDOMNode CDOMElement::appendChild(LPDISPATCH newChild)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x10, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		newChild);
	return CDOMNode(pDispatch);
}

BOOL CDOMElement::hasChildNodes()
{
	BOOL result;
	InvokeHelper(0x11, DISPATCH_METHOD, VT_BOOL, (void*)&result, NULL);
	return result;
}

CDOMDocument CDOMElement::GetOwnerDocument()
{
	LPDISPATCH pDispatch;
	InvokeHelper(0x12, DISPATCH_PROPERTYGET, VT_DISPATCH, (void*)&pDispatch, NULL);
	return CDOMDocument(pDispatch);
}

CDOMNode CDOMElement::cloneNode(BOOL deep)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BOOL;
	InvokeHelper(0x13, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		deep);
	return CDOMNode(pDispatch);
}

CString CDOMElement::GetTagName()
{
	CString result;
	InvokeHelper(0x62, DISPATCH_PROPERTYGET, VT_BSTR, (void*)&result, NULL);
	return result;
}

VARIANT CDOMElement::getAttribute(LPCTSTR name)
{
	VARIANT result;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x64, DISPATCH_METHOD, VT_VARIANT, (void*)&result, parms,
		name);
	return result;
}

void CDOMElement::setAttribute(LPCTSTR name, const VARIANT& value)
{
	static BYTE parms[] =
		VTS_BSTR VTS_VARIANT;
	InvokeHelper(0x65, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 name, &value);
}

void CDOMElement::removeAttribute(LPCTSTR name)
{
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x66, DISPATCH_METHOD, VT_EMPTY, NULL, parms,
		 name);
}

CDOMAttribute CDOMElement::getAttributeNode(LPCTSTR name)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x67, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		name);
	return CDOMAttribute(pDispatch);
}

CDOMAttribute CDOMElement::setAttributeNode(LPDISPATCH DOMAttribute)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x68, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		DOMAttribute);
	return CDOMAttribute(pDispatch);
}

CDOMAttribute CDOMElement::removeAttributeNode(LPDISPATCH DOMAttribute)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_DISPATCH;
	InvokeHelper(0x69, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		DOMAttribute);
	return CDOMAttribute(pDispatch);
}

CDOMNodeList CDOMElement::getElementsByTagName(LPCTSTR tagName)
{
	LPDISPATCH pDispatch;
	static BYTE parms[] =
		VTS_BSTR;
	InvokeHelper(0x6a, DISPATCH_METHOD, VT_DISPATCH, (void*)&pDispatch, parms,
		tagName);
	return CDOMNodeList(pDispatch);
}

void CDOMElement::normalize()
{
	InvokeHelper(0x6b, DISPATCH_METHOD, VT_EMPTY, NULL, NULL);
}