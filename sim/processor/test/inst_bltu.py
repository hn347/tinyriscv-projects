#=========================================================================
# bltu
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
    bltu   x2, x1, label_a
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
    gen_br2_src0_dep_test( 5, "bltu", 0, 1, True ),
    gen_br2_src0_dep_test( 4, "bltu", 1, 2, True ),
    gen_br2_src0_dep_test( 3, "bltu", 2, 3, True ),
    gen_br2_src0_dep_test( 2, "bltu", 3, 4, True ),
    gen_br2_src0_dep_test( 1, "bltu", 4, 5, True ),
    gen_br2_src0_dep_test( 0, "bltu", 5, 6, True ),
  ]

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "bltu", 1, 1, False ),
    gen_br2_src0_dep_test( 4, "bltu", 2, 2, False ),
    gen_br2_src0_dep_test( 3, "bltu", 3, 3, False ),
    gen_br2_src0_dep_test( 2, "bltu", 4, 4, False ),
    gen_br2_src0_dep_test( 1, "bltu", 5, 5, False ),
    gen_br2_src0_dep_test( 0, "bltu", 6, 5, False ),
  ]

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "bltu", 0, 1, True ),
    gen_br2_src1_dep_test( 4, "bltu", 1, 2, True ),
    gen_br2_src1_dep_test( 3, "bltu", 2, 3, True ),
    gen_br2_src1_dep_test( 2, "bltu", 3, 4, True ),
    gen_br2_src1_dep_test( 1, "bltu", 4, 5, True ),
    gen_br2_src1_dep_test( 0, "bltu", 5, 6, True ),
  ]

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "bltu", 1, 1, False ),
    gen_br2_src1_dep_test( 4, "bltu", 2, 2, False ),
    gen_br2_src1_dep_test( 3, "bltu", 3, 3, False ),
    gen_br2_src1_dep_test( 2, "bltu", 4, 4, False ),
    gen_br2_src1_dep_test( 1, "bltu", 5, 5, False ),
    gen_br2_src1_dep_test( 0, "bltu", 6, 5, False ),
  ]

def gen_value_test():
  return [
    gen_br2_value_test( "bltu", 0x00000000, 0x00000000, False ),
    gen_br2_value_test( "bltu", 0x00000000, 0x00000001, True  ),
    gen_br2_value_test( "bltu", 0x00000001, 0x00000000, False ),
    gen_br2_value_test( "bltu", 0x7fffffff, 0x80000000, True  ),
    gen_br2_value_test( "bltu", 0x80000000, 0x7fffffff, False ),
    gen_br2_value_test( "bltu", 0xffffffff, 0x00000000, False ),
    gen_br2_value_test( "bltu", 0x00000000, 0xffffffff, True  ),
  ]

def gen_random_test():
  asm_code = []
  for _ in range(50):
    a = b32(random.randint(0, 0xffffffff))
    b = b32(random.randint(0, 0xffffffff))
    taken = a.uint() < b.uint()
    asm_code.append( gen_br2_value_test("bltu", a.uint(), b.uint(), taken) )
  return asm_code

