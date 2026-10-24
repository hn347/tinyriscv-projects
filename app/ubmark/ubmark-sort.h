//========================================================================
// ubmark-sort
//========================================================================
// This microbenchmark sorts an array of integers.

#ifndef UBMARK_SORT_H
#define UBMARK_SORT_H
#include <stddef.h>

typedef struct {
  int *data;
  int size;
  int max_size;
} vector_int_t;

// construct/destruct
void vector_int_construct( vector_int_t *this );
void vector_int_destruct( vector_int_t *this );

// push and access
void vector_int_push_back( vector_int_t *this, int value );
int  vector_int_size( const vector_int_t *this );
int  vector_int_at( const vector_int_t *this, int idx );

// sorting
void vector_int_sort( vector_int_t *this );

void ubmark_sort( int* x, int size );

#endif /* UBMARK_SORT_H */

