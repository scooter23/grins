
// Microsoft PowerPoint File Format Record Names
// Based on PowerPoint BIFF.doc (PowerPoint 97)

#ifndef INC_PPNAMES
#define INC_PPNAMES

#ifndef INC_PPCON
#include "ppcon.h"
#endif

struct record_name {int n; char* s;};

// Record types to names
struct record_name pstnames[] = {
	{PST_Unknown, "Unknown"},
	{PST_SubContainerCompleted, "SubContainerCompleted"},
	{PST_IRRAtom, "IRRAtom"},
	{PST_PSS, "PSS"},
	{PST_SubContainerException, "SubContainerException"},
	{PST_ClientSignal1, "ClientSignal1"},
	{PST_ClientSignal2, "ClientSignal2"},
	{PST_PowerPointStateInfoAtom, "PowerPointStateInfoAtom"},
	{PST_Document, "Document"},
	{PST_DocumentAtom, "DocumentAtom"},
	{PST_EndDocument, "EndDocument"},
	{PST_SlidePersist, "SlidePersist"},
	{PST_SlideBase, "SlideBase"},
	{PST_SlideBaseAtom, "SlideBaseAtom"},
	{PST_Slide, "Slide"},
	{PST_SlideAtom, "SlideAtom"},
	{PST_Notes, "Notes"},
	{PST_NotesAtom, "NotesAtom"},
	{PST_Environment, "Environment"},
	{PST_SlidePersistAtom, "SlidePersistAtom"},
	{PST_Scheme, "Scheme"},
	{PST_SchemeAtom, "SchemeAtom"},
	{PST_DocViewInfo, "DocViewInfo"},
	{PST_SSlideLayoutAtom, "SSlideLayoutAtom"},
	{PST_MainMaster, "MainMaster"},
	{PST_SSSlideInfoAtom, "SSSlideInfoAtom"},
	{PST_SlideViewInfo, "SlideViewInfo"},
	{PST_GuideAtom, "GuideAtom"},
	{PST_ViewInfo, "ViewInfo"},
	{PST_ViewInfoAtom, "ViewInfoAtom"},
	{PST_SlideViewInfoAtom, "SlideViewInfoAtom"},
	{PST_VBAInfo, "VBAInfo"},
	{PST_VBAInfoAtom, "VBAInfoAtom"},
	{PST_SSDocInfoAtom, "SSDocInfoAtom"},
	{PST_Summary, "Summary"},
	{PST_Texture, "Texture"},
	{PST_VBASlideInfo, "VBASlideInfo"},
	{PST_VBASlideInfoAtom, "VBASlideInfoAtom"},
	{PST_DocRoutingSlip, "DocRoutingSlip"},
	{PST_OutlineViewInfo, "OutlineViewInfo"},
	{PST_SorterViewInfo, "SorterViewInfo"},
	{PST_ExObjList, "ExObjList"},
	{PST_ExObjListAtom, "ExObjListAtom"},
	{PST_PPDrawingGroup, "PPDrawingGroup"},
	{PST_PPDrawing, "PPDrawing"},
	{PST_NamedShows, "NamedShows"},
	{PST_NamedShow, "NamedShow"},
	{PST_NamedShowSlides, "NamedShowSlides"},
	{PST_List, "List"},
	{PST_FontCollection, "FontCollection"},
	{PST_ListPlaceholder, "ListPlaceholder"},
	{PST_BookmarkCollection, "BookmarkCollection"},
	{PST_SoundCollection, "SoundCollection"},
	{PST_SoundCollAtom, "SoundCollAtom"},
	{PST_Sound, "Sound"},
	{PST_SoundData, "SoundData"},
	{PST_BookmarkSeedAtom, "BookmarkSeedAtom"},
	{PST_GuideList, "GuideList"},
	{PST_RunArray, "RunArray"},
	{PST_RunArrayAtom, "RunArrayAtom"},
	{PST_ArrayElementAtom, "ArrayElementAtom"},
	{PST_Int4ArrayAtom, "Int4ArrayAtom"},
	{PST_ColorSchemeAtom, "ColorSchemeAtom"},
	{PST_OEShape, "OEShape"},
	{PST_ExObjRefAtom, "ExObjRefAtom"},
	{PST_OEPlaceholderAtom, "OEPlaceholderAtom"},
	{PST_GrColor, "GrColor"},
	{PST_GrectAtom, "GrectAtom"},
	{PST_GratioAtom, "GratioAtom"},
	{PST_Gscaling, "Gscaling"},
	{PST_GpointAtom, "GpointAtom"},
	{PST_OEShapeAtom, "OEShapeAtom"},
	{PST_OutlineTextRefAtom, "OutlineTextRefAtom"},
	{PST_TextHeaderAtom, "TextHeaderAtom"},
	{PST_TextCharsAtom, "TextCharsAtom"},
	{PST_StyleTextPropAtom, "StyleTextPropAtom"},
	{PST_BaseTextPropAtom, "BaseTextPropAtom"},
	{PST_TxMasterStyleAtom, "TxMasterStyleAtom"},
	{PST_TxCFStyleAtom, "TxCFStyleAtom"},
	{PST_TxPFStyleAtom, "TxPFStyleAtom"},
	{PST_TextRulerAtom, "TextRulerAtom"},
	{PST_TextBookmarkAtom, "TextBookmarkAtom"},
	{PST_TextBytesAtom, "TextBytesAtom"},
	{PST_TxSIStyleAtom, "TxSIStyleAtom"},
	{PST_TextSpecInfoAtom, "TextSpecInfoAtom"},
	{PST_DefaultRulerAtom, "DefaultRulerAtom"},
	{PST_FontEntityAtom, "FontEntityAtom"},
	{PST_FontEmbedData, "FontEmbedData"},
	{PST_TypeFace, "TypeFace"},
	{PST_CString, "CString"},
	{PST_ExternalObject, "ExternalObject"},
	{PST_MetaFile, "MetaFile"},
	{PST_ExOleObj, "ExOleObj"},
	{PST_ExOleObjAtom, "ExOleObjAtom"},
	{PST_ExPlainLinkAtom, "ExPlainLinkAtom"},
	{PST_CorePict, "CorePict"},
	{PST_CorePictAtom, "CorePictAtom"},
	{PST_ExPlainAtom, "ExPlainAtom"},
	{PST_SrKinsoku, "SrKinsoku"},
	{PST_Handout, "Handout"},
	{PST_ExEmbed, "ExEmbed"},
	{PST_ExEmbedAtom, "ExEmbedAtom"},
	{PST_ExLink, "ExLink"},
	{PST_ExLinkAtom_old, "ExLinkAtom_old"},
	{PST_BookmarkEntityAtom, "BookmarkEntityAtom"},
	{PST_ExLinkAtom, "ExLinkAtom"},
	{PST_SrKinsokuAtom, "SrKinsokuAtom"},
	{PST_ExHyperlinkAtom, "ExHyperlinkAtom"},
	{PST_ExPlain, "ExPlain"},
	{PST_ExPlainLink, "ExPlainLink"},
	{PST_ExHyperlink, "ExHyperlink"},
	{PST_SlideNumberMCAtom, "SlideNumberMCAtom"},
	{PST_HeadersFooters, "HeadersFooters"},
	{PST_HeadersFootersAtom, "HeadersFootersAtom"},
	{PST_RecolorEntryAtom, "RecolorEntryAtom"},
	{PST_TxInteractiveInfoAtom, "TxInteractiveInfoAtom"},
	{PST_EmFormatAtom, "EmFormatAtom"},
	{PST_CharFormatAtom, "CharFormatAtom"},
	{PST_ParaFormatAtom, "ParaFormatAtom"},
	{PST_MasterText, "MasterText"},
	{PST_RecolorInfoAtom, "RecolorInfoAtom"},
	{PST_ExQuickTime, "ExQuickTime"},
	{PST_ExQuickTimeMovie, "ExQuickTimeMovie"},
	{PST_ExQuickTimeMovieData, "ExQuickTimeMovieData"},
	{PST_ExSubscription, "ExSubscription"},
	{PST_ExSubscriptionSection, "ExSubscriptionSection"},
	{PST_ExControl, "ExControl"},
	{PST_ExControlAtom, "ExControlAtom"},
	{PST_SlideListWithText, "SlideListWithText"},
	{PST_AnimationInfoAtom, "AnimationInfoAtom"},
	{PST_InteractiveInfo, "InteractiveInfo"},
	{PST_InteractiveInfoAtom, "InteractiveInfoAtom"},
	{PST_SlideList, "SlideList"},
	{PST_UserEditAtom, "UserEditAtom"},
	{PST_CurrentUserAtom, "CurrentUserAtom"},
	{PST_DateTimeMCAtom, "DateTimeMCAtom"},
	{PST_GenericDateMCAtom, "GenericDateMCAtom"},
	{PST_HeaderMCAtom, "HeaderMCAtom"},
	{PST_FooterMCAtom, "FooterMCAtom"},
	{PST_ExMediaAtom, "ExMediaAtom"},
	{PST_ExVideo, "ExVideo"},
	{PST_ExAviMovie, "ExAviMovie"},
	{PST_ExMCIMovie, "ExMCIMovie"},
	{PST_ExMIDIAudio, "ExMIDIAudio"},
	{PST_ExCDAudio, "ExCDAudio"},
	{PST_ExWAVAudioEmbedded, "ExWAVAudioEmbedded"},
	{PST_ExWAVAudioLink, "ExWAVAudioLink"},
	{PST_ExOleObjStg, "ExOleObjStg"},
	{PST_ExCDAudioAtom, "ExCDAudioAtom"},
	{PST_ExWAVAudioEmbeddedAtom, "ExWAVAudioEmbeddedAtom"},
	{PST_AnimationInfo, "AnimationInfo"},
	{PST_RTFDateTimeMCAtom, "RTFDateTimeMCAtom"},
	{PST_ProgTags, "ProgTags"},
	{PST_ProgStringTag, "ProgStringTag"},
	{PST_ProgBinaryTag, "ProgBinaryTag"},
	{PST_BinaryTagData, "BinaryTagData"},
	{PST_PrintOptions, "PrintOptions"},
	{PST_PersistPtrFullBlock, "PersistPtrFullBlock"},
	{PST_PersistPtrIncrementalBlock, "PersistPtrIncrementalBlock"},
	{PST_RulerIndentAtom, "RulerIndentAtom"},
	{PST_GscalingAtom, "GscalingAtom"},
	{PST_GrColorAtom, "GrColorAtom"},
	{PST_GLPointAtom, "GLPointAtom"},
	{PST_GlineAtom, "GlineAtom"},
	{-1, ""}
	};

#endif



