__version__ = "$Id$"

EVALcomment = ' Created with an evaluation copy of GRiNS '
SMIL_BASIC = 'text/smil-basic-layout'
SMILpubid = '-//W3C//DTD SMIL 1.0//EN'
SMILdtd = 'http://www.w3.org/TR/REC-smil/SMIL10.dtd'
SMIL1 = 'http://www.w3.org/TR/REC-smil'
SMILBostonPubid = '-//W3C//DTD SMIL 2.0//EN'
SMILBostonDtd = 'http://www.w3.org/2001/SMIL20/SMIL20.dtd'
SMILBostonCRDtd = 'http://www.w3.org/2001/SMIL20/CR/SMIL20.dtd'
SMIL2 = 'http://www.w3.org/2001/SMIL20/'
# namespaces recognized by GRiNS
# the first one is the required default namespace, but SMIL1
# doesn't generate a warning
SMIL2ns = [
	   'http://www.w3.org/2001/SMIL20/Language',
	   'http://www.w3.org/2001/SMIL20/',
	   'http://www.w3.org/2001/SMIL20/PR/Language',
	   'http://www.w3.org/2001/SMIL20/PR/',
	   'http://www.w3.org/2001/SMIL20/WD/Language',
	   'http://www.w3.org/2001/SMIL20/WD/',
	   'http://www.w3.org/2000/SMIL20/CR/Language',
	   'http://www.w3.org/2000/SMIL20/CR/',
##	   'http://www.w3.org/TR/REC-smil/2000/SMIL20/LC/Language',
##	   'http://www.w3.org/TR/REC-smil/2000/SMIL20/LC/',
##	   'http://www.w3.org/TR/REC-smil/2000/SMIL20/Language',
##	   'http://www.w3.org/TR/REC-smil/2000/SMIL20',
	   SMIL1]
SMIL2DTDs = [SMILBostonDtd,
	     'http://www.w3.org/2001/SMIL20/PR/SMIL20.dtd',
	     'http://www.w3.org/2001/SMIL20/WD/SMIL20.dtd',
	     'http://www.w3.org/2000/SMIL20/CR/SMIL20.dtd',
##	     'http://www.w3.org/TR/REC-smil/2000/SMIL20/SMIL20.dtd',
	     ]
GRiNSns = 'http://www.oratrix.com/'
RP9ns = 'http://features.real.com/2001/SMIL20/Extensions'
QTns = 'http://www.apple.com/quicktime/resources/smilextensions'

# list elements here that are not valid in all namespaces with the
# namespaces they are valid in
limited = {
	# viewport was changed to topLayout after CR
	'viewport': SMIL2ns[6:],
	'topLayout': SMIL2ns[:8],
	}

ATTRIBUTES = {
	'abstract': ['MediaDescription'],
	'accelerate': ['TimeManipulations'],
	'accesskey': ['LinkingAttributes'],
	'accumulate': ['BasicAnimation'],
	'actuate': ['LinkingAttributes'],
	'additive': ['BasicAnimation'],
	'alt': ['MediaAccessibility'],
	'attributeName': ['BasicAnimation'],
	'attributeType': ['BasicAnimation'],
	'author': ['MediaDescription'],
	'autoReverse': ['TimeManipulations'],
	'background-color': ['BasicLayout'],
	'backgroundColor': {'BasicLayout': ['region', 'root-layout'], 'MultiWindowLayout': ['topLayout'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream']},
	'bandwidth': ['PrefetchControl'],
	'begin': {'AccessKeyTiming': None, 'EventTiming': None, 'MediaMarkerTiming': None, 'MultiArcTiming': None, 'RepeatValueTiming': None, 'BasicInlineTiming': None, 'SyncbaseTiming': None, 'WallclockTiming': None, 'InlineTransitions': ['transitionFilter']},
	'borderColor': ['TransitionModifiers'],
	'borderWidth': ['TransitionModifiers'],
	'bottom': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'by': {'BasicAnimation': None, 'InlineTransitions': ['transitionFilter']},
	'calcMode': {'BasicAnimation': None, 'SplineAnimation': None, 'InlineTransitions': ['transitionFilter']},
	'class': ['Structure'],
	'clip-begin': ['MediaClipping', 'MediaClipMarkers'],
	'clip-end': ['MediaClipping', 'MediaClipMarkers'],
	'clipBegin': ['MediaClipping', 'MediaClipMarkers'],
	'clipEnd': ['MediaClipping', 'MediaClipMarkers'],
	'close': ['MultiWindowLayout'],
	'color': ['BrushMedia'],
	'content': ['Metainformation'],
	'coords': ['BasicLinking'],
	'copyright': ['MediaDescription'],
	'customTest': ['CustomTestAttributes'],
	'decelerate': ['TimeManipulations'],
	'defaultState': ['CustomTestAttributes'],
	'destinationLevel': ['LinkingAttributes'],
	'destinationPlaystate': ['LinkingAttributes'],
	'direction': ['BasicTransitions'],
	'dur': {'BasicInlineTiming': ['a','animate','set','animateMotion','animateColor','area','anchor','transitionFilter','text','img','audio', 'animation', 'video', 'ref', 'textstream', 'brush', 'body', 'par', 'seq', 'excl', 'prefetch'], 'BasicTransitions': ['transition'], 'InlineTransitions': ['transitionFilter']},
	'end': {'AccessKeyTiming': None, 'EventTiming': None, 'MediaMarkerTiming': None, 'MultiArcTiming': None, 'RepeatValueTiming': None, 'BasicInlineTiming': None, 'SyncbaseTiming': None, 'WallclockTiming': None, 'InlineTransitions': ['transitionFilter']},
	'endProgress': ['BasicTransitions'],
	'endsync': {'ExclTimeContainers': ['excl'], 'TimeContainerAttributes': None, 'BasicTimeContainers': None},
	'erase': ['MediaParam'],
	'external': ['LinkingAttributes'],
	'fadeColor': {'BasicTransitions': None, 'InlineTransitions': ['transitionFilter']},
	'fill': {'ExclTimeContainers': ['excl'], 'TimeContainerAttributes': None, 'BasicTimeContainers': None},
	'fillDefault': ['FillDefault'],
	'fit': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref','audio','video','img','text','animation','textstream','brush']},
	'fragment': ['ObjectLinking'],
	'from': {'BasicAnimation': None, 'InlineTransitions': ['transitionFilter']},
	'height': {'BasicLayout': ['region', 'root-layout'], 'MultiWindowLayout': ['topLayout'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'horzRepeat': ['TransitionModifiers'],
	'href': ['BasicLinking'],
	'id': ['Structure'],
	'keySplines': ['SplineAnimation'],
	'keyTimes': ['SplineAnimation'],
	'left': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'longdesc': ['MediaAccessibility'],
	'max': ['MinMaxTiming'],
	'mediaRepeat': ['MediaParam'],
	'mediaSize': ['PrefetchControl'],
	'mediaTime': ['PrefetchControl'],
	'min': ['MinMaxTiming'],
	'mode': ['InlineTransitions'],
	'name': {'MediaParam': ['param'], 'Metainformation': ['meta']},
	'nohref': ['BasicLinking'],
	'open': ['MultiWindowLayout'],
	'origin': ['BasicAnimation'],
	'override': ['CustomTestAttributes'],
	'path': ['SplineAnimation'],
	'readIndex': ['MediaAccessibility'],
	'regAlign': ['HierarchicalLayout'],
	'regPoint': ['HierarchicalLayout'],
	'region': ['BasicLayout'],
	'regionName': ['BasicLayout'],
	'repeat': ['RepeatTiming'],
	'repeatCount': {'RepeatTiming': None, 'InlineTransitions': ['inlineTransition']},
	'repeatDur': {'RepeatTiming': None, 'InlineTransitions': ['inlineTransition']},
	'restart': ['RestartTiming'],
	'restartDefault': ['RestartDefault'],
	'right': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'sensitivity': ['MediaParam'],
	'shape': ['BasicLinking'],
	'show': ['LinkingAttributes'],
	'showBackground': ['BasicLayout'],
	'skip-content': ['SkipContentControl'],
	'soundLevel': ['AudioLayout'],
	'sourceLevel': ['LinkingAttributes'],
	'sourcePlaystate': ['LinkingAttributes'],
	'speed': ['TimeManipulations'],
	'src': ['BasicMedia'],
	'startProgress': ['BasicTransitions'],
	'subtype': {'BasicTransitions': None, 'InlineTransitions': ['inlineTransition']},
	'syncBehavior': ['SyncBehavior'],
	'syncBehaviorDefault': ['SyncBehaviorDefault'],
	'syncMaster': ['SyncMaster'],
	'syncTolerance': ['SyncBehavior'],
	'syncToleranceDefault': ['SyncBehaviorDefault'],
	'system-bitrate': ['BasicContentControl'],
	'system-captions': ['BasicContentControl'],
	'system-language': ['BasicContentControl'],
	'system-overdub-or-caption': ['BasicContentControl'],
	'system-required': ['BasicContentControl'],
	'system-screen-depth': ['BasicContentControl'],
	'system-screen-size': ['BasicContentControl'],
	'systemAudioDesc': ['BasicContentControl'],
	'systemBitrate': ['BasicContentControl'],
	'systemCPU': ['BasicContentControl'],
	'systemCaptions': ['BasicContentControl'],
	'systemComponent': ['BasicContentControl'],
	'systemLanguage': ['BasicContentControl'],
	'systemOperatingSystem': ['BasicContentControl'],
	'systemOverdubOrSubtitle': ['BasicContentControl'],
	'systemRequired': ['BasicContentControl'],
	'systemScreenDepth': ['BasicContentControl'],
	'systemScreenSize': ['BasicContentControl'],
	'tabindex': ['LinkingAttributes'],
	'target': ['LinkingAttributes'],
	'targetElement': {'BasicAnimation': None, 'InlineTransitions': ['inlineTransition']},
	'timeAction': ['TimeContainerAttributes'],
	'timeContainer': ['TimeContainerAttributes'],
	'title': ['Structure', 'MediaDescription'],
	'to': {'BasicAnimation': None, 'InlineTransitions': ['inlineTransition']},
	'top': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'transIn': ['BasicTransitions'],
	'transOut': ['BasicTransitions'],
	'type': {'BasicLayout': ['layout'], 'BasicMedia': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream'], 'MediaParam': ['param'], 'BasicTransitions': ['transition'], 'InlineTransitions': ['transitionFilter']},
	'uid': ['CustomTestAttributes'],
	'value': ['MediaParam'],
	'values': {'BasicAnimation': None, 'InlineTransitions': ['transitionFilter']},
	'valuetype': ['MediaParam'],
	'vertRepeat': ['TransitionModifiers'],
	'width': {'BasicLayout': ['region', 'root-layout'], 'MultiWindowLayout': ['topLayout'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	'xml:lang': ['Structure', 'MediaDescription'],
	'xmlns': ['Structure'],
	'z-index': {'BasicLayout': ['region'], 'HierarchicalLayout': ['ref', 'audio', 'video', 'img', 'text', 'animation', 'textstream', 'brush']},
	}

ELEMENTS = {
	'a': ['BasicLinking'],
	'anchor': ['BasicLinking'],
	'animate': ['BasicAnimation'],
	'animateColor': ['BasicAnimation'],
	'animateMotion': ['BasicAnimation'],
	'animation': ['BasicMedia'],
	'area': ['BasicLinking'],
	'audio': ['BasicMedia'],
	'body': ['Structure'],
	'brush': ['BrushMedia'],
	'customAttributes': ['CustomTestAttributes'],
	'customTest': ['CustomTestAttributes'],
	'excl': ['ExclTimeContainers'],
	'head': ['Structure'],
	'img': ['BasicMedia'],
	'layout': ['BasicLayout'],
	'meta': ['Metainformation'],
	'metadata': ['Metainformation'],
	'par': ['BasicTimeContainers'],
	'param': ['MediaParam'],
	'prefetch': ['PrefetchControl'],
	'priorityClass': ['ExclTimeContainers'],
	'ref': ['BasicMedia'],
	'regPoint': ['HierarchicalLayout'],
	'region': ['BasicLayout'],
	'root-layout': ['BasicLayout'],
	'seq': ['BasicTimeContainers'],
	'set': ['BasicAnimation'],
	'smil': ['Structure'],
	'switch': ['BasicContentControl'],
	'text': ['BasicMedia'],
	'textstream': ['BasicMedia'],
	'topLayout': ['MultiWindowLayout'],
	'transition': ['BasicTransitions'],
	'transitionFilter': ['InlineTransitions'],
	'video': ['BasicMedia'],
	}

class SMIL:
	# some abbreviations
	__layouts = GRiNSns + ' ' + 'layouts'
	__layout = GRiNSns + ' ' + 'layout'
	__assets = GRiNSns + ' ' 'assets'
	__viewinfo = GRiNSns + ' ' 'viewinfo'

	# abbreviations for collections of attributes
	__Core = {'alt':None,
		  'class':None,
		  'id':None,
		  'longdesc':None,
		  'title':None,
		  'xml:base':None,}
	__I18n = {'xml:lang':None,}
	__Test = {'system-bitrate':None,
		  'system-captions':None,
		  'system-language':None,
		  'system-overdub-or-caption':None,
		  'system-required':None,
		  'system-screen-depth':None,
		  'system-screen-size':None,
		  'systemAudioDesc':None,
		  'systemBitrate':None,
		  'systemCaptions':None,
		  'systemComponent':None,
		  'systemCPU':None,
		  'systemLanguage':None,
		  'systemOperatingSystem':None,
		  'systemOverdubOrSubtitle':None,
		  'systemRequired':None,
		  'systemScreenDepth':None,
		  'systemScreenSize':None,}
	__basicTiming = {'begin':None,
			 'dur':None,
			 'end':None,
			 'max':None,
			 'min':None,
			 'repeat':None,
			 'repeatCount':None,
			 'repeatDur':None,
			 }
	__Timing = {'fillDefault':None,
		    'restart':None,
		    'restartDefault':None,
		    'syncBehavior':None,
		    'syncBehaviorDefault':None,
		    'syncMaster':None,
		    'syncTolerance':None,
		    'syncToleranceDefault':None,
		    }
	__Timing.update(__basicTiming)

	# all allowed entities with all their attributes
	_attributes = {
		'smil': {QTns+' ' 'time-slider':None,
			 QTns+' ' 'next':None,
			 QTns+' ' 'autoplay':None,
			 QTns+' ' 'chapter-mode':None,
			 QTns+' ' 'immediate-instantiation':None,
			 },
		'head': {},
		'body': {'abstract':None,
			 'author':None,
			 'copyright':None,
			 'fill':None,
			 __layout:None,
			 GRiNSns+' ' 'hidden':None,
			 GRiNSns+' ' 'collapsed':None,
			 GRiNSns+' ' 'showtime':None,
			 GRiNSns+' ' 'timezoom':None,
			 GRiNSns+' ' 'comment':None,
			 GRiNSns+' ' 'thumbnailScale':None,
			 GRiNSns+' ' 'thumbnailIcon':None,
			 GRiNSns+' ' 'emptyIcon':None,
			 GRiNSns+' ' 'emptyText':None,
			 GRiNSns+' ' 'emptyColor':None,
			 GRiNSns+' ' 'emptyDur':None,
			 GRiNSns+' ' 'emptyShow':None,
			 GRiNSns+' ' 'nonEmptyIcon':None,
			 GRiNSns+' ' 'nonEmptyText':None,
			 GRiNSns+' ' 'nonEmptyColor':None,
			 GRiNSns+' ' 'dropIcon':None,
			 GRiNSns+' ' 'project_default_duration':None,
			 GRiNSns+' ' 'project_default_duration_image':None,
			 GRiNSns+' ' 'project_default_duration_text':None,
			 GRiNSns+' ' 'project_default_region_image':None,
			 GRiNSns+' ' 'project_default_region_video':None,
			 GRiNSns+' ' 'project_default_region_sound':None,
			 GRiNSns+' ' 'project_default_region_text':None,
			 GRiNSns+' ' 'project_forcechild':None,
			 },
		'meta': {'content':None,
			 'name':None,
			 'skip-content':None,
			 },
		'metadata': {'skip-content':None,
			     },
		__assets: {'skip-content':None,
			     },
		'layout': {'customTest':None,
			   'type':None,
			   },
		'root-layout': {'background-color':None,
				'backgroundColor':None,
				'customTest':None,
				'height':None,
				'skip-content':None,
				'width':None,
				GRiNSns+' ' 'showEditBackground':None,
				GRiNSns+' ' 'editBackground':None,
				GRiNSns+' ' 'traceImage':None,
				GRiNSns+' ' 'collapsed':None,
				RP9ns+' ' 'resizeBehavior':None,
				},
		'topLayout': {'backgroundColor':None,
			      'customTest':None,
			      'height':None,
			      'skip-content':None,
			      'width':None,
			      'close':None,
			      'open':None,
			      # edit preferences of new layout view
			      GRiNSns+' ' 'showEditBackground':None,
			      GRiNSns+' ' 'editBackground':None,
			      GRiNSns+' ' 'traceImage':None,
			      GRiNSns+' ' 'collapsed':None,
			      RP9ns+' ' 'resizeBehavior':None,
			      },
		'region': {'background-color':None,
			   'backgroundColor':None,
			   'bottom':None,
			   'customTest':None,
			   'fit':None,
			   'height':None,
			   'left':None,
##			   'regAlign':None,
##			   'regPoint':None,
			   'regionName': None,
			   'right':None,
			   'showBackground':None,
			   'skip-content':None,
			   'soundLevel':None,
			   'top':None,
			   'width':None,
			   'z-index':None,
			   GRiNSns+' ' 'comment':None,
			   GRiNSns+' ' 'duration':None,
			   GRiNSns+' ' 'fgcolor':None,
			   GRiNSns+' ' 'file':None,
			   GRiNSns+' ' 'transparent':None,
			   GRiNSns+' ' 'type':None,
			   GRiNSns+' ' 'visible':None,
			   GRiNSns+' ' 'collapsed':None,
			   RP9ns+' ' 'opacity':None,
			   # edit preferences of new layout view
			   GRiNSns+' ' 'showEditBackground':None,
			   GRiNSns+' ' 'editBackground':None,
			},
		'regPoint': {'bottom':None,
			     'customTest':None,
			     'left':None,
			     'regAlign':None,
			     'right':None,
			     'skip-content':None,
			     'top':None,
			     },
		__layouts: {},
		__layout: {GRiNSns+' ' 'regions':None},
		__viewinfo: {
				'view':None,
				'top': None,
				'left': None,
				'width': None,
				'height': None,
				},
		'par': {'abstract':None,
			'author':None,
			'copyright':None,
			'customTest':None,
			'endsync':None,
			'fill':None,
			'region':None,
			__layout:None,
			GRiNSns+' ' 'collapsed':None,
			GRiNSns+' ' 'showtime':None,
			GRiNSns+' ' 'timezoom':None,
			GRiNSns+' ' 'comment':None,
			GRiNSns+' ' 'thumbnailScale':None,
			GRiNSns+' ' 'thumbnailIcon':None,
			GRiNSns+' ' 'emptyIcon':None,
			GRiNSns+' ' 'emptyText':None,
			GRiNSns+' ' 'emptyColor':None,
			GRiNSns+' ' 'emptyDur':None,
			GRiNSns+' ' 'emptyShow':None,
			GRiNSns+' ' 'nonEmptyIcon':None,
			GRiNSns+' ' 'nonEmptyText':None,
			GRiNSns+' ' 'nonEmptyColor':None,
			GRiNSns+' ' 'dropIcon':None,
			GRiNSns+' ' 'project_default_duration':None,
			GRiNSns+' ' 'project_default_duration_image':None,
			GRiNSns+' ' 'project_default_duration_text':None,
			GRiNSns+' ' 'project_default_region_image':None,
			GRiNSns+' ' 'project_default_region_video':None,
			GRiNSns+' ' 'project_default_region_sound':None,
			GRiNSns+' ' 'project_default_region_text':None,
			GRiNSns+' ' 'project_forcechild':None,
			GRiNSns+' ' 'RTIPA-server':None,
			},
		'seq': {'abstract':None,
			'author':None,
			'copyright':None,
			'customTest':None,
			'fill':None,
			'region':None,
			__layout:None,
			GRiNSns+' ' 'collapsed':None,
			GRiNSns+' ' 'showtime':None,
			GRiNSns+' ' 'timezoom':None,
			GRiNSns+' ' 'comment':None,
			GRiNSns+' ' 'thumbnailScale':None,
			GRiNSns+' ' 'thumbnailIcon':None,
			GRiNSns+' ' 'emptyIcon':None,
			GRiNSns+' ' 'emptyText':None,
			GRiNSns+' ' 'emptyColor':None,
			GRiNSns+' ' 'emptyDur':None,
			GRiNSns+' ' 'emptyShow':None,
			GRiNSns+' ' 'nonEmptyIcon':None,
			GRiNSns+' ' 'nonEmptyText':None,
			GRiNSns+' ' 'nonEmptyColor':None,
			GRiNSns+' ' 'dropIcon':None,
			GRiNSns+' ' 'project_default_region':None,
			GRiNSns+' ' 'project_default_type':None,
			GRiNSns+' ' 'project_bandwidth_fraction':None,
			GRiNSns+' ' 'project_readonly':None,
			GRiNSns+' ' 'project_default_duration':None,
			GRiNSns+' ' 'project_default_duration_image':None,
			GRiNSns+' ' 'project_default_duration_text':None,
			GRiNSns+' ' 'project_default_region_image':None,
			GRiNSns+' ' 'project_default_region_video':None,
			GRiNSns+' ' 'project_default_region_sound':None,
			GRiNSns+' ' 'project_default_region_text':None,
			GRiNSns+' ' 'project_forcechild':None,
			GRiNSns+' ' 'RTIPA-server':None,
			},
		'switch': {'customTest':None,
			   __layout:None,
			   GRiNSns+' ' 'project_default_duration':None,
			   GRiNSns+' ' 'project_default_duration_image':None,
			   GRiNSns+' ' 'project_default_duration_text':None,
			   GRiNSns+' ' 'thumbnailScale':None,
			   GRiNSns+' ' 'thumbnailIcon':None,
			   GRiNSns+' ' 'emptyIcon':None,
			   GRiNSns+' ' 'emptyText':None,
			   GRiNSns+' ' 'emptyColor':None,
			   GRiNSns+' ' 'emptyDur':None,
			   GRiNSns+' ' 'emptyShow':None,
			   GRiNSns+' ' 'nonEmptyIcon':None,
			   GRiNSns+' ' 'nonEmptyText':None,
			   GRiNSns+' ' 'nonEmptyColor':None,
			   GRiNSns+' ' 'dropIcon':None,
			   GRiNSns+' ' 'collapsed':None,
			   GRiNSns+' ' 'showtime':None,
			   GRiNSns+' ' 'timezoom':None,
			   },
		'excl': {'abstract':None,
			 'author':None,
			 'copyright':None,
			 'customTest':None,
			 'endsync':None,
			 'fill':None,
			 'region':None,
			 'skip-content':None,
			 __layout:None,
			 GRiNSns+' ' 'collapsed':None,
			 GRiNSns+' ' 'showtime':None,
			 GRiNSns+' ' 'timezoom':None,
			 GRiNSns+' ' 'comment':None,
			 GRiNSns+' ' 'thumbnailScale':None,
			 GRiNSns+' ' 'thumbnailIcon':None,
			 GRiNSns+' ' 'emptyIcon':None,
			 GRiNSns+' ' 'emptyText':None,
			 GRiNSns+' ' 'emptyColor':None,
			 GRiNSns+' ' 'emptyDur':None,
			 GRiNSns+' ' 'emptyShow':None,
			 GRiNSns+' ' 'nonEmptyIcon':None,
			 GRiNSns+' ' 'nonEmptyText':None,
			 GRiNSns+' ' 'nonEmptyColor':None,
			 GRiNSns+' ' 'dropIcon':None,
			 GRiNSns+' ' 'project_default_duration':None,
			 GRiNSns+' ' 'project_default_duration_image':None,
			 GRiNSns+' ' 'project_default_duration_text':None,
			 GRiNSns+' ' 'project_default_region_image':None,
			 GRiNSns+' ' 'project_default_region_video':None,
			 GRiNSns+' ' 'project_default_region_sound':None,
			 GRiNSns+' ' 'project_default_region_text':None,
			 GRiNSns+' ' 'project_forcechild':None,
			 GRiNSns+' ' 'RTIPA-server':None,
			 },
		'priorityClass': {'abstract':None,
				  'author':None,
				  'copyright':None,
				  'customTest':None,
				  'higher':'pause',
				  'lower':'defer',
				  'pauseDisplay':None,
				  'peers':'stop',
				  'skip-content':None,
				  GRiNSns+' ' 'project_default_duration':None,
				  GRiNSns+' ' 'project_default_duration_image':None,
				  GRiNSns+' ' 'project_default_duration_text':None,
				  GRiNSns+' ' 'thumbnailScale':None,
				  GRiNSns+' ' 'thumbnailIcon':None,
				  GRiNSns+' ' 'emptyIcon':None,
				  GRiNSns+' ' 'emptyText':None,
				  GRiNSns+' ' 'emptyColor':None,
				  GRiNSns+' ' 'emptyDur':None,
				  GRiNSns+' ' 'emptyShow':None,
				  GRiNSns+' ' 'nonEmptyIcon':None,
				  GRiNSns+' ' 'nonEmptyText':None,
				  GRiNSns+' ' 'nonEmptyColor':None,
				  GRiNSns+' ' 'dropIcon':None,
				  GRiNSns+' ' 'collapsed':None,
				  GRiNSns+' ' 'showtime':None,
				  GRiNSns+' ' 'timezoom':None,
				  },
		'ref': {'abstract':None,
			'author':None,
			'clip-begin':None,
			'clip-end':None,
			'clipBegin':None,
			'clipEnd':None,
			'copyright':None,
			'customTest':None,
			'endsync':None,
			'erase':None,
			'fill':None,
			'mediaRepeat':None,
			'readIndex':None,
			'region':None,
			'sensitivity':None,
			'src':None,
			'tabindex':None,
			'transIn':None,
			'transOut':None,
			'type':None,
			# subregion positioning attributes
			'bottom':None,
			'height':None,
			'left':None,
			'right':None,
			'top':None,
			'width':None,
			'z-index':None,
			'fit':None,
			# registration point
			'regPoint':None,
			'regAlign':None,

			'backgroundColor':None,
			__layout:None,
			GRiNSns+' ' 'bgcolor':None,
			GRiNSns+' ' 'collapsed':None,
			GRiNSns+' ' 'comment':None,
			GRiNSns+' ' 'captionchannel':None,
			GRiNSns+' ' 'thumbnailScale':None,
			GRiNSns+' ' 'thumbnailIcon':None,
			GRiNSns+' ' 'project_audiotype':None,
			GRiNSns+' ' 'project_convert':None,
			GRiNSns+' ' 'project_mobile':None,
			GRiNSns+' ' 'project_perfect':None,
			GRiNSns+' ' 'project_quality':None,
			GRiNSns+' ' 'project_targets':None,
			GRiNSns+' ' 'project_videotype':None,
			GRiNSns+' ' 'showAnimationPath':None,
			GRiNSns+' ' 'showtime':None,
			GRiNSns+' ' 'timezoom':None,
			GRiNSns+' ' 'allowedmimetypes':None,
			GRiNSns+' ' 'RTIPA-server':None,
			QTns+' ' 'immediate-instantiation':None,
			QTns+' ' 'bitrate':None,
			QTns+' ' 'system-mime-type-supported':None,
			QTns+' ' 'attach-timebase':None,
			QTns+' ' 'chapter':None,
			QTns+' ' 'composite-mode':None,
			RP9ns+' ' 'backgroundOpacity':None,
			RP9ns+' ' 'chromaKey':None,
			RP9ns+' ' 'chromaKeyOpacity':None,
			RP9ns+' ' 'chromaKeyTolerance':None,
			RP9ns+' ' 'mediaOpacity':None,
			},
		'brush': {'abstract':None,
			  'author':None,
			  'color':None,
			  'copyright':None,
			  'customTest':None,
			  'endsync':None,
			  'erase':None,
			  'fill':None,
			  'readIndex':None,
			  'region':None,
			  'sensitivity':None,
			  'skip-content':None,
			  'tabindex':None,
			  'transIn':None,
			  'transOut':None,
			  # subregion positioning attributes
			  'bottom':None,
			  'height':None,
			  'left':None,
			  'right':None,
			  'top':None,
			  'width':None,
			  'z-index':None,
			  'fit':None,
			  # registration point
			  'regPoint':None,
			  'regAlign':None,

			  'backgroundColor':None,
			  __layout:None,
			  GRiNSns+' ' 'collapsed':None,
			  GRiNSns+' ' 'thumbnailScale':None,
			  GRiNSns+' ' 'thumbnailIcon':None,
			  GRiNSns+' ' 'bgcolor':None,
			  GRiNSns+' ' 'comment':None,
			  GRiNSns+' ' 'showtime':None,
			  GRiNSns+' ' 'showAnimationPath':None,
			  GRiNSns+' ' 'timezoom':None,
			  GRiNSns+' ' 'RTIPA-server':None,
			  QTns+' ' 'immediate-instantiation':None,
			  QTns+' ' 'bitrate':None,
			  QTns+' ' 'system-mime-type-supported':None,
			  QTns+' ' 'attach-timebase':None,
			  QTns+' ' 'chapter':None,
			  QTns+' ' 'composite-mode':None,
			  },
		'param': {'customTest':None,
			  'name':None,
			  'skip-content':None,
			  'type':None,
			  'value':None,
			  'valuetype':None,
			  },
		'a': {'accesskey':None,
		      'actuate':None,
		      'customTest':None,
		      'destinationLevel':None,
		      'destinationPlaystate':None,
		      'external':None,
		      'href':None,
		      'show':None,
		      'sourceLevel':None,
		      'sourcePlaystate':None,
		      'tabindex':None,
		      'target':None,
		      },
		'area': {'accesskey':None,
			 'actuate':None,
			 'coords':None,
			 'customTest':None,
			 'destinationLevel':None,
			 'destinationPlaystate':None,
			 'external':None,
			 'fragment':None,
			 'href':None,
			 'nohref':None,
			 'shape':None,
			 'show':None,
			 'skip-content':None,
			 'sourceLevel':None,
			 'sourcePlaystate':None,
			 'tabindex':None,
			 'target':None,
			 GRiNSns+' ' 'RTIPA-server':None,
			 RP9ns+' ' 'sendTo':None,
			 },
		'customAttributes': {'skip-content':None,
				     },
		'customTest': {'defaultState':None,
			       'override':None,
			       'skip-content':None,
			       'uid':None,
			       },
		'transition':{'type':None,
			      'subtype':None,
			      'dur':None,
			      'startProgress':None,
			      'endProgress':None,
			      'direction':None,
			      'fadeColor':None,
			      'horzRepeat':None,
			      'vertRepeat':None,
			      'borderWidth':None,
			      'borderColor':None,
##			      'coordinated':None,
##			      'clipBoundary':None,
			      'skip-content':None,
			      'customTest':None,
			      },
		'transitionFilter':{'type':None,
				    'subtype':None,
				    'mode':None,
				    'fadeColor':None,
				    'horzRepeat':None,
				    'vertRepeat':None,
				    'borderWidth':None,
				    'borderColor':None,
				    },
		'prefetch': {'bandwidth':None,
			     'clip-begin':None,
			     'clip-end':None,
			     'clipBegin':None,
			     'clipEnd':None,
			     'customTest':None,
			     'mediaSize':None,
			     'mediaTime':None,
			     'skip-content':None,
			     'src':None,
			     GRiNSns+' ' 'showtime':None,
			     GRiNSns+' ' 'timezoom':None,
			     GRiNSns+' ' 'RTIPA-server':None,
			     },
		}

	_attributes['viewport'] = _attributes['topLayout'].copy()
	_attributes['anchor'] = _attributes['area'].copy()

	__media_object = ['audio', 'video', 'text', 'img', 'animation',
			  'textstream', 'ref', 'brush',
			  'prefetch']

	__at = None
	for __el in __media_object:
		if not _attributes.has_key(__el):
			_attributes[__el] = _attributes['ref']

	__animate_elements = ['animate', 'animateMotion',
			      'animateColor', 'set', 'transitionFilter']
	__animate_attrs_core = {'attributeName':None,
				'attributeType':None,
				'customTest':None,
				'fill':None,
				'fillDefault':None,
				'skip-content':None,
				'targetElement': None,
				'to':None,
				}
	__animate_attrs_extra = {'accumulate':None,
				 'additive':None,
				 'by':None,
				 'calcMode':None,
				 'from':None,
				 'values':None,
				 'keySplines':None,
				 'keyTimes':None,
				 }
	__timeManipulations = {'speed':None,
		    'accelerate':None,
		    'decelerate':None,
		    'autoReverse':None,
		    }

	_attributes['animateMotion'] = __animate_attrs_core.copy()
	_attributes['animateMotion'].update(__animate_attrs_extra)
	_attributes['animateMotion']['calcMode'] = None
	_attributes['animateMotion']['path'] = None
	_attributes['animateMotion']['origin'] = None
	_attributes['animateMotion'][GRiNSns+' ' 'editGroup'] = None
	del _attributes['animateMotion']['attributeName']
	del _attributes['animateMotion']['attributeType']

	_attributes['animate'] = __animate_attrs_core.copy()
	_attributes['animate'].update(__animate_attrs_extra)
	_attributes['animate'][GRiNSns+' ' 'editGroup'] = None

	_attributes['animateColor'] = __animate_attrs_core.copy()
	_attributes['animateColor'].update(__animate_attrs_extra)

	_attributes['set'] = __animate_attrs_core.copy()

	_attributes['transitionFilter'].update(__animate_attrs_core)
	_attributes['transitionFilter'].update(__animate_attrs_extra)
	del _attributes['transitionFilter']['attributeName']
	del _attributes['transitionFilter']['attributeType']

	del __animate_attrs_core, __animate_attrs_extra

	# add TimeManipulations to certain elements
	for __el in __animate_elements:
		_attributes[__el].update(__timeManipulations)

	# Abbreviations for collections of elements
	__schedule = ['par', 'seq', 'excl'] + __media_object
	__container_content = __schedule + ['switch', 'a'] + __animate_elements + [__assets]
	__media_content = ['anchor', 'area', 'param', 'switch'] + __animate_elements

	# Core, Test and I18n attribs are added to all elements in the language
	for __el in _attributes.keys():
		_attributes[__el].update(__Core)
		if __el not in ('head', 'meta', 'metadata',
				'body', 'customTest'):
			_attributes[__el].update(__Test)
		_attributes[__el].update(__I18n)

	# add basicTiming to certain elements
	for __el in ('a', 'animate', 'set',
		     'animateMotion', 'animateColor',
		     'area', 'anchor', 'transitionFilter',
		     ):
		_attributes[__el].update(__basicTiming)

	# add Timing to certain other elements
	for __el in ('text', 'img', 'audio', 'animation', 'video', 'ref',
		     'textstream', 'brush', 'body', 'par', 'seq',
		     'excl', 'prefetch'):
		if __el[:len(GRiNSns)+1] == GRiNSns+' ':
			for __key, __val in __Timing.items():
				if ' ' in __key:
					_attributes[__el][__key] = __val
					_attributes[__el][GRiNSns+' '+__key.split(' ')[1]] = __val
				else:
					_attributes[__el][GRiNSns+' '+__key] = __val
		else:
			_attributes[__el].update(__Timing)

	# all entities with their allowed content
	# no allowed content is default, so we don't specify empty ones here
	entities = {
		'smil': ['head', 'body'],
		'head': ['layout', 'switch', 'meta', 'metadata',
			 'customAttributes', __layouts, 'transition', __viewinfo],
		'customAttributes': ['customTest'],
		'layout': ['region', 'root-layout', 'topLayout', 'viewport', 'regPoint', 'switch'],
		'topLayout': ['region', 'switch'],
		'region': ['region', 'switch'],
		'transition': ['param'],
		__layouts: [__layout],
		'body': __container_content,
		'par': __container_content,
		'seq': __container_content,
		'excl': __container_content + ['priorityClass'],
		'priorityClass': __container_content,
		'switch': ['layout', 'region', 'topLayout', 'viewport'] + __container_content,
		'ref': __media_content,
		'audio': __media_content,
		'img': __media_content,
		'video': __media_content,
		'text': __media_content,
		'animation': __media_content,
		'textstream': __media_content,
		'brush': __media_content,
		'a': __schedule + ['switch'],
		__assets: __container_content,

## when used, this should be moved outside of this dict
##	__Schedule = ['par', 'seq', 'excl']
##	__MediaContent = ['text', 'img', 'audio', 'video', 'ref', 'animation', 'textstream', 'brush', 'param']
##	__ContentControl = ['switch', 'prefetch']
##	__LinkAnchor = ['a', 'area', 'anchor']
##	__Animation = ['animate', 'set', 'animateMotion', 'animateColor', 'transitionFilter']

##		'switch': __Schedule + __MediaContent + __ContentControl + __LinkAnchor + __Animation + ['priorityClass','layout'],
##		'customAttributes': ['customTest'],
##		'region': ['region'],
##		'topLayout': ['region'],
##		'layout': ['root-layout', 'region', 'topLayout', 'viewport', 'regPoint'],
##		'a': __Schedule + __MediaContent + __ContentControl + __Animation,
##		'area': ['animate', 'set'],
##		'anchor': ['animate', 'set'],
##		'text': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'img': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'audio': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'animation': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'video': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'ref': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'textstream': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'brush': ['param', 'area', 'anchor', 'switch'] + __Animation,
##		'smil': ['head', 'body'],
##		'head': ['meta', 'customAttributes', 'metadata', 'layout', 'switch', 'transition'],
##		'body': __Schedule + __MediaContent + __ContentControl + ['a'],
##		'par': __Schedule + __MediaContent + __ContentControl + ['a'] + __Animation,
##		'seq': __Schedule + __MediaContent + __ContentControl + ['a'] + __Animation,
##		'excl': __Schedule + __MediaContent + __ContentControl + ['a'] + __Animation + ['priorityClass'],
##		'priorityClass': __Schedule + __MediaContent + __ContentControl + ['a'] + __Animation,
		}
	entities['viewport'] = entities['topLayout'][:]

	# cleanup
	__el = __atd = __at = __vl = __key = __val = __ns = __sns = None
	del __el, __atd, __at, __vl, __key, __val, __ns, __sns
	del __media_object, __schedule, __container_content,
	del __media_content
	del __layouts, __layout
	del __animate_elements
	del __I18n, __basicTiming, __Timing, __Core, __Test

extensions = {
	# SMIL 1.0
	'http://www.w3.org/TR/REC-smil/': 1,
}

from settings import MODULES
for _k, _v in MODULES.items():
	for _ns in SMIL2ns:
		if _ns[-1] == '/':
			extensions[_ns + _k] = _v
del _k, _v, _ns
