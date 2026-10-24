//========================================================================
// mtbmark-bsearch
//========================================================================

#include "mtbmark-bsearch.h"
#include "ubmark-bsearch.h"
#include "ece4750.h"

//------------------------------------------------------------------------
// arg_t
//------------------------------------------------------------------------
// This is used to pass arguments when we spawn work onto the cores.

typedef struct
{
  int* idxs;              // pointer to idxs array
  int* search_keys;       // pointer to search_keys array
  int  first;             // first search this core should process
  int  last;              // (one past) last search this core should process
  int* sorted_keys;       // pointer to sorted_keys array
  int  sorted_keys_size;  // size of sorted_keys array
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

  int* idxs             = arg_ptr->idxs;
  int* search_keys      = arg_ptr->search_keys;
  int  first            = arg_ptr->first;
  int  last             = arg_ptr->last;
  int* sorted_keys      = arg_ptr->sorted_keys;
  int  sorted_keys_size = arg_ptr->sorted_keys_size;

  // Do the actual work using the scalar function.

  ubmark_bsearch( idxs+first, search_keys+first, last-first,
                  sorted_keys, sorted_keys_size );
}

//------------------------------------------------------------------------
// mtbmark_bsearch
//------------------------------------------------------------------------

void mtbmark_bsearch( int* idxs, int* search_keys, int search_keys_size,
                      int* sorted_keys, int sorted_keys_size )
{
  // Determine how many elements cores 0, 1, and 2 will process. Core 3
  // will process all of the remaining elements. Core 3 might process a
  // few more elements than the others because size might not be evenly
  // divisible by four.

  int block_size = search_keys_size/4;

  // Create four argument structures that include the array pointers and
  // what elements each core should process.

  arg_t arg0 = { idxs, search_keys, 0*block_size, 1*block_size,     sorted_keys, sorted_keys_size };
  arg_t arg1 = { idxs, search_keys, 1*block_size, 2*block_size,     sorted_keys, sorted_keys_size };
  arg_t arg2 = { idxs, search_keys, 2*block_size, 3*block_size,     sorted_keys, sorted_keys_size };
  arg_t arg3 = { idxs, search_keys, 3*block_size, search_keys_size, sorted_keys, sorted_keys_size };

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

