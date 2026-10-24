//========================================================================
// Unit tests for mtbmark mfilt
//========================================================================

#include "ece4750.h"
#include "mtbmark-mfilt.h"
#include "ubmark-mfilt.dat"

//------------------------------------------------------------------------
// Test eval dataset
//------------------------------------------------------------------------

void test_case_1_eval_dataset()
{
  ECE4750_CHECK( L"test_case_1_eval_dataset" );

  int* dest = ece4750_malloc( eval_size*eval_size * (int)sizeof(int) );

  mtbmark_mfilt( dest, eval_mask, eval_src, eval_size );

  for ( int i = 0; i < eval_size*eval_size; i++ )
    ECE4750_CHECK_INT_EQ( dest[i], eval_ref[i] );

  ece4750_free(dest);
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece4750_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1) ) test_case_1_eval_dataset();

  ece4750_wprintf( L"\n\n" );
  return ece4750_check_status;
}

