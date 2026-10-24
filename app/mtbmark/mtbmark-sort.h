//========================================================================
// mtbmark-sort
//========================================================================
// This microbenchmark sorts an array of integers.

#ifndef MTBMARK_SORT_H
#define MTBMARK_SORT_H
#include <stddef.h>

#define NUM_BLOCKS 4

typedef struct {
  int* x;
  int start;
  int end;
} sort_arg_t;

void merge( int *dst, int *src0, int begin0, int end0, int *src1, int begin1, int end1 );

void mtbmark_sort( int* x, int size );

#endif /* MTBMARK_SORT_H */

