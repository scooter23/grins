/*----------------------
   EZFONT.H header file
  ----------------------*/

#ifdef __cplusplus
extern "C" {
#endif

HFONT EzCreateFont (HDC hdc, char * szFaceName, int iDeciPtHeight,
                    int iDeciPtWidth, int iAttributes, BOOL fLogRes) ;

#ifdef __cplusplus
}
#endif

#define EZ_ATTR_BOLD          1
#define EZ_ATTR_ITALIC        2
#define EZ_ATTR_UNDERLINE     4
#define EZ_ATTR_STRIKEOUT     8
