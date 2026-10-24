#=========================================================================
# lui
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
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
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
    lui x1, 0x00000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00000000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_max_pos_imm_test():
  return """
    lui x1, 0x7ffff
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x7ffff000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_min_neg_imm_test():
  return """
    lui x1, 0x80000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x80000000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

def gen_lower_bits_zero_test():
  return """
    lui x1, 0x12345
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x12345000
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
    lui x0, 0x54321
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
  for _ in range(50):
    imm20 = random.randint(0, 0xFFFFF)
    exp   = (imm20 << 12) & 0xffffffff
    asm_code.append(f"""
    lui x1, 0x{imm20:05x}
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x{exp:08x}
    nop
    """)
  return asm_code


