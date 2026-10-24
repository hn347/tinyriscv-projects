#=========================================================================
# sub
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from processor.test.inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sub x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sub",  2, 1, 1 ),
    gen_rr_dest_dep_test( 4, "sub",  3, 1, 2 ),
    gen_rr_dest_dep_test( 3, "sub",  4, 1, 3 ),
    gen_rr_dest_dep_test( 2, "sub",  5, 1, 4 ),
    gen_rr_dest_dep_test( 1, "sub",  6, 1, 5 ),
    gen_rr_dest_dep_test( 0, "sub",  7, 1, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sub",  8, 1,  7 ),
    gen_rr_src0_dep_test( 4, "sub",  9, 1,  8 ),
    gen_rr_src0_dep_test( 3, "sub", 10, 1,  9 ),
    gen_rr_src0_dep_test( 2, "sub", 11, 1, 10 ),
    gen_rr_src0_dep_test( 1, "sub", 12, 1, 11 ),
    gen_rr_src0_dep_test( 0, "sub", 13, 1, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sub", 13,  1, 12 ),
    gen_rr_src1_dep_test( 4, "sub", 14,  1, 13 ),
    gen_rr_src1_dep_test( 3, "sub", 15,  1, 14 ),
    gen_rr_src1_dep_test( 2, "sub", 16,  1, 15 ),
    gen_rr_src1_dep_test( 1, "sub", 17,  1, 16 ),
    gen_rr_src1_dep_test( 0, "sub", 18,  1, 17 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sub", 14,  2, 12 ),
    gen_rr_srcs_dep_test( 4, "sub", 16,  3, 13 ),
    gen_rr_srcs_dep_test( 3, "sub", 18,  4, 14 ),
    gen_rr_srcs_dep_test( 2, "sub", 20,  5, 15 ),
    gen_rr_srcs_dep_test( 1, "sub", 22,  6, 16 ),
    gen_rr_srcs_dep_test( 0, "sub", 24,  7, 17 ),
  ]


#-------------------------------------------------------------------------
# gen_x0_test 
#-------------------------------------------------------------------------

def gen_x0_test():
  return [
    
    """
    csrr x1, mngr2proc < 13
    csrr x2, mngr2proc <  5
    sub  x0, x1, x2
    csrw proc2mngr, x0 > 0
    """,
  
    """
    csrr x2, mngr2proc < 7
    sub  x3, x0, x2
    csrw proc2mngr, x3 > 0xfffffff9
    """,
  
    """
    csrr x1, mngr2proc < 0x12345678
    sub  x4, x1, x0
    csrw proc2mngr, x4 > 0x12345678
    """,
   
    """
    sub  x5, x0, x0
    csrw proc2mngr, x5 > 0
    """,
  ]

#-------------------------------------------------------------------------
# gen_value_test 
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    # simple
    gen_rr_value_test( "sub", 0x00000005, 0x00000004, 0x00000001 ),
    gen_rr_value_test( "sub", 0x00000000, 0x00000001, 0xffffffff ),  # -1
    gen_rr_value_test( "sub", 0x00000001, 0x00000000, 0x00000001 ),
    # edges with sign bits
    gen_rr_value_test( "sub", 0x80000000, 0x00000001, 0x7fffffff ),
    gen_rr_value_test( "sub", 0x80000000, 0xffffffff, 0x80000001 ),
    gen_rr_value_test( "sub", 0x7fffffff, 0xffffffff, 0x80000000 ),
    gen_rr_value_test( "sub", 0xffffffff, 0x7fffffff, 0x80000000 ),
    # zeros/ones
    gen_rr_value_test( "sub", 0xffffffff, 0x00000001, 0xfffffffe ),
    gen_rr_value_test( "sub", 0xffffffff, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "sub", 0x00000000, 0xffffffff, 0x00000001 ),
    # carry/borrow edge: 0x00000000 - 1 -> 0xffffffff
    gen_rr_value_test( "sub", 0x00000000, 0x00000001, 0xffffffff ),
  ]

#-------------------------------------------------------------------------
# gen_long_bypass_chain_test 
#-------------------------------------------------------------------------

def gen_long_bypass_chain_test():
  return """
    csrr x1, mngr2proc < 30
    csrr x2, mngr2proc <  7

    sub  x3, x1, x2      # 30-7  = 23
    sub  x4, x3, x2      # 23-7  = 16
    sub  x5, x4, x2      # 16-7  = 9
    sub  x6, x5, x3      # 9-23  = -14 -> 0xfffffff2
    sub  x7, x6, x1      # (-14)-30 = -44 -> 0xffffffd4

    csrw proc2mngr, x3 > 23
    csrw proc2mngr, x4 > 16
    csrw proc2mngr, x5 > 9
    csrw proc2mngr, x6 > 0xfffffff2
    csrw proc2mngr, x7 > 0xffffffd4
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for _ in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,0xffffffff) )
    dest = src0 - src1
    asm_code.append( gen_rr_value_test( "sub", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

