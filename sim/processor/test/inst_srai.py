#=========================================================================
# srai
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
    srai x3, x1, 0x03
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

def gen_zero_shamt_test():
  return """
    csrr x1, mngr2proc < 0xF0F0F0F0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 0x00
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0xF0F0F0F0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_max_shamt_pos_test():
  return """
    csrr x1, mngr2proc < 0x7FFFFFFF
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 31
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00000000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_max_shamt_neg_test():
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
    srai x3, x1, 31
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0xFFFFFFFF
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_pattern_test():
  return """
    csrr x1, mngr2proc < 0xF000000F
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0xFF000000
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
    src   = b32( random.randint(0, 0xffffffff) )
    shamt = random.randint(0, 31)
    s     = src.uint()
    if s & 0x80000000:
      s -= 0x100000000
    dest  = (s >> shamt) & 0xffffffff

    asm_code.append( gen_rimm_value_test("srai", src.uint(), shamt, dest) )
  return asm_code
