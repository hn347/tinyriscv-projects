//========================================================================
// mtbmark-bsearch
//========================================================================
// This microbenchmark performs a binary search in an array of sorted
// keys and returns the corresponding index.

#ifndef MTBMARK_BSEARCH_H
#define MTBMARK_BSEARCH_H

void mtbmark_bsearch( int* idxs, int* search_keys, int search_keys_size,
                      int* sorted_keys, int sorted_keys_size );

#endif /* MTBMARK_BSEARCH_H */

