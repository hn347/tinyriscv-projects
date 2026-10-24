//========================================================================
// Unit tests for ubmark sort
//========================================================================

#include "ece4750.h"
#include "ubmark-sort.h"
#include "ubmark-sort.dat"

//------------------------------------------------------------------------
// is_sorted
//------------------------------------------------------------------------
// Helper function that returns 1 if sorted and 0 if unsorted

int is_sorted( int* x, int n )
{
  for ( int i = 0; i < n-1; i++ ) {
    if ( x[i] > x[i+1] )
      return 0;
  }
  return 1;
}

//------------------------------------------------------------------------
// test_case_1_sort_basic
//------------------------------------------------------------------------

void test_case_1_sort_basic()
{
  ECE4750_CHECK( L"test_case_1_sort_basic" );

  int a[]     = { 4, 3, 6, 5, };
  int a_ref[] = { 3, 4, 5, 6, };

  ubmark_sort( a, 4 );

  for ( int i = 0; i < 4; i++ )
    ECE4750_CHECK_INT_EQ( a[i] , a_ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_2_vector_construct_destruct
//------------------------------------------------------------------------

void test_case_2_vector_construct_destruct()
{
  ECE4750_CHECK( L"test_case_2_vector_construct_destruct" );

  vector_int_t v;
  vector_int_construct( &v );

  ECE4750_CHECK_INT_EQ( v.size, 0 );
  ECE4750_CHECK_INT_EQ( v.max_size, 10 );
  ECE4750_CHECK_INT_EQ( v.data != NULL, 1 );

  vector_int_destruct( &v );

  ECE4750_CHECK_INT_EQ( v.size, 0 );
  ECE4750_CHECK_INT_EQ( v.max_size, 0 );
  ECE4750_CHECK_INT_EQ( v.data == NULL, 1 );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_3_vector_push_back
//------------------------------------------------------------------------

void test_case_3_vector_push_back()
{
  ECE4750_CHECK( L"test_case_3_vector_push_back" );

  vector_int_t v;
  vector_int_construct( &v );

  for ( int i = 0; i < 10; i++ ) {
    vector_int_push_back( &v, i );
    ECE4750_CHECK_INT_EQ( vector_int_at(&v, i), i );
  }

  ECE4750_CHECK_INT_EQ( vector_int_size(&v), 10 );
  ECE4750_CHECK_INT_EQ( v.max_size, 10 );

  vector_int_push_back( &v, 10 );

  ECE4750_CHECK_INT_EQ( vector_int_size(&v), 11 );
  ECE4750_CHECK_INT_EQ( vector_int_at(&v, 10), 10 );
  ECE4750_CHECK_INT_EQ( v.max_size, 20 ); // doubled capacity

  vector_int_destruct( &v );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_4_vector_sort
//------------------------------------------------------------------------

void test_case_4_vector_sort()
{
  ECE4750_CHECK( L"test_case_4_vector_sort" );

  vector_int_t v;
  vector_int_construct( &v );

  int xs[] = { 9, 1, 5, 3, 2 };
  for ( int i = 0; i < 5; i++ )
    vector_int_push_back( &v, xs[i] );

  vector_int_sort( &v );

  int ref[] = { 1, 2, 3, 5, 9 };
  for ( int i = 0; i < 5; i++ )
    ECE4750_CHECK_INT_EQ( vector_int_at(&v, i), ref[i] );

  vector_int_destruct( &v );
  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_5_sort_edge_sizes
//------------------------------------------------------------------------

void test_case_5_sort_edge_sizes()
{
  ECE4750_CHECK( L"test_case_5_sort_edge_sizes" );

  int a0[] = {};
  ubmark_sort( a0, 0 ); // should not crash

  int a1[] = { 42 };
  ubmark_sort( a1, 1 );

  ECE4750_CHECK_INT_EQ( a1[0], 42 );
  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_6_sort_all_equal
//------------------------------------------------------------------------

void test_case_6_sort_all_equal()
{
  ECE4750_CHECK( L"test_case_6_sort_all_equal" );

  int a[] = { 7, 7, 7, 7, 7, 7 };
  ubmark_sort( a, 6 );

  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( a[i], 7 );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_7_sort_negative_positive
//------------------------------------------------------------------------

void test_case_7_sort_negative_positive()
{
  ECE4750_CHECK( L"test_case_7_sort_negative_positive" );

  int a[]   = { 0, -5, 12, -1, 3, -4 };
  int ref[] = { -5, -4, -1, 0, 3, 12 };

  ubmark_sort( a, 6 );

  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( a[i], ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}


//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece4750_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1 ) ) test_case_1_sort_basic();
  if ( (__n <= 0) || (__n == 2 ) ) test_case_2_vector_construct_destruct();
  if ( (__n <= 0) || (__n == 3 ) ) test_case_3_vector_push_back();
  if ( (__n <= 0) || (__n == 4 ) ) test_case_4_vector_sort();
  if ( (__n <= 0) || (__n == 5 ) ) test_case_5_sort_edge_sizes();
  if ( (__n <= 0) || (__n == 6 ) ) test_case_6_sort_all_equal();
  if ( (__n <= 0) || (__n == 7 ) ) test_case_7_sort_negative_positive();

  ece4750_wprintf( L"\n\n" );
  return ece4750_check_status;
}
