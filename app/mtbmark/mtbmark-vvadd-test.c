//========================================================================
// Unit tests for mtbmark vvadd
//========================================================================

#include "ece4750.h"
#include "mtbmark-vvadd.h"
#include "ubmark-vvadd.dat"

//------------------------------------------------------------------------
// Test size 16 (4 elements/thread)
//------------------------------------------------------------------------

void test_case_1_size16()
{
  ECE4750_CHECK( L"test_case_1_size16" );

  int src0[16];
  int src1[16];
  int dest[16];
  int ref[16];

  for ( int i = 0; i < 16; i++ ) {
    src0[i] = i;
    src1[i] = 2*i;
    dest[i] = 0;
    ref[i]  = i + 2*i;
  }

  mtbmark_vvadd( dest, src0, src1, 16 );

  for ( int i = 0; i < 16; i++ )
    ECE4750_CHECK_INT_EQ( dest[i], ref[i] );
}

//------------------------------------------------------------------------
// Test size 19 (uneven elements/thread)
//------------------------------------------------------------------------

void test_case_2_size19()
{
  ECE4750_CHECK( L"test_case_2_size19" );

  int src0[19];
  int src1[19];
  int dest[19];
  int ref[19];

  for ( int i = 0; i < 19; i++ ) {
    src0[i] = i;
    src1[i] = 2*i;
    dest[i] = 0;
    ref[i]  = i + 2*i;
  }

  mtbmark_vvadd( dest, src0, src1, 19 );

  for ( int i = 0; i < 19; i++ )
    ECE4750_CHECK_INT_EQ( dest[i], ref[i] );
}

//------------------------------------------------------------------------
// Test eval dataset
//------------------------------------------------------------------------

void test_case_3_eval_dataset()
{
  ECE4750_CHECK( L"test_case_3_eval_dataset" );

  int* dest = ece4750_malloc( eval_size * (int)sizeof(int) );

  mtbmark_vvadd( dest, eval_src0, eval_src1, eval_size );

  for ( int i = 0; i < eval_size; i++ )
    ECE4750_CHECK_INT_EQ( dest[i], eval_ref[i] );

  ece4750_free(dest);
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece4750_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1) ) test_case_1_size16();
  if ( (__n <= 0) || (__n == 2) ) test_case_2_size19();
  if ( (__n <= 0) || (__n == 3) ) test_case_3_eval_dataset();

  ece4750_wprintf( L"\n\n" );
  return ece4750_check_status;
}
