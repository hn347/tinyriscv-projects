#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest

from random import randint

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from imul.IntMulFL import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, imul ):

    # Instantiate models

    s.src  = StreamSourceFL( Bits64 )
    s.sink = StreamSinkFL( Bits32 )
    s.imul = imul

    # Connect

    s.src.ostream  //= s.imul.istream
    s.imul.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.imul.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( a, b ):
  return concat( Bits32( a, trunc_int=True ), Bits32( b, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )


# helpers
def pairs_to_msgs( pairs ):
  msgs = []
  for a,b in pairs:
    msgs += [ mk_imsg(a,b), mk_omsg(a*b) ]
  return msgs

# random 
def gen_rand_msgs( n ):
  lo = -(1<<31); hi = (1<<31) - 1
  from random import randint, seed
  seed(0xBAD5EED)     
  pairs = [ (randint(lo,hi), randint(lo,hi)) for _ in range(n) ]
  return pairs_to_msgs(pairs)

def gen_pairs_with_b(patterns_b, n_repeat=1, a_lo=-(1<<31), a_hi=(1<<31)-1):
  from random import randint
  pairs = []
  for b in patterns_b:
    for _ in range(n_repeat):
      a = randint(a_lo, a_hi)
      pairs.append((a, b))
  return pairs
#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  mk_imsg(  2,  3 ), mk_omsg(   6 ),
  mk_imsg(  4,  5 ), mk_omsg(  20 ),
  mk_imsg(  3,  4 ), mk_omsg(  12 ),
  mk_imsg( 10, 13 ), mk_omsg( 130 ),
  mk_imsg(  8,  7 ), mk_omsg(  56 ),
]

# mixed numbers
mixed_number_msgs = [
  mk_imsg(0,0), mk_omsg(0*0),
  mk_imsg(0,5), mk_omsg(0*5),
  mk_imsg(5,0), mk_omsg(5*0),
  mk_imsg(1,7), mk_omsg(1*7),
  mk_imsg(7,1), mk_omsg(7*1),
  mk_imsg(-1,7), mk_omsg(-1*7),
  mk_imsg(7,-1), mk_omsg(7*-1),
  mk_imsg(1,-1), mk_omsg(1*-1),
  mk_imsg(-1,1), mk_omsg(-1*1),
  mk_imsg(-1,-1), mk_omsg((-1)*(-1)),
]

# small mixed signs
small_mixed_sign_msgs = [
  mk_imsg(-2,3), mk_omsg(-2*3),
  mk_imsg(-3,4), mk_omsg(-3*4),
  mk_imsg( 6,-5), mk_omsg( 6*-5),
  mk_imsg(-8,7), mk_omsg(-8*7),
  mk_imsg( 9,-10), mk_omsg( 9*-10),
]

# large numbers
large_numbers_msgs = [
  mk_imsg( 0x7fffffff,  2 ), mk_omsg( 0x7fffffff * 2 ),
  mk_imsg( 0x40000000,  3 ), mk_omsg( 0x40000000 * 3 ),
  mk_imsg(-0x80000000,  2 ), mk_omsg(-0x80000000 * 2 ),
  mk_imsg(-0x7fffffff, -2 ), mk_omsg(-0x7fffffff * -2 ),
  mk_imsg( 123456789,   987654321 ), mk_omsg( 123456789 * 987654321 ),
]

# powers of two 
sparse_msgs = [
  mk_imsg(1<<0,  0x12345   ), mk_omsg((1<<0)  * 0x12345),
  mk_imsg(1<<1, -0x13579  ), mk_omsg((1<<1)  * -0x13579),
  mk_imsg(1<<5,  0x33333333), mk_omsg((1<<5)  * 0x33333333),
  mk_imsg(1<<15, -7        ), mk_omsg((1<<15) * -7),
  mk_imsg(1<<31,  3        ), mk_omsg((1<<31) * 3),
]

# lots of one bits
dense_msgs = [
  mk_imsg(0xffffffff,  0x7fffffff), mk_omsg(0xffffffff  * 0x7fffffff),
  mk_imsg(0xffffff00,  0x0000ffff), mk_omsg(0xffffff00  * 0x0000ffff),
  mk_imsg(0xaaaaaaaa,  3         ), mk_omsg(0xaaaaaaaa  * 3),
  mk_imsg(0x55555555, -7         ), mk_omsg(0x55555555  * -7),
  mk_imsg(-1,          -1        ), mk_omsg((-1)        * (-1)),
]

# lower bits are ones
low_bits_ones_msgs = [
  mk_imsg(0x123400,  0x5678 ), mk_omsg(0x123400  * 0x5678),
  mk_imsg(-0x3300,   0x100  ), mk_omsg(-0x3300   * 0x100),
  mk_imsg(0x10000,   0x30001), mk_omsg(0x10000   * 0x30001),
  mk_imsg(0xABCDEF00,-5     ), mk_omsg(0xABCDEF00* -5),
]

# middle bits are ones
middle_bits_ones_msgs = [
  mk_imsg(0xFF00FF00, 3       ), mk_omsg(0xFF00FF00 * 3),
  mk_imsg(0x00FF00FF,-5       ), mk_omsg(0x00FF00FF * -5),
  mk_imsg(0xF0F0000F,0x0F0FFFF0), mk_omsg(0xF0F0000F * 0x0F0FFFF0),
]

dense_vs_sparse_msgs = [
  mk_imsg(0xFFFFFFFE, 0x00000001), mk_omsg(0xFFFFFFFE * 0x00000001),
  mk_imsg(0xFFFFFFF0, 0x0000000F), mk_omsg(0xFFFFFFF0 * 0x0000000F),
  mk_imsg(0x80000001, 0x7FFFFFFE), mk_omsg(0x80000001 * 0x7FFFFFFE),
  mk_imsg(0x00000002, 0x7FFFFFFF), mk_omsg(0x00000002 * 0x7FFFFFFF),
]

boundary_cases_msgs = [
  mk_imsg(-0x80000000,  1), mk_omsg(-0x80000000 * 1),
  mk_imsg(-0x80000000, -1), mk_omsg(-0x80000000 * -1),
  mk_imsg( 0x7fffffff,  0x7fffffff), mk_omsg(0x7fffffff * 0x7fffffff),
  mk_imsg(-0x80000000,  0), mk_omsg(-0x80000000 * 0),
  mk_imsg( 0x80000000, -1), mk_omsg(0x80000000 * -1),
]

identity_comm_msgs = pairs_to_msgs([
  (1,  n) for n in (0,1,2,3,0x7fffffff,-1,-2,-0x80000000)
] + [
  (n, 1) for n in (0,1,2,3,0x7fffffff,-1,-2,-0x80000000)
] + [
  (0x12345678, 0x9abcdef0), (0x9abcdef0, 0x12345678)
])

single_msg = pairs_to_msgs([(3,4)])
empty_msgs = []

rand_fast_msgs      = gen_rand_msgs(40) #inputs back to back 
rand_src_delay_msgs = gen_rand_msgs(40) #new input every few cycles
rand_sink_delay_msgs= gen_rand_msgs(40) #non-zero sink delay 
rand_heavy_msgs     = gen_rand_msgs(80) #large batches 
rand_mega_msgs = gen_rand_msgs(400)

# 1) Trivial/edge b (should be ~1–3 calc cycles)
b_edges_msgs = pairs_to_msgs(gen_pairs_with_b([
  0x00000000,        # done immediately
  0x00000001,        # one add then done
  0x80000000,        # long run of zeros then one add
  0x00000002,        # skip 1 zero then add
  0x00010000,        # mid bit
], n_repeat=6))

b_powers_msgs = pairs_to_msgs(
  gen_pairs_with_b([1<<k for k in [0,1,2,3,4,5,7,8,12,16,20,24,28,31]], n_repeat=4)
)

# 3) Dense b (worst-ish case; many adds)
b_dense_msgs = pairs_to_msgs(gen_pairs_with_b([
  0xFFFFFFFF, 0x7FFFFFFF, 0xFFFFFFFE,
  0xAAAAAAAA, 0x55555555, 0xFFFF000F,
  0xF0F0F0F0, 0x0F0F0F0F,
], n_repeat=6))


b_low_ones_msgs = pairs_to_msgs(gen_pairs_with_b([
  0x0000FFFF, 0x00000FFF, 0x000000FF, 0x0000000F
], n_repeat=8))

# 5) “One hot + tail zeros” and “two hot bits” b (shows CTZ skipping)
b_run_skip_msgs = pairs_to_msgs(gen_pairs_with_b([
  0x00000008,            # ...00001000
  0x00008000,            # ...1000 0000 0000 0000
  0x40000000,            # leading 1 near MSB
  0x00010001,            # two 1s far apart (two add steps)
  0x01000010,            # two 1s w/ long gap
], n_repeat=6))

# 7) Random A with controlled-B buckets
def gen_rand_fixed_b(n, b_val):
  from random import randint, seed
  seed(0xDEC0DE + (b_val & 0xFFFF))
  return pairs_to_msgs([(randint(-(1<<31),(1<<31)-1), b_val) for _ in range(n)])

rand_b_zero      = gen_rand_fixed_b(20, 0x0)
rand_b_one       = gen_rand_fixed_b(20, 0x1)
rand_b_altA      = gen_rand_fixed_b(20, 0xAAAAAAAA)
rand_b_alt5      = gen_rand_fixed_b(20, 0x55555555)
rand_b_allones   = gen_rand_fixed_b(20, 0xFFFFFFFF)
rand_b_power_hi  = gen_rand_fixed_b(20, 0x80000000)
#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                   src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,     0,        0          ],
  [ "mixed_numbers",        mixed_number_msgs,        0, 0 ],
  [ "small_mixed_sign",     small_mixed_sign_msgs,     0, 0 ],
  [ "large_numbers",      large_numbers_msgs,            0, 0 ],
  [ "sparse",               sparse_msgs,               0, 0 ],
  [ "dense",                dense_msgs,                0, 0 ],
  [ "low_bits_ones",      low_bits_ones_msgs,      0, 0 ],
  [ "middle_bits_ones",   middle_bits_ones_msgs,   0, 0 ],
  [ "dense_vs_sparse",      dense_vs_sparse_msgs,      0, 0 ],
  [ "rand_fast",            rand_fast_msgs,            0, 0 ],
  [ "rand_src_delay",       rand_src_delay_msgs,       7, 0 ],
  [ "rand_sink_delay",      rand_sink_delay_msgs,      0, 11 ],
  [ "rand_heavy_both",      rand_heavy_msgs,           5, 9 ],
  [ "boundary_cases",     boundary_cases_msgs,     0, 0 ],
  [ "identity_comm",      identity_comm_msgs,      0, 0 ],
  [ "rand_both_delay",    gen_rand_msgs(40),       7, 7 ],
  [ "single",             single_msg,              0, 0 ],
  [ "empty",              empty_msgs,              0, 0 ],

  [ "b_edges",                          b_edges_msgs,                0, 0 ],
  [ "b_powers",                         b_powers_msgs,               0, 0 ],
  [ "b_dense",                          b_dense_msgs,                0, 0 ],
  [ "b_low_ones",                       b_low_ones_msgs,             0, 0 ],
  [ "b_run_skip",                       b_run_skip_msgs,             0, 0 ],

  # random A with fixed B (clear per-bucket latency)
  [ "rand_B_zero",                      rand_b_zero,                 0, 0 ],
  [ "rand_B_one",                       rand_b_one,                  0, 0 ],
  [ "rand_B_altA",                      rand_b_altA,                 0, 0 ],
  [ "rand_B_alt5",                      rand_b_alt5,                 0, 0 ],
  [ "rand_B_allones",                   rand_b_allones,              0, 0 ],
  [ "rand_B_power_hi",                  rand_b_power_hi,             0, 0 ],
  # priority encoder 

])

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness( IntMulFL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['imul'] )

