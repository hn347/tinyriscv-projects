#=========================================================================
# srl
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
    csrr x1, mngr2proc < 0x00008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srl x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
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
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    # shift by 0 -> same
    gen_rr_value_test( "srl", 0x12345678, 0x00000000, 0x12345678 ),
    # basic logical right shifts
    gen_rr_value_test( "srl", 0x00008000, 0x00000003, 0x00001000 ),
    gen_rr_value_test( "srl", 0x80000000, 0x00000001, 0x40000000 ),  
    gen_rr_value_test( "srl", 0xffffffff, 0x00000001, 0x7fffffff ),
    # by 31
    gen_rr_value_test( "srl", 0xffffffff, 0x0000001f, 0x00000001 ),
    gen_rr_value_test( "srl", 0x7fffffff, 0x0000001f, 0x00000000 ),
    # rs2 > 31 -> mask to 5 bits
    gen_rr_value_test( "srl", 0x80000000, 0x00000021, 0x40000000 ),  
    gen_rr_value_test( "srl", 0xdeadbeef, 0x00000040, 0xdeadbeef ),  
  ]

#-------------------------------------------------------------------------
# gen_x0_test
#-------------------------------------------------------------------------

def gen_x0_test():
  return [
    # dest = x0: stays 0
    """
    csrr x1, mngr2proc < 0xffffffff
    csrr x2, mngr2proc < 31
    srl  x0, x1, x2
    csrw proc2mngr, x0 > 0
    """,
    # src0 = x0: 0 >> n = 0
    """
    csrr x2, mngr2proc < 13
    srl  x3, x0, x2
    csrw proc2mngr, x3 > 0
    """,
    # src1 = x0: shift by 0
    """
    csrr x1, mngr2proc < 0x89abcdef
    srl  x4, x1, x0
    csrw proc2mngr, x4 > 0x89abcdef
    """,
  ]

#-------------------------------------------------------------------------
# gen_alias_test
#-------------------------------------------------------------------------

def gen_alias_test():
  return [
    # rd == rs1
    """
    csrr x8,  mngr2proc < 0xf0000000
    csrr x9,  mngr2proc < 0x00000004
    srl  x8,  x8, x9                 # 0xf0000000 >> 4 = 0x0f000000
    csrw proc2mngr, x8 > 0x0f000000
    """,
    # rd == rs2 : ensure rs2 value is read before wb to rd
    """
    csrr x10, mngr2proc < 0x80000000
    csrr x11, mngr2proc < 0x0000001f
    srl  x11, x10, x11               # 0x80000000 >> 31 = 1
    csrw proc2mngr, x11 > 0x00000001
    """,
  ]

#-------------------------------------------------------------------------
# gen_hi_regs_edge_test
#-------------------------------------------------------------------------

def gen_hi_regs_edge_test():
  return """
    csrr x28, mngr2proc < 0xffffffff
    csrr x29, mngr2proc < 0x0000001f
    srl  x30, x28, x29               # 0xffffffff >> 31 = 1
    csrw proc2mngr, x30 > 0x00000001

    csrr x31, mngr2proc < 0x80000000
    csrr x29, mngr2proc < 0x0000001e
    srl  x30, x31, x29               # 0x80000000 >> 30 = 0x00000002
    csrw proc2mngr, x30 > 0x00000002
  """

#-------------------------------------------------------------------------
# gen_long_bypass_chain_test
#-------------------------------------------------------------------------

def gen_long_bypass_chain_test():
  return """
    csrr x1, mngr2proc < 0xf0000000
    csrr x2, mngr2proc < 0x00000004

    srl  x3, x1, x2      # 0x0f000000
    srl  x4, x3, x2      # 0x00f00000
    srl  x5, x4, x2      # 0x000f0000
    srl  x6, x5, x2      # 0x0000f000

    csrw proc2mngr, x3 > 0x0f000000
    csrw proc2mngr, x4 > 0x00f00000
    csrw proc2mngr, x5 > 0x000f0000
    csrw proc2mngr, x6 > 0x0000f000
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test(n=20):
  def srl32(a, sh):
    return ((a & 0xffffffff) >> (sh & 0x1f)) & 0xffffffff
  asm = []
  for _ in range(n):
    a  = random.randint(0, 0xffffffff)
    sh = random.randint(0, 0xffffffff)
    asm.append( gen_rr_value_test("srl", a, sh, srl32(a, sh)) )
  return asm

