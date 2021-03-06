#include "mpeg_video.h"

#include "mpeg2con.h"

#include "mpeg_video_bitstream.h"

#include "mpeg_video_globals.h"


/* decode all macroblocks of the current picture */
/* stages described in ISO/IEC 13818-2 section 7 */
void mpeg_video::picture_data(int framenum)
{
  int MBAmax;
  int ret;

  /* number of macroblocks per picture */
  MBAmax = mb_width*mb_height;

  if (picture_structure!=FRAME_PICTURE)
    MBAmax>>=1; /* field picture has half as mnay macroblocks as frame */

  for(;;)
	{
    if((ret=slice(framenum, MBAmax))<0)
      return;
	}
}


/* decode all macroblocks of the current picture */
/* ISO/IEC 13818-2 section 6.3.16 */
int mpeg_video::slice(int framenum, int MBAmax)
{
  int MBA; 
  int MBAinc, macroblock_type, motion_type, dct_type;
  int dc_dct_pred[3];
  int PMV[2][2][2], motion_vertical_field_select[2][2];
  int dmvector[2];
  int stwtype, stwclass;
  //int SNRMBA, SNRMBAinc;
  int ret;

  MBA = 0; /* macroblock address */
  MBAinc = 0;

  if((ret=start_of_slice(MBAmax, &MBA, &MBAinc, dc_dct_pred, PMV))!=1)
    return(ret);

  //if (Two_Streams && enhan.scalable_mode==SC_SNR)
  //{
  //  SNRMBA=0;
  //  SNRMBAinc=0;
  //}

  Fault_Flag=0;

  for (;;)
  {

    /* this is how we properly exit out of picture */
    if (MBA>=MBAmax)
      return(-1); /* all macroblocks decoded */

    if (MBAinc==0)
    {
      //if (m_pld->scalable_mode==SC_DP && m_pld->priority_breakpoint==1)
          //m_pld = &enhan;

      if (!m_bitstream->next_bits(23) || Fault_Flag) /* next_start_code or fault */
      {
resync: /* if Fault_Flag: resynchronize to next next_start_code */
        Fault_Flag = 0;
        return(0);     /* trigger: go to next slice */
      }
      else /* neither next_start_code nor Fault_Flag */
      {
        //if (m_pld->scalable_mode==SC_DP && m_pld->priority_breakpoint==1)
          //m_pld = &enhan;

        /* decode macroblock address increment */
        MBAinc = get_macroblock_address_increment();

        if (Fault_Flag) goto resync;
      }
    }

    if (MBA>=MBAmax)
    {
      /* MBAinc points beyond picture dimensions */
      if (!Quiet_Flag)
        printf("Too many macroblocks in picture\n");
      return(-1);
    }

    if (MBAinc==1) /* not skipped */
    {
      ret = decode_macroblock(&macroblock_type, &stwtype, &stwclass,
              &motion_type, &dct_type, PMV, dc_dct_pred, 
              motion_vertical_field_select, dmvector);

      if(ret==-1)
        return(-1);
   
      if(ret==0)
        goto resync;

    }
    else /* MBAinc!=1: skipped macroblock */
    {      
      /* ISO/IEC 13818-2 section 7.6.6 */
      skipped_macroblock(dc_dct_pred, PMV, &motion_type, 
        motion_vertical_field_select, &stwtype, &macroblock_type);
    }

    /* SCALABILITY: SNR */
    /* ISO/IEC 13818-2 section 7.8 */
    /* NOTE: we currently ignore faults encountered in this routine */
    //if (Two_Streams && enhan.scalable_mode==SC_SNR)
      //Decode_SNR_Macroblock(&SNRMBA, &SNRMBAinc, MBA, MBAmax, &dct_type);

    /* ISO/IEC 13818-2 section 7.6 */
    motion_compensation(MBA, macroblock_type, motion_type, PMV, 
      motion_vertical_field_select, dmvector, stwtype, dct_type);


    /* advance to next macroblock */
    MBA++;
    MBAinc--;
 
    /* SCALABILITY: SNR */
    //if (Two_Streams && enhan.scalable_mode==SC_SNR)
    //{
    //  SNRMBA++;
    //  SNRMBAinc--;
    //}

    if (MBA>=MBAmax)
      return(-1); /* all macroblocks decoded */
  }
}

 
/* ISO/IEC 13818-2 section 6.3.17.1: Macroblock modes */
void mpeg_video::macroblock_modes (int *pmacroblock_type, int *pstwtype, int *pstwclass, 
		int *pmotion_type, int *pmotion_vector_count, int *pmv_format, int *pdmv,
		int *pmvscale, int *pdct_type)
{
  int macroblock_type;
  int stwtype, stwcode, stwclass;
  int motion_type = 0;
  int motion_vector_count, mv_format, dmv, mvscale;
  int dct_type;
  static unsigned char stwc_table[3][4]
    = { {6,3,7,4}, {2,1,5,4}, {2,5,7,4} };
  static unsigned char stwclass_table[9]
    = {0, 1, 2, 1, 1, 2, 3, 3, 4};

  /* get macroblock_type */
  macroblock_type = get_macroblock_type();

  if (Fault_Flag) return;

  /* get spatial_temporal_weight_code */
  if (macroblock_type & MB_WEIGHT)
  {
    if (spatial_temporal_weight_code_table_index==0)
      stwtype = 4;
    else
    {
      stwcode = m_bitstream->get_bits(2);
#ifdef TRACE
      if (Trace_Flag)
      {
        printf("spatial_temporal_weight_code (");
        Print_Bits(stwcode,2,2);
        printf("): %d\n",stwcode);
      }
#endif /* TRACE */
      stwtype = stwc_table[spatial_temporal_weight_code_table_index-1][stwcode];
    }
  }
  else
    stwtype = (macroblock_type & MB_CLASS4) ? 8 : 0;

  /* SCALABILITY: derive spatial_temporal_weight_class (Table 7-18) */
  stwclass = stwclass_table[stwtype];

  /* get frame/field motion type */
  if (macroblock_type & (MACROBLOCK_MOTION_FORWARD|MACROBLOCK_MOTION_BACKWARD))
  {
    if (picture_structure==FRAME_PICTURE) /* frame_motion_type */
    {
      motion_type = frame_pred_frame_dct ? MC_FRAME : m_bitstream->get_bits(2);
#ifdef TRACE
      if (!frame_pred_frame_dct && Trace_Flag)
      {
        printf("frame_motion_type (");
        Print_Bits(motion_type,2,2);
        printf("): %s\n",motion_type==MC_FIELD?"Field":
                         motion_type==MC_FRAME?"Frame":
                         motion_type==MC_DMV?"Dual_Prime":"Invalid");
      }
#endif /* TRACE */
    }
    else /* field_motion_type */
    {
      motion_type = m_bitstream->get_bits(2);
#ifdef TRACE
      if (Trace_Flag)
      {
        printf("field_motion_type (");
        Print_Bits(motion_type,2,2);
        printf("): %s\n",motion_type==MC_FIELD?"Field":
                         motion_type==MC_16X8?"16x8 MC":
                         motion_type==MC_DMV?"Dual_Prime":"Invalid");
      }
#endif /* TRACE */
    }
  }
  else if ((macroblock_type & MACROBLOCK_INTRA) && concealment_motion_vectors)
  {
    /* concealment motion vectors */
    motion_type = (picture_structure==FRAME_PICTURE) ? MC_FRAME : MC_FIELD;
  }
#if 0
  else
  {
    printf("maroblock_modes(): unknown macroblock type\n");
    motion_type = -1;
  }
#endif

  /* derive motion_vector_count, mv_format and dmv, (table 6-17, 6-18) */
  if (picture_structure==FRAME_PICTURE)
  {
    motion_vector_count = (motion_type==MC_FIELD && stwclass<2) ? 2 : 1;
    mv_format = (motion_type==MC_FRAME) ? MV_FRAME : MV_FIELD;
  }
  else
  {
    motion_vector_count = (motion_type==MC_16X8) ? 2 : 1;
    mv_format = MV_FIELD;
  }

  dmv = (motion_type==MC_DMV); /* dual prime */

  /* field mv predictions in frame pictures have to be scaled
   * ISO/IEC 13818-2 section 7.6.3.1 Decoding the motion vectors
   * IMPLEMENTATION: mvscale is derived for later use in motion_vectors()
   * it displaces the stage:
   *
   *    if((mv_format=="field")&&(t==1)&&(picture_structure=="Frame picture"))
   *      prediction = PMV[r][s][t] DIV 2;
   */

  mvscale = ((mv_format==MV_FIELD) && (picture_structure==FRAME_PICTURE));

  /* get dct_type (frame DCT / field DCT) */
  dct_type = (picture_structure==FRAME_PICTURE)
             && (!frame_pred_frame_dct)
             && (macroblock_type & (MACROBLOCK_PATTERN|MACROBLOCK_INTRA))
             ? m_bitstream->get_bits(1)
             : 0;

#ifdef TRACE
  if (Trace_Flag  && (picture_structure==FRAME_PICTURE)
             && (!frame_pred_frame_dct)
             && (macroblock_type & (MACROBLOCK_PATTERN|MACROBLOCK_INTRA)))
    printf("dct_type (%d): %s\n",dct_type,dct_type?"Field":"Frame");
#endif /* TRACE */

  /* return values */
  *pmacroblock_type = macroblock_type;
  *pstwtype = stwtype;
  *pstwclass = stwclass;
  *pmotion_type = motion_type;
  *pmotion_vector_count = motion_vector_count;
  *pmv_format = mv_format;
  *pdmv = dmv;
  *pmvscale = mvscale;
  *pdct_type = dct_type;
}


/* move/add 8x8-Block from block[comp] to backward_reference_frame */
/* copy reconstructed 8x8 block from block[comp] to current_frame[]
 * ISO/IEC 13818-2 section 7.6.8: Adding prediction and coefficient data
 * This stage also embodies some of the operations implied by:
 *   - ISO/IEC 13818-2 section 7.6.7: Combining predictions
 *   - ISO/IEC 13818-2 section 6.1.3: Macroblock
*/
void mpeg_video::add_block (int comp, int bx, int by, int dct_type, int addflag)
{
  int cc,i, j, iincr;
  unsigned char *rfp;
  short *bp;

  
  /* derive color component index */
  /* equivalent to ISO/IEC 13818-2 Table 7-1 */
  cc = (comp<4) ? 0 : (comp&1)+1; /* color component index */

  if (cc==0)
  {
    /* luminance */

    if (picture_structure==FRAME_PICTURE)
      if (dct_type)
      {
        /* field DCT coding */
        rfp = current_frame[0]
              + Coded_Picture_Width*(by+((comp&2)>>1)) + bx + ((comp&1)<<3);
        iincr = (Coded_Picture_Width<<1) - 8;
      }
      else
      {
        /* frame DCT coding */
        rfp = current_frame[0]
              + Coded_Picture_Width*(by+((comp&2)<<2)) + bx + ((comp&1)<<3);
        iincr = Coded_Picture_Width - 8;
      }
    else
    {
      /* field picture */
      rfp = current_frame[0]
            + (Coded_Picture_Width<<1)*(by+((comp&2)<<2)) + bx + ((comp&1)<<3);
      iincr = (Coded_Picture_Width<<1) - 8;
    }
  }
  else
  {
    /* chrominance */

    /* scale coordinates */
    if (chroma_format!=CHROMA444)
      bx >>= 1;
    if (chroma_format==CHROMA420)
      by >>= 1;
    if (picture_structure==FRAME_PICTURE)
    {
      if (dct_type && (chroma_format!=CHROMA420))
      {
        /* field DCT coding */
        rfp = current_frame[cc]
              + Chroma_Width*(by+((comp&2)>>1)) + bx + (comp&8);
        iincr = (Chroma_Width<<1) - 8;
      }
      else
      {
        /* frame DCT coding */
        rfp = current_frame[cc]
              + Chroma_Width*(by+((comp&2)<<2)) + bx + (comp&8);
        iincr = Chroma_Width - 8;
      }
    }
    else
    {
      /* field picture */
      rfp = current_frame[cc]
            + (Chroma_Width<<1)*(by+((comp&2)<<2)) + bx + (comp&8);
      iincr = (Chroma_Width<<1) - 8;
    }
  }

  bp = m_pld->block[comp];

  if (addflag)
  {
    for (i=0; i<8; i++)
    {
      for (j=0; j<8; j++)
      {
        *rfp = Clip[*bp++ + *rfp];
        rfp++;
      }

      rfp+= iincr;
    }
  }
  else
  {
    for (i=0; i<8; i++)
    {
      for (j=0; j<8; j++)
        *rfp++ = Clip[*bp++ + 128];

      rfp+= iincr;
    }
  }
}


/* ISO/IEC 13818-2 section 7.8 */
void mpeg_video::secode_snr_nacroblock (int *SNRMBA, int *SNRMBAinc, int MBA, int MBAmax, int *dct_type)
{
  int SNRmacroblock_type, SNRcoded_block_pattern, SNRdct_type, dummy; 
  int slice_vert_pos_ext, quantizer_scale_code, comp, code;

  //m_pld = &enhan;

  if (*SNRMBAinc==0)
  {
    if (!m_bitstream->next_bits(23)) /* next_start_code */
    {
      m_bitstream->next_start_code();
      code = m_bitstream->next_bits(32);

      if (code<MPEG2_SLICE_START_CODE_MIN || code>MPEG2_SLICE_START_CODE_MAX)
      {
        /* only slice headers are allowed in picture_data */
        if (!Quiet_Flag)
          printf("SNR: Premature end of picture\n");
        return;
      }

      m_bitstream->flush_buffer32();

      /* decode slice header (may change quantizer_scale) */
      slice_vert_pos_ext = slice_header();

      /* decode macroblock address increment */
      *SNRMBAinc = get_macroblock_address_increment();

      /* set current location */
      *SNRMBA =
        ((slice_vert_pos_ext<<7) + (code&255) - 1)*mb_width + *SNRMBAinc - 1;

      *SNRMBAinc = 1; /* first macroblock in slice: not skipped */
    }
    else /* not next_start_code */
    {
      if (*SNRMBA>=MBAmax)
      {
        if (!Quiet_Flag)
          printf("Too many macroblocks in picture\n");
        return;
      }

      /* decode macroblock address increment */
      *SNRMBAinc = get_macroblock_address_increment();
    }
  }

  if (*SNRMBA!=MBA)
  {
    /* streams out of sync */
    if (!Quiet_Flag)
      printf("Cant't synchronize streams\n");
    return;
  }

  if (*SNRMBAinc==1) /* not skipped */
  {
    macroblock_modes(&SNRmacroblock_type, &dummy, &dummy,
      &dummy, &dummy, &dummy, &dummy, &dummy,
      &SNRdct_type);

    if (SNRmacroblock_type & MACROBLOCK_PATTERN)
      *dct_type = SNRdct_type;

    if (SNRmacroblock_type & MACROBLOCK_QUANT)
    {
      quantizer_scale_code = m_bitstream->get_bits(5);
      m_pld->quantizer_scale =
        m_pld->q_scale_type ? Non_Linear_quantizer_scale[quantizer_scale_code] : quantizer_scale_code<<1;
    }

    /* macroblock_pattern */
    if (SNRmacroblock_type & MACROBLOCK_PATTERN)
    {
      SNRcoded_block_pattern = get_coded_block_pattern();

      if (chroma_format==CHROMA422)
        SNRcoded_block_pattern = (SNRcoded_block_pattern<<2) | m_bitstream->get_bits(2); /* coded_block_pattern_1 */
      else if (chroma_format==CHROMA444)
        SNRcoded_block_pattern = (SNRcoded_block_pattern<<6) | m_bitstream->get_bits(6); /* coded_block_pattern_2 */
    }
    else
      SNRcoded_block_pattern = 0;

    /* decode blocks */
    for (comp=0; comp<block_count; comp++)
    {
      clear_block(comp);

      if (SNRcoded_block_pattern & (1<<(block_count-1-comp)))
        decode_mpeg2_non_intra_block(comp);
    }
  }
  else /* SNRMBAinc!=1: skipped macroblock */
  {
    for (comp=0; comp<block_count; comp++)
      clear_block(comp);
  }

  //m_pld = &base;
}



/* IMPLEMENTATION: set scratch pad macroblock to zero */
void mpeg_video::clear_block(int comp)
{
  short *Block_Ptr;
  int i;

  Block_Ptr = m_pld->block[comp];

  for (i=0; i<64; i++)
    *Block_Ptr++ = 0;
}


/* SCALABILITY: add SNR enhancement layer block data to base layer */
/* ISO/IEC 13818-2 section 7.8.3.4: Addition of coefficients from the two layes */
void mpeg_video::sum_block(int comp)
{
  //short *Block_Ptr1, *Block_Ptr2;
  //int i;

  //Block_Ptr1 = m_pld->block[comp];
  //Block_Ptr2 = enhan.block[comp];

  //for (i=0; i<64; i++)
  //  *Block_Ptr1++ += *Block_Ptr2++;
}


/* limit coefficients to -2048..2047 */
/* ISO/IEC 13818-2 section 7.4.3 and 7.4.4: Saturation and Mismatch control */
void mpeg_video::saturate(short *Block_Ptr)
{
  int i, sum, val;

  sum = 0;

  /* ISO/IEC 13818-2 section 7.4.3: Saturation */
  for (i=0; i<64; i++)
  {
    val = Block_Ptr[i];

    if (val>2047)
      val = 2047;
    else if (val<-2048)
      val = -2048;

    Block_Ptr[i] = val;
    sum+= val;
  }

  /* ISO/IEC 13818-2 section 7.4.4: Mismatch control */
  if ((sum&1)==0)
    Block_Ptr[63]^= 1;

}


/* reuse old picture buffers as soon as they are no longer needed 
   based on life-time axioms of MPEG */
void mpeg_video::update_picture_buffers()
{                           
  int cc;              /* color component index */
  unsigned char *tmp;  /* temporary swap pointer */

  for (cc=0; cc<3; cc++)
  {
    /* B pictures do not need to be save for future reference */
    if (picture_coding_type==B_TYPE)
    {
      current_frame[cc] = auxframe[cc];
    }
    else
    {
      /* only update at the beginning of the coded frame */
      if (!Second_Field)
      {
        tmp = forward_reference_frame[cc];

        /* the previously decoded reference frame is stored
           coincident with the location where the backward 
           reference frame is stored (backwards prediction is not
           needed in P pictures) */
        forward_reference_frame[cc] = backward_reference_frame[cc];
        
        /* update pointer for potential future B pictures */
        backward_reference_frame[cc] = tmp;
      }

      /* can erase over old backward reference frame since it is not used
         in a P picture, and since any subsequent B pictures will use the 
         previously decoded I or P frame as the backward_reference_frame */
      current_frame[cc] = backward_reference_frame[cc];
    }

    /* IMPLEMENTATION:
       one-time folding of a line offset into the pointer which stores the
       memory address of the current frame saves offsets and conditional 
       branches throughout the remainder of the picture processing loop */
    if (picture_structure==BOTTOM_FIELD)
      current_frame[cc]+= (cc==0) ? Coded_Picture_Width : Chroma_Width;
  }
}

/* ISO/IEC 13818-2 section 7.6 */
void mpeg_video::motion_compensation (int MBA, int macroblock_type, 
		int motion_type, int PMV[2][2][2], int motion_vertical_field_select[2][2], 
		int dmvector[2], int stwtype, int dct_type)
{
  int bx, by;
  int comp;

  /* derive current macroblock position within picture */
  /* ISO/IEC 13818-2 section 6.3.1.6 and 6.3.1.7 */
  bx = 16*(MBA%mb_width);
  by = 16*(MBA/mb_width);

  /* motion compensation */
  if (!(macroblock_type & MACROBLOCK_INTRA))
    form_predictions(bx,by,macroblock_type,motion_type,PMV,
      motion_vertical_field_select,dmvector,stwtype);
  
  /* SCALABILITY: Data Partitioning */
  //if (m_pld->scalable_mode==SC_DP)
    //m_pld = &base;

  /* copy or add block data into picture */
  for (comp=0; comp<block_count; comp++)
  {
    /* SCALABILITY: SNR */
    /* ISO/IEC 13818-2 section 7.8.3.4: Addition of coefficients from 
       the two a layers */
    //if (Two_Streams && enhan.scalable_mode==SC_SNR)
      //sum_block(comp); /* add SNR enhancement layer data to base layer */

    /* MPEG-2 saturation and mismatch control */
    /* base layer could be MPEG-1 stream, enhancement MPEG-2 SNR */
    /* ISO/IEC 13818-2 section 7.4.3 and 7.4.4: Saturation and Mismatch control */
    //if ((Two_Streams && enhan.scalable_mode==SC_SNR) || m_pld->MPEG2_Flag)
      //saturate(m_pld->block[comp]);

    /* ISO/IEC 13818-2 section Annex A: inverse DCT */
    //if (Reference_IDCT_Flag)
      //Reference_IDCT(m_pld->block[comp]);
    //else
      fast_idct(m_pld->block[comp]);
    
    /* ISO/IEC 13818-2 section 7.6.8: Adding prediction and coefficient data */
    add_block(comp,bx,by,dct_type,(macroblock_type & MACROBLOCK_INTRA)==0);
  }

}



/* ISO/IEC 13818-2 section 7.6.6 */
void mpeg_video::skipped_macroblock (int dc_dct_pred[3], int PMV[2][2][2], 
		int *motion_type, int motion_vertical_field_select[2][2],
		int *stwtype, int *macroblock_type)
{
  int comp;
  
  /* SCALABILITY: Data Paritioning */
  //if (m_pld->scalable_mode==SC_DP)
   // m_pld = &base;

  for (comp=0; comp<block_count; comp++)
    clear_block(comp);

  /* reset intra_dc predictors */
  /* ISO/IEC 13818-2 section 7.2.1: DC coefficients in intra blocks */
  dc_dct_pred[0]=dc_dct_pred[1]=dc_dct_pred[2]=0;

  /* reset motion vector predictors */
  /* ISO/IEC 13818-2 section 7.6.3.4: Resetting motion vector predictors */
  if (picture_coding_type==P_TYPE)
    PMV[0][0][0]=PMV[0][0][1]=PMV[1][0][0]=PMV[1][0][1]=0;

  /* derive motion_type */
  if (picture_structure==FRAME_PICTURE)
    *motion_type = MC_FRAME;
  else
  {
    *motion_type = MC_FIELD;

    /* predict from field of same parity */
    /* ISO/IEC 13818-2 section 7.6.6.1 and 7.6.6.3: P field picture and B field
       picture */
    motion_vertical_field_select[0][0]=motion_vertical_field_select[0][1] = 
      (picture_structure==BOTTOM_FIELD);
  }

  /* skipped I are spatial-only predicted, */
  /* skipped P and B are temporal-only predicted */
  /* ISO/IEC 13818-2 section 7.7.6: Skipped macroblocks */
  *stwtype = (picture_coding_type==I_TYPE) ? 8 : 0;

 /* IMPLEMENTATION: clear MACROBLOCK_INTRA */
  *macroblock_type&= ~MACROBLOCK_INTRA;

}



/* return==-1 means go to next picture */
/* the expression "start of slice" is used throughout the normative
   body of the MPEG specification */
int mpeg_video::start_of_slice (int MBAmax, int *MBA,
		int *MBAinc, int dc_dct_pred[3], int PMV[2][2][2])
{
  unsigned int code;
  int slice_vert_pos_ext;

  //m_pld = &base;

  Fault_Flag = 0;

  m_bitstream->next_start_code();
  code = m_bitstream->next_bits(32);

  if (code<MPEG2_SLICE_START_CODE_MIN || code>MPEG2_SLICE_START_CODE_MAX)
  {
    /* only slice headers are allowed in picture_data */
    if (!Quiet_Flag)
      printf("start_of_slice(): Premature end of picture\n");

    return(-1);  /* trigger: go to next picture */
  }

  m_bitstream->flush_buffer32(); 

  /* decode slice header (may change quantizer_scale) */
  slice_vert_pos_ext = slice_header();

 
  /* SCALABILITY: Data Partitioning */
  if (m_pld->scalable_mode==SC_DP)
  {
    //m_pld = &enhan;
    m_bitstream->next_start_code();
    code = m_bitstream->next_bits(32);

    if (code<MPEG2_SLICE_START_CODE_MIN || code>MPEG2_SLICE_START_CODE_MAX)
    {
      /* only slice headers are allowed in picture_data */
      if (!Quiet_Flag)
        printf("DP: Premature end of picture\n");
      return(-1);    /* trigger: go to next picture */
    }

    m_bitstream->flush_buffer32();

    /* decode slice header (may change quantizer_scale) */
    slice_vert_pos_ext = slice_header();

    //if (m_pld->priority_breakpoint!=1)
      //m_pld = &base;
  }

  /* decode macroblock address increment */
  *MBAinc = get_macroblock_address_increment();

  if (Fault_Flag) 
  {
    printf("start_of_slice(): MBAinc unsuccessful\n");
    return(0);   /* trigger: go to next slice */
  }

  /* set current location */
  /* NOTE: the arithmetic used to derive macroblock_address below is
   *       equivalent to ISO/IEC 13818-2 section 6.3.17: Macroblock
   */
  *MBA = ((slice_vert_pos_ext<<7) + (code&255) - 1)*mb_width + *MBAinc - 1;
  *MBAinc = 1; /* first macroblock in slice: not skipped */

  /* reset all DC coefficient and motion vector predictors */
  /* reset all DC coefficient and motion vector predictors */
  /* ISO/IEC 13818-2 section 7.2.1: DC coefficients in intra blocks */
  dc_dct_pred[0]=dc_dct_pred[1]=dc_dct_pred[2]=0;
  
  /* ISO/IEC 13818-2 section 7.6.3.4: Resetting motion vector predictors */
  PMV[0][0][0]=PMV[0][0][1]=PMV[1][0][0]=PMV[1][0][1]=0;
  PMV[0][1][0]=PMV[0][1][1]=PMV[1][1][0]=PMV[1][1][1]=0;

  /* successfull: trigger decode macroblocks in slice */
  return(1);
}


/* ISO/IEC 13818-2 sections 7.2 through 7.5 */
int mpeg_video::decode_macroblock (int *macroblock_type, 
		int *stwtype, int *stwclass, int *motion_type, int *dct_type,
		int PMV[2][2][2], int dc_dct_pred[3], 
		int motion_vertical_field_select[2][2], int dmvector[2])
{
  /* locals */
  int quantizer_scale_code; 
  int comp;

  int motion_vector_count; 
  int mv_format; 
  int dmv; 
  int mvscale;
  int coded_block_pattern;

  /* SCALABILITY: Data Patitioning */
  /*
  if (m_pld->scalable_mode==SC_DP)
  {
    if (m_pld->priority_breakpoint<=2)
      m_pld = &enhan;
    else
      m_pld = &base;
  }*/

  /* ISO/IEC 13818-2 section 6.3.17.1: Macroblock modes */
  macroblock_modes(macroblock_type, stwtype, stwclass,
    motion_type, &motion_vector_count, &mv_format, &dmv, &mvscale,
    dct_type);

  if (Fault_Flag) return(0);  /* trigger: go to next slice */

  if (*macroblock_type & MACROBLOCK_QUANT)
  {
    quantizer_scale_code = m_bitstream->get_bits(5);

#ifdef TRACE
    if (Trace_Flag)
    {
      printf("quantiser_scale_code (");
      Print_Bits(quantizer_scale_code,5,5);
      printf("): %d\n",quantizer_scale_code);
    }
#endif /* TRACE */

    /* ISO/IEC 13818-2 section 7.4.2.2: Quantizer scale factor */
    if (m_pld->MPEG2_Flag)
      m_pld->quantizer_scale =
      m_pld->q_scale_type ? Non_Linear_quantizer_scale[quantizer_scale_code] 
       : (quantizer_scale_code << 1);
    else
      m_pld->quantizer_scale = quantizer_scale_code;

    /* SCALABILITY: Data Partitioning */
    if (m_pld->scalable_mode==SC_DP)
      /* make sure m_pld->quantizer_scale is valid */
      m_pld->quantizer_scale = m_pld->quantizer_scale;
  }

  /* motion vectors */


  /* ISO/IEC 13818-2 section 6.3.17.2: Motion vectors */

  /* decode forward motion vectors */
  if ((*macroblock_type & MACROBLOCK_MOTION_FORWARD) 
    || ((*macroblock_type & MACROBLOCK_INTRA) 
    && concealment_motion_vectors))
  {
    if (m_pld->MPEG2_Flag)
      motion_vectors(PMV,dmvector,motion_vertical_field_select,
        0,motion_vector_count,mv_format,f_code[0][0]-1,f_code[0][1]-1,
        dmv,mvscale);
    else
      motion_vector(PMV[0][0],dmvector,
      forward_f_code-1,forward_f_code-1,0,0,full_pel_forward_vector);
  }

  if (Fault_Flag) return(0);  /* trigger: go to next slice */

  /* decode backward motion vectors */
  if (*macroblock_type & MACROBLOCK_MOTION_BACKWARD)
  {
    if (m_pld->MPEG2_Flag)
      motion_vectors(PMV,dmvector,motion_vertical_field_select,
        1,motion_vector_count,mv_format,f_code[1][0]-1,f_code[1][1]-1,0,
        mvscale);
    else
      motion_vector(PMV[0][1],dmvector,
        backward_f_code-1,backward_f_code-1,0,0,full_pel_backward_vector);
  }

  if (Fault_Flag) return(0);  /* trigger: go to next slice */

  if ((*macroblock_type & MACROBLOCK_INTRA) && concealment_motion_vectors)
    m_bitstream->flush_buffer(1); /* remove marker_bit */

  //if (m_pld->scalable_mode==SC_DP && m_pld->priority_breakpoint==3)
   // m_pld = &enhan;

  /* macroblock_pattern */
  /* ISO/IEC 13818-2 section 6.3.17.4: Coded block pattern */
  if (*macroblock_type & MACROBLOCK_PATTERN)
  {
    coded_block_pattern = get_coded_block_pattern();

    if (chroma_format==CHROMA422)
    {
      /* coded_block_pattern_1 */
      coded_block_pattern = (coded_block_pattern<<2) | m_bitstream->get_bits(2); 

#ifdef TRACE
       if (Trace_Flag)
       {
         printf("coded_block_pattern_1: ");
         Print_Bits(coded_block_pattern,2,2);
         printf(" (%d)\n",coded_block_pattern&3);
       }
#endif /* TRACE */
     }
     else if (chroma_format==CHROMA444)
     {
      /* coded_block_pattern_2 */
      coded_block_pattern = (coded_block_pattern<<6) | m_bitstream->get_bits(6); 

#ifdef TRACE
      if (Trace_Flag)
      {
        printf("coded_block_pattern_2: ");
        Print_Bits(coded_block_pattern,6,6);
        printf(" (%d)\n",coded_block_pattern&63);
      }
#endif /* TRACE */
    }
  }
  else
    coded_block_pattern = (*macroblock_type & MACROBLOCK_INTRA) ? 
      (1<<block_count)-1 : 0;

  if (Fault_Flag) return(0);  /* trigger: go to next slice */

  /* decode blocks */
  for (comp=0; comp<block_count; comp++)
  {
    /* SCALABILITY: Data Partitioning */
    //if (m_pld->scalable_mode==SC_DP)
    //m_pld = &base;

    clear_block(comp);

    if (coded_block_pattern & (1<<(block_count-1-comp)))
    {
      if (*macroblock_type & MACROBLOCK_INTRA)
      {
        if (m_pld->MPEG2_Flag)
          decode_mpeg2_intra_block(comp,dc_dct_pred);
        else
          decode_mpeg1_intra_block(comp,dc_dct_pred);
      }
      else
      {
        if (m_pld->MPEG2_Flag)
          decode_mpeg2_non_intra_block(comp);
        else
          decode_mpeg1_non_intra_block(comp);
      }

      if (Fault_Flag) return(0);  /* trigger: go to next slice */
    }
  }

  if(picture_coding_type==D_TYPE)
  {
    /* remove end_of_macroblock (always 1, prevents startcode emulation) */
    /* ISO/IEC 11172-2 section 2.4.2.7 and 2.4.3.6 */
    marker_bit("D picture end_of_macroblock bit");
  }

  /* reset intra_dc predictors */
  /* ISO/IEC 13818-2 section 7.2.1: DC coefficients in intra blocks */
  if (!(*macroblock_type & MACROBLOCK_INTRA))
    dc_dct_pred[0]=dc_dct_pred[1]=dc_dct_pred[2]=0;

  /* reset motion vector predictors */
  if ((*macroblock_type & MACROBLOCK_INTRA) && !concealment_motion_vectors)
  {
    /* intra mb without concealment motion vectors */
    /* ISO/IEC 13818-2 section 7.6.3.4: Resetting motion vector predictors */
    PMV[0][0][0]=PMV[0][0][1]=PMV[1][0][0]=PMV[1][0][1]=0;
    PMV[0][1][0]=PMV[0][1][1]=PMV[1][1][0]=PMV[1][1][1]=0;
  }

  /* special "No_MC" macroblock_type case */
  /* ISO/IEC 13818-2 section 7.6.3.5: Prediction in P pictures */
  if ((picture_coding_type==P_TYPE) 
    && !(*macroblock_type & (MACROBLOCK_MOTION_FORWARD|MACROBLOCK_INTRA)))
  {
    /* non-intra mb without forward mv in a P picture */
    /* ISO/IEC 13818-2 section 7.6.3.4: Resetting motion vector predictors */
    PMV[0][0][0]=PMV[0][0][1]=PMV[1][0][0]=PMV[1][0][1]=0;

    /* derive motion_type */
    /* ISO/IEC 13818-2 section 6.3.17.1: Macroblock modes, frame_motion_type */
    if (picture_structure==FRAME_PICTURE)
      *motion_type = MC_FRAME;
    else
    {
      *motion_type = MC_FIELD;
      /* predict from field of same parity */
      motion_vertical_field_select[0][0] = (picture_structure==BOTTOM_FIELD);
    }
  }

  if (*stwclass==4)
  {
    /* purely spatially predicted macroblock */
    /* ISO/IEC 13818-2 section 7.7.5.1: Resetting motion vector predictions */
    PMV[0][0][0]=PMV[0][0][1]=PMV[1][0][0]=PMV[1][0][1]=0;
    PMV[0][1][0]=PMV[0][1][1]=PMV[1][1][0]=PMV[1][1][1]=0;
  }

  /* successfully decoded macroblock */
  return(1);

} /* decode_macroblock */


