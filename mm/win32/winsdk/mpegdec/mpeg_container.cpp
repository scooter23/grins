#include "mpeg_container.h"

#include "streams/mpeg2demux.h"
#include "streams/mpeg2io.h"

#ifdef USE_AUDIO_STREAM
#include "audio/mpeg2audio.h"
#endif

//#include "video/mpeg2video.h"


#include <stdlib.h>
#include <memory.h>

///////////////
// open platform input stream
#include "wnds_mpeg_input_stream.h"

mpeg_input_stream *open_mpeg_input_stream(TCHAR *path)
	{
	wnds_mpeg_input_stream *p = new wnds_mpeg_input_stream(path);
	if(p != NULL && !p->is_valid())
		{
		delete p;
		p = NULL;
		}
	return p;
	}


///////////////
mpeg_container::mpeg_container() 
:	m_pmpeg2(0)
	{
	}

mpeg_container::~mpeg_container()
	{
	close();
	}

bool mpeg_container::open(const TCHAR *path, bool create_streams)
	{
	// Initialize the file structure
	m_pmpeg2 = new mpeg2_t;
	memset(m_pmpeg2, 0, sizeof(mpeg2_t));
	m_pmpeg2->fs = mpeg2_new_fs((TCHAR *)path);
	m_pmpeg2->demuxer = mpeg2_new_demuxer(m_pmpeg2, 0, 0, -1);
	m_pmpeg2->cpus = 1;

	// Need to perform authentication before reading a single byte
	if(mpeg2io_open_file(m_pmpeg2->fs))
		{
		close();
		return false;
		}

	// ============= Create the title objects ================== 

	unsigned int bits = mpeg2io_read_int32(m_pmpeg2->fs);

	if(bits == MPEG2_TOC_PREFIX || bits == MPEG2_TOC_PREFIXLOWER) 
		{
		if(bits == MPEG2_TOC_PREFIX) printf("MPEG2_TOC_PREFIX\n");
		else if(bits == MPEG2_TOC_PREFIXLOWER) printf("MPEG2_TOC_PREFIXLOWER\n");
		// Table of contents for another file
		if(!read_toc())
			{
			close();
			return false;
			}
		mpeg2io_close_file(m_pmpeg2->fs);
		}
	else if(((bits >> 24) & 0xff) == MPEG2_SYNC_BYTE)
		{
		// Transport stream
		//printf("Transport stream\n");
		m_pmpeg2->packet_size = MPEG2_TS_PACKET_SIZE;
		m_pmpeg2->is_transport_stream = 1;
		}
	else if(bits == MPEG2_PACK_START_CODE)
		{
		// *** Program stream
		//printf("Program stream\n");
		m_pmpeg2->packet_size = MPEG2_DVD_PACKET_SIZE;
		m_pmpeg2->is_program_stream = 1;
		}
	else if((bits & 0xfff00000) == 0xfff00000 ||
		((bits >> 8) == MPEG2_ID3_PREFIX) ||
		(bits == MPEG2_RIFF_CODE))
		{
		// MPEG Audio only
		//printf("MPEG Audio only\n");
		m_pmpeg2->packet_size = MPEG2_DVD_PACKET_SIZE;
		m_pmpeg2->has_audio = 1;
		m_pmpeg2->is_audio_stream = 1;
		}
	else if(bits == MPEG2_SEQUENCE_START_CODE ||
		bits == MPEG2_PICTURE_START_CODE)
		{
		// Video only
		//printf("Video only\n");
		m_pmpeg2->packet_size = MPEG2_DVD_PACKET_SIZE;
		m_pmpeg2->is_video_stream = 1;
		}
	else if(((bits & 0xffff0000) >> 16) == MPEG2_AC3_START_CODE)
		{
		// AC3 Audio only
		//printf("AC3 Audio only\n");
		m_pmpeg2->packet_size = MPEG2_DVD_PACKET_SIZE;
		m_pmpeg2->has_audio = 1;
		m_pmpeg2->is_audio_stream = 1;
		}
	else
		{
		close();
		fprintf(stderr, "mpeg2_open: not an MPEG 2 stream\n");
		return false;
		}

	// Create title 
	if(!m_pmpeg2->demuxer->total_titles)
		{
		mpeg2demux_create_title(m_pmpeg2->demuxer, 0, 0);
		}

	//  ====== Get title information =====================
	
	if((m_pmpeg2->is_transport_stream || m_pmpeg2->is_program_stream) && create_streams)
		{
		//printf("Create audio and video tracks\n");
		// Create video tracks
		// Video must be created before audio because audio uses the video timecode to get its length
		/*
		for(int i = 0; i < MPEG2_MAX_STREAMS; i++)
			{
			if(m_pmpeg2->demuxer->vstream_table[i])
				{
				printf("Create video track %d\n", i);
				m_pmpeg2->vtrack[m_pmpeg2->total_vstreams] = mpeg2_new_vtrack(m_pmpeg2, i, m_pmpeg2->demuxer);
				if(m_pmpeg2->vtrack[m_pmpeg2->total_vstreams]) m_pmpeg2->total_vstreams++;
				}
			}
		*/
		// Create audio tracks
#ifdef USE_AUDIO_STREAM
		for(int i = 0; i < MPEG2_MAX_STREAMS; i++)
			{
			if(m_pmpeg2->demuxer->astream_table[i])
				{
				//printf("Create audio track %d\n", i);
				m_pmpeg2->atrack[m_pmpeg2->total_astreams] = 
					mpeg2_new_atrack(m_pmpeg2, i, m_pmpeg2->demuxer->astream_table[i], m_pmpeg2->demuxer);
				if(m_pmpeg2->atrack[m_pmpeg2->total_astreams]) m_pmpeg2->total_astreams++;
				}
			}
#endif // USE_AUDIO_STREAM
		}
	else if(m_pmpeg2->is_video_stream && create_streams)
		{
		//printf("Create video track\n");
		// Create video tracks
		//m_pmpeg2->vtrack[0] = mpeg2_new_vtrack(m_pmpeg2, -1, m_pmpeg2->demuxer);
		//if(m_pmpeg2->vtrack[0]) m_pmpeg2->total_vstreams++;
		}
	else if(m_pmpeg2->is_audio_stream && create_streams)
		{
		//printf("Create audio track\n");
		// Create audio tracks
#ifdef USE_AUDIO_STREAM
		m_pmpeg2->atrack[0] = mpeg2_new_atrack(m_pmpeg2, -1, AUDIO_UNKNOWN, m_pmpeg2->demuxer);
		if(m_pmpeg2->atrack[0]) m_pmpeg2->total_astreams++;
#endif // USE_AUDIO_STREAM
		}

	if(m_pmpeg2->total_vstreams) m_pmpeg2->has_video = 1;
	if(m_pmpeg2->total_astreams) m_pmpeg2->has_audio = 1;
	mpeg2io_close_file(m_pmpeg2->fs);
	return true;
	}



void mpeg_container::close()
	{
	if(m_pmpeg2 != 0) 
		{
		//for(int i = 0; i < m_pmpeg2->total_vstreams; i++)
		//	mpeg2_delete_vtrack(m_pmpeg2, m_pmpeg2->vtrack[i]);

#ifdef USE_AUDIO_STREAM
		for(int i = 0; i < m_pmpeg2->total_astreams; i++)
			mpeg2_delete_atrack(m_pmpeg2, m_pmpeg2->atrack[i]);
#endif

		mpeg2_delete_fs(m_pmpeg2->fs);
		mpeg2_delete_demuxer(m_pmpeg2->demuxer);
		delete m_pmpeg2;
		m_pmpeg2 = 0;
		}
	}

bool mpeg_container::read_toc()
	{
	return true;
	}

double mpeg_container::get_duration()
	{
	return m_pmpeg2->demuxer->time; 
	}

#ifdef USE_AUDIO_STREAM

long mpeg_container::read_audio(short *output, long samples, int stream, int channel)
	{
	if(!m_pmpeg2->has_audio) return 0;
	long writelen = 0;
	bool res = mpeg2audio_decode_audio(m_pmpeg2->atrack[stream]->audio, output, channel, 
		m_pmpeg2->atrack[stream]->current_position, samples, &writelen);
	if(!res) return 0;
	m_pmpeg2->last_type_read = 1;
	m_pmpeg2->last_stream_read = stream;
	m_pmpeg2->atrack[stream]->current_position += writelen;
	return writelen;
	}

long mpeg_container::read_audio(std::basic_string<char>& audio_data, int stream, int channel)
	{
	if(!m_pmpeg2->has_audio) return 0;
	size_t ts = m_pmpeg2->atrack[stream]->total_samples + 8*1024;
	audio_data.reserve(ts);
	int samples = 8*1024;
	short *output = new short[samples];
	while(true)
		{
		long n = read_audio(output, samples, stream, channel);
		if(n == 0) break;
		audio_data.append((char*)output, 2*n);
		}
	delete[] output;
	return audio_data.size();
	}


long mpeg_container::read_audio_chunk(char **pp, int stream, int channel)
	{
	*pp = 0;
	if(!m_pmpeg2->has_audio) return 0;
	if(m_pmpeg2->atrack[stream]->total_samples == m_pmpeg2->atrack[stream]->current_position)
		return 0;
	size_t ts = 128*1024;
	*pp = new char[ts];
	int samples = ts/2;
	long n = read_audio((short*)*pp, samples, stream, channel);
	return 2*n;
	}

long mpeg_container::read_raw_audio_chunk(char **pp, size_t ts, int stream, int channel)
	{
	*pp = 0;
	if(!m_pmpeg2->has_audio) return 0;
	*pp = new char[ts];
	long size = 0;
	int ret = mpeg2audio_read_raw(m_pmpeg2->atrack[stream]->audio, (unsigned char*)*pp, &size, ts);
	if(ret != 0 || size==0)
		{
		delete *pp;
		*pp = 0;
		return 0;
		}
	return size;
	}

#endif // USE_AUDIO_STREAM

