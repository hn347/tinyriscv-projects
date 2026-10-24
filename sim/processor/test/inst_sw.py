#=========================================================================
# sw
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
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0xdeadbeef

    .data
    .word 0x01020304
  """

def gen_pos_offset_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0x11223344
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 16(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 16(x1)
    csrw proc2mngr, x3 > 0x11223344

    .data
    .space 64
  """

def gen_neg_offset_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0xa5a5a5a5
    addi x1, x1, 32
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, -32(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, -32(x1)
    csrw proc2mngr, x3 > 0xa5a5a5a5

    .data
    .space 64
  """

def gen_overwrite_same_addr_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0xdeadbeef
    csrr x4, mngr2proc < 0x0badc0de
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x4, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0x0badc0de

    .data
    .space 64
  """

def gen_random_test():
  asm = []
  base_addr = 0x00002000
  NUM_CASES = 20  # keep moderate; makes delay runs stable

  asm.append(f"    csrr x1, mngr2proc < 0x{base_addr:08x}\n")

  used_offsets = set()
  for _ in range(NUM_CASES):
    # choose 4-byte aligned offsets within a 0..(4*(NUM_CASES+4)) window
    off = random.randrange(0, 4*(NUM_CASES+4), 4)
    # ensure uniqueness so we don't overwrite a prior case
    while off in used_offsets:
      off = random.randrange(0, 4*(NUM_CASES+4), 4)
    used_offsets.add(off)

    val = random.randint(0, 0xffffffff)

    asm.append(f"""
    # ---- random case: off={off}, val=0x{val:08x} ----
    csrr x2, mngr2proc < 0x{val:08x}
    sw   x2, {off}(x1)
    nop
    nop
    nop
    nop
    lw   x3, {off}(x1)
    csrw proc2mngr, x3 > 0x{val:08x}
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    """)

  asm.append("""
    .data
    .space 256
  """)
  return "\n".join(asm)
