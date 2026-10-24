#=========================================================================
# blt
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

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0

    csrr  x1, mngr2proc < 2
    csrr  x2, mngr2proc < 1

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    blt   x2, x1, label_a
    addi  x3, x3, 0b01

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Only the second bit should be set if branch was taken
    csrw proc2mngr, x3 > 0b10

  """

def gen_src0_dep_taken_test():
  return [
    gen_br2_src0_dep_test( 5, "blt", -2, -1, True ),
    gen_br2_src0_dep_test( 4, "blt", -1,  0, True ),
    gen_br2_src0_dep_test( 3, "blt",  0,  1, True ),
    gen_br2_src0_dep_test( 2, "blt",  1,  2, True ),
    gen_br2_src0_dep_test( 1, "blt",  2,  3, True ),
    gen_br2_src0_dep_test( 0, "blt",  3,  4, True ),
  ]

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "blt",  1,  1, False ),
    gen_br2_src0_dep_test( 4, "blt",  2,  2, False ),
    gen_br2_src0_dep_test( 3, "blt",  3,  3, False ),
    gen_br2_src0_dep_test( 2, "blt",  4,  4, False ),
    gen_br2_src0_dep_test( 1, "blt",  5,  5, False ),
    gen_br2_src0_dep_test( 0, "blt",  6,  5, False ),
  ]

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "blt", -2, -1, True ),
    gen_br2_src1_dep_test( 4, "blt", -1,  0, True ),
    gen_br2_src1_dep_test( 3, "blt",  0,  1, True ),
    gen_br2_src1_dep_test( 2, "blt",  1,  2, True ),
    gen_br2_src1_dep_test( 1, "blt",  2,  3, True ),
    gen_br2_src1_dep_test( 0, "blt",  3,  4, True ),
  ]

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "blt",  1,  1, False ),
    gen_br2_src1_dep_test( 4, "blt",  2,  2, False ),
    gen_br2_src1_dep_test( 3, "blt",  3,  3, False ),
    gen_br2_src1_dep_test( 2, "blt",  4,  4, False ),
    gen_br2_src1_dep_test( 1, "blt",  5,  5, False ),
    gen_br2_src1_dep_test( 0, "blt",  6,  5, False ),
  ]

def gen_value_test():
  return [
    gen_br2_value_test( "blt", -2, -1, True  ),
    gen_br2_value_test( "blt", -1,  0, True  ),
    gen_br2_value_test( "blt", -1, -1, False ),
    gen_br2_value_test( "blt",  0, -1, False ),
    gen_br2_value_test( "blt",  0,  0, False ),
    gen_br2_value_test( "blt",  0,  1, True  ),
    gen_br2_value_test( "blt",  1,  0, False ),
    gen_br2_value_test( "blt",  1,  1, False ),
    gen_br2_value_test( "blt",  1,  2, True  ),
    gen_br2_value_test( "blt",  0x80000000, 0, True ),
    gen_br2_value_test( "blt",  0x7fffffff, -1, False ),
  ]

def gen_random_test():
  asm_code = []
  for _ in range(50):
    a = random.randint(-100000, 100000)
    b = random.randint(-100000, 100000)
    taken = a < b
    asm_code.append( gen_br2_value_test("blt", a, b, taken) )
  return asm_code

