#ifndef INC_PYCPPAPI
#define INC_PYCPPAPI

// Cpp framework 
// for modules that export PyObjects
// for modules that need a mechanism to call back 
// methods of cpp objects overridden in Python

// For rapid-dev we borrow win32ui's core mechanisms
// we 'll revisit this module

// Using Std C++ (not MFC or other lib)

#ifndef Py_PYTHON_H
#include "Python.h"
#endif

#ifndef INC_MT
#include "mt.h"
#endif

inline void Trace(const char*, ...){}
#define TRACE Trace
#define ASSERT(f) ((void)0)

#ifdef PY_EXPORTS
#define DLL_API __declspec(dllexport)
#else
#define DLL_API __declspec(dllimport)
#endif
#define PY_API extern "C" DLL_API

#define MAKE_PY_CTOR(classname) static Object * classname::PyObConstruct()\
	{Object* ret = new classname;return ret;}
#define GET_PY_CTOR(classname) classname::PyObConstruct

#define BGN_SAVE PyThreadState *_save = PyEval_SaveThread()
#define END_SAVE PyEval_RestoreThread(_save)
#define BLOCK_THREADS Py_BLOCK_THREADS
class CEnterLeavePython
	{
	public:
	CEnterLeavePython(){}
	~CEnterLeavePython(){}
	};
#define GET_THREAD_AND_DECREF(object) \
	if ((object) && (object)->ob_refcnt==1) { \
		CEnterLeavePython elp;Py_XDECREF((object)); \
	} else Py_XDECREF((object));

#define CHECK_NO_ARGS(args)		do {if (!PyArg_ParseTuple(args,"")) return NULL;} while (0)
#define CHECK_NO_ARGS2(args,fnName) do {if (!PyArg_ParseTuple(args,":"#fnName)) return NULL;} while (0)
#define RETURN_NONE				do {Py_INCREF(Py_None);return Py_None;} while (0)
#define RETURN_ERR(err)			do {PyErr_SetString(module_error,err);return NULL;} while (0)
#define RETURN_MEM_ERR(err)		do {PyErr_SetString(PyExc_MemoryError,err);return NULL;} while (0)
#define RETURN_TYPE_ERR(err)	do {PyErr_SetString(PyExc_TypeError,err);return NULL;} while (0)
#define RETURN_VALUE_ERR(err)	do {PyErr_SetString(PyExc_ValueError,err);return NULL;} while (0)

#define DOINCREF(o) Py_INCREF(o)
#define DODECREF(o) Py_DECREF(o)
#define XDODECREF(o) Py_XDECREF(o)

extern DLL_API PyObject *module_error;

// helper PyTypeObject class.
class Object;
class DLL_API TypeObject : public PyTypeObject 
	{
	public:
	TypeObject(const char *name,TypeObject *pBaseType,int typeSize,
		struct PyMethodDef* methodList,Object *(*thector)());
	~TypeObject();
	public:
	TypeObject *base;
	struct PyMethodDef* methods;
	Object *(*ctor)();
	};

// helper PyObject class.
class DLL_API Object : public PyObject 
	{
	public:
	static Object* make(TypeObject &type);

	// virtuals for Python support
	virtual string repr();
	virtual PyObject *getattr(char *name);
	virtual int setattr(char *name, PyObject *v);
	virtual void cleanup();

	static struct PyMethodDef Object::empty_methods[];
	static TypeObject type;	

	protected:
	Object();
	virtual ~Object();

	public:
	static BOOL is_object(PyObject*&,TypeObject *which);
	static BOOL is_nativeobject(PyObject *ob,TypeObject *which);

	BOOL is_object(TypeObject *which);
	static void so_dealloc(PyObject *ob);
	static PyObject *so_repr(PyObject *ob);
	static PyObject *so_getattr(PyObject *self,char *name);
	static int so_setattr(PyObject *op,char *name,PyObject *v);

	static PyObject* GetMethodByType(PyObject *self,PyObject *args);
	};

/////////////////////////////////////////
/////////////////////////////////////////
/////////////////////////////////////////
// MECHANISM TO SUPPORT PYTHON OVERRIDES OF CPP OBJECTS

class AssocObject;

class DLL_API AssocManager 
	{
	public:
	AssocManager();
	~AssocManager();
	void Assoc(void *assoc, AssocObject *PyObject, void *oldAssoc=NULL);
	AssocObject *GetAssocObject(const void * handle);
	void cleanup(void);	

	private:

	typedef pair<void*,AssocObject*> ObjectPair;
	typedef map<void*,AssocObject*> ObjectMap;
	ObjectMap objectMap;
	const void  *lastLookup;
	AssocObject *lastObject;
	SyncObject m_sync;
	};

class DLL_API AssocObject : public Object
	{
	public:	
	PyObject *GetGoodRet();
	static AssocObject *make(TypeObject &makeType,void* search);

	// Given a C++ object, return a PyObject associated (map lookup)
	static AssocObject *GetPyObject(void *search);

	// Return the C++ object associated with this Python object.
	// Do as much type checking as possible.
	// Static version may have "self" pointer changed if it does
	// auto conversion from Instance to Object.
	static void *GetGoodCppObject(PyObject *&self, TypeObject *Type_check);
	virtual void *GetGoodCppObject(TypeObject *Type_check=NULL) const;

	// Call this when the C++ object dies, or otherwise becomes invalid.
	void KillAssoc();	// maps to a virtual with some protection wrapping.

	// virtuals for Python support
	virtual string repr();

	// methods
	static PyObject *AttachObject(PyObject *self, PyObject *args);

	PyObject *virtualInst;

	static TypeObject type;
	static AssocManager assocMgr;

	protected:
	// Does the actual killing.
	virtual void DoKillAssoc(BOOL bDestructing = FALSE); // does the actual work.
	// Called during KillAssoc - normally zeroes association.
	// Override to keep handle after destruction (eg, the association
	// with a dialog is valid after the Window's window has closed).
	virtual void SetAssocInvalid(){assoc = 0;}

	AssocObject(); 
	virtual ~AssocObject();
	void *assoc;
	};

////////////////////////////////////////////////
// A helper class for calling "virtual methods" - ie, given a C++ object
// call a Python method of that name on the attached Python object.
class DLL_API VirtualHelper
	{
	public:
	VirtualHelper(const char *iname, const void *iassoc);
	~VirtualHelper();

	BOOL HaveHandler() {return handler!=NULL;}
	// All the "call" functions return FALSE if the call failed, or no handler exists.
	BOOL call();
	BOOL call(int);
	BOOL call(int, int, int);
	BOOL call(long);
	BOOL call(const char *);
	BOOL call(const char *, int);
	BOOL call(PyObject *);
	BOOL call(PyObject *, PyObject *);
	BOOL call(PyObject *, PyObject *, int);
	BOOL call_args(PyObject *arglst);
	// All the retval functions will ASSERT if the call failed!
	BOOL retval( int &ret );
	BOOL retval( long &ret );
	BOOL retval( PyObject* &ret );
	BOOL retval( char * &ret );
	BOOL retval( string &ret );
	BOOL retnone();
	PyObject *GetHandler();
	
	private:
	BOOL do_call(PyObject *args);
	PyObject *handler;
	PyObject *retVal;
	PyObject *py_ob;
	string csHandlerName;
	};

#endif

