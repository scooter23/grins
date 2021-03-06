/****************************************************************************
 * 
 *  $Id$
 *
 *  Copyright (C) 1995,1996,1997 RealNetworks, Inc.
 *  All rights reserved.
 *
 *  http://www.real.com/devzone
 *
 *  This program contains proprietary information of RealNetworks, Inc.,
 *  and is licensed subject to restrictions on use and distribution.
 * 
 *  fivemmap.cpp
 *
 *  Basic map class.
 */


/****************************************************************************
 * Includes
 */
#include <string.h>
#include "pntypes.h"
#include "fivemmap.h"


/****************************************************************************
 *  FiveMinuteMap::GetFirstValue                             ref:  fivemmap.h
 *
 */
void* FiveMinuteMap::GetFirstValue()
{
    m_nCursor = 0;

    if (m_nMapSize)
    {
       return m_pValueArray[m_nCursor];
    }
    else
    {
       return NULL;
    }
}


/****************************************************************************
 *  FiveMinuteMap::GetNextValue                             ref:  fivemmap.h
 *
 */
void* FiveMinuteMap::GetNextValue()
{
    m_nCursor++;

    if (m_nCursor < m_nMapSize)
    {
       return m_pValueArray[m_nCursor];
    }
    else
    {
       return NULL;
    }
}


/****************************************************************************
 *  FiveMinuteMap::Lookup                                    ref:  fivemmap.h
 *
 */
BOOL FiveMinuteMap::Lookup(void* Key, void*& Value) const
{
    BOOL bFound = FALSE;
    int nIndex = 0;

    // If Key is alrady in the list, replace value
    for (; nIndex < m_nMapSize; nIndex++)
    {
	if (m_pKeyArray[nIndex] == Key)
	{
	    Value = m_pValueArray[nIndex];
	    bFound = TRUE;
	    goto exit;
	}
    }

exit:
    return bFound;    
}


/****************************************************************************
 *  FiveMinuteMap::RemoveKey                                 ref:  fivemmap.h
 *
 */
void FiveMinuteMap::RemoveKey(void* Key)
{
    int nIndex = 0;

    // If Key is alrady in the list, replace value
    for (; nIndex < m_nMapSize; nIndex++)
    {
	if (m_pKeyArray[nIndex] == Key)
	{
	    if (nIndex < (m_nMapSize-1))
	    {
		memmove(&(m_pKeyArray[nIndex]),&(m_pKeyArray[nIndex+1]),sizeof(void*)*(m_nMapSize-(nIndex+1)));
		memmove(&(m_pValueArray[nIndex]),&(m_pValueArray[nIndex+1]),sizeof(void*)*(m_nMapSize-(nIndex+1)));
	    }
	    m_nMapSize--;
	    goto exit;
	}
    }

exit:
    ; // We're done!
}


/****************************************************************************
 *  FiveMinuteMap::RemoveValue                               ref:  fivemmap.h
 *
 */
void FiveMinuteMap::RemoveValue(void* Value)
{
    int nIndex = 0;

    // If Value is alrady in the list, replace value
    for (; nIndex < m_nMapSize; nIndex++)
    {
	if (m_pValueArray[nIndex] == Value)
	{
	    if (nIndex < (m_nMapSize-1))
	    {
		memmove(&(m_pKeyArray[nIndex]),&(m_pKeyArray[nIndex+1]),sizeof(void*)*(m_nMapSize-(nIndex+1)));
		memmove(&(m_pValueArray[nIndex]),&(m_pValueArray[nIndex+1]),sizeof(void*)*(m_nMapSize-(nIndex+1)));
	    }
	    m_nMapSize--;
	    goto exit;
	}
    }

exit:
    ; // We're done!
}


/****************************************************************************
 *  FiveMinuteMap::SetAt                                     ref:  fivemmap.h
 *
 */
void FiveMinuteMap::SetAt(void* Key, void* Value)
{
    int nIndex = 0;

    // If Key is alrady in the list, replace value
    for (; nIndex < m_nMapSize; nIndex++)
    {
	if (m_pKeyArray[nIndex] == Key)
	{
	    m_pValueArray[nIndex] = Value;
	    goto exit;
	}
    }

    // If we have room, add it to the end!
    if (m_nAllocSize == m_nMapSize)
    {
	m_nAllocSize += AllocationSize;
	void** pNewKeys   = new void*[m_nAllocSize];
	void** pNewValues = new void*[m_nAllocSize];

	memcpy(pNewKeys,m_pKeyArray,sizeof(void*)*m_nMapSize);
	memcpy(pNewValues,m_pValueArray,sizeof(void*)*m_nMapSize);

	delete [] m_pKeyArray;
	delete [] m_pValueArray;

	m_pKeyArray = pNewKeys;
	m_pValueArray = pNewValues;
    }

    m_pKeyArray[m_nMapSize] = Key;
    m_pValueArray[m_nMapSize] = Value;
    m_nMapSize++;

exit:
    ; // We're done!
}

