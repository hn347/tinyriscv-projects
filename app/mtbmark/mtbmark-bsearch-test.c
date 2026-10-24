//========================================================================
// Unit tests for ubmark bsearch
//========================================================================

#include "ece4750.h"
#include "mtbmark-bsearch.h"
#include "ubmark-bsearch.dat"

//------------------------------------------------------------------------
// Test sizs 16
//------------------------------------------------------------------------

void test_case_1_size16()
{
  ECE4750_CHECK( L"test_case_1_size16" );

  int sorted_keys[16];
  int search_keys[33];
  int idxs[33];
  int ref[33];

  int j = 0;
  for ( int i = 0; i < 33; i++ ) {
    search_keys[i] = i;
    idxs[i]        = 0;

    // if i is odd, add this key to sorted keys
    if ( i % 2 == 1 ) {
      ref[i] = j;
      sorted_keys[j] = i;
      j += 1;
    }

    // if i is even, then do not add to sorted keys
    else {
      ref[i] = -1;
    }
  }

  mtbmark_bsearch( idxs, search_keys, 33, sorted_keys, 16 );

  for ( int i = 0; i < 33; i++ )
    ECE4750_CHECK_INT_EQ( idxs[i], ref[i] );
}

//------------------------------------------------------------------------
// Test sizs 17
//------------------------------------------------------------------------
// Non-power of two is good to test

void test_case_2_size17()
{
  ECE4750_CHECK( L"test_case_2_size17" );

  int sorted_keys[17];
  int search_keys[35];
  int idxs[35];
  int ref[35];

  int j = 0;
  for ( int i = 0; i < 35; i++ ) {
    search_keys[i] = i;
    idxs[i]        = 0;

    // if i is odd, add this key to sorted keys
    if ( i % 2 == 1 ) {
      ref[i] = j;
      sorted_keys[j] = i;
      j += 1;
    }

    // if i is even, then do not add to sorted keys
    else {
      ref[i] = -1;
    }
  }

  mtbmark_bsearch( idxs, search_keys, 35, sorted_keys, 17 );

  for ( int i = 0; i < 35; i++ )
    ECE4750_CHECK_INT_EQ( idxs[i], ref[i] );
}

//------------------------------------------------------------------------
// Test eval dataset
//------------------------------------------------------------------------

void test_case_3_eval_dataset()
{
  ECE4750_CHECK( L"test_case_3_eval_dataset" );

  int* idxs = ece4750_malloc( eval_search_keys_size * (int)sizeof(int) );

  mtbmark_bsearch( idxs, eval_search_keys, eval_search_keys_size,
                   eval_sorted_keys, eval_sorted_keys_size );

  for ( int i = 0; i < eval_search_keys_size; i++ )
    ECE4750_CHECK_INT_EQ( idxs[i], eval_ref[i] );

  ece4750_free(idxs);
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece4750_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1) ) test_case_1_size16();
  if ( (__n <= 0) || (__n == 2) ) test_case_2_size17();
  if ( (__n <= 0) || (__n == 3) ) test_case_3_eval_dataset();

  ece4750_wprintf( L"\n\n" );
  return ece4750_check_status;
}

