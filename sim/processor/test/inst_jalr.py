#=========================================================================
# jalr
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

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0           # 0x0200
                              #
    lui x1,      %hi[label_a] # 0x0204
    addi x1, x1, %lo[label_a] # 0x0208
                              #
    nop                       # 0x020c
    nop                       # 0x0210
    nop                       # 0x0214
    nop                       # 0x0218
    nop                       # 0x021c
    nop                       # 0x0220
    nop                       # 0x0224
    nop                       # 0x0228
                              #
    jalr  x31, x1, 0          # 0x022c
    addi  x3, x3, 0b01        # 0x0230

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

    # Check the link address
    csrw  proc2mngr, x31 > 0x0230

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3  > 0b10

  """

def gen_value_test():
  return """
    # Simple jalr value test
    # jalr at 0x204 -> link = 0x208
    csrr x1, mngr2proc < 0x00000220
    jalr x2, x1, 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000208
  """

def gen_immediate_test():
  return """
    # Test jalr with immediate offset
    # Address: 0x200
    addi x1, x0, 0x210    # Base address = 0x210
    # Address: 0x204
    jalr x2, x1, 8        # Jump to base + 8 = 0x218
    
    # This should be skipped (0x208)
    addi x3, x0, 0xbad
    
    nop
    nop
    nop
    
  target:  # Address: 0x218
    # Verify return address (0x204 + 4 = 0x208)
    csrw proc2mngr, x2 > 0x00000208
    # Verify skipped instruction
    csrw proc2mngr, x3 > 0
  """

def gen_reg_test():
  return """
    # Test jalr with computed address
    # Address: 0x200
    addi x1, x0, 0x200
    # Address: 0x204
    addi x1, x1, 0x20     # x1 = 0x220
    # Address: 0x208
    jalr x2, x1, 0        # Jump to 0x220
    
    # This should be skipped (0x20c)
    addi x3, x0, 0xbad
    nop
    nop
    nop
    nop
    
  target:  # Address: 0x220
    # Verify return address (0x208 + 4 = 0x20c)
    csrw proc2mngr, x2 > 0x0000020c
    # Verify skipped instruction
    csrw proc2mngr, x3 > 0
  """


def gen_negative_offset_test():
  return """
    # Test jalr with negative immediate offset
    addi x1, x0, 0x228       # 0x0200: Base address = 0x228
    jalr x2, x1, -0x10       # 0x0204: Jump to 0x218 (0x228 - 0x10)
    
    # This should be skipped
    addi x3, x0, 0xbad       # 0x0208: SKIPPED
    nop                       # 0x020c
    nop                       # 0x0210
    nop                       # 0x0214
    
  target:                     # 0x0218
    # Verify return address (0x0204 + 4 = 0x0208)
    csrw proc2mngr, x2 > 0x00000208
    
    nop                       # 0x021c
    nop                       # 0x0220
    nop                       # 0x0224
    nop                       # 0x0228
  """

def gen_dest_dep_test():
  return """
    # Simple jalr destination dependency test
    # jalr at 0x204 -> link = 0x208
    csrr x1, mngr2proc < 0x00000220
    jalr x2, x1, 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000208
  """


def gen_srcs_dest_test():
  return """
    # Simple jalr src == dest test
    # jalr at 0x204 -> link = 0x208
    csrr x1, mngr2proc < 0x00000220
    jalr x1, x1, 0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00000208
  """

#new test
def gen_random_test():
  reset_jalr_addr()
  asm_list = []

  for _ in range(20):
    base = random.randint(0, 10)
    imm  = random.randint(1, 10)
    asm_list.append(
      gen_jalr_template(base, base, "x1", "x2", imm)
    )

  return asm_list