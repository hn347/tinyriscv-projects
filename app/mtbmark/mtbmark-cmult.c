//========================================================================
// mtbmark-cmult
//========================================================================

#include "mtbmark-cmult.h"
#include "ubmark-cmult.h"
#include "ece4750.h"

//------------------------------------------------------------------------
// arg_t
//------------------------------------------------------------------------
// This is used to pass arguments when we spawn work onto the cores.

typedef struct
{
  complex_t* dest;  // pointer to dest array
  complex_t* src0;  // pointer to src0 array
  complex_t* src1;  // pointer to src1 array
  int        first; // first element this core should process
  int        last;  // (one past) last element this core should process
}
arg_t;

//------------------------------------------------------------------------
// work
//------------------------------------------------------------------------
// Each thread uses the argument structure to figure out what part of the
// array it should work on.

void work( void* arg_vptr )
{
  // Cast void* to argument pointer.

  arg_t* arg_ptr = (arg_t*) arg_vptr;

  // Create local variables for each field of the argument structure.

  complex_t* dest  = arg_ptr->dest;
  complex_t* src0  = arg_ptr->src0;
  complex_t* src1  = arg_ptr->src1;
  int        first = arg_ptr->first;
  int        last  = arg_ptr->last;

  // Do the actual work using the scalar function.

  ubmark_cmult( dest+first, src0+first, src1+first, last-first );
}

//------------------------------------------------------------------------
// mtbmark_cmult
//------------------------------------------------------------------------

void mtbmark_cmult( complex_t* dest, complex_t* src0,
                    complex_t* src1, int size )
{
  // Determine how many elements cores 0, 1, and 2 will process. Core 3
  // will process all of the remaining elements. Core 3 might process a
  // few more elements than the others because size might not be evenly
  // divisible by four.

  int block_size = size/4;

  // Create four argument structures that include the array pointers and
  // what elements each core should process.

  arg_t arg0 = { dest, src0, src1, 0*block_size, 1*block_size };
  arg_t arg1 = { dest, src0, src1, 1*block_size, 2*block_size };
  arg_t arg2 = { dest, src0, src1, 2*block_size, 3*block_size };
  arg_t arg3 = { dest, src0, src1, 3*block_size, size         };

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

