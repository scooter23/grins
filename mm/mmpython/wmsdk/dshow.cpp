/***********************************************************
Copyright 1991-1999 by Oratrix Development BV, Amsterdam, The Netherlands.

                        All Rights Reserved

******************************************************************/

#include "Python.h"

#include <streams.h>
#include <objbase.h>
#include <stdio.h>
#include <UUIDS.H> // CLSID_FilterGraph,...

#pragma comment (lib,"winmm.lib")
#pragma comment (lib,"amstrmid.lib")
#pragma comment (lib,"guids.lib")
#pragma comment (lib,"strmbase.lib")

#define  OATRUE (-1)
#define  OAFALSE (0)

#include <initguid.h>
DEFINE_GUID(IID_IRealConverter,
0xe8d61c44, 0xd313, 0x472a, 0x84, 0x68, 0x2b, 0x1e, 0xd5, 0xb0, 0x5c, 0xab);
struct IRealConverter : public IUnknown
	{
	virtual HRESULT __stdcall SetInterface(IUnknown *p,LPCOLESTR hint)=0;
	};

static PyObject *ErrorObject;

#define RELEASE(x) if(x) x->Release();x=NULL;

static void
seterror(const char *funcname, HRESULT hr)
{
	char* pszmsg;
	::FormatMessage( 
		 FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		 NULL,
		 hr,
		 MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		 (LPTSTR) &pszmsg,
		 0,
		 NULL 
		);
	PyErr_Format(ErrorObject, "%s failed, error = %s", funcname, pszmsg);
	LocalFree(pszmsg);
}


/* Declarations for objects of type GraphBuilder */

typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IGraphBuilder* pGraphBuilder;
} GraphBuilderObject;

staticforward PyTypeObject GraphBuilderType;

static GraphBuilderObject *
newGraphBuilderObject()
{
	GraphBuilderObject *self;

	self = PyObject_NEW(GraphBuilderObject, &GraphBuilderType);
	if (self == NULL)
		return NULL;
	self->pGraphBuilder = NULL;
	/* XXXX Add your own initializers here */
	return self;
}



typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IBaseFilter* pFilter;
} BaseFilterObject;

staticforward PyTypeObject BaseFilterType;

static BaseFilterObject *
newBaseFilterObject()
{
	BaseFilterObject *self;

	self = PyObject_NEW(BaseFilterObject, &BaseFilterType);
	if (self == NULL)
		return NULL;
	self->pFilter = NULL;
	/* XXXX Add your own initializers here */
	return self;
}



typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IPin* pPin;
} PinObject;

staticforward PyTypeObject PinType;

static PinObject *
newPinObject()
{
	PinObject *self;

	self = PyObject_NEW(PinObject, &PinType);
	if (self == NULL)
		return NULL;
	self->pPin = NULL;
	/* XXXX Add your own initializers here */
	return self;
}


typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IEnumPins* pPins;
} EnumPinsObject;

staticforward PyTypeObject EnumPinsType;

static EnumPinsObject *
newEnumPinsObject()
{
	EnumPinsObject *self;

	self = PyObject_NEW(EnumPinsObject, &EnumPinsType);
	if (self == NULL)
		return NULL;
	self->pPins = NULL;
	/* XXXX Add your own initializers here */
	return self;
}


typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IFileSinkFilter* pFilter;
} FileSinkFilterObject;

staticforward PyTypeObject FileSinkFilterType;


static FileSinkFilterObject *
newFileSinkFilterObject()
{
	FileSinkFilterObject *self;

	self = PyObject_NEW(FileSinkFilterObject, &FileSinkFilterType);
	if (self == NULL)
		return NULL;
	self->pFilter = NULL;
	/* XXXX Add your own initializers here */
	return self;
}

//
typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IMediaControl* pCtrl;
} MediaControlObject;

staticforward PyTypeObject MediaControlType;


static MediaControlObject *
newMediaControlObject()
{
	MediaControlObject *self;

	self = PyObject_NEW(MediaControlObject, &MediaControlType);
	if (self == NULL)
		return NULL;
	self->pCtrl = NULL;
	/* XXXX Add your own initializers here */
	return self;
}
//


//
typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IVideoWindow* pI;
} VideoWindowObject;

staticforward PyTypeObject VideoWindowType;


static VideoWindowObject *
newVideoWindowObject()
{
	VideoWindowObject *self;

	self = PyObject_NEW(VideoWindowObject, &VideoWindowType);
	if (self == NULL)
		return NULL;
	self->pI = NULL;
	/* XXXX Add your own initializers here */
	return self;
}
//

typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IMediaEventEx* pI;
} MediaEventExObject;

staticforward PyTypeObject MediaEventExType;


static MediaEventExObject *
newMediaEventExObject()
{
	MediaEventExObject *self;

	self = PyObject_NEW(MediaEventExObject, &MediaEventExType);
	if (self == NULL)
		return NULL;
	self->pI = NULL;
	/* XXXX Add your own initializers here */
	return self;
}

//
typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IRealConverter* pRealConverter;
} RealConverterObject;

staticforward PyTypeObject RealConverterType;

static RealConverterObject *
newRealConverterObject()
{
	RealConverterObject *self;

	self = PyObject_NEW(RealConverterObject, &RealConverterType);
	if (self == NULL)
		return NULL;
	self->pRealConverter = NULL;
	/* XXXX Add your own initializers here */
	return self;
}


typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IUnknown* pUk;
} UnknownObject;

staticforward PyTypeObject UnknownType;

static UnknownObject *
newUnknownObject()
{
	UnknownObject *self;

	self = PyObject_NEW(UnknownObject, &UnknownType);
	if (self == NULL)
		return NULL;
	self->pUk = NULL;
	/* XXXX Add your own initializers here */
	return self;
}


typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IMediaPosition* pI;
} MediaPositionObject;

staticforward PyTypeObject MediaPositionType;

static MediaPositionObject *
newMediaPositionObject()
{
	MediaPositionObject *self;

	self = PyObject_NEW(MediaPositionObject, &MediaPositionType);
	if (self == NULL)
		return NULL;
	self->pI = NULL;
	/* XXXX Add your own initializers here */
	return self;
}

 
typedef struct {
	PyObject_HEAD
	/* XXXX Add your own stuff here */
	IEnumFilters* pI;
} EnumFiltersObject;

staticforward PyTypeObject EnumFiltersType;

static EnumFiltersObject *
newEnumFiltersObject()
{
	EnumFiltersObject *self;

	self = PyObject_NEW(EnumFiltersObject, &EnumFiltersType);
	if (self == NULL)
		return NULL;
	self->pI = NULL;
	/* XXXX Add your own initializers here */
	return self;
}

////////////////////////////////////////////////////

static char GraphBuilder_AddSourceFilter__doc__[] =
""
;


static PyObject *
GraphBuilder_AddSourceFilter(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	char *pszFile;
	BaseFilterObject *obj;
	if (!PyArg_ParseTuple(args, "s", &pszFile))
		return NULL;
	obj = newBaseFilterObject();
	WCHAR wPath[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,pszFile,-1,wPath,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->AddSourceFilter(wPath,L"File reader",&obj->pFilter);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_AddSourceFilter", res);
		obj->pFilter=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}

static char GraphBuilder_AddFilter__doc__[] =
""
;

static PyObject *
GraphBuilder_AddFilter(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	char *psz;
	BaseFilterObject *obj;
	if (!PyArg_ParseTuple(args, "Os", &obj, &psz))
		return NULL;

	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,psz,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->AddFilter(obj->pFilter,wsz);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_AddFilter", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}


static char GraphBuilder_EnumFilters__doc__[] =
""
;

static PyObject *
GraphBuilder_EnumFilters(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	EnumFiltersObject *obj = newEnumFiltersObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->EnumFilters(&obj->pI);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_EnumPins", res);
		Py_DECREF(obj);
		obj->pI=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}


static char GraphBuilder_Render__doc__[] =
""
;

static PyObject *
GraphBuilder_Render(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	PinObject *obj;
	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->Render(obj->pPin);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_Render", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char GraphBuilder_Connect__doc__[] =
""
;

static PyObject *
GraphBuilder_Connect(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	PinObject *pinOut,*pinIn;
	if (!PyArg_ParseTuple(args, "OO", &pinOut,&pinIn))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->Connect(pinOut->pPin,pinIn->pPin);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_Connect", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}



static char GraphBuilder_QueryIMediaControl__doc__[] =
""
;

static PyObject *
GraphBuilder_QueryIMediaControl(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	MediaControlObject *obj = newMediaControlObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->QueryInterface(IID_IMediaControl, (void **) &obj->pCtrl);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_QueryIMediaControl", res);
		obj->pCtrl=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}


static char GraphBuilder_QueryIMediaPosition__doc__[] =
""
;
static PyObject *
GraphBuilder_QueryIMediaPosition(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	MediaPositionObject *obj = newMediaPositionObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->QueryInterface(IID_IMediaPosition, (void **) &obj->pI);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_QueryIMediaPosition", res);
		obj->pI=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}

static char GraphBuilder_QueryIVideoWindow__doc__[] =
""
;
static PyObject *
GraphBuilder_QueryIVideoWindow(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	VideoWindowObject *obj = newVideoWindowObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->QueryInterface(IID_IVideoWindow, (void **) &obj->pI);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_QueryIVideoWindow", res);
		obj->pI=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}


static char GraphBuilder_QueryIMediaEventEx__doc__[] =
""
;
static PyObject *
GraphBuilder_QueryIMediaEventEx(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	MediaEventExObject *obj = newMediaEventExObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->QueryInterface(IID_IMediaEventEx, (void **) &obj->pI);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_QueryIMediaEventEx", res);
		obj->pI=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}
	
	
static char GraphBuilder_WaitForCompletion__doc__[] =
""
;

static PyObject *
GraphBuilder_WaitForCompletion(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	long msTimeout=INFINITE;
	if (!PyArg_ParseTuple(args, "|l",&msTimeout))
		return NULL;

    IMediaEventEx *pME;
	res=self->pGraphBuilder->QueryInterface(IID_IMediaEventEx, (void **) &pME);
	if (FAILED(res)) {
		seterror("GraphBuilder_WaitForCompletion", res);
		return NULL;
	}
	long evCode=0;
	Py_BEGIN_ALLOW_THREADS
	res=pME->WaitForCompletion(msTimeout,&evCode);
	Py_END_ALLOW_THREADS
	pME->Release();
	
	// res is S_OK or E_ABORT 
	// evCode is:
	//		EC_COMPLETE  Operation completed.  
	//		EC_ERRORABORT  Error. Playback can't continue.  
	//		EC_USERABORT  User terminated the operation.  
	//		Zero Operation has not completed.  
	int ret=(res==S_OK && evCode!=0)?1:0; 
	return Py_BuildValue("i", ret);
}


//////////
// Convert some std file references to the windows media form
// 1. file:///D|/<filepath>
// 2. file:/D|/<filepath>
// 3. file:////<filepath>
static void ConvToWindowsMediaUrl(char *pszUrl)
	{
	int l = strlen(pszUrl);
	if(strstr(pszUrl,"file:///")==pszUrl && l>10 && pszUrl[9]=='|')
		{
		pszUrl[0]=pszUrl[8];
		pszUrl[1]=':';
		char *ps = pszUrl+10;
		char *pd = pszUrl+2;
		while(*ps){
			if(*ps=='/'){*pd++='\\';ps++;}
			else {*pd++ = *ps++;}
			}
		*pd='\0';
		}
	else if(strstr(pszUrl,"file:/")==pszUrl && l>8 && pszUrl[7]=='|')
		{
		pszUrl[0]=pszUrl[6];
		pszUrl[1]=':';
		char *ps = pszUrl+8;
		char *pd = pszUrl+2;
		while(*ps){
			if(*ps=='/'){*pd++='\\';ps++;}
			else {*pd++ = *ps++;}
			}
		*pd='\0';
		}
	else if(strstr(pszUrl,"file:////")==pszUrl && l>9 && strstr(pszUrl,"|")==NULL) // UNC
		{
		pszUrl[0]='\\';pszUrl[1]='\\';pszUrl[2]='\\';pszUrl[3]='\\';
		char *ps = pszUrl+9;
		char *pd = pszUrl+4;
		while(*ps){
			if(*ps=='/'){*pd++='\\';ps++;}
			else {*pd++ = *ps++;}
			}
		*pd='\0';
		}
	//else no change
	}

//////////
static char GraphBuilder_RenderFile__doc__[] =
""
;

static PyObject *
GraphBuilder_RenderFile(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	char *psz;
	if (!PyArg_ParseTuple(args, "s", &psz))
		return NULL;
	char buf[MAX_PATH];
	strcpy(buf,psz);
	ConvToWindowsMediaUrl(buf);
	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,buf,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->RenderFile(wsz,NULL);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_RenderFile", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}



static char GraphBuilder_FindFilterByName__doc__[] =
""
;

static PyObject *
GraphBuilder_FindFilterByName(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	char *psz;
	BaseFilterObject *obj;
	if (!PyArg_ParseTuple(args, "s", &psz))
		return NULL;
	obj = newBaseFilterObject();
	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,psz,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->FindFilterByName(wsz,&obj->pFilter);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_AddSourceFilter", res);
		obj->pFilter=NULL;
		Py_DECREF(obj);
		return NULL;
	}
	return (PyObject *) obj;
}



static char GraphBuilder_RemoveFilter__doc__[] =
""
;

static PyObject *
GraphBuilder_RemoveFilter(GraphBuilderObject *self, PyObject *args)
{
	HRESULT res;
	BaseFilterObject *obj;
	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pGraphBuilder->RemoveFilter(obj->pFilter);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("GraphBuilder_RemoveFilter", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char GraphBuilder_Release__doc__[] =
""
;

static PyObject *
GraphBuilder_Release(GraphBuilderObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	RELEASE(self->pGraphBuilder);
	Py_END_ALLOW_THREADS
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef GraphBuilder_methods[] = {
	{"AddSourceFilter", (PyCFunction)GraphBuilder_AddSourceFilter, METH_VARARGS, GraphBuilder_AddSourceFilter__doc__},
	{"AddFilter", (PyCFunction)GraphBuilder_AddFilter, METH_VARARGS, GraphBuilder_AddFilter__doc__},
	{"Render", (PyCFunction)GraphBuilder_Render, METH_VARARGS, GraphBuilder_Render__doc__},
	{"QueryIMediaControl", (PyCFunction)GraphBuilder_QueryIMediaControl, METH_VARARGS, GraphBuilder_QueryIMediaControl__doc__},
	{"WaitForCompletion", (PyCFunction)GraphBuilder_WaitForCompletion, METH_VARARGS, GraphBuilder_WaitForCompletion__doc__},
	{"RenderFile", (PyCFunction)GraphBuilder_RenderFile, METH_VARARGS, GraphBuilder_RenderFile__doc__},
	{"FindFilterByName", (PyCFunction)GraphBuilder_FindFilterByName, METH_VARARGS, GraphBuilder_FindFilterByName__doc__},
	{"RemoveFilter", (PyCFunction)GraphBuilder_RemoveFilter, METH_VARARGS, GraphBuilder_RemoveFilter__doc__},
	{"QueryIMediaPosition", (PyCFunction)GraphBuilder_QueryIMediaPosition, METH_VARARGS, GraphBuilder_QueryIMediaPosition__doc__},
	{"QueryIVideoWindow", (PyCFunction)GraphBuilder_QueryIVideoWindow, METH_VARARGS, GraphBuilder_QueryIVideoWindow__doc__},
	{"QueryIMediaEventEx", (PyCFunction)GraphBuilder_QueryIMediaEventEx, METH_VARARGS, GraphBuilder_QueryIMediaEventEx__doc__},
	{"EnumFilters", (PyCFunction)GraphBuilder_EnumFilters, METH_VARARGS, GraphBuilder_EnumFilters__doc__},
	{"Connect", (PyCFunction)GraphBuilder_Connect, METH_VARARGS, GraphBuilder_Connect__doc__},
	{"Release", (PyCFunction)GraphBuilder_Release, METH_VARARGS, GraphBuilder_Release__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


static void
GraphBuilder_dealloc(GraphBuilderObject *self)
{
	/* XXXX Add your own cleanup code here */
	Py_BEGIN_ALLOW_THREADS
	RELEASE(self->pGraphBuilder);
	Py_END_ALLOW_THREADS
	PyMem_DEL(self);
}

static PyObject *
GraphBuilder_getattr(GraphBuilderObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(GraphBuilder_methods, (PyObject *)self, name);
}

static char GraphBuilderType__doc__[] =
"GraphBuilder"
;

static PyTypeObject GraphBuilderType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"GraphBuilder",			/*tp_name*/
	sizeof(GraphBuilderObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)GraphBuilder_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)GraphBuilder_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	GraphBuilderType__doc__ /* Documentation string */
};

// End of code for GraphBuilder object 
/////////////////////////////////////////////////////////////


static char BaseFilter_FindPin__doc__[] =
""
;

static PyObject *
BaseFilter_FindPin(BaseFilterObject *self, PyObject *args)
{
	HRESULT res;
	char *psz;
	if (!PyArg_ParseTuple(args, "s", &psz))
		return NULL;
	PinObject *obj = newPinObject();
	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,psz,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->FindPin(wsz,&obj->pPin);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("BaseFilter_FindPin", res);
		Py_DECREF(obj);
		obj->pPin=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}


static char BaseFilter_QueryIFileSinkFilter__doc__[] =
""
;

static PyObject *
BaseFilter_QueryIFileSinkFilter(BaseFilterObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	FileSinkFilterObject *obj = newFileSinkFilterObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->QueryInterface(IID_IFileSinkFilter,(void**)&obj->pFilter);;
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("BaseFilter_QueryIFileSinkFilter", res);
		Py_DECREF(obj);
		obj->pFilter=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}

static char BaseFilter_QueryFilterName__doc__[] =
""
;

static PyObject *
BaseFilter_QueryFilterName(BaseFilterObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	FILTER_INFO fi;
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->QueryFilterInfo(&fi);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("BaseFilter_QueryFilterName", res);
		return NULL;
	}
	char buf[256];
	WideCharToMultiByte(CP_ACP,0,fi.achName,-1,buf,256,NULL,NULL);		
	return Py_BuildValue("s",buf);
}

static char BaseFilter_QueryIRealConverter__doc__[] =
""
;

static PyObject *
BaseFilter_QueryIRealConverter(BaseFilterObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	RealConverterObject *obj = newRealConverterObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->QueryInterface(IID_IRealConverter,(void**)&obj->pRealConverter);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("BaseFilter_QueryIRealConverter", res);
		Py_DECREF(obj);
		obj->pRealConverter=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}

static char BaseFilter_EnumPins__doc__[] =
""
;

static PyObject *
BaseFilter_EnumPins(BaseFilterObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	EnumPinsObject *obj = newEnumPinsObject();
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->EnumPins(&obj->pPins);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("BaseFilter_EnumPins", res);
		Py_DECREF(obj);
		obj->pPins=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}

static struct PyMethodDef BaseFilter_methods[] = {
	{"FindPin", (PyCFunction)BaseFilter_FindPin, METH_VARARGS, BaseFilter_FindPin__doc__},
	{"QueryIFileSinkFilter", (PyCFunction)BaseFilter_QueryIFileSinkFilter, METH_VARARGS, BaseFilter_QueryIFileSinkFilter__doc__},
	{"QueryIRealConverter", (PyCFunction)BaseFilter_QueryIRealConverter, METH_VARARGS, BaseFilter_QueryIRealConverter__doc__},
	{"QueryFilterName", (PyCFunction)BaseFilter_QueryFilterName, METH_VARARGS, BaseFilter_QueryFilterName__doc__},
	{"EnumPins", (PyCFunction)BaseFilter_EnumPins, METH_VARARGS, BaseFilter_EnumPins__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
BaseFilter_dealloc(BaseFilterObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pFilter);
	PyMem_DEL(self);
}

static PyObject *
BaseFilter_getattr(BaseFilterObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(BaseFilter_methods, (PyObject *)self, name);
}

static char BaseFilterType__doc__[] =
""
;

static PyTypeObject BaseFilterType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"BaseFilter",			/*tp_name*/
	sizeof(BaseFilterObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)BaseFilter_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)BaseFilter_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	BaseFilterType__doc__ /* Documentation string */
};

// End of code for BaseFilter object 
////////////////////////////////////////////

static char Pin_ConnectedTo__doc__[] =
""
;

static PyObject *
Pin_ConnectedTo(PinObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	PinObject *obj = newPinObject();
	Py_BEGIN_ALLOW_THREADS
	res=self->pPin->ConnectedTo(&obj->pPin);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("Pin_ConnectedTo", res);
		Py_DECREF(obj);
		obj->pPin=NULL;
		return NULL;
	}
	return (PyObject *) obj;
}


static struct PyMethodDef Pin_methods[] = {
	{"ConnectedTo", (PyCFunction)Pin_ConnectedTo, METH_VARARGS, Pin_ConnectedTo__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
Pin_dealloc(PinObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pPin);
	PyMem_DEL(self);
}

static PyObject *
Pin_getattr(PinObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(Pin_methods, (PyObject *)self, name);
}

static char PinType__doc__[] =
""
;

static PyTypeObject PinType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"Pin",			/*tp_name*/
	sizeof(PinObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)Pin_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)Pin_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	PinType__doc__ /* Documentation string */
};

// End of code for Pin object 
////////////////////////////////////////////

/////////////////////////////////////////////
// FileSinkFilter


static char FileSinkFilter_SetFileName__doc__[] =
""
;

static PyObject *
FileSinkFilter_SetFileName(FileSinkFilterObject *self, PyObject *args)
{
	HRESULT res;
	char *psz;
	AM_MEDIA_TYPE *pmt=NULL;
	if (!PyArg_ParseTuple(args, "s", &psz))
		return NULL;
	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,psz,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	res = self->pFilter->SetFileName(wsz,pmt);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("FileSinkFilter_SetFileName", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef FileSinkFilter_methods[] = {
	{"SetFileName", (PyCFunction)FileSinkFilter_SetFileName, METH_VARARGS, FileSinkFilter_SetFileName__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
FileSinkFilter_dealloc(FileSinkFilterObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pFilter);
	PyMem_DEL(self);
}

static PyObject *
FileSinkFilter_getattr(FileSinkFilterObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(FileSinkFilter_methods, (PyObject *)self, name);
}

static char FileSinkFilterType__doc__[] =
""
;

static PyTypeObject FileSinkFilterType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"FileSinkFilter",			/*tp_name*/
	sizeof(FileSinkFilterObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)FileSinkFilter_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)FileSinkFilter_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	FileSinkFilterType__doc__ /* Documentation string */
};

// End of FileSinkFilter
////////////////////////////////////////////

/////////////////////////////////////////////
// MediaControl


static char MediaControl_Run__doc__[] =
""
;

static PyObject *
MediaControl_Run(MediaControlObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pCtrl->Run();
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaControl_Run", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char MediaControl_Stop__doc__[] =
""
;

static PyObject *
MediaControl_Stop(MediaControlObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pCtrl->Stop();
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaControl_Stop", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char MediaControl_Pause__doc__[] =
""
;

static PyObject *
MediaControl_Pause(MediaControlObject *self, PyObject *args)
{
	HRESULT res;
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pCtrl->Pause();
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaControl_Pause", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef MediaControl_methods[] = {
	{"Run", (PyCFunction)MediaControl_Run, METH_VARARGS, MediaControl_Run__doc__},
	{"Stop", (PyCFunction)MediaControl_Stop, METH_VARARGS, MediaControl_Stop__doc__},
	{"Pause", (PyCFunction)MediaControl_Pause, METH_VARARGS, MediaControl_Pause__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
MediaControl_dealloc(MediaControlObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pCtrl);
	PyMem_DEL(self);
}

static PyObject *
MediaControl_getattr(MediaControlObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(MediaControl_methods, (PyObject *)self, name);
}

static char MediaControlType__doc__[] =
""
;

static PyTypeObject MediaControlType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"MediaControl",			/*tp_name*/
	sizeof(MediaControlObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)MediaControl_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)MediaControl_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	MediaControlType__doc__ /* Documentation string */
};

// End of MediaControl
////////////////////////////////////////////

////////////////////////////////////////////
// EnumPins object 


static char EnumPins_Next__doc__[] =
""
;

static PyObject *
EnumPins_Next(EnumPinsObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	PinObject *obj = newPinObject();
	ULONG fetched=0;
	HRESULT res ;
	Py_BEGIN_ALLOW_THREADS
	res = self->pPins->Next(1,&obj->pPin,&fetched);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("EnumPins_Next", res);
		Py_DECREF(obj);
		obj->pPin=NULL;
		return NULL;
	}
	if(fetched==1)
		return (PyObject *) obj;
	Py_DECREF(obj);
	obj->pPin=NULL;
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef EnumPins_methods[] = {
	{"Next", (PyCFunction)EnumPins_Next, METH_VARARGS, EnumPins_Next__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
EnumPins_dealloc(EnumPinsObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pPins);
	PyMem_DEL(self);
}

static PyObject *
EnumPins_getattr(EnumPinsObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(EnumPins_methods, (PyObject *)self, name);
}

static char EnumPinsType__doc__[] =
""
;

static PyTypeObject EnumPinsType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"EnumPins",			/*tp_name*/
	sizeof(EnumPinsObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)EnumPins_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)EnumPins_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	EnumPinsType__doc__ /* Documentation string */
};

// End of code for EnumPins object 
////////////////////////////////////////////

////////////////////////////////////////////
// EnumFilters object 


static char EnumFilters_Next__doc__[] =
""
;

static PyObject *
EnumFilters_Next(EnumFiltersObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	BaseFilterObject *obj = newBaseFilterObject();
	ULONG fetched=0;
	HRESULT res;
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->Next(1,&obj->pFilter,&fetched);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("EnumFilters_Next", res);
		Py_DECREF(obj);
		obj->pFilter=NULL;
		return NULL;
	}
	if(fetched==1)
		return (PyObject*) obj;
	Py_DECREF(obj);
	obj->pFilter=NULL;
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef EnumFilters_methods[] = {
	{"Next", (PyCFunction)EnumFilters_Next, METH_VARARGS, EnumFilters_Next__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
EnumFilters_dealloc(EnumFiltersObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pI);
	PyMem_DEL(self);
}

static PyObject *
EnumFilters_getattr(EnumFiltersObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(EnumFilters_methods, (PyObject *)self, name);
}

static char EnumFiltersType__doc__[] =
""
;

static PyTypeObject EnumFiltersType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"EnumFilters",			/*tp_name*/
	sizeof(EnumFiltersObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)EnumFilters_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)EnumFilters_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	EnumFiltersType__doc__ /* Documentation string */
};

// End of code for EnumFilters object 
////////////////////////////////////////////

/////////////////////////////////////////////
// VideoWindow


static char VideoWindow_SetOwner__doc__[] =
""
;

static PyObject *
VideoWindow_SetOwner(VideoWindowObject *self, PyObject *args)
{
	HRESULT res;
	HWND hWnd;
	if (!PyArg_ParseTuple(args, "i",&hWnd))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	// temp batch intil split
	res = self->pI->put_Owner((OAHWND)hWnd);
	res = self->pI->put_MessageDrain((OAHWND)hWnd);
	res = self->pI->put_WindowStyle(WS_CHILD|WS_CLIPSIBLINGS|WS_CLIPCHILDREN);
	res = self->pI->put_AutoShow(OAFALSE);
	res = self->pI->SetWindowForeground(OAFALSE);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("VideoWindow_SetOwner", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}


static char VideoWindow_SetWindowPosition__doc__[] =
""
;

static PyObject *
VideoWindow_SetWindowPosition(VideoWindowObject *self, PyObject *args)
{
	HRESULT res;
	long x,y,w,h;
	if (!PyArg_ParseTuple(args,"(llll):SetWindowPosition", &x,&y,&w,&h))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->SetWindowPosition(x,y,w,h);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("VideoWindow_SetWindowPosition", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}


static char VideoWindow_GetWindowPosition__doc__[] =
""
;

static PyObject *
VideoWindow_GetWindowPosition(VideoWindowObject *self, PyObject *args)
{
	HRESULT res;
	long x=0,y=0,w=0,h=0;
	if (!PyArg_ParseTuple(args,""))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->GetWindowPosition(&x,&y,&w,&h);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("VideoWindow_GetWindowPosition", res);
		return NULL;
	}
	// Temp fix. We must find a better way
	long dh=GetSystemMetrics(SM_CYCAPTION)+2*GetSystemMetrics(SM_CYFRAME);
	long dw=2*GetSystemMetrics(SM_CXFRAME);
	return Py_BuildValue("(llll)",x,y,(w>0?w-dw:0),(h>0?h-dh:0));
}



static char VideoWindow_SetVisible__doc__[] =
""
;

static PyObject *
VideoWindow_SetVisible(VideoWindowObject *self, PyObject *args)
{
	HRESULT res;
	int flag; 
	if(!PyArg_ParseTuple(args,"i",&flag))
		return NULL;
	long visible=flag?-1:0; // OATRUE (-1),OAFALSE (0)	
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->put_Visible(visible);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("VideoWindow_SetVisible", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef VideoWindow_methods[] = {
	{"SetOwner", (PyCFunction)VideoWindow_SetOwner, METH_VARARGS, VideoWindow_SetOwner__doc__},
	{"SetWindowPosition", (PyCFunction)VideoWindow_SetWindowPosition, METH_VARARGS, VideoWindow_SetWindowPosition__doc__},
	{"GetWindowPosition", (PyCFunction)VideoWindow_GetWindowPosition, METH_VARARGS, VideoWindow_GetWindowPosition__doc__},
	{"SetVisible", (PyCFunction)VideoWindow_SetVisible, METH_VARARGS, VideoWindow_SetVisible__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
VideoWindow_dealloc(VideoWindowObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pI);
	PyMem_DEL(self);
}

static PyObject *
VideoWindow_getattr(VideoWindowObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(VideoWindow_methods, (PyObject *)self, name);
}

static char VideoWindowType__doc__[] =
""
;

static PyTypeObject VideoWindowType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"VideoWindow",			/*tp_name*/
	sizeof(VideoWindowObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)VideoWindow_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)VideoWindow_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	VideoWindowType__doc__ /* Documentation string */
};

// End of VideoWindow
////////////////////////////////////////////

/////////////////////////////////////////////
// MediaEventEx

static char MediaEventEx_SetNotifyWindow__doc__[] =
""
;

static PyObject *
MediaEventEx_SetNotifyWindow(MediaEventExObject *self, PyObject *args)
{
	HRESULT res;
	HWND hWnd;
	int msgid;
	if (!PyArg_ParseTuple(args, "ii",&hWnd,&msgid))
		return NULL;
	Py_BEGIN_ALLOW_THREADS
	res=self->pI->SetNotifyWindow((OAHWND)hWnd,msgid,0);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaEventEx_SetOwner", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}



static struct PyMethodDef MediaEventEx_methods[] = {
	{"SetNotifyWindow", (PyCFunction)MediaEventEx_SetNotifyWindow, METH_VARARGS, MediaEventEx_SetNotifyWindow__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
MediaEventEx_dealloc(MediaEventExObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pI);
	PyMem_DEL(self);
}

static PyObject *
MediaEventEx_getattr(MediaEventExObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(MediaEventEx_methods, (PyObject *)self, name);
}

static char MediaEventExType__doc__[] =
""
;

static PyTypeObject MediaEventExType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"MediaEventEx",			/*tp_name*/
	sizeof(MediaEventExObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)MediaEventEx_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)MediaEventEx_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	MediaEventExType__doc__ /* Documentation string */
};

// End of MediaEventEx
////////////////////////////////////////////

////////////////////////////////////////////
// RealConverter object 

static char RealConverter_SetInterface__doc__[] =
""
;

static PyObject *
RealConverter_SetInterface(RealConverterObject *self, PyObject *args)
{
	UnknownObject *obj;
	char *hint;
	if (!PyArg_ParseTuple(args, "Os",&obj, &hint))
		return NULL;
	WCHAR wsz[MAX_PATH];
	MultiByteToWideChar(CP_ACP,0,hint,-1,wsz,MAX_PATH);
	Py_BEGIN_ALLOW_THREADS
	self->pRealConverter->SetInterface(obj->pUk,wsz);
	Py_END_ALLOW_THREADS
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef RealConverter_methods[] = {
	{"SetInterface", (PyCFunction)RealConverter_SetInterface, METH_VARARGS, RealConverter_SetInterface__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
RealConverter_dealloc(RealConverterObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pRealConverter);
	PyMem_DEL(self);
}

static PyObject *
RealConverter_getattr(RealConverterObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(RealConverter_methods, (PyObject *)self, name);
}

static char RealConverterType__doc__[] =
""
;

static PyTypeObject RealConverterType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"RealConverter",			/*tp_name*/
	sizeof(RealConverterObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)RealConverter_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)RealConverter_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	RealConverterType__doc__ /* Documentation string */
};

// End of code for RealConverter object 
////////////////////////////////////////////

////////////////////////////////////////////
// Unknown object 


static struct PyMethodDef Unknown_methods[] = {
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
Unknown_dealloc(UnknownObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pUk);
	PyMem_DEL(self);
}

static PyObject *
Unknown_getattr(UnknownObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(Unknown_methods, (PyObject *)self, name);
}

static char UnknownType__doc__[] =
""
;

static PyTypeObject UnknownType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"Unknown",			/*tp_name*/
	sizeof(UnknownObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)Unknown_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)Unknown_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	UnknownType__doc__ /* Documentation string */
};

// End of code for Unknown object 
////////////////////////////////////////////

////////////////////////////////////////////
// MediaPosition object 

static char MediaPosition_GetDuration__doc__[] =
""
;

static PyObject *
MediaPosition_GetDuration(MediaPositionObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	HRESULT res ;
    REFTIME tLength; // double in secs
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->get_Duration(&tLength);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaPosition_GetDuration", res);
		return NULL;
	}
	return Py_BuildValue("d",tLength); // in sec
}


static char MediaPosition_GetCurrentPosition__doc__[] =
""
;

static PyObject *
MediaPosition_GetCurrentPosition(MediaPositionObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	HRESULT res ;
    REFTIME tLength=0; // double in secs
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->get_CurrentPosition(&tLength);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaPosition_GetCurrentPosition", res);
		return NULL;
	}
	return Py_BuildValue("d",tLength); // in sec
}


static char MediaPosition_SetCurrentPosition__doc__[] =
""
;

static PyObject *
MediaPosition_SetCurrentPosition(MediaPositionObject *self, PyObject *args)
{
	double tPos; // in sec
	if(!PyArg_ParseTuple(args,"d",&tPos))
		return NULL;
	HRESULT res ;
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->put_CurrentPosition((REFTIME)tPos);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaPosition_SetCurrentPosition", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char MediaPosition_GetStopTime__doc__[] =
""
;

static PyObject *
MediaPosition_GetStopTime(MediaPositionObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	HRESULT res ;
    REFTIME tStop; // double in secs
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->get_StopTime(&tStop);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaPosition_GetStopTime", res);
		return NULL;
	}
	return Py_BuildValue("d",tStop); // in sec
}


static char MediaPosition_SetStopTime__doc__[] =
""
;

static PyObject *
MediaPosition_SetStopTime(MediaPositionObject *self, PyObject *args)
{
	double tPos; // in sec
	if(!PyArg_ParseTuple(args,"d",&tPos))
		return NULL;
	HRESULT res ;
	Py_BEGIN_ALLOW_THREADS
	res = self->pI->put_StopTime((REFTIME)tPos);
	Py_END_ALLOW_THREADS
	if (FAILED(res)) {
		seterror("MediaPosition_SetStopTime", res);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef MediaPosition_methods[] = {
	{"GetDuration", (PyCFunction)MediaPosition_GetDuration, METH_VARARGS, MediaPosition_GetDuration__doc__},
	{"GetCurrentPosition", (PyCFunction)MediaPosition_GetCurrentPosition, METH_VARARGS, MediaPosition_GetCurrentPosition__doc__},
	{"SetCurrentPosition", (PyCFunction)MediaPosition_SetCurrentPosition, METH_VARARGS, MediaPosition_SetCurrentPosition__doc__},
	{"GetStopTime", (PyCFunction)MediaPosition_GetStopTime, METH_VARARGS, MediaPosition_GetStopTime__doc__},
	{"SetStopTime", (PyCFunction)MediaPosition_SetStopTime, METH_VARARGS, MediaPosition_SetStopTime__doc__},
	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static void
MediaPosition_dealloc(MediaPositionObject *self)
{
	/* XXXX Add your own cleanup code here */
	RELEASE(self->pI);
	PyMem_DEL(self);
}

static PyObject *
MediaPosition_getattr(MediaPositionObject *self, char *name)
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(MediaPosition_methods, (PyObject *)self, name);
}

static char MediaPositionType__doc__[] =
""
;

static PyTypeObject MediaPositionType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,				/*ob_size*/
	"MediaPosition",			/*tp_name*/
	sizeof(MediaPositionObject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)MediaPosition_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)MediaPosition_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	MediaPositionType__doc__ /* Documentation string */
};

// End of code for MediaPosition object 
////////////////////////////////////////////

///////////////////////////////////////////
// MODULE
//
static char CreateGraphBuilder__doc__[] =
""
;

static PyObject *
CreateGraphBuilder(PyObject *self, PyObject *args)
{
	HRESULT res;
	GraphBuilderObject *obj;

	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	
	obj = newGraphBuilderObject();
	if (obj == NULL)
		return NULL;

    IGraphBuilder *pGraphBuilder=NULL;
	Py_BEGIN_ALLOW_THREADS
	res=CoCreateInstance(CLSID_FilterGraph,NULL,CLSCTX_INPROC_SERVER,
				 IID_IGraphBuilder,(void**)&pGraphBuilder);
	Py_END_ALLOW_THREADS
	if (!SUCCEEDED(res)) {
		Py_DECREF(obj);
		seterror("CoCreateInstance FilterGraph", res);
		return NULL;
	}
	else
		obj->pGraphBuilder=pGraphBuilder;
	return (PyObject *) obj;
}

static IBaseFilter* CreateDirectShowFilter(LPCTSTR strFilter,LPCTSTR strCat)
	{
	static const GUID CLSID_ActiveMovieFilterClassManager =
		{0x083863F1,0x70DE,0x11d0,{0xBD,0x40,0x00,0xA0,0xC9,0x11,0xCE,0x86}};

	static const GUID CLSID_AudioRendererCategory =
		{0xe0f158e1, 0xcb04, 0x11d0, {0xbd, 0x4e, 0x0, 0xa0, 0xc9, 0x11, 0xce, 0x86}};

	const GUID *pGUID;
	if(strCat && strCat[0] && strcmpi(strCat,"AudioRenderer")==0)
		pGUID=&CLSID_AudioRendererCategory;
	else
		pGUID=&CLSID_ActiveMovieFilterClassManager;

	HRESULT hr;
    ICreateDevEnum *pCreateDevEnum;
    hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER,
			  IID_ICreateDevEnum, (void**)&pCreateDevEnum);
    if (hr != S_OK)
		{
		//cout << "Failed to create system device enumerator" << endl;
		return NULL;
		}
	else 
		;//cout << "System device enumerator created" << endl;


    IEnumMoniker *pEnMk;
    hr = pCreateDevEnum->CreateClassEnumerator(*pGUID,&pEnMk,0);
    pCreateDevEnum->Release();
    if (hr != S_OK)
		{
		//cout << "Failed to create class enumerator" << endl;
		return NULL;
		}
	else
		;//cout << "Class enumerator created" << endl;

    pEnMk->Reset();
    ULONG cFetched;
    IMoniker *pMk;
	IBaseFilter *pFilter=NULL;
	bool bFound=false;
	//cout << "Enumerating DirectShow filters" << endl;
    while(!bFound && pEnMk->Next(1,&pMk,&cFetched)==S_OK)
		{
		IPropertyBag *pBag;
		hr = pMk->BindToStorage(0,0,IID_IPropertyBag,(void **)&pBag);
		if(SUCCEEDED(hr)) 
			{
			VARIANT var;
			var.vt = VT_BSTR;
			hr = pBag->Read(L"FriendlyName",&var,NULL);
			if(SUCCEEDED(hr)) 
				{
				char achName[256];
				WideCharToMultiByte(CP_ACP, 0,var.bstrVal,-1,achName, 80,NULL, NULL);
				SysFreeString(var.bstrVal);
				if(lstrcmpi(strFilter,achName)==0)
					{
					//cout << "Requested filter "<< strFilter <<  " found!" << endl;
					IBindCtx *pbc=NULL;
					CreateBindCtx(0,&pbc);
					hr = pMk->BindToObject(pbc,NULL,IID_IBaseFilter, (void**)&pFilter);
					pbc->Release();
					bFound=true;
					if(FAILED(hr)) 
						{
						//cout << "BindToObject failed" << endl;
						//ErrorMessage(hr);
						pFilter=NULL;
						}
					}
				}
			pBag->Release();
			}
	    pMk->Release();
		}
    pEnMk->Release();
	return pFilter;
    }

static char CreateFilter__doc__[] =
""
;

static PyObject *
CreateFilter(PyObject *self, PyObject *args)
{
	BaseFilterObject *obj;
	char *psz;
	if (!PyArg_ParseTuple(args, "s", &psz))
		return NULL;
	obj = newBaseFilterObject();
	if (obj == NULL)
		return NULL;
	IBaseFilter *pFilter;
	Py_BEGIN_ALLOW_THREADS
	pFilter=CreateDirectShowFilter(psz,"ActiveMovieFilter");
	Py_END_ALLOW_THREADS
	if (!pFilter) {
		Py_DECREF(obj);
		seterror("CreateFilter", S_OK);
		return NULL;
	}
	else
		obj->pFilter=pFilter;
	return (PyObject *) obj;
	}

static char CoInitialize__doc__[] =
""
;

static PyObject*
CoInitialize(PyObject *self, PyObject *args) 
	{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	HRESULT hr=CoInitialize(NULL);
	int res=(hr==S_OK || hr==S_FALSE)?1:0;
	return Py_BuildValue("i",res);
	}

static char CoUninitialize__doc__[] =
""
;
static PyObject*
CoUninitialize(PyObject *self, PyObject *args) 
	{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;
	CoUninitialize();
	Py_INCREF(Py_None);
	return Py_None;
	}

static struct PyMethodDef DShow_methods[] = {
	{"CreateGraphBuilder", (PyCFunction)CreateGraphBuilder, METH_VARARGS, CreateGraphBuilder__doc__},
	{"CreateFilter", (PyCFunction)CreateFilter, METH_VARARGS, CreateFilter__doc__},
	{"CoInitialize", (PyCFunction)CoInitialize, METH_VARARGS, CoInitialize__doc__},
	{"CoUninitialize", (PyCFunction)CoUninitialize, METH_VARARGS, CoUninitialize__doc__},

	{NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

static char dshow_module_documentation[] =
""
;

extern "C" __declspec(dllexport)
void initdshow()
{
	PyObject *m, *d;

	/* Create the module and add the functions */
	m = Py_InitModule4("dshow", DShow_methods,
		dshow_module_documentation,
		(PyObject*)NULL,PYTHON_API_VERSION);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyString_FromString("dshow.error");
	PyDict_SetItemString(d, "error", ErrorObject);


	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module dshow");
}
