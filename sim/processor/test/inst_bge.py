#=========================================================================
# bge
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
    csrr  x2, mngr2proc < 2

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    bge   x1, x2, label_a
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
    gen_br2_src0_dep_test( 5, "bge", -1, -2, True ),
    gen_br2_src0_dep_test( 4, "bge",  0, -1, True ),
    gen_br2_src0_dep_test( 3, "bge",  0,  0, True ),
    gen_br2_src0_dep_test( 2, "bge",  1,  0, True ),
    gen_br2_src0_dep_test( 1, "bge",  2,  1, True ),
    gen_br2_src0_dep_test( 0, "bge",  3,  2, True ),
  ]

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "bge", -2, -1, False ),
    gen_br2_src0_dep_test( 4, "bge", -1,  0, False ),
    gen_br2_src0_dep_test( 3, "bge",  0,  1, False ),
    gen_br2_src0_dep_test( 2, "bge",  1,  2, False ),
    gen_br2_src0_dep_test( 1, "bge",  2,  3, False ),
    gen_br2_src0_dep_test( 0, "bge",  3,  4, False ),
  ]

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "bge", -1, -2, True ),
    gen_br2_src1_dep_test( 4, "bge",  0, -1, True ),
    gen_br2_src1_dep_test( 3, "bge",  0,  0, True ),
    gen_br2_src1_dep_test( 2, "bge",  1,  0, True ),
    gen_br2_src1_dep_test( 1, "bge",  2,  1, True ),
    gen_br2_src1_dep_test( 0, "bge",  3,  2, True ),
  ]

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "bge", -2, -1, False ),
    gen_br2_src1_dep_test( 4, "bge", -1,  0, False ),
    gen_br2_src1_dep_test( 3, "bge",  0,  1, False ),
    gen_br2_src1_dep_test( 2, "bge",  1,  2, False ),
    gen_br2_src1_dep_test( 1, "bge",  2,  3, False ),
    gen_br2_src1_dep_test( 0, "bge",  3,  4, False ),
  ]

def gen_value_test():
  return [
    # basic signed comparisons
    gen_br2_value_test( "bge", -2, -1, False ),
    gen_br2_value_test( "bge", -1, -2, True  ),
    gen_br2_value_test( "bge", -1, -1, True  ),
    gen_br2_value_test( "bge",  0, -1, True  ),
    gen_br2_value_test( "bge",  0,  0, True  ),
    gen_br2_value_test( "bge",  0,  1, False ),
    gen_br2_value_test( "bge",  1,  0, True  ),
    gen_br2_value_test( "bge",  1,  1, True  ),
    gen_br2_value_test( "bge",  1,  2, False ),

    # edge-ish signed cases with hex
    # 0x80000000 = -2147483648 (smallest signed int)
    # 0x7fffffff =  2147483647 (largest signed int)
    gen_br2_value_test( "bge",  0x80000000, 0, False ),
    gen_br2_value_test( "bge",  0x7fffffff, -1, True ),
  ]

def gen_random_test():
  asm_code = []
  for _ in range(50):
    a = random.randint(-100000, 100000)
    b = random.randint(-100000, 100000)
    taken = (a >= b)
    asm_code.append( gen_br2_value_test("bge", a, b, taken) )
  return asm_code

