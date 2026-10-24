#=========================================================================
# mul
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
    mul x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 20
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
# gen_x0_test
#-------------------------------------------------------------------------

def gen_x0_test():
  return [
    # dest = x0 (should stay 0)
    """
    csrr x1, mngr2proc < 7
    csrr x2, mngr2proc < 9
    mul  x0, x1, x2
    csrw proc2mngr, x0 > 0
    """,
    # src0 = x0
    """
    csrr x2, mngr2proc < 0x1234abcd
    mul  x3, x0, x2
    csrw proc2mngr, x3 > 0
    """,
    # src1 = x0
    """
    csrr x1, mngr2proc < 0xfeedbeef
    mul  x4, x1, x0
    csrw proc2mngr, x4 > 0
    """,
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    # basics
    gen_rr_value_test( "mul", 0x00000000, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x00000001, 0x00000007, 0x00000007 ),
    gen_rr_value_test( "mul", 0xffffffff, 0x00000001, 0xffffffff ),   
    gen_rr_value_test( "mul", 0xffffffff, 0xffffffff, 0x00000001 ),  

    # sign edges
    gen_rr_value_test( "mul", 0x80000000, 0x00000002, 0x00000000 ),   
    gen_rr_value_test( "mul", 0x7fffffff, 0x00000002, 0xfffffffe ), 

    # mixed signs
    gen_rr_value_test( "mul", 0x80000000, 0xffffffff, 0x80000000 ),  
    gen_rr_value_test( "mul", 0x00007fff, 0xffff8000, 0xc0008000 ),   
  ]


#-------------------------------------------------------------------------
# Long dependency / forwarding chain 
#-------------------------------------------------------------------------

def gen_long_bypass_chain_test():
  return """
    csrr x1, mngr2proc < 3
    csrr x2, mngr2proc < 4

    mul  x3, x1, x2          # 3*4 = 12
    mul  x4, x3, x2          # 12*4 = 48
    mul  x5, x4, x1          # 48*3 = 144
    mul  x6, x5, x3          # 144*12 = 1728

    csrw proc2mngr, x3 > 12
    csrw proc2mngr, x4 > 48
    csrw proc2mngr, x5 > 144
    csrw proc2mngr, x6 > 1728
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test(n=20):
  asm_code = []
  for _ in range(n):
    a = b32( random.randint(0,0xffffffff) )
    b = b32( random.randint(0,0xffffffff) )
    prod_low32 = (a.int() * b.int()) & 0xffffffff
    asm_code.append( gen_rr_value_test( "mul", a.uint(), b.uint(), prod_low32 ) )
  return asm_code

