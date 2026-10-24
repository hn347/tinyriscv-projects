#=========================================================================
# NetRouter_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from multicore.NetMsg import mk_net_msg
from multicore.NetRouter import NetRouter
from random import seed, randint, getrandbits

#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

NetMsgType = mk_net_msg( 32 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, router_id=0 ):

    # Instantiate models

    s.srcs   = [ StreamSourceFL( NetMsgType ) for _ in range(3) ]
    s.router = NetRouter( p_msg_nbits=44 )
    s.sinks  = [ StreamSinkFL( NetMsgType ) for _ in range(3) ]

    # Connect

    s.router.router_id //= router_id
    for i in range(3):
      s.srcs[i].ostream   //= s.router.istream[i]
      s.router.ostream[i] //= s.sinks[i].istream

  def done( s ):
    for i in range(3):
      if not s.srcs[i].done() or not s.sinks[i].done():
        return False
    return True

  def line_trace( s ):
    srcs_str  = "|".join([ src.line_trace()  for src  in s.srcs  ])
    sinks_str = "|".join([ sink.line_trace() for sink in s.sinks ])
    return f"{srcs_str} > ({s.router.line_trace()}) > {sinks_str}"

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------
# These is an example of a basic test. This tests may not be valid
# depending on your routing and arbitration algorithms. You are free to
# change this test. We will not test your router since its functionality
# depends on the chosen routing and arbitration algorithms.

def test_basic( cmdline_opts ):

  th = TestHarness()

  msgs = [
    #           src  dest opaq  payload
    NetMsgType( 1,   0,   0x10, 0x10101010 ),
    NetMsgType( 2,   1,   0x11, 0x11111111 ),
    NetMsgType( 0,   2,   0x12, 0x12121212 ),
  ]

  th.set_param("top.srcs[0].construct",  msgs=[ m for m in msgs if m.src  == 0 ] )
  th.set_param("top.srcs[1].construct",  msgs=[ m for m in msgs if m.src  == 1 ] )
  th.set_param("top.srcs[2].construct",  msgs=[ m for m in msgs if m.src  == 2 ] )
  th.set_param("top.sinks[0].construct", msgs=[ m for m in msgs if m.dest == 0 ] )
  th.set_param("top.sinks[1].construct", msgs=[ m for m in msgs if m.dest != 0 ] )
  th.set_param("top.sinks[2].construct", msgs=[] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['router'] )

#-------------------------------------------------------------------------
# Test Cases: Very Simple
#-------------------------------------------------------------------------
# These are examples of a simple tests using a test case table. These
# tests may not be valid depending on your routing and arbitration
# algorithms. You are free to change these tests. We will not test your
# switch unit since its functionality depends on the chosen routing and
# arbitration algorithms.

one = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

rotate0 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   0,   0x10, 0x10101010 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
]

rotate1 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   3,   0x13, 0x13131313 ),
  NetMsgType( 2,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
]

rotate2 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   2,   0x12, 0x12121212 ),
  NetMsgType( 2,   3,   0x13, 0x13131313 ),
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
]

rotate3 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   1,   0x11, 0x11111111 ),
  NetMsgType( 2,   2,   0x12, 0x12121212 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

all_to_dest0 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   0,   0x10, 0x10101010 ),
  NetMsgType( 2,   0,   0x11, 0x11111111 ),
  NetMsgType( 0,   0,   0x12, 0x12121212 ),
]

all_to_dest1 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   1,   0x10, 0x10101010 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   1,   0x12, 0x12121212 ),
]

all_to_dest2 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   2,   0x10, 0x10101010 ),
  NetMsgType( 2,   2,   0x11, 0x11111111 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
]

all_to_dest3 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   3,   0x10, 0x10101010 ),
  NetMsgType( 2,   3,   0x11, 0x11111111 ),
  NetMsgType( 0,   3,   0x12, 0x12121212 ),
]

fan_in0 = [
  NetMsgType( 1, 0, 0x01, 0xAAAA1111 ),
  NetMsgType( 2, 0, 0x02, 0xBBBB2222 ),
  NetMsgType( 0, 0, 0x03, 0xCCCC3333 ),
]

fan_out_from2 = [
  NetMsgType( 2, 1, 0x10, 0x11110000 ),
  NetMsgType( 2, 2, 0x11, 0x22220000 ),
  NetMsgType( 2, 3, 0x12, 0x33330000 ),
]

loopback = [
  NetMsgType( 0, 0, 0x20, 0x12121212 ),
]

arb_conflict = [
  NetMsgType( 1, 3, 0x30, 0xFACE0001 ),
  NetMsgType( 2, 3, 0x31, 0xFACE0002 ),
]

def gen_random_msgs(n=12):
  msgs = []
  for _ in range(n):
    src     = randint(0,2)
    dest    = randint(0,3)
    opaq    = randint(0,255)
    payload = getrandbits(32)
    msgs.append(NetMsgType(src, dest, opaq, payload))
  return msgs

random_small  = gen_random_msgs(6)
random_medium = gen_random_msgs(12)
random_heavy  = gen_random_msgs(20)

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                  "msgs    src_delay sink_delay delay_mode ordered"),
  [ "one",                            one,                 0,  0,  'fixed',   True  ],
  [ "rotate0",                        rotate0,             0,  0,  'fixed',   True  ],
  [ "rotate1",                        rotate1,             0,  0,  'fixed',   True  ],
  [ "rotate2",                        rotate2,             0,  0,  'fixed',   True  ],
  [ "rotate3",                        rotate3,             0,  0,  'fixed',   True  ],
  [ "all_to_dest0",                   all_to_dest0,        0,  0,  'fixed',   True  ],
  [ "all_to_dest1",                   all_to_dest1,        0,  0,  'fixed',   True  ],
  [ "all_to_dest2",                   all_to_dest2,        0,  0,  'fixed',   True  ],
  [ "all_to_dest3",                   all_to_dest3,        0,  0,  'fixed',   True  ],

  [ "fan_in0",                        fan_in0,             0, 0,   'fixed',   True  ],
  [ "fan_out_from2",                  fan_out_from2,       0, 0,   'fixed',   True  ],
  [ "loopback",                       loopback,            0, 0,   'fixed',   True  ],
  [ "arb_conflict",                   arb_conflict,        0, 0,   'fixed',   False ],

  [ "random_small",                   random_small,        1, 1,   'random',  False ],
  [ "random_medium",                  random_medium,       2, 2,   'random',  False ],
  [ "random_heavy",                   random_heavy,        3, 3,   'random',  False ],
])

def run_router_test( router_id, test_params, cmdline_opts ):

  th = TestHarness( router_id=router_id )

  th.set_param("top.srcs[0].construct",
    msgs = [m for m in test_params.msgs if m.src == 0],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.src_delay,
    interval_delay = test_params.src_delay)

  th.set_param("top.srcs[1].construct",
    msgs = [m for m in test_params.msgs if m.src == 1],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.src_delay,
    interval_delay = test_params.src_delay)

  th.set_param("top.srcs[2].construct",
    msgs = [m for m in test_params.msgs if m.src == 2],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.src_delay,
    interval_delay = test_params.src_delay)

  th.set_param("top.sinks[0].construct",
    msgs = [m for m in test_params.msgs if m.dest == router_id],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.sink_delay,
    interval_delay = test_params.sink_delay,
    ordered = test_params.ordered )

  th.set_param("top.sinks[1].construct",
    msgs = [m for m in test_params.msgs if m.dest != router_id],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.sink_delay,
    interval_delay = test_params.sink_delay,
    ordered = test_params.ordered )

  th.set_param("top.sinks[2].construct",
    msgs = [],
    interval_delay_mode = test_params.delay_mode,
    initial_delay = test_params.sink_delay,
    interval_delay = test_params.sink_delay,
    ordered = True )

  th.elaborate()
  run_sim(th, cmdline_opts, duts=['router'])

#-------------------------------------------------------------------------
# run with all router ids
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_0( test_params, cmdline_opts ):
  run_router_test(0, test_params, cmdline_opts)

@pytest.mark.parametrize( **test_case_table )
def test_router_id_1( test_params, cmdline_opts ):
  run_router_test(1, test_params, cmdline_opts)

@pytest.mark.parametrize( **test_case_table )
def test_router_id_2( test_params, cmdline_opts ):
  run_router_test(2, test_params, cmdline_opts)

@pytest.mark.parametrize( **test_case_table )
def test_router_id_3( test_params, cmdline_opts ):
  run_router_test(3, test_params, cmdline_opts)

