#=========================================================================
# auipc
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
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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
    auipc x3, 0x00000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00000200
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
    auipc x3, 0x7ffff
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x7ffff200
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
    auipc x3, 0x80000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x80000200
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
    auipc x0, 0x12345
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
  for _ in range(25):
    imm20 = random.randint(0, 0xFFFFF)
    exp   = (imm20 << 12) & 0xffffffff
    asm_code.append(f"""
    auipc x1, 0x{imm20:05x}
    auipc x2, 0x00000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sub  x3, x1, x2
    addi x3, x3, 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x{exp:08x}
    nop
    """)
  return asm_code


def gen_random_test_delays():
  asm = []
  NUM_CASES = 24  
  for _ in range(NUM_CASES):
    imm20 = random.randint(0, 0xFFFFF)
    exp   = (imm20 << 12) & 0xffffffff
    asm.append(f"""

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    auipc x1, 0x{imm20:05x}
    auipc x2, 0x00000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sub  x3, x1, x2
    addi x3, x3, 4

    csrw proc2mngr, x3 > 0x{exp:08x}
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    """)
  return "\n".join(asm)

