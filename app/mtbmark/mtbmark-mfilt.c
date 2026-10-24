//========================================================================
// mtbmark-mfilt
//========================================================================
// We cannot easily reuse the single-threaded implementation since we
// want to partition by rows and need to also be careful about the
// windowing.

#include "mtbmark-mfilt.h"
#include "ece4750.h"

//------------------------------------------------------------------------
// arg_t
//------------------------------------------------------------------------
// This is used to pass arguments when we spawn work onto the cores.

typedef struct
{
  int* dest;  // pointer to dest array
  int* mask;  // pointer to mask array
  int* src;   // pointer to src array
  int  first; // first row this core should process
  int  last;  // (one past) last row this core should process
  int  size;  // number of columns
}
arg_t;

//------------------------------------------------------------------------
// Helper functions for setting and getting pixels in image
//------------------------------------------------------------------------

inline
void set( int* image, int size, int row, int col, int v )
{
  image[ row*size + col ] = v;
}

inline
int get( int* image, int size, int row, int col )
{
  return image[ row*size + col ];
}

//------------------------------------------------------------------------
// work
//------------------------------------------------------------------------
// Each thread uses the argument structure to figure out what rows it
// should work on.

void work( void* arg_vptr )
{
  // Cast void* to argument pointer.

  arg_t* arg_ptr = (arg_t*) arg_vptr;

  // Create local variables for each field of the argument structure.

  int* dest   = arg_ptr->dest;
  int* mask   = arg_ptr->mask;
  int* src    = arg_ptr->src;
  int  first = arg_ptr->first;
  int  last   = arg_ptr->last;
  int  size   = arg_ptr->size;

  int coeff0 = 8;
  int coeff1 = 6;

  // norm is calculated as coeff0 + 4*coeff1. Because it is a power of 2,
  // we can represent it as a shift

  int norm_shamt = 5;

  for ( int i = first; i < last; i++ ) {
    for ( int j = 0; j < size; j++ ) {

      // Set pixels at edge to be zero

      if ( (i == 0) || (i == size-1) || (j == 0) || (j == size-1) )
        set( dest, size, i, j, 0 );

      else {

        // If mask is set, then do the filter ...

        if ( get( mask, size, i, j ) != 0 ) {
          int out0 = get( src, size, i-1, j   ) * coeff1;
          int out1 = get( src, size, i,   j-1 ) * coeff1;
          int out2 = get( src, size, i,   j   ) * coeff0;
          int out3 = get( src, size, i,   j+1 ) * coeff1;
          int out4 = get( src, size, i+1, j   ) * coeff1;
          int out  = out0 + out1 + out2 + out3 + out4;
          set( dest, size, i, j, out >> norm_shamt );
        }

        // ... otherwise copy src to dest

        else {
          int out = get( src, size, i, j );
          set( dest, size, i, j, out );
        }

      }

    }
  }
}

//------------------------------------------------------------------------
// mtbmark_mfilt
//------------------------------------------------------------------------

void mtbmark_mfilt( int* dest, int* mask, int* src, int size )
{
  // Determine how many elements cores 0, 1, and 2 will process. Core 3
  // will process all of the remaining elements. Core 3 might process a
  // few more elements than the others because size might not be evenly
  // divisible by four.

  int block_size = size/4;

  // Create four argument structures that include the array pointers and
  // what elements each core should process.

  arg_t arg0 = { dest, mask, src, 1+0*block_size, 1+1*block_size, size };
  arg_t arg1 = { dest, mask, src, 1+1*block_size, 1+2*block_size, size };
  arg_t arg2 = { dest, mask, src, 1+2*block_size, 1+3*block_size, size };
  arg_t arg3 = { dest, mask, src, 1+3*block_size, size-1,         size };

  // Spawn work onto cores 1, 2, and 3.

  ece4750_bthread_spawn( 1, &work, &arg1 );
  ece4750_bthread_spawn( 2, &work, &arg2 );
  ece4750_bthread_spawn( 3, &work, &arg3 );

  // Have core 0 also do some work.

  work( &arg0 );

  // Wait for core 1, 2, and 3 to finish.

  ece4750_bthread_join(1);
  ece4750_bthread_join(2);
  ece4750_bthread_join(3);
}

