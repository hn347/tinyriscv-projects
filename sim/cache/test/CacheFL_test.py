#=========================================================================
# CacheFL_test.py
#=========================================================================

import pytest

from random import seed, randint

from pymtl3 import *
from pymtl3.stdlib.mem        import MemMsgType
from pymtl3.stdlib.test_utils import mk_test_case_table

from cache.test.harness import req, resp, run_test
from cache.CacheFL      import CacheFL

seed(0xa4e28cc2)

#-------------------------------------------------------------------------
# cmp_wo_test_field
#-------------------------------------------------------------------------
# The test field in the cache response is used to indicate if the
# corresponding memory access resulted in a hit or a miss. However, the
# FL model always sets the test field to zero since it does not track
# hits/misses. So we need to do something special to ignore the test
# field when using the FL model. To do this, we can pass in a specialized
# comparison function to the StreamSinkFL.

def cmp_wo_test_field( msg, ref ):

  if msg.type_ != ref.type_:
    return False

  if msg.len != ref.len:
    return False

  if msg.opaque != msg.opaque:
    return False

  if ref.data != msg.data:
    return False

  # do not check the test field

  return True

#-------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------
# These functions are used to specify the address/data to preload into
# the main memory before running a test.

# 64B of sequential data

def data_64B():
  return [
    # addr      data
    0x00001000, 0x000c0ffe,
    0x00001004, 0x10101010,
    0x00001008, 0x20202020,
    0x0000100c, 0x30303030,
    0x00001010, 0x40404040,
    0x00001014, 0x50505050,
    0x00001018, 0x60606060,
    0x0000101c, 0x70707070,
    0x00001020, 0x80808080,
    0x00001024, 0x90909090,
    0x00001028, 0xa0a0a0a0,
    0x0000102c, 0xb0b0b0b0,
    0x00001030, 0xc0c0c0c0,
    0x00001034, 0xd0d0d0d0,
    0x00001038, 0xe0e0e0e0,
    0x0000103c, 0xf0f0f0f0,
  ]

# 512B of sequential data

def data_512B():
  data = []
  for i in range(128):
    data.extend([0x00001000+i*4,0xabcd1000+i*4])
  return data

# 1024B of random data

def data_random():
  seed(0xdeadbeef)
  data = []
  for i in range(256):
    data.extend([0x00001000+i*4,randint(0,0xffffffff)])
  return data

#----------------------------------------------------------------------
# Test Cases for Write Init
#----------------------------------------------------------------------

# Just make sure a single write init goes through the memory system.

def write_init_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),
  ]

# Write init a word multiple times, also tests opaque bits

def write_init_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x3, 0,   0,  0    ),
  ]

# Use write inits for each word in a cache line

def write_init_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1004, 0, 0x02020202 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1008, 0, 0x03030303 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x100c, 0, 0x04040404 ), resp( 'in', 0x3, 0,   0,  0    ),
  ]

# Write init one word in each cacheline in half the cache. For the direct
# mapped cache, this will write the first half of all the sets. For the
# set associative cache, this will write all of the sets in the first
# way.

def write_init_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0    ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0    ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0    ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0    ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0    ),
  ]

#----------------------------------------------------------------------
# Test Cases for Read Hits
#----------------------------------------------------------------------

# Single read hit

def read_hit_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xdeadbeef ),
  ]

# Read same word multiple times, also tests opaque bits

def read_hit_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xdeadbeef ),
  ]

# Read every word in cache line

def read_hit_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1004, 0, 0x02020202 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1008, 0, 0x03030303 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x100c, 0, 0x04040404 ), resp( 'in', 0x3, 0,   0,  0    ),

    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x01010101 ),
    req( 'rd', 0x5, 0x1004, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x02020202 ),
    req( 'rd', 0x6, 0x1008, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'rd', 0x7, 0x100c, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x04040404 ),
  ]

# Read one word from each cacheline

def read_hit_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0          ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0          ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0          ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0          ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0          ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0          ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0          ),

    req( 'rd', 0x0, 0x0000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x00000000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x01010101 ),
    req( 'rd', 0x2, 0x2020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x02020202 ),
    req( 'rd', 0x3, 0x3030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x03030303 ),
    req( 'rd', 0x4, 0x4040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x04040404 ),
    req( 'rd', 0x5, 0x5050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x05050505 ),
    req( 'rd', 0x6, 0x6060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x06060606 ),
    req( 'rd', 0x7, 0x7070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x07070707 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Write Hits
#----------------------------------------------------------------------

# Single write hit to one word

def write_hit_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
  ]

# Write/read word multiple times, also tests opaque bits

def write_hit_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),

    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'wr', 0x3, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'wr', 0x5, 0x1000, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'rd', 0x6, 0x1000, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'wr', 0x7, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),
    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read every word in cache line

def write_hit_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x1004, 0, 0x02020202 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x1008, 0, 0x03030303 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x100c, 0, 0x04040404 ), resp( 'in', 0x0, 0,   0,  0          ),

    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x3, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x5, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x7, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'rd', 0x4, 0x1004, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'rd', 0x6, 0x1008, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'rd', 0x8, 0x100c, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read one word from each cacheline

def write_hit_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0          ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0          ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0          ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0          ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0          ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0          ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0          ),

    req( 'wr', 0x0, 0x0000, 0, 0x10101010 ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x2, 0x2020, 0, 0x12121212 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x3030, 0, 0x13131313 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x4, 0x4040, 0, 0x14141414 ), resp( 'wr', 0x4, 1,   0,  0          ),
    req( 'wr', 0x5, 0x5050, 0, 0x15151515 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x6, 0x6060, 0, 0x16161616 ), resp( 'wr', 0x6, 1,   0,  0          ),
    req( 'wr', 0x7, 0x7070, 0, 0x17171717 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x0, 0x0000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x2020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x3030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x4040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x5050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x6060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x7070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Refill on Read Miss
#----------------------------------------------------------------------

# Single read miss (uses data_64B)

def read_miss_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x000c0ffe ),
  ]

# Read same word multiple times, also tests opaque bits (uses data_64B)

def read_miss_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x000c0ffe ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x000c0ffe ),
  ]

# Read every word in cache line (uses data_64B)

def read_miss_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x000c0ffe ),
    req( 'rd', 0x2, 0x1004, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x10101010 ),
    req( 'rd', 0x3, 0x1008, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x20202020 ),
    req( 'rd', 0x4, 0x100c, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x30303030 ),
  ]

# Read miss for each cacheline, then read hit for each cacheline (uses data_512B)

def read_miss_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0xabcd1010 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0xabcd1020 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0xabcd1030 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1040 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0xabcd1050 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1060 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0xabcd1070 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1080 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0xabcd1090 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd10a0 ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0xabcd10b0 ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0xabcd10c0 ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0xabcd10d0 ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0xabcd10e0 ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0xabcd10f0 ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xabcd1000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xabcd1010 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xabcd1020 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xabcd1030 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xabcd1040 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0xabcd1050 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0xabcd1060 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0xabcd1070 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0xabcd1080 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0xabcd1090 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0xabcd10a0 ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0xabcd10b0 ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0xabcd10c0 ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0xabcd10d0 ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0xabcd10e0 ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0xabcd10f0 ),

    req( 'rd', 0x0, 0x1004, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xabcd1004 ),
    req( 'rd', 0x1, 0x1014, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xabcd1014 ),
    req( 'rd', 0x2, 0x1024, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xabcd1024 ),
    req( 'rd', 0x3, 0x1034, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xabcd1034 ),
    req( 'rd', 0x4, 0x1044, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xabcd1044 ),
    req( 'rd', 0x5, 0x1054, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0xabcd1054 ),
    req( 'rd', 0x6, 0x1064, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0xabcd1064 ),
    req( 'rd', 0x7, 0x1074, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0xabcd1074 ),
    req( 'rd', 0x8, 0x1084, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0xabcd1084 ),
    req( 'rd', 0x9, 0x1094, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0xabcd1094 ),
    req( 'rd', 0xa, 0x10a4, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0xabcd10a4 ),
    req( 'rd', 0xb, 0x10b4, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0xabcd10b4 ),
    req( 'rd', 0xc, 0x10c4, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0xabcd10c4 ),
    req( 'rd', 0xd, 0x10d4, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0xabcd10d4 ),
    req( 'rd', 0xe, 0x10e4, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0xabcd10e4 ),
    req( 'rd', 0xf, 0x10f4, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0xabcd10f4 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Refill on Write Miss
#----------------------------------------------------------------------

# Single write miss to one word (uses data_64B)

def write_miss_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
  ]

# Write/read word multiple times, also tests opaque bits (uses data_64B)

def write_miss_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'wr', 0x3, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'wr', 0x5, 0x1000, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'rd', 0x6, 0x1000, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'wr', 0x7, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),
    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read every word in cache line (uses data_64B)

def write_miss_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x4, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x4, 1,   0,  0          ),

    req( 'rd', 0x5, 0x1000, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x01010101 ),
    req( 'rd', 0x6, 0x1004, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x02020202 ),
    req( 'rd', 0x7, 0x1008, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x03030303 ),
    req( 'rd', 0x8, 0x100c, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read one word from each cacheline (uses data_512B)

def write_miss_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x10101010 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1020, 0, 0x12121212 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x1030, 0, 0x13131313 ), resp( 'wr', 0x3, 0,   0,  0          ),
    req( 'wr', 0x4, 0x1040, 0, 0x14141414 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1050, 0, 0x15151515 ), resp( 'wr', 0x5, 0,   0,  0          ),
    req( 'wr', 0x6, 0x1060, 0, 0x16161616 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'wr', 0x7, 0x1070, 0, 0x17171717 ), resp( 'wr', 0x7, 0,   0,  0          ),
    req( 'wr', 0x8, 0x1080, 0, 0x18181818 ), resp( 'wr', 0x8, 0,   0,  0          ),
    req( 'wr', 0x9, 0x1090, 0, 0x19191919 ), resp( 'wr', 0x9, 0,   0,  0          ),
    req( 'wr', 0xa, 0x10a0, 0, 0x1a1a1a1a ), resp( 'wr', 0xa, 0,   0,  0          ),
    req( 'wr', 0xb, 0x10b0, 0, 0x1b1b1b1b ), resp( 'wr', 0xb, 0,   0,  0          ),
    req( 'wr', 0xc, 0x10c0, 0, 0x1c1c1c1c ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'wr', 0xd, 0x10d0, 0, 0x1d1d1d1d ), resp( 'wr', 0xd, 0,   0,  0          ),
    req( 'wr', 0xe, 0x10e0, 0, 0x1e1e1e1e ), resp( 'wr', 0xe, 0,   0,  0          ),
    req( 'wr', 0xf, 0x10f0, 0, 0x1f1f1f1f ), resp( 'wr', 0xf, 0,   0,  0          ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x1f1f1f1f ),
  ]

#----------------------------------------------------------------------
# Test Cases for Evict
#----------------------------------------------------------------------

# Write miss to two cachelines, and then a read to a third cacheline.
# This read to the third cacheline is guaranteed to cause an eviction on
# both the direct mapped and set associative caches. (uses data_512B)

def evict_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
    req( 'wr', 0x0, 0x1080, 0, 0x000c0ffe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1080, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xcafecafe ),
  ]

# Write word and evict multiple times. Test is carefully crafted to
# ensure it applies to both direct mapped and set associative caches.
# (uses data_512B)

def evict_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x01010101 ),
    req( 'wr', 0x2, 0x1080, 0, 0x11111111 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'rd', 0x3, 0x1080, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x11111111 ),
    req( 'rd', 0x4, 0x1100, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x5, 0x1080, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x11111111 ), # make sure way1 is still LRU

    req( 'wr', 0x6, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'rd', 0x7, 0x1000, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x02020202 ),
    req( 'wr', 0x8, 0x1080, 0, 0x12121212 ), resp( 'wr', 0x8, 1,   0,  0          ),
    req( 'rd', 0x9, 0x1080, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x12121212 ),
    req( 'rd', 0xa, 0x1100, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0xb, 0x1080, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x12121212 ), # make sure way1 is still LRU

    req( 'wr', 0xc, 0x1000, 0, 0x03030303 ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'rd', 0xd, 0x1000, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x03030303 ),
    req( 'wr', 0xe, 0x1080, 0, 0x13131313 ), resp( 'wr', 0xe, 1,   0,  0          ),
    req( 'rd', 0xf, 0x1080, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x13131313 ),
    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x1, 0x1080, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x13131313 ), # make sure way1 is still LRU

    req( 'wr', 0x2, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x04040404 ),
    req( 'wr', 0x4, 0x1080, 0, 0x14141414 ), resp( 'wr', 0x4, 1,   0,  0          ),
    req( 'rd', 0x5, 0x1080, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x14141414 ),
    req( 'rd', 0x6, 0x1100, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x7, 0x1080, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x14141414 ), # make sure way1 is still LRU

    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0x04040404 ),
  ]

# Write every word on two cachelines, and then a read to a third
# cacheline. This read to the third cacheline is guaranteed to cause an
# eviction on both the direct mapped and set associative caches. (uses
# data_512B)

def evict_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x2, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x3, 1,   0,  0          ),

    req( 'wr', 0x4, 0x1080, 0, 0x11111111 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1084, 0, 0x12121212 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x6, 0x1088, 0, 0x13131313 ), resp( 'wr', 0x6, 1,   0,  0          ),
    req( 'wr', 0x7, 0x108c, 0, 0x14141414 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x8, 0x1100, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1100 ), # conflicts

    req( 'rd', 0x9, 0x1000, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0x01010101 ),
    req( 'rd', 0xa, 0x1004, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x02020202 ),
    req( 'rd', 0xb, 0x1008, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x03030303 ),
    req( 'rd', 0xc, 0x100c, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x04040404 ),
  ]

# Write one word from each cacheline, then evict (uses data_512B)

def evict_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x10101010 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1020, 0, 0x12121212 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x1030, 0, 0x13131313 ), resp( 'wr', 0x3, 0,   0,  0          ),
    req( 'wr', 0x4, 0x1040, 0, 0x14141414 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1050, 0, 0x15151515 ), resp( 'wr', 0x5, 0,   0,  0          ),
    req( 'wr', 0x6, 0x1060, 0, 0x16161616 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'wr', 0x7, 0x1070, 0, 0x17171717 ), resp( 'wr', 0x7, 0,   0,  0          ),
    req( 'wr', 0x8, 0x1080, 0, 0x18181818 ), resp( 'wr', 0x8, 0,   0,  0          ),
    req( 'wr', 0x9, 0x1090, 0, 0x19191919 ), resp( 'wr', 0x9, 0,   0,  0          ),
    req( 'wr', 0xa, 0x10a0, 0, 0x1a1a1a1a ), resp( 'wr', 0xa, 0,   0,  0          ),
    req( 'wr', 0xb, 0x10b0, 0, 0x1b1b1b1b ), resp( 'wr', 0xb, 0,   0,  0          ),
    req( 'wr', 0xc, 0x10c0, 0, 0x1c1c1c1c ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'wr', 0xd, 0x10d0, 0, 0x1d1d1d1d ), resp( 'wr', 0xd, 0,   0,  0          ),
    req( 'wr', 0xe, 0x10e0, 0, 0x1e1e1e1e ), resp( 'wr', 0xe, 0,   0,  0          ),
    req( 'wr', 0xf, 0x10f0, 0, 0x1f1f1f1f ), resp( 'wr', 0xf, 0,   0,  0          ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x1f1f1f1f ),

    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x1, 0x1110, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0xabcd1110 ), # conflicts
    req( 'rd', 0x2, 0x1120, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0xabcd1120 ), # conflicts
    req( 'rd', 0x3, 0x1130, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0xabcd1130 ), # conflicts
    req( 'rd', 0x4, 0x1140, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1140 ), # conflicts
    req( 'rd', 0x5, 0x1150, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0xabcd1150 ), # conflicts
    req( 'rd', 0x6, 0x1160, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1160 ), # conflicts
    req( 'rd', 0x7, 0x1170, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0xabcd1170 ), # conflicts
    req( 'rd', 0x8, 0x1180, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1180 ), # conflicts
    req( 'rd', 0x9, 0x1190, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0xabcd1190 ), # conflicts
    req( 'rd', 0xa, 0x11a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd11a0 ), # conflicts
    req( 'rd', 0xb, 0x11b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0xabcd11b0 ), # conflicts
    req( 'rd', 0xc, 0x11c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0xabcd11c0 ), # conflicts
    req( 'rd', 0xd, 0x11d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0xabcd11d0 ), # conflicts
    req( 'rd', 0xe, 0x11e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0xabcd11e0 ), # conflicts
    req( 'rd', 0xf, 0x11f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0xabcd11f0 ), # conflicts

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0x1f1f1f1f ),
  ]

#----------------------------------------------------------------------
# More Directed Test Cases
#----------------------------------------------------------------------

# Stream reads across two consecutive cache lines (8 words total)
def read_stream_two_lines():
  return [
    #           type opq  addr     len data                type opq  test len data
    req( 'rd',  0x0, 0x1000, 0, 0 ),  resp( 'rd', 0x0, 0,   0,  0x000c0ffe ),
    req( 'rd',  0x1, 0x1004, 0, 0 ),  resp( 'rd', 0x1, 1,   0,  0x10101010 ),
    req( 'rd',  0x2, 0x1008, 0, 0 ),  resp( 'rd', 0x2, 1,   0,  0x20202020 ),
    req( 'rd',  0x3, 0x100c, 0, 0 ),  resp( 'rd', 0x3, 1,   0,  0x30303030 ),

    req( 'rd',  0x4, 0x1010, 0, 0 ),  resp( 'rd', 0x4, 0,   0,  0x40404040 ),
    req( 'rd',  0x5, 0x1014, 0, 0 ),  resp( 'rd', 0x5, 1,   0,  0x50505050 ),
    req( 'rd',  0x6, 0x1018, 0, 0 ),  resp( 'rd', 0x6, 1,   0,  0x60606060 ),
    req( 'rd',  0x7, 0x101c, 0, 0 ),  resp( 'rd', 0x7, 1,   0,  0x70707070 ),
  ]

# After a write miss (write-allocate), another word in the same line should
# be a read hit returning data from backing store
def write_miss_then_read_same_line():
  return [
    req( 'wr', 0x0, 0x1000, 0, 0xaaaa5555 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, 0x1008, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x20202020 ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xaaaa5555 ),
  ]

# Cross-line boundary behavior with mixed write/read
def cross_line_write_read_mix():
  return [
    req( 'wr', 0x0, 0x100c, 0, 0xcafebabe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x40404040 ),
    req( 'rd', 0x2, 0x100c, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xcafebabe ),
  ]

# A longer streaming write across two lines via write-misses, then verify reads
def stream_write_then_verify_reads():
  return [
    # write-miss across first line
    req( 'wr', 0x0, 0x1000, 0, 0x11111111 ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'wr', 0x1, 0x1004, 0, 0x22222222 ), resp( 'wr', 0x1, 1, 0, 0 ),
    req( 'wr', 0x2, 0x1008, 0, 0x33333333 ), resp( 'wr', 0x2, 1, 0, 0 ),
    req( 'wr', 0x3, 0x100c, 0, 0x44444444 ), resp( 'wr', 0x3, 1, 0, 0 ),

    # write-miss across second line
    req( 'wr', 0x4, 0x1010, 0, 0x55555555 ), resp( 'wr', 0x4, 0, 0, 0 ),
    req( 'wr', 0x5, 0x1014, 0, 0x66666666 ), resp( 'wr', 0x5, 1, 0, 0 ),
    req( 'wr', 0x6, 0x1018, 0, 0x77777777 ), resp( 'wr', 0x6, 1, 0, 0 ),
    req( 'wr', 0x7, 0x101c, 0, 0x88888888 ), resp( 'wr', 0x7, 1, 0, 0 ),

    # verify reads should be hits with written data
    req( 'rd', 0x8, 0x1000, 0, 0 ), resp( 'rd', 0x8, 1, 0, 0x11111111 ),
    req( 'rd', 0x9,  0x1004, 0, 0 ), resp( 'rd', 0x9, 1, 0, 0x22222222 ),
    req( 'rd', 0xa,  0x1008, 0, 0 ), resp( 'rd', 0xa, 1, 0, 0x33333333 ),
    req( 'rd', 0xb,  0x100c, 0, 0 ), resp( 'rd', 0xb, 1, 0, 0x44444444 ),
    req( 'rd', 0xc,  0x1010, 0, 0 ), resp( 'rd', 0xc, 1, 0, 0x55555555 ),
    req( 'rd', 0xd,  0x1014, 0, 0 ), resp( 'rd', 0xd, 1, 0, 0x66666666 ),
    req( 'rd', 0xe,  0x1018, 0, 0 ), resp( 'rd', 0xe, 1, 0, 0x77777777 ),
    req( 'rd', 0xf,  0x101c, 0, 0 ), resp( 'rd', 0xf, 1, 0, 0x88888888 ),
  ]


#-------------------------------------------------------------------------
# Generic tests
#-------------------------------------------------------------------------

test_case_table_generic = mk_test_case_table([
  (                                    "msg_func                    mem_data_func stall lat src sink"),

  [ "write_init_word",                  write_init_word,            None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_word",            write_init_multi_word,      None,         0.0,  0,  0,  0    ],
  [ "write_init_cacheline",             write_init_cacheline,       None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_cacheline",       write_init_multi_cacheline, None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_word_sink_delay", write_init_multi_word,      None,         0.0,  0,  0,  10   ],
  [ "write_init_multi_word_src_delay",  write_init_multi_word,      None,         0.0,  0,  10, 0    ],

  [ "read_hit_word",                    read_hit_word,              None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_word",              read_hit_multi_word,        None,         0.0,  0,  0,  0    ],
  [ "read_hit_cacheline",               read_hit_cacheline,         None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_cacheline",         read_hit_multi_cacheline,   None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_word_sink_delay",   read_hit_multi_word,        None,         0.0,  0,  0,  10   ],
  [ "read_hit_multi_word_src_delay",    read_hit_multi_word,        None,         0.0,  0,  10, 0    ],

  [ "write_hit_word",                   write_hit_word,             None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_word",             write_hit_multi_word,       None,         0.0,  0,  0,  0    ],
  [ "write_hit_cacheline",              write_hit_cacheline,        None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_cacheline",        write_hit_multi_cacheline,  None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_word_sink_delay",  write_hit_multi_word,       None,         0.0,  0,  0,  10   ],
  [ "write_hit_multi_word_src_delay",   write_hit_multi_word,       None,         0.0,  0,  10, 0    ],

  [ "read_miss_word",                   read_miss_word,             data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_multi_word",             read_miss_multi_word,       data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_cacheline",              read_miss_cacheline,        data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_multi_cacheline",        read_miss_multi_cacheline,  data_512B,    0.0,  0,  0,  0    ],
  [ "read_miss_multi_word_sink_delay",  read_miss_multi_word,       data_64B,     0.9,  3,  0,  10   ],
  [ "read_miss_multi_word_src_delay",   read_miss_multi_word,       data_64B,     0.9,  3,  10, 0    ],

  [ "write_miss_word",                  write_miss_word,            data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_multi_word",            write_miss_multi_word,      data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_cacheline",             write_miss_cacheline,       data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_multi_cacheline",       write_miss_multi_cacheline, data_512B,    0.0,  0,  0,  0    ],
  [ "write_miss_multi_word_sink_delay", write_miss_multi_word,      data_64B,     0.9,  3,  0,  10   ],
  [ "write_miss_multi_word_src_delay",  write_miss_multi_word,      data_64B,     0.9,  3,  10, 0    ],

  [ "evict_word",                       evict_word,                 data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_word",                 evict_multi_word,           data_512B,    0.0,  0,  0,  0    ],
  [ "evict_cacheline",                  evict_cacheline,            data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_cacheline",            evict_multi_cacheline,      data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_word_sink_delay",      evict_multi_word,           data_512B,    0.9,  3,  0,  10   ],
  [ "evict_multi_word_src_delay",       evict_multi_word,           data_512B,    0.9,  3,  10, 0    ],

  [ "read_stream_two_lines",             read_stream_two_lines,         data_64B,   0.0,  0,   0,   0 ],
  [ "read_stream_two_lines_stress",      read_stream_two_lines,         data_64B,   0.9,  4,   7,  11 ],

  [ "write_miss_then_read_same_line",    write_miss_then_read_same_line,data_64B,   0.0,  0,   0,   0 ],
  [ "write_miss_then_read_same_stress",  write_miss_then_read_same_line,data_64B,   0.9,  4,   6,  10 ],

  [ "cross_line_write_read_mix",         cross_line_write_read_mix,     data_64B,   0.0,  0,   0,   0 ],
  [ "cross_line_write_read_stress",      cross_line_write_read_mix,     data_64B,   0.9,  3,   9,   9 ],

  [ "stream_write_then_verify_reads",    stream_write_then_verify_reads,data_64B,   0.0,  0,   0,   0 ],
  [ "stream_write_then_verify_stress",   stream_write_then_verify_reads,data_64B,   0.9,  3,   7,  10 ],

])

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Case with Random Addresses and Data
#-------------------------------------------------------------------------

# Helper
def _mk_memdict(mem_data_list):
  return { mem_data_list[i]: mem_data_list[i+1] for i in range(0,len(mem_data_list),2) }

# Verifies that every read returns the backing-store value
def rand_reads_only_1kb():
  mem = _mk_memdict( data_random() )
  msgs = []
  opq  = 0
  for _ in range(50):
    k     = randint(0,255)
    addr  = 0x00001000 + (k<<2)
    exp   = mem[addr]
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, exp) ]
    opq  += 1
  return msgs

# Random writes into 512B window, then verify by reading back every written word
def rand_writes_then_verify():
  msgs   = []
  opq    = 0
  wrote  = {}

  for _ in range(40):
    k     = randint(0,127)
    addr  = 0x00001000 + (k<<2)
    data  = randint(0,0xffffffff)
    wrote[addr] = data
    msgs += [ req('wr', opq, addr, 0, data), resp('wr', opq, 0, 0, 0) ]
    opq  += 1

  for addr in sorted(wrote.keys()):
    exp  = wrote[addr]
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, exp) ]
    opq  += 1

  return msgs

# Mixed random sequence (reads/writes) with shadow model
def rand_mixed_rw_shadow():
  base_mem = _mk_memdict( data_random() )
  shadow   = dict(base_mem)
  msgs     = []
  opq      = 0

  for _ in range(80):
    k    = randint(0,255)
    addr = 0x00001000 + (k<<2)

    if randint(0,1) == 0:
      # read
      exp  = shadow[addr]
      msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, exp) ]
    else:
      # write
      data = randint(0,0xffffffff)
      shadow[addr] = data
      msgs += [ req('wr', opq, addr, 0, data), resp('wr', opq, 0, 0, 0) ]
    opq += 1

  for _ in range(16):
    k    = randint(0,255)
    addr = 0x00001000 + (k<<2)
    exp  = shadow[addr]
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, exp) ]
    opq += 1

  return msgs

# Strided reads: stride = 32B (0x20)
def rand_stride_reads_32B():
  mem  = _mk_memdict( data_random() )
  msgs = []; opq = 0
  addr = 0x00001000
  for _ in range(128):
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, mem[addr]) ]
    opq += 1
    addr = 0x00001000 + (((addr - 0x00001000 + 0x20) & 0x3FC))
  return msgs

# Unit stride with shared address (temporal locality) mixed in
def rand_unit_stride_mixed_temporal():
  mem    = _mk_memdict( data_random() )
  shadow = dict(mem)
  msgs = []; opq = 0
  hot_addr = 0x00001000 + (randint(0,255)<<2)
  addr = 0x00001000
  for _ in range(200):
    if randint(0,4) == 0:
      if randint(0,1) == 0:
        msgs += [ req('rd', opq, hot_addr, 0, 0), resp('rd', opq, 0, 0, shadow[hot_addr]) ]
      else:
        data = randint(0,0xffffffff)
        shadow[hot_addr] = data
        msgs += [ req('wr', opq, hot_addr, 0, data), resp('wr', opq, 0, 0, 0) ]
    else:
      if randint(0,1) == 0:
        msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, shadow[addr]) ]
      else:
        data = randint(0,0xffffffff)
        shadow[addr] = data
        msgs += [ req('wr', opq, addr, 0, data), resp('wr', opq, 0, 0, 0) ]
      addr = 0x00001000 + (((addr - 0x00001000 + 0x10) & 0x3FC)) 
    opq += 1
  for _ in range(16):
    a = hot_addr if _ < 4 else (0x00001000 + (randint(0,255)<<2))
    msgs += [ req('rd', opq, a, 0, 0), resp('rd', opq, 0, 0, shadow[a]) ]
    opq += 1
  return msgs

# Two or three same-set tags mixed reads/writes to stress LRU/conflicts in a random way
def rand_two_tags_same_set_mixed():
  base_mem = _mk_memdict( data_random() )
  shadow   = dict(base_mem)
  msgs = []; opq = 0
  A = 0x00001000       
  B = 0x00001080 
  C = 0x00001100 
  for _ in range(120):
    addr = [A,B,C][ randint(0, 2 if randint(0,3)==0 else 1) ]
    if randint(0,1) == 0:
      # read
      msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, shadow[addr]) ]
    else:
      # write
      data = randint(0,0xffffffff)
      shadow[addr] = data
      msgs += [ req('wr', opq, addr, 0, data), resp('wr', opq, 0, 0, 0) ]
    opq += 1
  for addr in (A,B,C):
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, shadow[addr]) ]
    opq += 1
  return msgs

def rand_unit_stride_reads_1kb():
  mem = _mk_memdict( data_random() ) 
  msgs = []; opq = 0
  addr = 0x00001000
  for _ in range(256):
    exp  = mem[addr]
    msgs += [ req('rd', opq, addr, 0, 0), resp('rd', opq, 0, 0, exp) ]
    opq += 1
    addr = 0x00001000 + (((addr - 0x00001000 + 0x4) & 0x3FC))
  return msgs


test_case_table_random = mk_test_case_table([
  (                        "msg_func       mem_data_func stall lat src sink"),


  # Read-only random (backed by random preload)
  [ "rand_reads_only_1kb",            rand_reads_only_1kb,        data_random,  0.0,  0,   0,    0 ],
  [ "rand_reads_only_1kb_stress",     rand_reads_only_1kb,        data_random,  0.9,  3,   7,   10 ],

  # Random writes then verify (no preload needed)
  [ "rand_writes_then_verify",        rand_writes_then_verify,    None,         0.0,  0,   0,    0 ],
  [ "rand_writes_then_verify_stress", rand_writes_then_verify,    None,         0.95, 4,   8,   12 ],

  # Mixed random read/write with shadow model (needs random preload)
  [ "rand_mixed_rw_shadow",           rand_mixed_rw_shadow,       data_random,  0.0,  0,   0,    0 ],
  [ "rand_mixed_rw_shadow_stress",    rand_mixed_rw_shadow,       data_random,  0.95, 5,  10,   10 ],

  [ "rand_stride_reads_32B",                 rand_stride_reads_32B,              data_random, 0.0,  0,  0,  0 ],
  [ "rand_stride_reads_32B_stress",          rand_stride_reads_32B,              data_random, 0.9,  3,  8, 12 ],

  [ "rand_unit_stride_mixed_temporal",       rand_unit_stride_mixed_temporal,    data_random, 0.0,  0,  0,  0 ],
  [ "rand_unit_stride_mixed_temporal_stress",rand_unit_stride_mixed_temporal,    data_random, 0.95, 4, 10, 10 ],

  [ "rand_two_tags_same_set_mixed",          rand_two_tags_same_set_mixed,       data_random, 0.0,  0,  0,  0 ],
  [ "rand_two_tags_same_set_mixed_stress",   rand_two_tags_same_set_mixed,       data_random, 0.95, 5,  9, 12 ],

  [ "rand_unit_stride_reads_1kb",        rand_unit_stride_reads_1kb,        data_random, 0.0, 0, 0, 0 ],
  [ "rand_unit_stride_reads_1kb_stress", rand_unit_stride_reads_1kb,        data_random, 0.9, 3, 8, 12 ],

])

@pytest.mark.parametrize( **test_case_table_random )
def test_random( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Cases for Direct Mapped
#-------------------------------------------------------------------------

# Repeatedly alternate two addresses that map to the same index but
# different tags
def dmap_conflict_alternate_reads():
  return [
    #         type opq  addr     len data                type opq  test len data
    req('rd', 0x0, 0x1000, 0, 0), resp('rd', 0x0, 0,   0, 0xabcd1000),
    req('rd', 0x1, 0x1100, 0, 0), resp('rd', 0x1, 0,   0, 0xabcd1100),
    req('rd', 0x2, 0x1000, 0, 0), resp('rd', 0x2, 0,   0, 0xabcd1000),
    req('rd', 0x3, 0x1100, 0, 0), resp('rd', 0x3, 0,   0, 0xabcd1100),
    req('rd', 0x4, 0x1000, 0, 0), resp('rd', 0x4, 0,   0, 0xabcd1000),
    req('rd', 0x5, 0x1100, 0, 0), resp('rd', 0x5, 0,   0, 0xabcd1100),
  ]

# Write to one conflicting line, then to the other, forcing eviction of
# the first
def dmap_conflict_writeback_on_eviction():
  return [
    req('wr', 0x0, 0x1000, 0, 0x44444444), resp('wr', 0x0, 0, 0, 0),
    req('wr', 0x1, 0x1100, 0, 0x55555555), resp('wr', 0x1, 0, 0, 0),
    req('rd', 0x2, 0x1000, 0, 0),         resp('rd', 0x2, 0, 0, 0x44444444),
    req('rd', 0x3, 0x1100, 0, 0),         resp('rd', 0x3, 0, 0, 0x55555555),
  ]

# Start with a read hit, then conflict to evict, then ensure the original
# address misses again
def dmap_read_hit_then_conflict_then_miss():
  return [
    req('rd', 0x0, 0x1000, 0, 0), resp('rd', 0x0, 0, 0, 0xabcd1000),
    req('rd', 0x1, 0x1004, 0, 0), resp('rd', 0x1, 1, 0, 0xabcd1004),

    req('rd', 0x2, 0x1100, 0, 0), resp('rd', 0x2, 0, 0, 0xabcd1100),

    req('rd', 0x3, 0x1000, 0, 0), resp('rd', 0x3, 0, 0, 0xabcd1000),
  ]

def dmap_capacity_writeback_sweep():
  return [
    req('wr', 0x0, 0x1000, 0, 0xaaaaaaaa), resp('wr', 0x0, 0, 0, 0),
    req('wr', 0x1, 0x1100, 0, 0xbbbbbbbb), resp('wr', 0x1, 0, 0, 0),
    req('wr', 0x2, 0x1200, 0, 0xcccccccc), resp('wr', 0x2, 0, 0, 0),
    req('wr', 0x3, 0x1300, 0, 0xdddddddd), resp('wr', 0x3, 0, 0, 0),

    req('rd', 0x4, 0x1000, 0, 0),          resp('rd', 0x4, 0, 0, 0xaaaaaaaa),
    req('rd', 0x5, 0x1100, 0, 0),          resp('rd', 0x5, 0, 0, 0xbbbbbbbb),
    req('rd', 0x6, 0x1200, 0, 0),          resp('rd', 0x6, 0, 0, 0xcccccccc),
    req('rd', 0x7, 0x1300, 0, 0),          resp('rd', 0x7, 0, 0, 0xdddddddd),
  ]


test_case_table_dmap = mk_test_case_table([
  (                                   "msg_func                         mem_data_func stall lat src sink"),

  [ "dmap_conflict_alternate_reads",       dmap_conflict_alternate_reads,     data_512B,   0.0,  0,  0,   0 ],
  [ "dmap_conflict_alternate_reads_stress",dmap_conflict_alternate_reads,     data_512B,   0.9,  3,  8,  10 ],

  [ "dmap_conflict_writeback_on_eviction",dmap_conflict_writeback_on_eviction,data_512B,  0.0,  0,  0,   0 ],
  [ "dmap_conflict_writeback_stress",     dmap_conflict_writeback_on_eviction,data_512B,  0.95, 4,  9,  12 ],


  [ "dmap_read_hit_then_conflict_then_miss", dmap_read_hit_then_conflict_then_miss, data_512B, 0.0, 0, 0, 0 ],
  [ "dmap_read_hit_conflict_miss_stress",    dmap_read_hit_then_conflict_then_miss, data_512B, 0.9, 3, 7, 9 ],

  [ "dmap_capacity_writeback_sweep", dmap_capacity_writeback_sweep, data_512B, 0.0, 0, 0, 0 ],
  [ "dmap_capacity_writeback_sweep_stress", dmap_capacity_writeback_sweep, data_512B, 0.95, 4, 9, 12 ],

])

@pytest.mark.parametrize( **test_case_table_dmap )
def test_dmap( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Cases for Set Associative
#-------------------------------------------------------------------------

# Two conflicting tags can co-exist in a 2-way SA cache
def sassoc_two_way_coexist_reads():
  return [
    req('rd', 0x0, 0x1000, 0, 0), resp('rd', 0x0, 0, 0, 0xabcd1000),
    req('rd', 0x1, 0x1080, 0, 0), resp('rd', 0x1, 0, 0, 0xabcd1080),

    req('rd', 0x2, 0x1000, 0, 0), resp('rd', 0x2, 1, 0, 0xabcd1000),
    req('rd', 0x3, 0x1080, 0, 0), resp('rd', 0x3, 1, 0, 0xabcd1080),
  ]

# Write hit path for a line that was just made clean by refill
def sassoc_write_hit_on_clean_then_readback():
  return [
    req('rd', 0x0, 0x1000, 0, 0),          resp('rd', 0x0, 0, 0, 0x000c0ffe),
    req('wr', 0x1, 0x1004, 0, 0xfacecafe), resp('wr', 0x1, 1, 0, 0),
    req('rd', 0x2, 0x1004, 0, 0),          resp('rd', 0x2, 1, 0, 0xfacecafe),
  ]

# Read hit path for a dirty line (after a prior write hit)
def sassoc_read_hit_from_dirty():
  return [
    req('rd', 0x0, 0x1000, 0, 0),          resp('rd', 0x0, 0, 0, 0x000c0ffe),
    req('wr', 0x1, 0x1000, 0, 0x11111111), resp('wr', 0x1, 1, 0, 0),
    req('rd', 0x2, 0x1000, 0, 0),          resp('rd', 0x2, 1, 0, 0x11111111),
  ]

# Read miss with refill and no eviction (empty set)
def sassoc_read_miss_refill_no_evict():
  return [
    req('rd', 0x0, 0x1100, 0, 0), resp('rd', 0x0, 0, 0, 0xabcd1100),
    req('rd', 0x1, 0x1104, 0, 0), resp('rd', 0x1, 1, 0, 0xabcd1104),
  ]

# Write miss with refill and NO eviction (empty set)
def sassoc_write_miss_refill_no_evict():
  return [
    req('wr', 0x0, 0x1180, 0, 0x22223333), resp('wr', 0x0, 0, 0, 0),
    req('rd', 0x1, 0x1180, 0, 0),          resp('rd', 0x1, 1, 0, 0x22223333),
  ]

# LRU: Fill both ways (A,B), use A so B becomes LRU, then bring C (same set)
# Expect B to be evicted; A and C remain
def sassoc_lru_clean_evict():
  return [
    req('rd', 0x0, 0x1000, 0, 0), resp('rd', 0x0, 0, 0, 0xabcd1000), 
    req('rd', 0x1, 0x1080, 0, 0), resp('rd', 0x1, 0, 0, 0xabcd1080), 
    req('rd', 0x2, 0x1000, 0, 0), resp('rd', 0x2, 1, 0, 0xabcd1000),
    req('rd', 0x3, 0x1100, 0, 0), resp('rd', 0x3, 0, 0, 0xabcd1100), 

    req('rd', 0x4, 0x1000, 0, 0), resp('rd', 0x4, 1, 0, 0xabcd1000), 
    req('rd', 0x5, 0x1080, 0, 0), resp('rd', 0x5, 0, 0, 0xabcd1080), 
  ]

# LRU + dirty eviction: Make B dirty, make B LRU, bring C; B must write back
def sassoc_lru_dirty_writeback_evict():
  return [
    req('rd', 0x0, 0x1000, 0, 0),          resp('rd', 0x0, 0, 0, 0xabcd1000), 
    req('rd', 0x1, 0x1080, 0, 0),          resp('rd', 0x1, 0, 0, 0xabcd1080), 

    req('wr', 0x2, 0x1080, 0, 0x5555eeee), resp('wr', 0x2, 1, 0, 0),

    req('rd', 0x3, 0x1000, 0, 0),          resp('rd', 0x3, 1, 0, 0xabcd1000),

    req('rd', 0x4, 0x1100, 0, 0),          resp('rd', 0x4, 0, 0, 0xabcd1100),

    req('rd', 0x5, 0x1080, 0, 0),          resp('rd', 0x5, 0, 0, 0x5555eeee),
  ]

# Conflict misses that a 2-way SA should absorb before eviction
def sassoc_three_tags_sequence():
  return [
    req('rd', 0x0, 0x1000, 0, 0), resp('rd', 0x0, 0, 0, 0xabcd1000), 
    req('rd', 0x1, 0x1080, 0, 0), resp('rd', 0x1, 0, 0, 0xabcd1080), 
    req('rd', 0x2, 0x1100, 0, 0), resp('rd', 0x2, 0, 0, 0xabcd1100), 

    req('rd', 0x3, 0x1100, 0, 0), resp('rd', 0x3, 1, 0, 0xabcd1100),
  ]

# Four-bank exercise within a single line
def sassoc_four_bank_intra_line_mix():
  return [
    req('rd', 0x0, 0x1000, 0, 0),      resp('rd', 0x0, 0, 0, 0x000c0ffe),

    req('wr', 0x1, 0x1008, 0, 0x88888888), resp('wr', 0x1, 1, 0, 0),
    req('wr', 0x2, 0x1000, 0, 0x00000099), resp('wr', 0x2, 1, 0, 0),
    req('wr', 0x3, 0x100c, 0, 0xcccccccc), resp('wr', 0x3, 1, 0, 0),
    req('wr', 0x4, 0x1004, 0, 0x44444444), resp('wr', 0x4, 1, 0, 0),

    req('rd', 0x5, 0x1000, 0, 0),      resp('rd', 0x5, 1, 0, 0x00000099),
    req('rd', 0x6, 0x1004, 0, 0),      resp('rd', 0x6, 1, 0, 0x44444444),
    req('rd', 0x7, 0x1008, 0, 0),      resp('rd', 0x7, 1, 0, 0x88888888),
    req('rd', 0x8, 0x100c, 0, 0),      resp('rd', 0x8, 1, 0, 0xcccccccc),
  ]

# End-to-end set-wide stream: walk two tags across many sets to ensure broad coverage
def sassoc_wide_stream_two_tags():
  msgs = []
  opq  = 0
  for i in range(8):
    a = 0x00001000 + i*0x10
    b = a + 0x80
    msgs += [ req('rd', opq, a, 0, 0), resp('rd', opq, 0, 0, 0xabcd0000 + a) ]; opq += 1
    msgs += [ req('rd', opq, b, 0, 0), resp('rd', opq, 0, 0, 0xabcd0000 + b) ]; opq += 1
   
    msgs += [ req('rd', opq, a, 0, 0), resp('rd', opq, 1, 0, 0xabcd0000 + a) ]; opq += 1
    msgs += [ req('rd', opq, b, 0, 0), resp('rd', opq, 1, 0, 0xabcd0000 + b) ]; opq += 1
  return msgs

def sassoc_lru_update_on_write():
  return [
    req('rd', 0x0, 0x1000, 0, 0),          resp('rd', 0x0, 0, 0, 0xabcd1000), 
    req('rd', 0x1, 0x1080, 0, 0),          resp('rd', 0x1, 0, 0, 0xabcd1080), 
    req('wr', 0x2, 0x1080, 0, 0xfacecafe), resp('wr', 0x2, 1, 0, 0),
    req('rd', 0x3, 0x1100, 0, 0),          resp('rd', 0x3, 0, 0, 0xabcd1100),
    req('rd', 0x4, 0x1080, 0, 0),          resp('rd', 0x4, 1, 0, 0xfacecafe),
    req('rd', 0x5, 0x1000, 0, 0),          resp('rd', 0x5, 0, 0, 0xabcd1000),
  ]

def sassoc_write_miss_evicts_dirty_other_way_verify():
  return [
    req('rd', 0x0, 0x1000, 0, 0),          resp('rd', 0x0, 0, 0, 0xabcd1000),  
    req('rd', 0x1, 0x1080, 0, 0),          resp('rd', 0x1, 0, 0, 0xabcd1080),  

    req('wr', 0x2, 0x1000, 0, 0xaaaa7777), resp('wr', 0x2, 1, 0, 0),

    req('rd', 0x3, 0x1080, 0, 0),          resp('rd', 0x3, 1, 0, 0xabcd1080),

    req('wr', 0x4, 0x1100, 0, 0x22224444), resp('wr', 0x4, 0, 0, 0),

    req('rd', 0x5, 0x1000, 0, 0),          resp('rd', 0x5, 0, 0, 0xaaaa7777),

    req('rd', 0x6, 0x1100, 0, 0),          resp('rd', 0x6, 1, 0, 0x22224444),
  ]


test_case_table_sassoc = mk_test_case_table([
  (                       "msg_func            mem_data_func    stall lat src sink"),

  [ "sassoc_two_way_coexist_reads",        sassoc_two_way_coexist_reads,        data_512B,   0.0,   0,  0,   0 ],
  [ "sassoc_two_way_coexist_reads_stress", sassoc_two_way_coexist_reads,        data_512B,   0.9,   3,  7,  10 ],

  [ "sassoc_write_hit_on_clean_then_readback", sassoc_write_hit_on_clean_then_readback, data_64B, 0.0, 0, 0, 0 ],
  [ "sassoc_read_hit_from_dirty",              sassoc_read_hit_from_dirty,              data_64B, 0.0, 0, 0, 0 ],

  [ "sassoc_read_miss_refill_no_evict",    sassoc_read_miss_refill_no_evict,    data_512B,   0.0,   0,  0,   0 ],
  [ "sassoc_write_miss_refill_no_evict",   sassoc_write_miss_refill_no_evict,   None,        0.0,   0,  0,   0 ],

  [ "sassoc_lru_clean_evict",              sassoc_lru_clean_evict,              data_512B,   0.0,   0,  0,   0 ],
  [ "sassoc_lru_clean_evict_stress",       sassoc_lru_clean_evict,              data_512B,   0.95,  4,  8,  12 ],

  [ "sassoc_lru_dirty_writeback_evict",    sassoc_lru_dirty_writeback_evict,    data_512B,   0.0,   0,  0,   0 ],
  [ "sassoc_lru_dirty_writeback_stress",   sassoc_lru_dirty_writeback_evict,    data_512B,   0.95,  5, 10,  10 ],

  [ "sassoc_three_tags_sequence",          sassoc_three_tags_sequence,          data_512B,   0.0,   0,  0,   0 ],

  [ "sassoc_four_bank_intra_line_mix",     sassoc_four_bank_intra_line_mix,     data_64B,    0.0,   0,  0,   0 ],
  [ "sassoc_four_bank_intra_line_stress",  sassoc_four_bank_intra_line_mix,     data_64B,    0.9,   4,  8,  12 ],

  [ "sassoc_wide_stream_two_tags",        sassoc_wide_stream_two_tags,        data_512B, 0.0, 0, 0, 0 ],
  [ "sassoc_wide_stream_two_tags_stress", sassoc_wide_stream_two_tags,        data_512B, 0.95, 4, 8, 12 ],

  [ "sassoc_lru_update_on_write", sassoc_lru_update_on_write, data_512B, 0.0, 0, 0, 0 ],
  [ "sassoc_lru_update_on_write_stress", sassoc_lru_update_on_write, data_512B, 0.95, 4, 9, 12 ],

  [ "sassoc_write_miss_evicts_dirty_other_way_verify", sassoc_write_miss_evicts_dirty_other_way_verify, data_512B, 0.0, 0, 0, 0 ],
  [ "sassoc_write_miss_evicts_dirty_other_way_stress", sassoc_write_miss_evicts_dirty_other_way_verify, data_512B, 0.95, 5, 9, 12 ],

])

@pytest.mark.parametrize( **test_case_table_sassoc )
def test_sassoc( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Banked cache test
#-------------------------------------------------------------------------
# This test case is to test if the bank offset is implemented correctly.
# The idea behind this test case is to differentiate between a cache with
# no bank bits and a design has one/two bank bits by looking at cache
# request hit/miss status.

# We first design a test case for 2-way set-associative cache. The last
# request should hit only if students implement the correct index bit to
# be [6:9]. If they implement the index bit to be [4:7] or [5:8], the
# last request is a miss, which is wrong. See below for explanation. This
# test case also works for the baseline direct-mapped cache.

# Direct-mapped
#
#   no bank(should fail):
#      idx
#   00 0000 0000
#   01 0000 0000
#   10 0000 0000
#   00 0000 0000
#   idx: 0, 0, 0 so the third one with tag 10 will evict the first one
#   with tag 00, and thus the fourth read will miss instead of hit.
#
#   4-bank(correct):
#    idx  bk
#   00 00 00 0000
#   01 00 00 0000
#   10 00 00 0000
#   00 00 00 0000
#   idx: 0, 4, 8 so the third one with tag 10 won't evict anything, and
#   thus the fourth read will hit.

# 2-way set-associative
#
#   no bank(should fail):
#        idx
#   00 0 000 0000
#   01 0 000 0000
#   10 0 000 0000
#   00 0 000 0000
#   idx: 0, 0, 0 so the third one with tag 10 will evict the first one
#   with tag 00, and thus the fourth read will miss instead of hit.
#
#   4-bank(correct):
#     idx  bk
#   0 0 00 00 0000
#   0 1 00 00 0000
#   1 0 00 00 0000
#   idx: 0, 4, 0 so the third one with tag 10 won't evict anything, and
#   thus the fourth read will hit.

def bank_test():
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'rd', 0x0, 0x00000000, 0, 0 ), resp( 'rd', 0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x00000100, 0, 0 ), resp( 'rd', 0x1, 0,   0,  0x00c0ffee ),
    req( 'rd', 0x2, 0x00000200, 0, 0 ), resp( 'rd', 0x2, 0,   0,  0xffffffff ),
    req( 'rd', 0x3, 0x00000000, 0, 0 ), resp( 'rd', 0x3, 1,   0,  0xdeadbeef ),
  ]

def bank_test_data():
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000100, 0x00c0ffee,
    0x00000200, 0xffffffff,
  ]

def bank_test_write_then_hits():
  return [
    req('rd', 0x0, 0x00000000, 0, 0), resp('rd', 0x0, 0, 0, 0xdeadbeef),
    req('rd', 0x1, 0x00000100, 0, 0), resp('rd', 0x1, 0, 0, 0x00c0ffee),
    req('rd', 0x2, 0x00000200, 0, 0), resp('rd', 0x2, 0, 0, 0xffffffff),

    req('wr', 0x3, 0x00000000, 0, 0x11112222), resp('wr', 0x3, 1, 0, 0),
    req('rd', 0x4, 0x00000000, 0, 0),          resp('rd', 0x4, 1, 0, 0x11112222),
    req('rd', 0x5, 0x00000100, 0, 0),          resp('rd', 0x5, 1, 0, 0x00c0ffee),
    req('rd', 0x6, 0x00000200, 0, 0),          resp('rd', 0x6, 1, 0, 0xffffffff),
  ]

test_case_table_bank = mk_test_case_table([
  (             "msg_func   mem_data_func   stall lat src sink"),
  [ "bank_test", bank_test, bank_test_data, 0.0,  0,  0,  0    ],
  [ "bank_test_write_then_hits", bank_test_write_then_hits, bank_test_data, 0.0, 0, 0, 0 ],
])

@pytest.mark.parametrize( **test_case_table_bank )
def test_bank( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )
