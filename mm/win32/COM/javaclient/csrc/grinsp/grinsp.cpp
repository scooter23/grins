// grinsp.cpp : Defines the entry point for the DLL application.
//

#include "stdafx.h"

#include "..\..\GRiNSPlayer.h"

#include "jni.h"
#include "jvmdi.h"
#include "jawt.h"

#include "jawt_md.h"

#include <assert.h>

#include "..\..\..\grinscomsvr\idl\IGRiNSPlayerAuto.h"

inline IGRiNSPlayerAuto* GetIGRiNSPlayer(jint h) {return h?(IGRiNSPlayerAuto*)h:NULL;}


extern "C" {


JNIEXPORT jint JNICALL Java_GRiNSPlayer_nconnect__(JNIEnv *env, jobject player)
	{
	CoInitialize(NULL);

	DWORD dwClsContext = CLSCTX_LOCAL_SERVER;
	IGRiNSPlayerAuto *pIGRiNSPlayer = NULL;
	HRESULT hr = CoCreateInstance(CLSID_GRiNSPlayerAuto, NULL, dwClsContext, IID_IGRiNSPlayerAuto,(void**)&pIGRiNSPlayer);
 	jint hgrins = 0;
	if(SUCCEEDED(hr))
		hgrins = jint(pIGRiNSPlayer);
	return hgrins;
	}

/*
 * Class:     GRiNSCanvas
 * Method:    connect
 * Signature: (Ljava/awt/Graphics;)V
 */
JNIEXPORT jint JNICALL Java_GRiNSPlayer_nconnect__Ljava_awt_Component_2(JNIEnv *env, jobject player, jobject component)
	{
	CoInitialize(NULL);
	
	// Get the AWT
	JAWT awt;
 	awt.version = JAWT_VERSION_1_3;
 	jboolean result = JAWT_GetAWT(env, &awt);
 	assert(result != JNI_FALSE);
 
 	// Get the drawing surface
 	JAWT_DrawingSurface* ds = awt.GetDrawingSurface(env, component);
 	assert(ds != NULL);
 
 	// Lock the drawing surface
 	jint lock = ds->Lock(ds);
 	assert((lock & JAWT_LOCK_ERROR) == 0);
 
 	// Get the drawing surface info
 	JAWT_DrawingSurfaceInfo* dsi = ds->GetDrawingSurfaceInfo(ds);
 
 	// Get the platform-specific drawing info
 	JAWT_Win32DrawingSurfaceInfo *dsi_win = (JAWT_Win32DrawingSurfaceInfo*)dsi->platformInfo;

 	//////////////////////////////
	DWORD dwClsContext = CLSCTX_LOCAL_SERVER;
	IGRiNSPlayerAuto *pIGRiNSPlayer = NULL;
	HRESULT hr = CoCreateInstance(CLSID_GRiNSPlayerAuto, NULL, dwClsContext, IID_IGRiNSPlayerAuto,(void**)&pIGRiNSPlayer);
 	jint hgrins = 0;
	if(SUCCEEDED(hr))
		{
		pIGRiNSPlayer->setWindow(dsi_win->hwnd);
		hgrins = jint(pIGRiNSPlayer);
		}
 	//////////////////////////////
	
 	// Free the drawing surface info
 	ds->FreeDrawingSurfaceInfo(dsi);
 
 	// Unlock the drawing surface
 	ds->Unlock(ds);
 
 	// Free the drawing surface
 	awt.FreeDrawingSurface(ds);

	return hgrins;
	}

/*
 * Class:     GRiNSCanvas
 * Method:    disconnect
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_ndisconnect(JNIEnv *env, jobject player, jint hgrins)
	{
	if(hgrins) 
		{
		IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
		if(pIGRiNSPlayer) pIGRiNSPlayer->Release();
		}

	CoUninitialize();	
	}

/*
 * Class:     GRiNSCanvas
 * Method:    open
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_nopen(JNIEnv *env, jobject player, jint hgrins, jstring url)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	if(pIGRiNSPlayer)
		{
		const char *psz = env->GetStringUTFChars(url, NULL);
		WCHAR wPath[MAX_PATH];
		MultiByteToWideChar(CP_ACP,0,LPCTSTR(psz),-1,wPath,MAX_PATH);	
		pIGRiNSPlayer->open(wPath);
		env->ReleaseStringUTFChars(url, psz);
		}	
	}

/*
 * Class:     GRiNSCanvas
 * Method:    close
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_nclose(JNIEnv *env, jobject player, jint hgrins)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	if(pIGRiNSPlayer) pIGRiNSPlayer->close();	
	}

/*
 * Class:     GRiNSPlayer
 * Method:    getSizeAdvice
 * Signature: (I)Ljava/awt/Dimension;
 */
JNIEXPORT jobject JNICALL Java_GRiNSPlayer_ngetPreferredSize(JNIEnv *env, jobject player, jint hgrins)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	jint w=0, h=0;
	if(pIGRiNSPlayer)pIGRiNSPlayer->getSize((int*)&w, (int*)&h);
	jclass clazz = env->FindClass("java/awt/Dimension");
	jmethodID methodID = env->GetMethodID(clazz, "<init>", "(II)V");
	return env->NewObject(clazz, methodID, w, h);
	}

/*
 * Class:     GRiNSCanvas
 * Method:    play
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_nplay(JNIEnv *env, jobject player, jint hgrins)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	if(pIGRiNSPlayer)pIGRiNSPlayer->play();	
	}

/*
 * Class:     GRiNSCanvas
 * Method:    paint
 * Signature: (Ljava/awt/Graphics;)V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_nupdate(JNIEnv *env, jobject player, jint hgrins)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	if(pIGRiNSPlayer)pIGRiNSPlayer->update();		
	}

/*
 * Class:     GRiNSCanvas
 * Method:    pause
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_npause(JNIEnv *env, jobject player, jint hgrins)
	{
	IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	if(pIGRiNSPlayer)pIGRiNSPlayer->pause();		
	}


/*
 * Class:     GRiNSCanvas
 * Method:    stop
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_GRiNSPlayer_nstop(JNIEnv *, jobject, jint hgrins)
	 {
	 IGRiNSPlayerAuto *pIGRiNSPlayer = GetIGRiNSPlayer(hgrins);
	 if(pIGRiNSPlayer)pIGRiNSPlayer->stop();		
	 }

} //extern "C"

