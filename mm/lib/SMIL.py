SMIL_BASIC = 'text/smil-basic-layout'
SMIL_EXTENDED = 'text/smil-extended-layout'
SMILpubid = "-//W3C//DTD SMIL 1.0//EN"
SMILdtd = "http://www.w3.org/TR/REC-smil/SMIL10.dtd"
SMILBostonPubid = "-//W3C//DTD SMIL 2.0//EN"
SMILBostonDtd = "http://www.w3.org/TR/REC-smil/SMIL20.dtd"
GRiNSns = "http://www.oratrix.com/"

class SMIL:
	# some abbreviations
	__layouts = GRiNSns + ' ' + 'layouts'
	__layout = GRiNSns + ' ' + 'layout'
	__choice = GRiNSns + ' ' 'choice'
	__bag = GRiNSns + ' ' 'bag'
	__null = GRiNSns + ' ' 'null'
	__cmif = GRiNSns + ' ' 'cmif'
	__shell = GRiNSns + ' ' 'shell'
	__socket = GRiNSns + ' ' 'socket'

	# all allowed entities with all their attributes
	attributes = {
		'smil': {'id':None},
		'head': {'id':None},
		'body': {'abstract':'',
			 'author':'',
			 'begin':None,
			 'copyright':'',
			 'dur':None,
			 'end':None,
			 'fill':None,
			 'id':None,
			 'repeat':'1',
			 'repeatCount':None,
			 'repeatDur':None,
			 'restart':None,
			 'system-bitrate':None,
			 'system-captions':None,
			 'system-language':None,
			 'system-overdub-or-caption':None,
			 'system-required':None,
			 'system-screen-depth':None,
			 'system-screen-size':None,
			 'systemBitrate':None,
			 'systemCaptions':None,
			 'systemLanguage':None,
			 'systemOverdubOrCaption':None,
			 'systemRequired':None,
			 'systemScreenDepth':None,
			 'systemScreenSize':None,
			 'title':None,
			 'uGroup':None,
			 __layout:None,
			 GRiNSns+' ' 'comment':None,
			 },
		'meta': {'content':None,
			 'id':None,
			 'name':None},
		'layout': {'id':None,
			   'type':SMIL_BASIC},
		'root-layout': {'background-color':'transparent',
				'backgroundColor':None,
				'height':'0',
				'id':None,
				'overflow':'hidden',
				'skip-content':'true',
				'title':None,
				'width':'0'},
		'top-layout': {'background-color':'transparent',
			       'backgroundColor':None,
			       'height':'0',
			       'id':None,
			       'skip-content':'true',
			       'title':None,
			       'width':'0',
			       },
		'region': {'background-color':'transparent',
			   'backgroundColor':None,
			   'bottom':None,
			   'fit':'hidden',
			   'height':None,
			   'id':None,
			   'left':None,
			   'skip-content':'true',
			   'right':None,
			   'title':None,
			   'top':None,
			   'width':None,
			   'z-index':'0',
			   GRiNSns+' ' 'border':None,
			   GRiNSns+' ' 'bucolor':None,
			   GRiNSns+' ' 'center':None,
			   GRiNSns+' ' 'comment':None,
			   GRiNSns+' ' 'drawbox':None,
			   GRiNSns+' ' 'duration':None,
			   GRiNSns+' ' 'fgcolor':None,
			   GRiNSns+' ' 'file':None,
			   GRiNSns+' ' 'font':None,
			   GRiNSns+' ' 'hicolor':None,
			   GRiNSns+' ' 'pointsize':None,
			   GRiNSns+' ' 'transparent':None,
			   GRiNSns+' ' 'type':None,
			   GRiNSns+' ' 'visible':None,
			   },
		__layouts: {GRiNSns+' ' 'id':None},
		__layout: {GRiNSns+' ' 'id':None,
##			   GRiNSns+' ' 'title':None,
			   GRiNSns+' ' 'regions':None},
		'par': {'abstract':'',
			'author':'',
			'begin':None,
			'copyright':'',
			'dur':None,
			'end':None,
			'endsync':None,
			'fill':None,
			'id':None,
			'region':None,
			'repeat':'1',
			'repeatCount':None,
			'repeatDur':None,
			'restart':None,
			'system-bitrate':None,
			'system-captions':None,
			'system-language':None,
			'system-overdub-or-caption':None,
			'system-required':None,
			'system-screen-depth':None,
			'system-screen-size':None,
			'systemBitrate':None,
			'systemCaptions':None,
			'systemLanguage':None,
			'systemOverdubOrCaption':None,
			'systemRequired':None,
			'systemScreenDepth':None,
			'systemScreenSize':None,
			'title':None,
			'uGroup':None,
			__layout:None,
			GRiNSns+' ' 'comment':None,
			},
##		'seq': {'abstract':'',
##			'author':'',
##			'begin':None,
##			'copyright':'',
##			'dur':None,
##			'end':None,
##			'fill':None,
##			'id':None,
##			'repeat':'1',
##			'repeatCount':None,
##			'repeatDur':None,
##			'restart':None,
##			'system-bitrate':None,
##			'system-captions':None,
##			'system-language':None,
##			'system-overdub-or-caption':None,
##			'system-required':None,
##			'system-screen-depth':None,
##			'system-screen-size':None,
##			'systemBitrate':None,
##			'systemCaptions':None,
##			'systemLanguage':None,
##			'systemOverdubOrCaption':None,
##			'systemRequired':None,
##			'systemScreenDepth':None,
##			'systemScreenSize':None,
##			'title':None,
##			'uGroup':None,
##			__layout:None,
##			GRiNSns+' ' 'comment':None,
##			},
		'switch': {'id':None,
			   'system-bitrate':None,
			   'system-captions':None,
			   'system-language':None,
			   'system-overdub-or-caption':None,
			   'system-required':None,
			   'system-screen-depth':None,
			   'system-screen-size':None,
			   'systemBitrate':None,
			   'systemCaptions':None,
			   'systemLanguage':None,
			   'systemOverdubOrCaption':None,
			   'systemRequired':None,
			   'systemScreenDepth':None,
			   'systemScreenSize':None,
			   'uGroup':None,
			   __layout:None},
		'excl': {'abstract':'',
			 'author':'',
			 'begin':None,
			 'copyright':'',
			 'dur':None,
			 'end':None,
			 'endsync':None,
			 'fill':None,
			 'id':None,
			 'region':None,
			 'repeat':'1',
			 'repeatCount':None,
			 'repeatDur':None,
			 'restart':None,
			 'system-bitrate':None,
			 'system-captions':None,
			 'system-language':None,
			 'system-overdub-or-caption':None,
			 'system-required':None,
			 'system-screen-depth':None,
			 'system-screen-size':None,
			 'systemBitrate':None,
			 'systemCaptions':None,
			 'systemLanguage':None,
			 'systemOverdubOrCaption':None,
			 'systemRequired':None,
			 'systemScreenDepth':None,
			 'systemScreenSize':None,
			 'title':None,
			 'uGroup':None,
			 __layout:None,
			 GRiNSns+' ' 'comment':None,
			 },
		__choice: {GRiNSns+' ' 'abstract':'',
			   GRiNSns+' ' 'author':'',
			   GRiNSns+' ' 'choice-index':None,
			   GRiNSns+' ' 'copyright':'',
			   GRiNSns+' ' 'id':None,
			   GRiNSns+' ' 'restart':None,
			   GRiNSns+' ' 'system-bitrate':None,
			   GRiNSns+' ' 'system-captions':None,
			   GRiNSns+' ' 'system-language':None,
			   GRiNSns+' ' 'system-overdub-or-caption':None,
			   GRiNSns+' ' 'system-required':None,
			   GRiNSns+' ' 'system-screen-depth':None,
			   GRiNSns+' ' 'system-screen-size':None,
			   GRiNSns+' ' 'systemBitrate':None,
			   GRiNSns+' ' 'systemCaptions':None,
			   GRiNSns+' ' 'systemLanguage':None,
			   GRiNSns+' ' 'systemOverdubOrCaption':None,
			   GRiNSns+' ' 'systemRequired':None,
			   GRiNSns+' ' 'systemScreenDepth':None,
			   GRiNSns+' ' 'systemScreenSize':None,
			   GRiNSns+' ' 'title':None,
			   GRiNSns+' ' 'uGroup':None,
			   __layout:None,
			   GRiNSns+' ' 'comment':None,
			   },
		'ref': {'abstract':'',
			'alt':None,
			'author':'',
			'begin':None,
			'clip-begin':None,
			'clip-end':None,
			'copyright':'',
			'dur':None,
			'end':None,
			'fill':None,
			'id':None,
			'longdesc':None,
			'region':None,
			'repeat':'1',
			'repeatCount':None,
			'repeatDur':None,
			'restart':None,
			'src':None,
			'system-bitrate':None,
			'system-captions':None,
			'system-language':None,
			'system-overdub-or-caption':None,
			'system-required':None,
			'system-screen-depth':None,
			'system-screen-size':None,
			'systemBitrate':None,
			'systemCaptions':None,
			'systemLanguage':None,
			'systemOverdubOrCaption':None,
			'systemRequired':None,
			'systemScreenDepth':None,
			'systemScreenSize':None,
			'title':None,
			'type':None,
			'uGroup':None,
			__layout:None,
			GRiNSns+' ' 'bgcolor':None,
			GRiNSns+' ' 'comment':None,
			GRiNSns+' ' 'font':None,
			GRiNSns+' ' 'hicolor':None,
			GRiNSns+' ' 'pointsize':None,
			GRiNSns+' ' 'scale':None,
			GRiNSns+' ' 'captionchannel':None,
			GRiNSns+' ' 'project_audiotype':None,
			GRiNSns+' ' 'project_mobile':None,
			GRiNSns+' ' 'project_perfect':None,
			GRiNSns+' ' 'project_quality':None,
			GRiNSns+' ' 'project_targets':None,
			GRiNSns+' ' 'project_videotype':None,
			},
		'a': {'href':None,
		      'id':None,
		      'show':'replace',
		      'title':None},
		'anchor': {'begin':None,
			   'coords':None,
			   'end':None,
			   'href':None,
			   'id':None,
			   'show':'replace',
			   'skip-content':'true',
			   'title':None,
			   GRiNSns+' ' 'fragment-id':None},
		'area': {'begin':None,
			   'coords':None,
			   'end':None,
			   'href':None,
			   'id':None,
			   'show':'replace',
			   'skip-content':'true',
			   'title':None,
			   GRiNSns+' ' 'fragment-id':None},
		'userAttributes': {'id':None,},
		'uGroup': {GRiNSns+' ' 'id':None,
			    GRiNSns+' ' 'u-state':'RENDERED',
			    GRiNSns+' ' 'title':None,
			    GRiNSns+' ' 'override':'allowed',
			    },
		'uGroup': {'id':None,
			   'uState':'RENDERED',
			   'title':None,
##			   'override':'allowed',
			   },
		}
	attributes['seq'] = attributes['body']
	attributes[__bag] = attributes[__choice]

	__media_object = ['audio', 'video', 'text', 'img', 'animation',
			  'textstream', 'ref', __null, __cmif, __shell,
			  __socket]

	__at = None
	for __el in __media_object:
		if ' ' in __el:
			attributes[__el] = __at = {}
			for key, val in attributes['ref'].items():
				if ' ' in key:
					__at[key] = val
				else:
					__at[GRiNSns+' '+key] = val
		else:
			attributes[__el] = attributes['ref']
	del __el, __at

	__schedule = ['par', 'seq', 'excl', __choice, __bag] + __media_object
	__container_content = __schedule + ['switch', 'a']
	__assoc_link = ['anchor', 'area']

	# all entities with their allowed content
	# no allowed content is default, so we don't specify empty ones here
	entities = {
		'smil': ['head', 'body'],
		'head': ['layout', 'switch', 'meta', 'userAttributes', __layouts],
		'userAttributes': ['uGroup'],
		'layout': ['region', 'root-layout', 'top-layout'],
		'top-layout': ['region'],
		'region': ['region'],
		__layouts: [__layout],
		'body': __container_content,
		'par': __container_content,
		'seq': __container_content,
		'excl': __container_content,
		__choice: __container_content,
		__bag: __container_content,
		'switch': ['layout'] + __container_content,
		'ref': __assoc_link,
		'audio': __assoc_link,
		'img': __assoc_link,
		'video': __assoc_link,
		'text': __assoc_link,
		'animation': __assoc_link,
		'textstream': __assoc_link,
		__null: __assoc_link,
		__cmif: __assoc_link,
		__shell: __assoc_link,
		__socket: __assoc_link,
		'a': __schedule + ['switch'],
		}

	# cleanup
	del __choice, __bag, __cmif, __shell, __socket
	del __media_object, __schedule, __container_content,
	del __assoc_link
	del __layouts, __layout
