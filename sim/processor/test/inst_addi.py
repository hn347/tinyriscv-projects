#=========================================================================
# addi
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

    csrr x1, mngr2proc, < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    addi x3, x1, 0x0004
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 9
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_zero_imm_test():
  return """
    csrr x1, mngr2proc, < 42
    nop
    addi x3, x1, 0
    nop
    csrw proc2mngr, x3 > 42
    nop
  """

def gen_neg_imm_test():
  return """
    csrr x1, mngr2proc, < 100
    nop
    addi x3, x1, -1
    nop
    csrw proc2mngr, x3 > 99
    nop
  """

def gen_large_pos_imm_test():
  return """
    csrr x1, mngr2proc, < 3
    nop
    addi x3, x1, 2047
    nop
    csrw proc2mngr, x3 > 2050
    nop
  """

def gen_write_x0_test():
  return """
    csrr x1, mngr2proc, < 123
    nop
    addi x0, x1, 77
    nop
    csrw proc2mngr, x0 > 0
    nop
  """

def gen_chain_dep_test():
  return """
    csrr x1, mngr2proc, < 10
    addi x2, x1, 7
    addi x3, x2, -3
    csrw proc2mngr, x3 > 14
    nop
  """

def gen_random_test():
  asm_code = []
  for _ in range(50):
    src  = b32( random.randint(0, 0xffffffff) )
    imm  = random.randint(-2048, 2047)
    dest = b32( (src.uint() + imm) & 0xffffffff )
    asm_code.append( gen_rimm_value_test("addi", src.uint(), imm, dest.uint()) )
  return asm_code

def bypass_logic_test():
  return """
    csrr x2, mngr2proc, < 0 
    addi x1, x2, 1
    addi x3, x1, 1
    addi x4, x3, 1
    csrw proc2mngr, x4 > 3
  """
