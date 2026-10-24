#=========================================================================
# NetRouterRouteUnit_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from multicore.NetMsg import mk_net_msg
from multicore.NetRouterRouteUnit import NetRouterRouteUnit

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

    s.src   = StreamSourceFL( NetMsgType )
    s.runit = NetRouterRouteUnit( p_msg_nbits=44 )
    s.sinks = [ StreamSinkFL( NetMsgType ) for _ in range(3) ]

    # Connect

    s.runit.router_id  //= router_id
    s.src.ostream      //= s.runit.istream
    s.runit.ostream[0] //= s.sinks[0].istream
    s.runit.ostream[1] //= s.sinks[1].istream
    s.runit.ostream[2] //= s.sinks[2].istream

  def done( s ):
    return s.src.done() and s.sinks[0].done() and s.sinks[1].done() and s.sinks[2].done()

  def line_trace( s ):
    return s.src.line_trace()   + " > (" + \
           s.runit.line_trace() + ") > " + \
           s.sinks[0].line_trace() + "|" + \
           s.sinks[1].line_trace() + "|" + \
           s.sinks[2].line_trace()

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------
# This is an example of a basic test. This test may not be valid
# depending on your routing algorithm. You are free to change this test.
# We will not test your route unit since its functionality depends on the
# chosen routing algorithm.

def test_basic( cmdline_opts ):

  th = TestHarness( router_id=0 )

  msgs = [
    #           src  dest opaq  payload
    NetMsgType( 0,   0,   0x10, 0x10101010 ),
    NetMsgType( 0,   1,   0x11, 0x11111111 ),
    NetMsgType( 0,   2,   0x12, 0x12121212 ),
    NetMsgType( 0,   3,   0x13, 0x13131313 ),
  ]

  th.set_param("top.src.construct",   msgs=msgs  )
  th.set_param("top.sinks[0].construct", msgs=[ m for m in msgs if m.dest == 0 ] )
  th.set_param("top.sinks[1].construct", msgs=[ m for m in msgs if m.dest != 0 ] )
  th.set_param("top.sinks[2].construct", msgs=[] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['runit'] )

#-------------------------------------------------------------------------
# Test Cases: Very Simple
#-------------------------------------------------------------------------
# These are examples of a simple tests using a test case table. These
# tests may not be valid depending on your routing algorithm. You are
# free to change these tests. We will not test your route unit since its
# functionality depends on the chosen routing algorithm.

one = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

four = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
]

four_diff_src = [
  #           src  dest opaq  payload
  NetMsgType( 3,   0,   0x10, 0x10101010 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
  NetMsgType( 1,   2,   0x12, 0x12121212 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
]

four_same_src = [
  NetMsgType(0, 0, 0x30, 0xCCCC0000),
  NetMsgType(0, 1, 0x31, 0xCCCC0001),
  NetMsgType(0, 2, 0x32, 0xCCCC0002),
  NetMsgType(0, 3, 0x33, 0xCCCC0003),
]

four_diff_src = [
  NetMsgType(3, 0, 0x40, 0xDDDD0000), 
  NetMsgType(2, 1, 0x41, 0xDDDD0001), 
  NetMsgType(1, 2, 0x42, 0xDDDD0002), 
  NetMsgType(0, 3, 0x43, 0xDDDD0003), 
]

eight_same_src = [
  NetMsgType(0, 0, 0x50, 0xEEEE0000),
  NetMsgType(0, 1, 0x51, 0xEEEE0001),
  NetMsgType(0, 2, 0x52, 0xEEEE0002),
  NetMsgType(0, 3, 0x53, 0xEEEE0003),
  NetMsgType(0, 0, 0x54, 0xEEEE0004),
  NetMsgType(0, 1, 0x55, 0xEEEE0005),
  NetMsgType(0, 2, 0x56, 0xEEEE0006),
  NetMsgType(0, 3, 0x57, 0xEEEE0007),
]

eight_diff_src = [
  NetMsgType(3, 0, 0x60, 0xAAAA1111),
  NetMsgType(2, 1, 0x61, 0xAAAA1112),
  NetMsgType(1, 2, 0x62, 0xAAAA1113),
  NetMsgType(0, 3, 0x63, 0xAAAA1114),
  NetMsgType(3, 0, 0x64, 0xAAAA1115),
  NetMsgType(2, 1, 0x65, 0xAAAA1116),
  NetMsgType(1, 2, 0x66, 0xAAAA1117),
  NetMsgType(0, 3, 0x67, 0xAAAA1118),
]

stream_to_dest0 = [ NetMsgType(0, 0, i, i) for i in range(16) ]
stream_to_dest1 = [ NetMsgType(0, 1, i, i) for i in range(16) ]
stream_to_dest2 = [ NetMsgType(0, 2, i, i) for i in range(16) ]
stream_to_dest3 = [ NetMsgType(0, 3, i, i) for i in range(16) ]

stream_to_all = []
for i in range(16):
  stream_to_all.extend([
      NetMsgType(0, 0, 0x00+i, 0x1000+i),
      NetMsgType(0, 1, 0x40+i, 0x2000+i),
      NetMsgType(0, 2, 0x80+i, 0x3000+i),
      NetMsgType(0, 3, 0xC0+i, 0x4000+i),
  ])

tie_breaking = [
  NetMsgType(1, 3, 0x70, 0x12340001),
  NetMsgType(2, 0, 0x71, 0x12340002),
  NetMsgType(3, 1, 0x72, 0x12340003),
  NetMsgType(0, 2, 0x73, 0x12340004),
]

high_traffic = [
  NetMsgType(0, 1, 0x90, 0x33330001),
  NetMsgType(1, 2, 0x91, 0x33330002),
  NetMsgType(2, 3, 0x92, 0x33330003),
  NetMsgType(3, 0, 0x93, 0x33330004),
  NetMsgType(0, 3, 0x94, 0x33330005),
  NetMsgType(3, 2, 0x95, 0x33330006),
  NetMsgType(2, 1, 0x96, 0x33330007),
  NetMsgType(1, 0, 0x97, 0x33330008),
]

wraparound = [
  NetMsgType(0, 3, 0xA0, 0x44440001),
  NetMsgType(3, 0, 0xA1, 0x44440002),
  NetMsgType(1, 0, 0xA2, 0x44440003),
  NetMsgType(2, 1, 0xA3, 0x44440004),
]


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  ( "msgs                 src_delay sink_delay delay_mode" ),

  [ "one",                 one,                 0, 0, 'fixed' ],
  [ "four_same_src",       four_same_src,       0, 0, 'fixed' ],
  [ "four_diff_src",       four_diff_src,       0, 0, 'fixed' ],
  [ "eight_same_src",      eight_same_src,      0, 0, 'fixed' ],
  [ "eight_diff_src",      eight_diff_src,      0, 0, 'fixed' ],

  [ "stream_to_dest0",     stream_to_dest0,     0, 0, 'fixed' ],
  [ "stream_to_dest1",     stream_to_dest1,     0, 0, 'fixed' ],
  [ "stream_to_dest2",     stream_to_dest2,     0, 0, 'fixed' ],
  [ "stream_to_dest3",     stream_to_dest3,     0, 0, 'fixed' ],
  [ "stream_to_all",       stream_to_all,       0, 0, 'fixed' ],

  [ "tie_breaking",        tie_breaking,        0, 0, 'fixed' ],
  [ "high_traffic",        high_traffic,        0, 0, 'fixed' ],
  [ "wraparound",          wraparound,          0, 0, 'fixed' ],

  [ "one_fixed_2x0",                 one,                 2, 0, 'fixed' ],
  [ "four_same_src_fixed_2x0",       four_same_src,       2, 0, 'fixed' ],
  [ "four_diff_src_fixed_2x0",       four_diff_src,       2, 0, 'fixed' ],
  [ "eight_same_src_fixed_2x0",      eight_same_src,      2, 0, 'fixed' ],
  [ "eight_diff_src_fixed_2x0",      eight_diff_src,      2, 0, 'fixed' ],
  [ "stream_to_dest0_fixed_2x0",     stream_to_dest0,     2, 0, 'fixed' ],
  [ "stream_to_dest1_fixed_2x0",     stream_to_dest1,     2, 0, 'fixed' ],
  [ "stream_to_dest2_fixed_2x0",     stream_to_dest2,     2, 0, 'fixed' ],
  [ "stream_to_dest3_fixed_2x0",     stream_to_dest3,     2, 0, 'fixed' ],
  [ "stream_to_all_fixed_2x0",       stream_to_all,       2, 0, 'fixed' ],
  [ "tie_breaking_fixed_2x0",        tie_breaking,        2, 0, 'fixed' ],
  [ "high_traffic_fixed_2x0",        high_traffic,        2, 0, 'fixed' ],
  [ "wraparound_fixed_2x0",          wraparound,          2, 0, 'fixed' ],

  [ "one_fixed_0x2",                 one,                 0, 2, 'fixed' ],
  [ "four_same_src_fixed_0x2",       four_same_src,       0, 2, 'fixed' ],
  [ "four_diff_src_fixed_0x2",       four_diff_src,       0, 2, 'fixed' ],
  [ "eight_same_src_fixed_0x2",      eight_same_src,      0, 2, 'fixed' ],
  [ "eight_diff_src_fixed_0x2",      eight_diff_src,      0, 2, 'fixed' ],
  [ "stream_to_dest0_fixed_0x2",     stream_to_dest0,     0, 2, 'fixed' ],
  [ "stream_to_dest1_fixed_0x2",     stream_to_dest1,     0, 2, 'fixed' ],
  [ "stream_to_dest2_fixed_0x2",     stream_to_dest2,     0, 2, 'fixed' ],
  [ "stream_to_dest3_fixed_0x2",     stream_to_dest3,     0, 2, 'fixed' ],
  [ "stream_to_all_fixed_0x2",       stream_to_all,       0, 2, 'fixed' ],
  [ "tie_breaking_fixed_0x2",        tie_breaking,        0, 2, 'fixed' ],
  [ "high_traffic_fixed_0x2",        high_traffic,        0, 2, 'fixed' ],
  [ "wraparound_fixed_0x2",          wraparound,          0, 2, 'fixed' ],

  [ "one_rand_delay",                 one,                 3, 20, 'random' ],
  [ "four_same_src_rand_delay",       four_same_src,       3, 20, 'random' ],
  [ "four_diff_src_rand_delay",       four_diff_src,       3, 20, 'random' ],
  [ "stream_to_dest0_rand_delay",     stream_to_dest0,     3, 20, 'random' ],
  [ "stream_to_dest1_rand_delay",     stream_to_dest1,     3, 20, 'random' ],
  [ "stream_to_dest2_rand_delay",     stream_to_dest2,     3, 20, 'random' ],
  [ "stream_to_dest3_rand_delay",     stream_to_dest3,     3, 20, 'random' ],
  [ "stream_to_all_rand_delay",       stream_to_all,       3, 20, 'random' ],
  [ "tie_breaking_rand_delay",        tie_breaking,        3, 20, 'random' ],
  [ "high_traffic_rand_delay",        high_traffic,        3, 20, 'random' ],
  [ "wraparound_rand_delay",          wraparound,          3, 20, 'random' ],
])

#-------------------------------------------------------------------------
# test w/ router id 0
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_0( test_params, cmdline_opts ):

  th = TestHarness( router_id=0 )

  th.set_param("top.src.construct",
    msgs                = test_params.msgs,
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest != 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = [],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['runit'] )

#-------------------------------------------------------------------------
# test w/ router id 1
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_1( test_params, cmdline_opts ):

  router_id = 1
  th = TestHarness( router_id )

  th.set_param("top.src.construct",
    msgs                = test_params.msgs,
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest != router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = [],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()
  run_sim( th, cmdline_opts, duts=['runit'] )

#-------------------------------------------------------------------------
# test w/ router id 2
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_2( test_params, cmdline_opts ):

  router_id = 2
  th = TestHarness( router_id )

  th.set_param("top.src.construct",
    msgs                = test_params.msgs,
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest != router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = [],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()
  run_sim( th, cmdline_opts, duts=['runit'] )

#-------------------------------------------------------------------------
# test w/ router id 3
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_3( test_params, cmdline_opts ):

  router_id = 3
  th = TestHarness( router_id )

  th.set_param("top.src.construct",
    msgs                = test_params.msgs,
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest != router_id ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = [],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()
  run_sim( th, cmdline_opts, duts=['runit'] )


