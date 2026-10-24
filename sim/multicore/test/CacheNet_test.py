#=========================================================================
# CacheNet_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim

from pymtl3.stdlib.mem.ifcs    import MemResponderIfc
from pymtl3.stdlib.mem         import mk_mem_msg, MemMsgType
from pymtl3.stdlib.stream      import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.stream      import IStreamDeqAdapterFL, OStreamEnqAdapterFL

from multicore.CacheNet import CacheNet

#-------------------------------------------------------------------------
# Cache Message Types
#-------------------------------------------------------------------------

CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )

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
# CacheMock
#-------------------------------------------------------------------------
# Mock-up for cache. Accepts cache requests and turns them directly into
# cache response using the id as the data for read responses.

class CacheMock( Component ):

  def construct( s, src_id=0 ):

    # Interface

    s.proc2cache = MemResponderIfc( CacheReqType, CacheRespType )

    # Proc <-> Cache Adapters

    s.cache_reqstream_q  = IStreamDeqAdapterFL( CacheReqType  )
    s.cache_respstream_q = OStreamEnqAdapterFL( CacheRespType )

    connect( s.proc2cache.reqstream, s.cache_reqstream_q.istream   )
    connect( s.cache_respstream_q.ostream, s.proc2cache.respstream )

    # Line Tracing

    s.trace_str = " "

    # Logic

    @update_once
    def logic():

      s.trace_str = " "

      # Process cache request if input and output stream are both ready

      if s.cache_reqstream_q.deq.rdy() and s.cache_respstream_q.enq.rdy():

        s.trace_str = "*"

        # Dequeue cache request

        cachereq = s.cache_reqstream_q.deq()

        # Create cache response by copying over fields from request

        cacheresp = CacheRespType( cachereq.type_, cachereq.opaque,
                                   Bits2(0), cachereq.len, Bits32(0) )

        # Handle read transactions

        if ( cachereq.type_ == MemMsgType.READ ):
          cacheresp.data = Bits32(src_id)

        # Enqueue cache response on output stream

        s.cache_respstream_q.enq( cacheresp )

  def line_trace( s ):
    return s.trace_str

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.srcs  = [ StreamSourceFL( CacheReqType ) for _ in range(4) ]
    s.sinks = [ StreamSinkFL( CacheRespType, ordered=False ) for _ in range(4) ]
    s.net   = CacheNet()
    s.cachemocks = [ CacheMock(i) for i in range(4) ]

    # Connect

    for i in range(4):
      s.srcs[i].ostream  //= s.net.proc2net[i].reqstream
      s.sinks[i].istream //= s.net.proc2net[i].respstream
      s.net.net2cache[i] //= s.cachemocks[i].proc2cache

  def done( s ):
    for i in range(4):
      if not s.srcs[i].done() or not s.sinks[i].done():
        return False
    return True

  def line_trace( s ):
    srcs_str      = "|".join([ src.line_trace()  for src  in s.srcs  ])
    sinks_str     = "|".join([ sink.line_trace() for sink in s.sinks ])
    cachemock_str = "".join([ cachemock.line_trace() for cachemock in s.cachemocks ])
    return f"{srcs_str} > ({s.net.line_trace()}){cachemock_str} > {sinks_str}"

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):

  th = TestHarness()

  msgs0 = [
    #    type  opq  addr   len data                type  opq  test len data
    creq( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 0
    creq( 'in', 0x0, 0x1010, 0, 0xdeadbeef ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 1
    creq( 'in', 0x0, 0x1020, 0, 0xdeadbeef ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 2
    creq( 'in', 0x0, 0x1030, 0, 0xdeadbeef ), cresp( 'in', 0x0, 0,   0,  0    ), # go to bank 3
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

  run_sim( th, cmdline_opts, duts=['net'] )

#-------------------------------------------------------------------------
# Test Cases: One of each type
#-------------------------------------------------------------------------

one_in = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), cresp( 'in', 0x0, 0,   0,  0    ),
]

one_wr = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'wr', 0x0, 0x1000, 0, 0xdeadbeef ), cresp( 'wr', 0x0, 0,   0,  0    ),
]

one_rd = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  0    ),
]

#-------------------------------------------------------------------------
# Test Cases: one per bank
#-------------------------------------------------------------------------

one_per_bank = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  0    ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  1    ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  2    ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  3    ),
]

#-------------------------------------------------------------------------
# Test Cases: stream to one bank
#-------------------------------------------------------------------------

stream_to_bank0 = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  0    ),
  creq( 'rd', 0x1, 0x1000, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  0    ),
  creq( 'rd', 0x2, 0x1000, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  0    ),
  creq( 'rd', 0x3, 0x1000, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  0    ),
  creq( 'rd', 0x4, 0x1000, 0, 0          ), cresp( 'rd', 0x4, 0,   0,  0    ),
  creq( 'rd', 0x5, 0x1000, 0, 0          ), cresp( 'rd', 0x5, 0,   0,  0    ),
  creq( 'rd', 0x6, 0x1000, 0, 0          ), cresp( 'rd', 0x6, 0,   0,  0    ),
  creq( 'rd', 0x7, 0x1000, 0, 0          ), cresp( 'rd', 0x7, 0,   0,  0    ),
]

stream_to_bank1 = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1010, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  1    ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  1    ),
  creq( 'rd', 0x2, 0x1010, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  1    ),
  creq( 'rd', 0x3, 0x1010, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  1    ),
  creq( 'rd', 0x4, 0x1010, 0, 0          ), cresp( 'rd', 0x4, 0,   0,  1    ),
  creq( 'rd', 0x5, 0x1010, 0, 0          ), cresp( 'rd', 0x5, 0,   0,  1    ),
  creq( 'rd', 0x6, 0x1010, 0, 0          ), cresp( 'rd', 0x6, 0,   0,  1    ),
  creq( 'rd', 0x7, 0x1010, 0, 0          ), cresp( 'rd', 0x7, 0,   0,  1    ),
]

stream_to_bank2 = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1020, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  2    ),
  creq( 'rd', 0x1, 0x1020, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  2    ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  2    ),
  creq( 'rd', 0x3, 0x1020, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  2    ),
  creq( 'rd', 0x4, 0x1020, 0, 0          ), cresp( 'rd', 0x4, 0,   0,  2    ),
  creq( 'rd', 0x5, 0x1020, 0, 0          ), cresp( 'rd', 0x5, 0,   0,  2    ),
  creq( 'rd', 0x6, 0x1020, 0, 0          ), cresp( 'rd', 0x6, 0,   0,  2    ),
  creq( 'rd', 0x7, 0x1020, 0, 0          ), cresp( 'rd', 0x7, 0,   0,  2    ),
]

stream_to_bank3 = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1030, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  3    ),
  creq( 'rd', 0x1, 0x1030, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  3    ),
  creq( 'rd', 0x2, 0x1030, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  3    ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  3    ),
  creq( 'rd', 0x4, 0x1030, 0, 0          ), cresp( 'rd', 0x4, 0,   0,  3    ),
  creq( 'rd', 0x5, 0x1030, 0, 0          ), cresp( 'rd', 0x5, 0,   0,  3    ),
  creq( 'rd', 0x6, 0x1030, 0, 0          ), cresp( 'rd', 0x6, 0,   0,  3    ),
  creq( 'rd', 0x7, 0x1030, 0, 0          ), cresp( 'rd', 0x7, 0,   0,  3    ),
]

#-------------------------------------------------------------------------
# Test Cases: stream to all banks
#-------------------------------------------------------------------------
# Note that we can only use 4-bits of the opaque field because the
# adapters use the top four bits. And since we are using an unordered
# stream sink, every response has to be unique. So we use the len field
# to help give us ways to create more unique responses.

stream_to_all = [
  #    type  opq  addr   len data                type  opq  test len data
  creq( 'rd', 0x0, 0x1000, 0, 0          ), cresp( 'rd', 0x0, 0,   0,  0    ),
  creq( 'rd', 0x1, 0x1010, 0, 0          ), cresp( 'rd', 0x1, 0,   0,  1    ),
  creq( 'rd', 0x2, 0x1020, 0, 0          ), cresp( 'rd', 0x2, 0,   0,  2    ),
  creq( 'rd', 0x3, 0x1030, 0, 0          ), cresp( 'rd', 0x3, 0,   0,  3    ),
  creq( 'rd', 0x4, 0x1000, 0, 0          ), cresp( 'rd', 0x4, 0,   0,  0    ),
  creq( 'rd', 0x5, 0x1010, 0, 0          ), cresp( 'rd', 0x5, 0,   0,  1    ),
  creq( 'rd', 0x6, 0x1020, 0, 0          ), cresp( 'rd', 0x6, 0,   0,  2    ),
  creq( 'rd', 0x7, 0x1030, 0, 0          ), cresp( 'rd', 0x7, 0,   0,  3    ),
  creq( 'rd', 0x8, 0x1000, 0, 0          ), cresp( 'rd', 0x8, 0,   0,  0    ),
  creq( 'rd', 0x9, 0x1010, 0, 0          ), cresp( 'rd', 0x9, 0,   0,  1    ),
  creq( 'rd', 0xa, 0x1020, 0, 0          ), cresp( 'rd', 0xa, 0,   0,  2    ),
  creq( 'rd', 0xb, 0x1030, 0, 0          ), cresp( 'rd', 0xb, 0,   0,  3    ),
  creq( 'rd', 0xc, 0x1000, 0, 0          ), cresp( 'rd', 0xc, 0,   0,  0    ),
  creq( 'rd', 0xd, 0x1010, 0, 0          ), cresp( 'rd', 0xd, 0,   0,  1    ),
  creq( 'rd', 0xe, 0x1020, 0, 0          ), cresp( 'rd', 0xe, 0,   0,  2    ),
  creq( 'rd', 0xf, 0x1030, 0, 0          ), cresp( 'rd', 0xf, 0,   0,  3    ),
  creq( 'rd', 0x0, 0x1000, 1, 0          ), cresp( 'rd', 0x0, 0,   1,  0    ),
  creq( 'rd', 0x1, 0x1010, 1, 0          ), cresp( 'rd', 0x1, 0,   1,  1    ),
  creq( 'rd', 0x2, 0x1020, 1, 0          ), cresp( 'rd', 0x2, 0,   1,  2    ),
  creq( 'rd', 0x3, 0x1030, 1, 0          ), cresp( 'rd', 0x3, 0,   1,  3    ),
  creq( 'rd', 0x4, 0x1000, 1, 0          ), cresp( 'rd', 0x4, 0,   1,  0    ),
  creq( 'rd', 0x5, 0x1010, 1, 0          ), cresp( 'rd', 0x5, 0,   1,  1    ),
  creq( 'rd', 0x6, 0x1020, 1, 0          ), cresp( 'rd', 0x6, 0,   1,  2    ),
  creq( 'rd', 0x7, 0x1030, 1, 0          ), cresp( 'rd', 0x7, 0,   1,  3    ),
  creq( 'rd', 0x8, 0x1000, 1, 0          ), cresp( 'rd', 0x8, 0,   1,  0    ),
  creq( 'rd', 0x9, 0x1010, 1, 0          ), cresp( 'rd', 0x9, 0,   1,  1    ),
  creq( 'rd', 0xa, 0x1020, 1, 0          ), cresp( 'rd', 0xa, 0,   1,  2    ),
  creq( 'rd', 0xb, 0x1030, 1, 0          ), cresp( 'rd', 0xb, 0,   1,  3    ),
  creq( 'rd', 0xc, 0x1000, 1, 0          ), cresp( 'rd', 0xc, 0,   1,  0    ),
  creq( 'rd', 0xd, 0x1010, 1, 0          ), cresp( 'rd', 0xd, 0,   1,  1    ),
  creq( 'rd', 0xe, 0x1020, 1, 0          ), cresp( 'rd', 0xe, 0,   1,  2    ),
  creq( 'rd', 0xf, 0x1030, 1, 0          ), cresp( 'rd', 0xf, 0,   1,  3    ),
]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                  "msgs    src_delay sink_delay delay_mode"),
  [ "one_in",                         one_in,                 0,  0,  'fixed'  ],
  [ "one_wr",                         one_wr,                 0,  0,  'fixed'  ],
  [ "one_rd",                         one_rd,                 0,  0,  'fixed'  ],
  [ "one_per_bank",                   one_per_bank,           0,  0,  'fixed'  ],
  [ "stream_to_bank0",                stream_to_bank0,        0,  0,  'fixed'  ],
  [ "stream_to_bank1",                stream_to_bank1,        0,  0,  'fixed'  ],
  [ "stream_to_bank2",                stream_to_bank2,        0,  0,  'fixed'  ],
  [ "stream_to_bank3",                stream_to_bank3,        0,  0,  'fixed'  ],
  [ "stream_to_all",                  stream_to_all,          0,  0,  'fixed'  ],
  [ "stream_to_all_fixed_2x0",        stream_to_all,          2,  0,  'fixed'  ],
  [ "stream_to_all_fixed_0x2",        stream_to_all,          0,  2,  'fixed'  ],
  [ "stream_to_all_fixed_0x4",        stream_to_all,          0,  4,  'fixed'  ],
  [ "stream_to_all_random_20x0",      stream_to_all,         20,  0,  'random' ],
  [ "stream_to_all_random_0x20",      stream_to_all,          0, 20,  'random' ],
  [ "stream_to_all_random_20x20",     stream_to_all,         20, 20,  'random' ],
])

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness()

  th.set_param("top.srcs[0].construct",
    msgs                = test_params.msgs[::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[1].construct",
    msgs                = test_params.msgs[::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[2].construct",
    msgs                = test_params.msgs[::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[3].construct",
    msgs                = test_params.msgs[::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = test_params.msgs[1::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = test_params.msgs[1::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = test_params.msgs[1::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[3].construct",
    msgs                = test_params.msgs[1::2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['net'] )
