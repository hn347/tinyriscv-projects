//========================================================================
// mtbmark-bsearch-eval
//========================================================================

#include "ece4750.h"
#include "mtbmark-bsearch.h"
#include "ubmark-bsearch.dat"

int main( int argc, char** argv )
{
  // Get number of workers to use from command line

  int nworkers = ( argc == 1 ) ? 4 : ece4750_atoi( argv[1] );
  ece4750_bthread_set_num_workers( nworkers );

  // Allocate destination array for results

  int* idxs = ece4750_malloc( eval_search_keys_size * (int)sizeof(int) );

  // Run the evaluation

  ece4750_stats_on();

  mtbmark_bsearch( idxs, eval_search_keys, eval_search_keys_size,
                  eval_sorted_keys, eval_sorted_keys_size );

  ece4750_stats_off();

  // Verify the results

  for ( int i = 0; i < eval_search_keys_size; i++ ) {
    if ( idxs[i] != eval_ref[i] ) {
      ece4750_wprintf( L"\n FAILED: idxs[%d] != eval_ref[%d] (%d != %d)\n\n",
                       i, i, idxs[i], eval_ref[i] );
      ece4750_exit(1);
    }
  }

  // Free destination array

  ece4750_free(idxs);

  // Check for no memory leaks

  if ( ece4750_get_heap_usage() != 0 ) {
    ece4750_wprintf( L"\n FAILED: memory leak of %d bytes!\n\n",
                     ece4750_get_heap_usage() );
    ece4750_exit(1);
  }

  // Otherwise we passed

  ece4750_wprintf( L"\n **PASSED** \n\n" );

  return 0;
}

