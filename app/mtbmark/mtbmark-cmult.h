//========================================================================
// mtbmark-cmult
//========================================================================
// This microbenchmark performs elementwise complex multiplication across
// two input arrays and stores the result in the destination array. We
// include ubmark-cmult.h to get access to the complx_t struct
// definition.

#ifndef MTBMARK_CMULT_H
#define MTBMARK_CMULT_H

#include "ubmark-cmult.h"

void mtbmark_cmult( complex_t* dest, complex_t* src0,
                    complex_t* src1, int size );

#endif /* MTBMARK_CMULT_H */

