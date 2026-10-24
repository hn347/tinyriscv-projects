#=========================================================================
# slt
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
    csrr x1, mngr2proc < 4
    csrr x2, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slt x3, x1, x2
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

#-------------------------------------------------------------------------
# gen_mixed_signs_test
#-------------------------------------------------------------------------

def gen_mixed_signs_test():
  return """
    # a0 < b0 : (-1 < 0) -> 1        (bit 0)
    csrr x1, mngr2proc < 0xffffffff      # -1
    csrr x2, mngr2proc < 0x00000000      #  0

    # a1 < b1 : (0 < -1) -> 0        (bit 1)
    csrr x3, mngr2proc < 0x00000000
    csrr x4, mngr2proc < 0xffffffff

    # a2 < b2 : (0x7fffffff < 0x80000000) -> 0   (+max < -min? false)
    csrr x5, mngr2proc < 0x7fffffff
    csrr x6, mngr2proc < 0x80000000

    # a3 < b3 : (-2^31 < -1) -> 1
    csrr x7, mngr2proc < 0x80000000
    csrr x8, mngr2proc < 0xffffffff

    addi x9,  x0, 0                # mask = 0

    slt  x10, x1, x2               # bit0
    slli x10, x10, 0
    add  x9,  x9, x10

    slt  x10, x3, x4               # bit1
    slli x10, x10, 1
    add  x9,  x9, x10

    slt  x10, x5, x6               # bit2
    slli x10, x10, 2
    add  x9,  x9, x10

    slt  x10, x7, x8               # bit3
    slli x10, x10, 3
    add  x9,  x9, x10

    csrw proc2mngr, x9 > 9
  """

#-------------------------------------------------------------------------
# gen_threshold_count_test
#-------------------------------------------------------------------------

def gen_threshold_count_test():
  return """
    # T = 10
    csrr x20, mngr2proc < 10
    # values
    csrr x1,  mngr2proc < 5
    csrr x2,  mngr2proc < 10
    csrr x3,  mngr2proc < 11
    csrr x4,  mngr2proc < 0xffffffff     # -1

    addi x21, x0, 0           # count = 0

    slt  x5, x1, x20          # 5 < 10 -> 1
    add  x21, x21, x5

    slt  x6, x2, x20          # 10 < 10 -> 0
    add  x21, x21, x6

    slt  x7, x3, x20          # 11 < 10 -> 0
    add  x21, x21, x7

    slt  x8, x4, x20          # -1 < 10 -> 1
    add  x21, x21, x8

    csrw proc2mngr, x21 > 2
  """

#-------------------------------------------------------------------------
# gen_equal_false_sweep_test
#-------------------------------------------------------------------------

def gen_equal_false_sweep_test():
  return """
    csrr x1,  mngr2proc < 0x00000000
    csrr x2,  mngr2proc < 0xffffffff     # -1
    csrr x3,  mngr2proc < 0x80000000     # -2^31
    csrr x4,  mngr2proc < 0x7fffffff

    addi x9,  x0, 0

    slt  x5, x1, x1      # 0 < 0 -> 0
    add  x9, x9, x5

    slt  x6, x2, x2      # -1 < -1 -> 0 (forward 0)
    add  x9, x9, x6

    slt  x7, x3, x3      # -2^31 < -2^31 -> 0
    add  x9, x9, x7

    slt  x8, x4, x4      # +max < +max -> 0
    add  x9, x9, x8

    csrw proc2mngr, x9 > 0
  """

#-------------------------------------------------------------------------
# gen_write_after_write_test
#-------------------------------------------------------------------------

def gen_write_after_write_test():
  return """
    csrr x1, mngr2proc < 0xffffffff   # -1
    csrr x2, mngr2proc < 0x00000000   # 0
    csrr x3, mngr2proc < 0x00000005
    csrr x4, mngr2proc < 0x80000000   # -2^31

    slt  x5, x1, x2      # -1 < 0  -> 1
    slt  x5, x3, x4      # 5 < -2^31 -> 0  (overwrite)
    slt  x5, x4, x3      # -2^31 < 5 -> 1  (final)

    csrw proc2mngr, x5 > 1
  """

#-------------------------------------------------------------------------
# gen_hi_regs_edge_test
#-------------------------------------------------------------------------

def gen_hi_regs_edge_test():
  return """
    csrr x28, mngr2proc < 0x80000000   # -2^31
    csrr x29, mngr2proc < 0x7fffffff   # +max

    slt  x30, x28, x29   # -2^31 < +max -> 1
    slt  x31, x29, x28   # +max < -2^31 -> 0

    # mask = (x31<<1) | x30 = (0<<1) | 1 = 1 ? Wait, we want 2: put x30 into bit1.
    slli x30, x30, 1     # x30 = 2
    add  x30, x30, x31   # x30 = 2 + 0 = 2

    csrw proc2mngr, x30 > 2
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test(n=20):
  def to_i32(x):
    x &= 0xffffffff
    return x - 0x100000000 if (x & 0x80000000) else x
  asm = []
  for _ in range(n):
    a = random.randint(0, 0xffffffff)
    b = random.randint(0, 0xffffffff)
    exp = 1 if to_i32(a) < to_i32(b) else 0
    asm.append( gen_rr_value_test("slt", a, b, exp) )
  return asm
