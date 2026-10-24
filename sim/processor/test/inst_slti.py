#=========================================================================
# slti
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 6
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

def gen_equal_test():
  return """
    csrr x1, mngr2proc < 123
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 123
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_neg_vs_pos_test():
  return """
    csrr x1, mngr2proc < -1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 0
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

def gen_neg_vs_more_neg_test():
  return """
    csrr x1, mngr2proc < -1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, -2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_signbit_src_test():
  return """
    csrr x1, mngr2proc < 0x80000000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 0
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

def gen_write_x0_test():
  return """
    csrr x1, mngr2proc < 42
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x0, x1, 100
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x0 > 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_random_test():
  asm_code = []
  for _ in range(100):
    src  = b32( random.randint(0, 0xffffffff) )
    imm  = random.randint(-2048, 2047)
    ssrc = src.int()
    exp  = 1 if ssrc < imm else 0
    asm_code.append( gen_rimm_value_test("slti", src.uint(), imm, exp) )
  return asm_code  
