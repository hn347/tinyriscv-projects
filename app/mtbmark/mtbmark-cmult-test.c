//========================================================================
// Unit tests for mtbmark cmult
//========================================================================

#include "ece4750.h"
#include "mtbmark-cmult.h"
#include "ubmark-cmult.dat"

//------------------------------------------------------------------------
// Test size 16 (4 elements/thread)
//------------------------------------------------------------------------

void test_case_1_size16()
{
  ECE4750_CHECK( L"test_case_1_size16" );

  ece4750_srand(0x0000cafe);

  // Generate random complex numbers

  complex_t src0[16];
  complex_t src1[16];

  for ( int i = 0; i < 16; i++ ) {
    src0[i].re = ece4750_rand() & 0x000000ff;
    src0[i].im = ece4750_rand() & 0x000000ff;
    src1[i].re = ece4750_rand() & 0x000000ff;
    src1[i].im = ece4750_rand() & 0x000000ff;
  }

  // Call single-threaded implementation to determine reference output

  complex_t ref[16];

  ubmark_cmult( ref, src0, src1, 16 );

  // Call multi-threaded implementation

  complex_t dest[16];

  mtbmark_cmult( dest, src0, src1, 16 );

  // Verify the results

  for ( int i = 0; i < 16; i++ ) {
    ECE4750_CHECK_INT_EQ( dest[i].re, ref[i].re );
    ECE4750_CHECK_INT_EQ( dest[i].im, ref[i].im );
  }
}

//------------------------------------------------------------------------
// Test size 19 (uneven elements/thread)
//------------------------------------------------------------------------

void test_case_2_size19()
{
  ECE4750_CHECK( L"test_case_2_size19" );

  ece4750_srand(0x0000beef);

  // Generate random complex numbers

  complex_t src0[19];
  complex_t src1[19];

  for ( int i = 0; i < 19; i++ ) {
    src0[i].re = ece4750_rand() & 0x000000ff;
    src0[i].im = ece4750_rand() & 0x000000ff;
    src1[i].re = ece4750_rand() & 0x000000ff;
    src1[i].im = ece4750_rand() & 0x000000ff;
  }

  // Call single-threaded implementation to determine reference output

  complex_t ref[19];

  ubmark_cmult( ref, src0, src1, 19 );

  // Call multi-threaded implementation

  complex_t dest[19];

  mtbmark_cmult( dest, src0, src1, 19 );

  // Verify the results

  for ( int i = 0; i < 19; i++ ) {
    ECE4750_CHECK_INT_EQ( dest[i].re, ref[i].re );
    ECE4750_CHECK_INT_EQ( dest[i].im, ref[i].im );
  }
}

//------------------------------------------------------------------------
// Test eval dataset
//------------------------------------------------------------------------

void test_case_3_eval_dataset()
{
  ECE4750_CHECK( L"test_case_3_eval_dataset" );

  complex_t* dest = ece4750_malloc( eval_size * (int)sizeof(complex_t) );

  mtbmark_cmult( dest, eval_src0, eval_src1, eval_size );

  for ( int i = 0; i < eval_size; i++ ) {
    ECE4750_CHECK_INT_EQ( dest[i].re, eval_ref[i].re );
    ECE4750_CHECK_INT_EQ( dest[i].im, eval_ref[i].im );
  }

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

