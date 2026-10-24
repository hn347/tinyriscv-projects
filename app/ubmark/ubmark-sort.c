#include "ece4750.h"
#include "ubmark-sort.h"
#include <stddef.h>

static int partition( int *a, int lo, int hi )
{
  int mid_index = lo + ((hi - lo) >> 1);
  int pivot     = a[mid_index];

  int i = lo - 1;
  int j = hi + 1;

  while ( 1 ) {
    do { i++; } while ( a[i] < pivot );
    do { j--; } while ( a[j] > pivot );
    if ( i >= j ) return j;
    int tmp = a[i]; a[i] = a[j]; a[j] = tmp;
  }
}

static void quicksort( int *a, int lo, int hi )
{
  if ( lo < hi ) {
    int p = partition( a, lo, hi );
    quicksort( a, lo, p );
    quicksort( a, p + 1, hi );
  }
}

void ubmark_sort( int *x, int size )
{
  if ( size <= 0 || x == NULL ) return;
  quicksort( x, 0, size - 1 );
}

static int vector_storage[20];

static void insertion_sort( int *a, int size )
{
  for ( int i = 1; i < size; i++ ) {
    int key = a[i];
    int j   = i - 1;
    while ( j >= 0 && a[j] > key ) {
      a[j + 1] = a[j];
      j--;
    }
    a[j + 1] = key;
  }
}

void vector_int_construct( vector_int_t *this )
{
  this->size     = 0;
  this->max_size = 10;          
  this->data     = vector_storage; 
}

void vector_int_push_back( vector_int_t *this, int value )
{
  if ( this->size >= this->max_size && this->max_size < 20 ) {
    this->max_size = 20;       
  }

  int capacity = (int)( sizeof(vector_storage) / sizeof(vector_storage[0]) );
  if ( this->size < capacity ) {
    this->data[this->size] = value;
    this->size++;
  }
}

void vector_int_sort( vector_int_t *this )
{
  insertion_sort( this->data, this->size );
}

void vector_int_destruct( vector_int_t *this )
{
  this->data     = NULL;
  this->size     = 0;
  this->max_size = 0;
}

int vector_int_size( const vector_int_t *this )
{
  return this->size;
}

int vector_int_at( const vector_int_t *this, int idx )
{
  return this->data[idx];
}
