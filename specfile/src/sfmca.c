#/*##########################################################################
# Copyright (C) 2004-2007 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem to you.
#############################################################################*/
/*char RcsId[] = "$Header: /segfs/bliss/source/python/specfile/specfile-3.1/src/RCS/sfmca.c,v 1.3 2002/11/15 16:25:44 sole Exp $"; */
/************************************************************************
 *
 *   File:          sfmca.c
 *
 *   Project:       SpecFile library
 *
 *   Description:   Access to MCA spectra
 * 
 *   Author:        V.Rey
 *
 *   Date:          $Date: 2002/11/15 16:25:44 $
 *
 ************************************************************************/
/*
 *   Log: $Log: sfmca.c,v $
 *   Log: Revision 1.3  2002/11/15 16:25:44  sole
 *   Log: free(retline) replaced by freeArrNZ((void ***) &retline,nb_lines); to eliminate the memory leak when reading mca
 *   Log:
 *   Log: Revision 1.2  2002/11/15 10:44:36  sole
 *   Log: added free(retline) after call to SfHeader
 *   Log:
 *   Log: Revision 1.1  2002/11/15 10:17:38  sole
 *   Log: Initial revision
 *   Log:
 *   Log: Revision 3.0  2000/12/20 14:17:19  rey
 *   Log: Python version available
 *   Log:
 * Revision 2.1  2000/07/31  19:05:12  19:05:12  rey (Vicente Rey-Bakaikoa)
 * SfUpdate and bug corrected in ReadIndex
 * 
 * Revision 2.0  2000/04/13  13:28:54  13:28:54  rey (Vicente Rey-Bakaikoa)
 * New version of the library. Complete rewrite
 * Adds support for MCA
 */
#include <SpecFile.h>
#include <SpecFileP.h>

#include <ctype.h>
#include <stdlib.h>
/*
 * Define macro
 */
#define isnumber(this) ( isdigit(this) || this == '-' || this == '+'  || this =='e' || this == 'E' || this == '.' )

/*
 * Mca continuation character
 */
#define MCA_CONT '\\'
#define D_INFO   3

/*
 * Declarations
 */
DllExport long SfNoMca    ( SpecFile *sf, long index, int *error );
DllExport int  SfGetMca   ( SpecFile *sf, long index, long mcano, 
                                          double **retdata, int *error );
DllExport long SfMcaCalib ( SpecFile *sf, long index, double **calib, 
                                          int *error );


/*********************************************************************
 *   Function:        long SfNoMca( sf, index, error )
 *
 *   Description:    Gets number of mca spectra in a scan
 *
 *   Parameters:
 *        Input :    (1) File pointer   
 *            (2) Index
 *        Output:
 *            (3) error number
 *   Returns:
 *            Number of data lines , 
 *            ( -1 ) => errors.
 *   Possible errors:
 *            SF_ERR_SCAN_NOT_FOUND
 *
 *********************************************************************/
DllExport long
SfNoMca( SpecFile *sf, long index, int *error )
{

     if (sfSetCurrent(sf,index,error) == -1 )
             return(-1);

     return( ((SpecScan *)sf->current->contents)->mcaspectra );

}  


/*********************************************************************
 *   Function:        int SfGetMca(sf, index, number, data, error)
 *
 *   Description:    Gets data.
 *   Parameters:
 *        Input :    (1) File pointer   
 *            (2) Index
 *        Output:
 *            (3) Data array
 *            (4) Data info : [0] => no_lines
 *                    [1] => no_columns
 *                    [2] = ( 0 ) => regular    
 *                          ( 1 ) => not regular ! 
 *            (5) error number
 *   Returns:
 *            (  0 ) => OK
 *                ( -1 ) => errors occured
 *   Possible errors:
 *            SF_ERR_MEMORY_ALLOC   
 *            SF_ERR_FILE_READ
 *            SF_ERR_SCAN_NOT_FOUND
 *            SF_ERR_LINE_NOT_FOUND
 *
 *   Remark:  The memory allocated should be freed by the application
 *
 *********************************************************************/
DllExport int 
SfGetMca( SpecFile *sf, long index, long number, double **retdata, int *error )
{
     double  *data  = NULL;
     long     headersize;
     int                  old_fashion;
     static char*         last_from = NULL;
     static char*         last_pos = NULL;
     static long          last_number = 0;
     long int             scanno = 0;
     static long int last_scanno = 0;
     char *ptr,
          *from,
          *to;

     char    strval[100];
     double  val;

     int     i,spect_no=0;
     long    vals;

     long    blocks=1, 
             initsize=1024;


     headersize = ((SpecScan *)sf->current->contents)->data_offset
                - ((SpecScan *)sf->current->contents)->offset;
                
     scanno = ((SpecScan *)sf->current->contents)->scan_no;

    /*
     *  check that mca number is available
     */
    if (number < 1) {
        *error = SF_ERR_MCA_NOT_FOUND;
        *retdata = (double *)NULL;
         return(-1);
    }
     
    /* 
     * Get MCA info from header
     */

     from = sf->scanbuffer + headersize;
     to   = sf->scanbuffer + ((SpecScan *)sf->current->contents)->size;

     old_fashion = 1;
     if (last_scanno == scanno)
     {
         if (last_from == from)
         {
            /* same scan as before */
            if (number > last_number)
            {
                spect_no = last_number;
                old_fashion = 0;
            }
         }
    }
    if (old_fashion)
    {
        last_scanno = scanno;  
	    last_from = from;
        spect_no   = 0;
        last_pos  = from;
    }
     /*
      * go and find the beginning of spectrum 
      */
     ptr = last_pos;
  
     if ( *ptr == '@' ) {
         spect_no++;
         ptr++; 
         last_pos = ptr;
     } 

     while ( spect_no != number  && ptr < to ) {
            if (*ptr == '@') spect_no++;
            ptr++;
            last_pos = ptr;
     } 
     ptr++;

     if ( spect_no != number ) {
        *error = SF_ERR_MCA_NOT_FOUND;
        *retdata = (double *)NULL;
         return(-1);
     }
     last_number = spect_no;
    /*
     * Calculate size and book memory
     */ 
     initsize = 2048;

     i    = 0;
     vals = 0;

     /*
      * Alloc memory
      */
     if ((data = (double *)malloc (sizeof(double) * initsize)) == (double *)NULL) {
         *error = SF_ERR_MEMORY_ALLOC;
          return(-1);
     }

    /*
     * continue
     */
     for ( ;(*(ptr+1) != '\n' || (*ptr == MCA_CONT)) && ptr < to - 1 ; ptr++)
     { 
         if (*ptr == ' ' || *ptr == '\t' || *ptr == '\\' || *ptr == '\n') {
             if ( i ) {
                if ( vals%initsize  == 0 ) {
                    blocks++;
                    if ((data = (double *)realloc (data, sizeof(double) * blocks * initsize)) 
                                       == (double *)NULL) {
                          *error = SF_ERR_MEMORY_ALLOC;
                          return(-1);
                    }

                }
                strval[i] = '\0';
                i = 0;
                val = atof(strval);
                data[vals] = val;
                vals++;
             }
         } else if (isnumber(*ptr)) {
             strval[i] = *ptr;
             i++;
         }
     }

     if (isnumber(*ptr)) {
       strval[i]    = *ptr;
       strval[i+1]  = '\0';
       val = atof(strval);
       data[vals] = val;
       vals++;
     }

    *retdata = data;

     return( vals );
}


DllExport long 
SfMcaCalib ( SpecFile *sf, long index, double **calib, int *error )
{

     long   nb_lines;
     char **retline;
     char  *strptr;

     double val1,val2,val3;

     double *retdata;

     nb_lines   = SfHeader(sf,index,"@CALIB",&retline,error);

     if (nb_lines > 0) {
          strptr = retline[0] + 8; 
          sscanf(strptr,"%lf %lf %lf",&val1,&val2,&val3);
     }  else {
         *calib = (double *)NULL;
          return(-1);
     }

     retdata = (double *) malloc(sizeof(double) * 3 );
     retdata[0] = val1; retdata[1] = val2; retdata[2] = val3;

     *calib = retdata;
     return(0);
}
