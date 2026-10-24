//========================================================================
// Unit tests for mtbmark sort
//========================================================================

#include "ece4750.h"
#include "mtbmark-sort.h"
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

  mtbmark_sort( a, 4 );

  for ( int i = 0; i < 4; i++ )
    ECE4750_CHECK_INT_EQ( a[i] , a_ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_2_merge_basic
//------------------------------------------------------------------------

void test_case_2_merge_basic()
{
  ECE4750_CHECK( L"test_case_2_merge_basic" );

  int src0[] = { 1, 4, 7 };
  int src1[] = { 2, 3, 9 };
  int dst[6];

  merge( dst, src0, 0, 3, src1, 0, 3 );

  int ref[] = { 1, 2, 3, 4, 7, 9 };
  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( dst[i], ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_3_merge_uneven
//------------------------------------------------------------------------

void test_case_3_merge_uneven()
{
  ECE4750_CHECK( L"test_case_3_merge_uneven" );

  int src0[] = { 0, 5 };
  int src1[] = { 1, 2, 9, 10 };
  int dst[6];

  merge( dst, src0, 0, 2, src1, 0, 4 );

  int ref[] = { 0, 1, 2, 5, 9, 10 };
  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( dst[i], ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_4_merge_disjoint
//------------------------------------------------------------------------

void test_case_4_merge_disjoint()
{
  ECE4750_CHECK( L"test_case_4_merge_disjoint" );

  int src0[] = { 1, 2, 3 };
  int src1[] = { 10, 11, 12 };
  int dst[6];

  merge( dst, src0, 0, 3, src1, 0, 3 );

  int ref[] = { 1, 2, 3, 10, 11, 12 };
  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( dst[i], ref[i] );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_5_block_partition
//------------------------------------------------------------------------

void test_case_5_block_partition()
{
  ECE4750_CHECK( L"test_case_5_block_partition" );

  int size = 17;
  int x[17];

  sort_arg_t args[NUM_BLOCKS];

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

  ECE4750_CHECK_INT_EQ( args[0].start, 0 );
  ECE4750_CHECK_INT_EQ( args[0].end,   5 );

  ECE4750_CHECK_INT_EQ( args[1].start, 5 );
  ECE4750_CHECK_INT_EQ( args[1].end,   9 );

  ECE4750_CHECK_INT_EQ( args[2].start, 9 );
  ECE4750_CHECK_INT_EQ( args[2].end,   13 );

  ECE4750_CHECK_INT_EQ( args[3].start, 13 );
  ECE4750_CHECK_INT_EQ( args[3].end,   17 );

  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_6_sort_small
//------------------------------------------------------------------------

void test_case_6_sort_small()
{
  ECE4750_CHECK( L"test_case_6_sort_small" );

  int a[]     = { 9, 1, 5, 3, 7, 2 };
  int ref[]   = { 1, 2, 3, 5, 7, 9 };

  mtbmark_sort( a, 6 );

  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( a[i], ref[i] );

  ECE4750_CHECK_INT_EQ( is_sorted( a, 6 ), 1 );
  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// test_case_7_sort_negative_positive
//------------------------------------------------------------------------

void test_case_7_sort_negative_positive()
{
  ECE4750_CHECK( L"test_case_7_sort_negative_positive" );

  int a[]   = { -5, 10, 3, -1, 4, -2 };
  int ref[] = { -5, -2, -1, 3, 4, 10 };

  mtbmark_sort( a, 6 );

  for ( int i = 0; i < 6; i++ )
    ECE4750_CHECK_INT_EQ( a[i], ref[i] );

  ECE4750_CHECK_INT_EQ( is_sorted( a, 6 ), 1 );
  ECE4750_CHECK_INT_EQ( ece4750_get_heap_usage(), 0 );
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece4750_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1 ) ) test_case_1_sort_basic();
  if ( (__n <= 0) || (__n == 2 ) ) test_case_2_merge_basic();
  if ( (__n <= 0) || (__n == 3 ) ) test_case_3_merge_uneven();
  if ( (__n <= 0) || (__n == 4 ) ) test_case_4_merge_disjoint();
  if ( (__n <= 0) || (__n == 5 ) ) test_case_5_block_partition();
  if ( (__n <= 0) || (__n == 6 ) ) test_case_6_sort_small();
  if ( (__n <= 0) || (__n == 7 ) ) test_case_7_sort_negative_positive();

  ece4750_wprintf( L"\n\n" );
  return ece4750_check_status;
}
