#=========================================================================
# slli
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
    csrr x1, mngr2proc < 0x80008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
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
    csrr x1, mngr2proc < 0x12345678
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x00
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x12345678
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_max_shamt_test():
  return """
    csrr x1, mngr2proc < 0x00000001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 31
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x80000000
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
    csrr x1, mngr2proc < 0x0F00000F
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0xF00000F0
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
    csrr x1, mngr2proc < 0xDEADBEEF
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x0, x1, 13
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x0 > 0x00000000
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
    src   = b32(random.randint(0, 0xffffffff))
    shamt = random.randint(0, 31)
    dest  = b32((src.uint() << shamt) & 0xffffffff).uint()
    asm_code.append(gen_rimm_value_test("slli", src.uint(), shamt, dest))
  return asm_code

