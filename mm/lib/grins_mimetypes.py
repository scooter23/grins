"""Additional MIME types for the GRiNS player and editor."""

mimetypes = {
	'.smi': 'application/smil',
	'.smil': 'application/smil',
	'.cmi': 'application/x-grins-cmif',
	'.cmif': 'application/x-grins-cmif',
	'.grins': 'application/x-grins-project',

	'.ra': 'audio/vnd.rn-realaudio',
	'.ram': 'audio/x-pn-realaudio',
	'.rmm': 'audio/x-pn-realaudio',
	'.rp': 'image/vnd.rn-realpix',
	'.rt': 'text/vnd.rn-realtext',
	'.rv': 'video/vnd.rn-realvideo',
	'.rf': 'image/vnd.rn-realflash',
	'.swf': 'application/x-shockwave-flash',
	'.rm': 'application/vnd.rn-realmedia',

	'.mp3': 'audio/mpeg',
	}

descriptions = {
	'application/smil': 'SMIL presentations',
	'application/x-grins-cmif': 'CMIF presentations',
	'application/x-grins-project': 'GRiNS Project files',
}
