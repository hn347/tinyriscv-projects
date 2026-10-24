//========================================================================
// mtbmark-sort
//========================================================================

#include "mtbmark-sort.h"
#include "ece4750.h"

// We include ubmark-sort.h so you can call the single-threaded sort
// (which is already tested!) in your multi-threaded sort if you want.

#include "ubmark-sort.h"
#define NUM_BLOCKS 4

// typedef struct {
//   int* x;
//   int start;
//   int end;
// } sort_arg_t;

void sort_block( void* arg_vptr){
  sort_arg_t* a = (sort_arg_t*) arg_vptr;
  ubmark_sort( a->x + a->start, a->end - a->start);
}

//------------------------------------------------------------------------
// merge
//------------------------------------------------------------------------
// Helper function that merges two sorted arrays.

void merge(int *dst, int *src0, int begin0, int end0, int *src1, int begin1, int end1) {

  int i = 0;

  while (begin0 < end0 && begin1 < end1) {
    if (src0[begin0] <= src1[begin1]) {
      dst[i++] = src0[begin0++];
    } else {
      dst[i++] = src1[begin1++];
    }
  }

  while (begin0 < end0) {
    dst[i++] = src0[begin0++];
  }

  while (begin1 < end1) {
    dst[i++] = src1[begin1++];
  }
}

//------------------------------------------------------------------------
// mtbmark_sort
//------------------------------------------------------------------------

void mtbmark_sort( int* x, int size )
{
  if ( size <= 0 || x == NULL )
    return;
  if ( size == 1 )
    return;

  sort_arg_t args[NUM_BLOCKS];
  
  // 1) Split into 4 contiguous blocks, handling remainder
  int base_block_size = size / NUM_BLOCKS;
  int remainder       = size % NUM_BLOCKS;

  int offset = 0;
  for ( int b = 0; b < NUM_BLOCKS; b++ ) {
    int this_size = base_block_size + (b < remainder ? 1 : 0);
    args[b].x     = x;
    args[b].start = offset;
    args[b].end   = offset + this_size;
    offset       += this_size;
  }

  // spawn work onto core 1, 2, 3
  ece4750_bthread_spawn( 1, &sort_block, &args[1] );
  ece4750_bthread_spawn( 2, &sort_block, &args[2] );
  ece4750_bthread_spawn( 3, &sort_block, &args[3] );

  // have core 0 also do some work
  sort_block( &args[0]);

  // wait for core 1, 2, 3
  ece4750_bthread_join(1);
  ece4750_bthread_join(2);
  ece4750_bthread_join(3);

  int* temp = ece4750_malloc( size * (int)sizeof(int) );

  // Block boundaries
  int s0 = args[0].start; // should be 0
  int e0 = args[0].end;

  // int s1 = args[1].start; // should equal e0
  int e1 = args[1].end;

  int s2 = args[2].start; // should equal e1
  int e2 = args[2].end;

  // int s3 = args[3].start; // should equal e2
  int e3 = args[3].end;   // should be size

  // 1) Merge block 0 + 1 into [s0 .. e1)
  if ( e0 < e1 ) {
    merge( temp + s0, x, s0, e0, x, e0, e1 );
    for ( int i = s0; i < e1; i++ )
      x[i] = temp[i];
  }

  // 2) Merge block 2 + 3 into [s2 .. e3)
  if ( e2 < e3 ) {
    merge( temp + s2, x, s2, e2, x, e2, e3 );
    for ( int i = s2; i < e3; i++ )
      x[i] = temp[i];
  }

  // 3) Final merge of [s0 .. e1) and [s2 .. e3) into [s0 .. e3)
  if ( e1 < e3 ) {
    merge( temp + s0, x, s0, e1, x, s2, e3 );
    for ( int i = s0; i < e3; i++ )
      x[i] = temp[i];
  }

  ece4750_free( temp );
  // ECE4750_UNUSED_PTR(x);
  // ECE4750_UNUSED_INT(size);
}