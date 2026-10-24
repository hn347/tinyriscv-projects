#=========================================================================
# srli
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srli x3, x1, 0x03
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
    gen_rimm_value_test( "srli", 0x12345678, 0x00, 0x12345678 ),

    # basic logical right shifts
    gen_rimm_value_test( "srli", 0x00008000, 0x03, 0x00001000 ),
    gen_rimm_value_test( "srli", 0x80000000, 0x01, 0x40000000 ),
    gen_rimm_value_test( "srli", 0xffffffff, 0x01, 0x7fffffff ),

    # by 31
    gen_rimm_value_test( "srli", 0xffffffff, 0x1f, 0x00000001 ),
    gen_rimm_value_test( "srli", 0x7fffffff, 0x1f, 0x00000000 ),

    # a couple of extra patterns
    gen_rimm_value_test( "srli", 0xdeadbeef, 0x04, 0x0deadbee ),
    gen_rimm_value_test( "srli", 0x01000000, 0x08, 0x00010000 ),
  ]

#-------------------------------------------------------------------------
# gen_x0_test
#-------------------------------------------------------------------------

def gen_x0_test():
  return [
    # dest = x0: stays 0
    """
    csrr x1, mngr2proc < 0xffffffff
    srli x0, x1, 31
    csrw proc2mngr, x0 > 0
    """,

    # src = x0: 0 >> n = 0
    """
    srli x3, x0, 13
    csrw proc2mngr, x3 > 0
    """,

    # shift by 0 (imm = 0): value unchanged
    """
    csrr x1, mngr2proc < 0x89abcdef
    srli x4, x1, 0
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
    csrr x8, mngr2proc < 0xf0000000
    srli x8, x8, 4              # 0xf0000000 >> 4 = 0x0f000000
    csrw proc2mngr, x8 > 0x0f000000
    """,
  ]

#-------------------------------------------------------------------------
# gen_hi_regs_edge_test
#-------------------------------------------------------------------------

def gen_hi_regs_edge_test():
  return """
    csrr x28, mngr2proc < 0xffffffff
    srli x30, x28, 31           # 0xffffffff >> 31 = 1
    csrw proc2mngr, x30 > 0x00000001

    csrr x31, mngr2proc < 0x80000000
    srli x30, x31, 30           # 0x80000000 >> 30 = 0x00000002
    csrw proc2mngr, x30 > 0x00000002
  """

#-------------------------------------------------------------------------
# gen_long_bypass_chain_test
#-------------------------------------------------------------------------

def gen_long_bypass_chain_test():
  return """
    csrr x1, mngr2proc < 0xf0000000

    srli x3, x1, 4      # 0x0f000000
    srli x4, x3, 4      # 0x00f00000
    srli x5, x4, 4      # 0x000f0000
    srli x6, x5, 4      # 0x0000f000

    csrw proc2mngr, x3 > 0x0f000000
    csrw proc2mngr, x4 > 0x00f00000
    csrw proc2mngr, x5 > 0x000f0000
    csrw proc2mngr, x6 > 0x0000f000
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test( n=20 ):
  def srl32(a, sh):
    return ((a & 0xffffffff) >> (sh & 0x1f)) & 0xffffffff

  asm = []
  for _ in range(n):
    a  = random.randint(0, 0xffffffff)
    sh = random.randint(0, 31)  # imm shamt is 0–31 in RV32I
    asm.append( gen_rimm_value_test("srli", a, sh, srl32(a, sh)) )
  return asm

