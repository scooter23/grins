#if !defined(AFX_DOMNODE_H__76603FFC_3D7B_427D_BABC_7708D3850EA0__INCLUDED_)
#define AFX_DOMNODE_H__76603FFC_3D7B_427D_BABC_7708D3850EA0__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// Machine generated IDispatch wrapper class(es) created by Microsoft Visual C++

// NOTE: Do not modify the contents of this file.  If this class is regenerated by
//  Microsoft Visual C++, your modifications will be overwritten.


// Dispatch interfaces referenced by this interface
class CDOMNodeList;
class CDOMNamedNodeMap;
class CDOMDocument;

/////////////////////////////////////////////////////////////////////////////
// CDOMNode wrapper class

class CDOMNode : public COleDispatchDriver
{
public:
	CDOMNode() {}		// Calls COleDispatchDriver default constructor
	CDOMNode(LPDISPATCH pDispatch) : COleDispatchDriver(pDispatch) {}
	CDOMNode(const CDOMNode& dispatchSrc) : COleDispatchDriver(dispatchSrc) {}

// Attributes
public:

// Operations
public:
	CString GetNodeName();
	VARIANT GetNodeValue();
	void SetNodeValue(const VARIANT& newValue);
	long GetNodeType();
	CDOMNode GetParentNode();
	CDOMNodeList GetChildNodes();
	CDOMNode GetFirstChild();
	CDOMNode GetLastChild();
	CDOMNode GetPreviousSibling();
	CDOMNode GetNextSibling();
	CDOMNamedNodeMap GetAttributes();
	CDOMNode insertBefore(LPDISPATCH newChild, const VARIANT& refChild);
	CDOMNode replaceChild(LPDISPATCH newChild, LPDISPATCH oldChild);
	CDOMNode removeChild(LPDISPATCH childNode);
	CDOMNode appendChild(LPDISPATCH newChild);
	BOOL hasChildNodes();
	CDOMDocument GetOwnerDocument();
	CDOMNode cloneNode(BOOL deep);
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_DOMNODE_H__76603FFC_3D7B_427D_BABC_7708D3850EA0__INCLUDED_)
