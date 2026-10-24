//========================================================================
// mtbmark-vvadd
//========================================================================
// This microbenchmark performs elementwise addition across two input
// arrays and stores the result in the destination array.

#ifndef MTBMARK_VVADD_H
#define MTBMARK_VVADD_H

void mtbmark_vvadd( int* dest, int* src0, int* src1, int size );

#endif /* MTBMARK_VVADD_H */

