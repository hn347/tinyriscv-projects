#=========================================================================
# sll
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
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sll x3, x1, x2
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

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 4, "sll", 1, 2, 4 ),
    gen_rr_dest_dep_test( 3, "sll", 1, 3, 8 ),
    gen_rr_dest_dep_test( 2, "sll", 1, 4, 16 ),
    gen_rr_dest_dep_test( 1, "sll", 1, 5, 32 ),
    gen_rr_dest_dep_test( 0, "sll", 1, 6, 64 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sll", 1, 2, 4 ),
    gen_rr_src0_dep_test( 4, "sll", 3, 2, 12 ),
    gen_rr_src0_dep_test( 3, "sll", 7, 3, 56 ),
    gen_rr_src0_dep_test( 2, "sll", 15, 4, 240 ),
    gen_rr_src0_dep_test( 1, "sll", 31, 5, 992 ),
    gen_rr_src0_dep_test( 0, "sll", 63, 6, 4032 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sll", 2, 1, 4 ),
    gen_rr_src1_dep_test( 4, "sll", 3, 2, 12 ),
    gen_rr_src1_dep_test( 3, "sll", 5, 3, 40 ),
    gen_rr_src1_dep_test( 2, "sll", 6, 4, 96 ),
    gen_rr_src1_dep_test( 1, "sll", 7, 5, 224 ),
    gen_rr_src1_dep_test( 0, "sll", 8, 6, 512 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 4, "sll", 2, 2, 8 ),
    gen_rr_srcs_dep_test( 3, "sll", 3, 3, 24 ),
    gen_rr_srcs_dep_test( 2, "sll", 4, 4, 64 ),
    gen_rr_srcs_dep_test( 1, "sll", 5, 5, 160 ),
    gen_rr_srcs_dep_test( 0, "sll", 6, 6, 384 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sll", 1, 1, 2 ),
    gen_rr_src1_eq_dest_test( "sll", 2, 1, 4 ),
    gen_rr_src0_eq_src1_test( "sll", 2, 8 ),
    gen_rr_srcs_eq_dest_test( "sll", 3, 24 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rr_value_test( "sll", 0x00000001, 0x00000000, 0x00000001 ), # Shift 1 by 0 -> 1
    gen_rr_value_test( "sll", 0x00000001, 0x00000001, 0x00000002 ), # Shift 1 by 1 -> 2
    gen_rr_value_test( "sll", 0x00000001, 0x0000001F, 0x80000000 ), # Shift 1 by 31 -> 0x80000000
    gen_rr_value_test( "sll", 0x00000001, 0x00000020, 0x00000001 ), # Shift 1 by 32 (masked to 0x1F) -> 1
    gen_rr_value_test( "sll", 0xFFFFFFFF, 0x00000001, 0xFFFFFFFE ), # Shift -1 (0xFFFFFFFF) by 1 -> 0xFFFFFFFE
    gen_rr_value_test( "sll", 0x80000000, 0x00000001, 0x00000000 ), # Shift 0x80000000 by 1 -> 0x00000000 (overflow)
    gen_rr_value_test( "sll", 0x12345678, 0x00000004, 0x23456780 ), # Shift 0x12345678 by 4 -> 0x23456780
    gen_rr_value_test( "sll", 0x7FFFFFFF, 0x00000002, 0xFFFFFFFC ), # Shift 0x7FFFFFFF by 2 -> 0xFFFFFFFC
    gen_rr_value_test( "sll", 0x00000001, 0x0000001C, 0x10000000 ), # Shift 1 by 28 -> 0x10000000
    gen_rr_value_test( "sll", 0x00000001, 0xFFFFFFFF, 0x80000000 ), # Shift 1 by -1 (0xFFFFFFFF masked to 31) -> 0x80000000
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32(random.randint(0, 0xffffffff))  
    src1 = b32(random.randint(0, 0x1f))  
    dest = (src0.uint() << src1.uint()) & 0xFFFFFFFF
    asm_code.append(gen_rr_value_test("sll", f"0x{src0.uint():08x}", f"0x{src1.uint():08x}", f"0x{dest:08x}"))
  
  return asm_code