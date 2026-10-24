#=========================================================================
# MultiCoreDatacache_test
#=========================================================================

import pytest
import struct

from random import seed, randint

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.mem        import MemoryFL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL

from cache.test.CacheFL_test import cmp_wo_test_field
from multicore.MultiCoreDataCache import MultiCoreDataCache

#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )
MemReqType,   MemRespType   = mk_mem_msg( 8, 32, 128 )

def creq( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return CacheReqType( type_, opaque, addr, len, data )

def cresp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return CacheRespType( type_, opaque, test, len, data )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.srcs  = [ StreamSourceFL( CacheReqType ) for _ in range(4) ]
    s.sinks = [ StreamSinkFL( CacheRespType, cmp_fn=cmp_wo_test_field, ordered=False ) for _ in range(4) ]
    s.cache = MultiCoreDataCache()
    s.mem   = MemoryFL( 1, [(MemReqType,MemRespType)] )

    # Connect

    for i in range(4):
      s.srcs[i].ostream  //= s.cache.proc2cache[i].reqstream
      s.sinks[i].istream //= s.cache.proc2cache[i].respstream
    s.cache.cache2mem //= s.mem.ifc[0]

  def load( s, addrs, data_ints ):
    for addr, data_int in zip( addrs, data_ints ):
      data_bytes_a = bytearray()
      data_bytes_a.extend( struct.pack("<I",data_int) )
      s.mem.write_mem( addr, data_bytes_a )

  def done( s ):
    for i in range(4):
      if not s.srcs[i].done() or not s.sinks[i].done():
        return False
    return True

  def line_trace( s ):
    srcs_str  = "|".join([ src.line_trace()  for src  in s.srcs  ])
    sinks_str = "|".join([ sink.line_trace() for sink in s.sinks ])
    return f"{srcs_str} > ({s.cache.line_trace()}) > {sinks_str}"

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):

  th = TestHarness()

  msgs0 = [
    #    type  opq  addr   len data                type  opq  test len data
    creq( 'in', 0x0, 0x1000, 0, 0x01010101 ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 0
    creq( 'in', 0x1, 0x1010, 0, 0x02020202 ), cresp( 'in', 0x1, 0,   0,  0    ), # go to bank 1
    creq( 'in', 0x2, 0x1020, 0, 0x03030303 ), cresp( 'in', 0x2, 0,   0,  0    ), # go to bank 2
    creq( 'in', 0x3, 0x1030, 0, 0x04040404 ), cresp( 'in', 0x3, 0,   0,  0    ), # go to bank 3
  ]

  # Set parameters

  th.set_param("top.srcs[0].construct",  msgs=msgs0[::2]  )
  th.set_param("top.sinks[0].construct", msgs=msgs0[1::2] )
  th.set_param("top.srcs[1].construct",  msgs=[]          )
  th.set_param("top.sinks[1].construct", msgs=[]          )
  th.set_param("top.srcs[2].construct",  msgs=[]          )
  th.set_param("top.sinks[2].construct", msgs=[]          )
  th.set_param("top.srcs[3].construct",  msgs=[]          )
  th.set_param("top.sinks[3].construct", msgs=[]          )

  th.elaborate()

  # Run the test

  run_sim( th, cmdline_opts, duts=['cache'] )

#-------------------------------------------------------------------------
# read_hit_word
#-------------------------------------------------------------------------

read_hit_word = [
  #     type  opq  addr   len data                type  opq  test len data
  creq( 'in', 0x0, 0x1000, 0, 0x01010101 ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 0
  creq( 'in', 0x1, 0x1010, 0, 0x02020202 ), cresp( 'in', 0x1, 0,   0,  0    ), # go to bank 1
  creq( 'in', 0x2, 0x1020, 0, 0x03030303 ), cresp( 'in', 0x2, 0,   0,  0    ), # go to bank 2
  creq( 'in', 0x3, 0x1030, 0, 0x04040404 ), cresp( 'in', 0x3, 0,   0,  0    ), # go to bank 3
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 1,   0,  0x01010101 ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 1,   0,  0x02020202 ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 1,   0,  0x03030303 ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 1,   0,  0x04040404 ),
]

#-------------------------------------------------------------------------
# read_hit_cacheline
#-------------------------------------------------------------------------

read_hit_cacheline = [
  #     type  opq  addr   len data                type  opq  test len data

  creq( 'in', 0x0, 0x1000, 0, 0x01010101 ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 0
  creq( 'in', 0x1, 0x1010, 0, 0x02020202 ), cresp( 'in', 0x1, 0,   0,  0    ), # go to bank 1
  creq( 'in', 0x2, 0x1020, 0, 0x03030303 ), cresp( 'in', 0x2, 0,   0,  0    ), # go to bank 2
  creq( 'in', 0x3, 0x1030, 0, 0x04040404 ), cresp( 'in', 0x3, 0,   0,  0    ), # go to bank 3
  creq( 'in', 0x4, 0x1000, 0, 0x11111111 ), cresp( 'in', 0x4, 0,   0,  0    ), # go to bank 0
  creq( 'in', 0x5, 0x1014, 0, 0x12121212 ), cresp( 'in', 0x5, 0,   0,  0    ), # go to bank 1
  creq( 'in', 0x6, 0x1028, 0, 0x13131313 ), cresp( 'in', 0x6, 0,   0,  0    ), # go to bank 2
  creq( 'in', 0x7, 0x103c, 0, 0x14141414 ), cresp( 'in', 0x7, 0,   0,  0    ), # go to bank 3
  creq( 'in', 0x8, 0x1000, 0, 0x21212121 ), cresp( 'in', 0x8, 0,   0,  0    ), # go to bank 0
  creq( 'in', 0x9, 0x1014, 0, 0x22222222 ), cresp( 'in', 0x9, 0,   0,  0    ), # go to bank 1
  creq( 'in', 0xa, 0x1028, 0, 0x23232323 ), cresp( 'in', 0xa, 0,   0,  0    ), # go to bank 2
  creq( 'in', 0xb, 0x103c, 0, 0x24242424 ), cresp( 'in', 0xb, 0,   0,  0    ), # go to bank 3
  creq( 'in', 0xc, 0x1000, 0, 0x31313131 ), cresp( 'in', 0xc, 0,   0,  0    ), # go to bank 0
  creq( 'in', 0xd, 0x1014, 0, 0x32323232 ), cresp( 'in', 0xd, 0,   0,  0    ), # go to bank 1
  creq( 'in', 0xe, 0x1028, 0, 0x33333333 ), cresp( 'in', 0xe, 0,   0,  0    ), # go to bank 2
  creq( 'in', 0xf, 0x103c, 0, 0x34343434 ), cresp( 'in', 0xf, 0,   0,  0    ), # go to bank 3

  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 1,   0,  0x01010101 ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 1,   0,  0x02020202 ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 1,   0,  0x03030303 ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 1,   0,  0x04040404 ),
  creq( 'rd', 0x4, 0x1000, 0, 0          ), cresp( 'rd', 0x4, 1,   0,  0x11111111 ),
  creq( 'rd', 0x5, 0x1014, 0, 0          ), cresp( 'rd', 0x5, 1,   0,  0x12121212 ),
  creq( 'rd', 0x6, 0x1028, 0, 0          ), cresp( 'rd', 0x6, 1,   0,  0x13131313 ),
  creq( 'rd', 0x7, 0x103c, 0, 0          ), cresp( 'rd', 0x7, 1,   0,  0x14141414 ),
  creq( 'rd', 0x8, 0x1000, 0, 0          ), cresp( 'rd', 0x8, 1,   0,  0x21212121 ),
  creq( 'rd', 0x9, 0x1014, 0, 0          ), cresp( 'rd', 0x9, 1,   0,  0x22222222 ),
  creq( 'rd', 0xa, 0x1028, 0, 0          ), cresp( 'rd', 0xa, 1,   0,  0x23232323 ),
  creq( 'rd', 0xb, 0x103c, 0, 0          ), cresp( 'rd', 0xb, 1,   0,  0x24242424 ),
  creq( 'rd', 0xc, 0x1000, 0, 0          ), cresp( 'rd', 0xc, 1,   0,  0x31313131 ),
  creq( 'rd', 0xd, 0x1014, 0, 0          ), cresp( 'rd', 0xd, 1,   0,  0x32323232 ),
  creq( 'rd', 0xe, 0x1028, 0, 0          ), cresp( 'rd', 0xe, 1,   0,  0x33333333 ),
  creq( 'rd', 0xf, 0x103c, 0, 0          ), cresp( 'rd', 0xf, 1,   0,  0x34343434 ),

]

#-------------------------------------------------------------------------
# write_miss_word
#-------------------------------------------------------------------------

write_miss_word = [
  #     type  opq  addr   len data                type  opq  test len data
  creq( 'wr', 0x0, 0x1000, 0, 0x01010101 ), cresp( 'wr', 0x0, 0,   0,  0    ), # go to bank 0
  creq( 'wr', 0x1, 0x1010, 0, 0x02020202 ), cresp( 'wr', 0x1, 0,   0,  0    ), # go to bank 1
  creq( 'wr', 0x2, 0x1020, 0, 0x03030303 ), cresp( 'wr', 0x2, 0,   0,  0    ), # go to bank 2
  creq( 'wr', 0x3, 0x1030, 0, 0x04040404 ), cresp( 'wr', 0x3, 0,   0,  0    ), # go to bank 3
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  0x01010101 ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  0x02020202 ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  0x03030303 ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  0x04040404 ),
]

#-------------------------------------------------------------------------
# write_miss_cacheline
#-------------------------------------------------------------------------

write_miss_cacheline = [
  #     type  opq  addr   len data                type  opq  test len data

  creq( 'wr', 0x0, 0x1000, 0, 0x01010101 ), cresp( 'wr', 0x0, 0,   0,  0    ), # go to bank 0
  creq( 'wr', 0x1, 0x1010, 0, 0x02020202 ), cresp( 'wr', 0x1, 0,   0,  0    ), # go to bank 1
  creq( 'wr', 0x2, 0x1020, 0, 0x03030303 ), cresp( 'wr', 0x2, 0,   0,  0    ), # go to bank 2
  creq( 'wr', 0x3, 0x1030, 0, 0x04040404 ), cresp( 'wr', 0x3, 0,   0,  0    ), # go to bank 3
  creq( 'wr', 0x4, 0x1000, 0, 0x11111111 ), cresp( 'wr', 0x4, 0,   0,  0    ), # go to bank 0
  creq( 'wr', 0x5, 0x1014, 0, 0x12121212 ), cresp( 'wr', 0x5, 0,   0,  0    ), # go to bank 1
  creq( 'wr', 0x6, 0x1028, 0, 0x13131313 ), cresp( 'wr', 0x6, 0,   0,  0    ), # go to bank 2
  creq( 'wr', 0x7, 0x103c, 0, 0x14141414 ), cresp( 'wr', 0x7, 0,   0,  0    ), # go to bank 3
  creq( 'wr', 0x8, 0x1000, 0, 0x21212121 ), cresp( 'wr', 0x8, 0,   0,  0    ), # go to bank 0
  creq( 'wr', 0x9, 0x1014, 0, 0x22222222 ), cresp( 'wr', 0x9, 0,   0,  0    ), # go to bank 1
  creq( 'wr', 0xa, 0x1028, 0, 0x23232323 ), cresp( 'wr', 0xa, 0,   0,  0    ), # go to bank 2
  creq( 'wr', 0xb, 0x103c, 0, 0x24242424 ), cresp( 'wr', 0xb, 0,   0,  0    ), # go to bank 3
  creq( 'wr', 0xc, 0x1000, 0, 0x31313131 ), cresp( 'wr', 0xc, 0,   0,  0    ), # go to bank 0
  creq( 'wr', 0xd, 0x1014, 0, 0x32323232 ), cresp( 'wr', 0xd, 0,   0,  0    ), # go to bank 1
  creq( 'wr', 0xe, 0x1028, 0, 0x33333333 ), cresp( 'wr', 0xe, 0,   0,  0    ), # go to bank 2
  creq( 'wr', 0xf, 0x103c, 0, 0x34343434 ), cresp( 'wr', 0xf, 0,   0,  0    ), # go to bank 3

  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 1,   0,  0x01010101 ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 1,   0,  0x02020202 ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 1,   0,  0x03030303 ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 1,   0,  0x04040404 ),
  creq( 'rd', 0x4, 0x1000, 0, 0          ), cresp( 'rd', 0x4, 1,   0,  0x11111111 ),
  creq( 'rd', 0x5, 0x1014, 0, 0          ), cresp( 'rd', 0x5, 1,   0,  0x12121212 ),
  creq( 'rd', 0x6, 0x1028, 0, 0          ), cresp( 'rd', 0x6, 1,   0,  0x13131313 ),
  creq( 'rd', 0x7, 0x103c, 0, 0          ), cresp( 'rd', 0x7, 1,   0,  0x14141414 ),
  creq( 'rd', 0x8, 0x1000, 0, 0          ), cresp( 'rd', 0x8, 1,   0,  0x21212121 ),
  creq( 'rd', 0x9, 0x1014, 0, 0          ), cresp( 'rd', 0x9, 1,   0,  0x22222222 ),
  creq( 'rd', 0xa, 0x1028, 0, 0          ), cresp( 'rd', 0xa, 1,   0,  0x23232323 ),
  creq( 'rd', 0xb, 0x103c, 0, 0          ), cresp( 'rd', 0xb, 1,   0,  0x24242424 ),
  creq( 'rd', 0xc, 0x1000, 0, 0          ), cresp( 'rd', 0xc, 1,   0,  0x31313131 ),
  creq( 'rd', 0xd, 0x1014, 0, 0          ), cresp( 'rd', 0xd, 1,   0,  0x32323232 ),
  creq( 'rd', 0xe, 0x1028, 0, 0          ), cresp( 'rd', 0xe, 1,   0,  0x33333333 ),
  creq( 'rd', 0xf, 0x103c, 0, 0          ), cresp( 'rd', 0xf, 1,   0,  0x34343434 ),

]

#-------------------------------------------------------------------------
# random
#-------------------------------------------------------------------------

# 1024B of random data

def data_random():
  seed(0xdeadbeef)
  data = []
  for i in range(256):
    data.extend([0x00001000+i*4,randint(0,0xffffffff)])
  return data

def random_misses():

  vmem = data_random()[1::2]
  msgs = []

  for i in range(100):
    idx = randint(0,255)

    correct_data = vmem[idx]
    msgs.extend([
      creq( 'rd', i, 0x00001000+4*idx, 0, 0 ), cresp( 'rd', i, 0, 0, correct_data ),
    ])

  return msgs

def random_hits():

  vmem = data_random()[1::2]
  msgs = []

  # First fill the cache with read misses

  for i in range(0,64):
    correct_data = vmem[i]
    msgs.extend([
      creq( 'rd', i, 0x00001000+4*i, 0, 0 ), cresp( 'rd', i, 0, 0, correct_data ),
    ])

  # Now all remaining accesses should be hits

  for i in range(100):
    idx = randint(0,63)

    correct_data = vmem[idx]
    msgs.extend([
      creq( 'rd', i, 0x00001000+4*idx, 0, 0 ), cresp( 'rd', i, 0, 0, correct_data ),
    ])

  return msgs

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                         "msgs                  mem_data_func stall  lat src sink"),
  [ "read_hit_word",         read_hit_word,        None,           0,   0,  0,  0  ],
  [ "read_hit_cacheline",    read_hit_cacheline,   None,           0,   0,  0,  0  ],
  [ "write_miss_word",       write_miss_word,      None,           0,   0,  0,  0  ],
  [ "write_miss_cacheline",  write_miss_cacheline, None,           0,   0,  0,  0  ],
  [ "random_misses",         random_misses,        data_random,    0,   0,  0,  0  ],
  [ "random_hits",           random_hits,          data_random,    0,   0,  0,  0  ],
  [ "random_misses_delays",  random_misses,        data_random,    0.9, 3,  10, 10 ],
  [ "random_hits_delays",    random_hits,          data_random,    0.9, 3,  10, 10 ],
])

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness()

  # Generate messages

  msgs = test_params.msgs
  if callable(test_params.msgs):
    msgs = test_params.msgs()

  # Set parameters

  th.set_param("top.srcs[0].construct",
    msgs                = msgs[::2],
    initial_delay       = test_params.src,
    interval_delay      = test_params.src )

  th.set_param("top.srcs[1].construct",
    msgs                = msgs[::2],
    initial_delay       = test_params.src,
    interval_delay      = test_params.src )

  th.set_param("top.srcs[2].construct",
    msgs                = msgs[::2],
    initial_delay       = test_params.src,
    interval_delay      = test_params.src )

  th.set_param("top.srcs[3].construct",
    msgs                = msgs[::2],
    initial_delay       = test_params.src,
    interval_delay      = test_params.src )

  th.set_param("top.sinks[0].construct",
    msgs                = msgs[1::2],
    initial_delay       = test_params.sink,
    interval_delay      = test_params.sink )

  th.set_param("top.sinks[1].construct",
    msgs                = msgs[1::2],
    initial_delay       = test_params.sink,
    interval_delay      = test_params.sink )

  th.set_param("top.sinks[2].construct",
    msgs                = msgs[1::2],
    initial_delay       = test_params.sink,
    interval_delay      = test_params.sink )

  th.set_param("top.sinks[3].construct",
    msgs                = msgs[1::2],
    initial_delay       = test_params.sink,
    interval_delay      = test_params.sink )

  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall,
    extra_latency=test_params.lat )

  th.elaborate()

  # Load memory before the test

  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func()
    th.load( mem[::2], mem[1::2] )

  # Run the test

  run_sim( th, cmdline_opts, duts=['cache'] )
