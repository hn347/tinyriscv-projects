#=========================================================================
# sra
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
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sra x3, x1, x2
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

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    # shift by 0 -> same value
    gen_rr_value_test( "sra", 0x7fffffff, 0x00000000, 0x7fffffff ),
    # positive number: zeros shift in
    gen_rr_value_test( "sra", 0x00008000, 0x00000003, 0x00001000 ),
    # negative number: ones shift in
    gen_rr_value_test( "sra", 0x80000000, 0x00000001, 0xc0000000 ),
    # shift by 31
    gen_rr_value_test( "sra", 0xffffffff, 0x0000001f, 0xffffffff ),  
    gen_rr_value_test( "sra", 0x7fffffff, 0x0000001f, 0x00000000 ), 
    # rs2 larger than 31: only low 5 bits count
    gen_rr_value_test( "sra", 0x80000000, 0x00000040, 0x80000000 ),  
    gen_rr_value_test( "sra", 0x80000000, 0x00000021, 0xc0000000 ), 
  ]

#-------------------------------------------------------------------------
# gen_x0_test
#-------------------------------------------------------------------------

def gen_x0_test():
  return [
    # dest = x0 ignored
    """
    csrr x1, mngr2proc < 0x80000000
    csrr x2, mngr2proc < 1
    sra  x0, x1, x2
    csrw proc2mngr, x0 > 0
    """,
    # src0 = x0 -> 0 >> n = 0 (any n)
    """
    csrr x2, mngr2proc < 13
    sra  x3, x0, x2
    csrw proc2mngr, x3 > 0
    """,
    # src1 = x0 -> shift by 0
    """
    csrr x1, mngr2proc < 0x89abcdef
    sra  x4, x1, x0
    csrw proc2mngr, x4 > 0x89abcdef
    """,
  ]

#-------------------------------------------------------------------------
# gen_alias_test
#-------------------------------------------------------------------------

def gen_alias_test():
  return [
    # rd == rs1
    """
    csrr x8,  mngr2proc < 0x80000000
    csrr x9,  mngr2proc < 0x00000004
    sra  x8,  x8, x9              # 0x80000000 >> 4 = 0xf8000000
    csrw proc2mngr, x8 > 0xf8000000
    """,
    # rd == rs2 (ensure rs2 read before wb to rd)
    """
    csrr x10, mngr2proc < 0x7fffffff
    csrr x11, mngr2proc < 0x0000001f
    sra  x11, x10, x11            # +max >> 31 = 0
    csrw proc2mngr, x11 > 0x00000000
    """,
  ]

#-------------------------------------------------------------------------
# gen_hi_regs_edge_test
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# gen_hi_regs_edge_test  
#-------------------------------------------------------------------------

def gen_hi_regs_edge_test():
  return """
    csrr x28, mngr2proc < 0xffffffff      
    csrr x29, mngr2proc < 0x0000001f
    sra  x30, x28, x29                    
    csrw proc2mngr, x30 > 0xffffffff

    csrr x31, mngr2proc < 0x80000000      
    csrr x29, mngr2proc < 0x0000001e      
    sra  x30, x31, x29                    
    csrw proc2mngr, x30 > 0xfffffffe
  """

#-------------------------------------------------------------------------
# gen_random_test  
#-------------------------------------------------------------------------

def gen_random_test(n=20):
  def to_i32(x):
    x &= 0xffffffff
    return x - 0x100000000 if (x & 0x80000000) else x

  def sra32(a, sh):
    sh &= 0x1f
    return (to_i32(a) >> sh) & 0xffffffff

  asm = []
  for _ in range(n):
    a  = random.randint(0, 0xffffffff)
    sh = random.randint(0, 0xffffffff)
    asm.append( gen_rr_value_test("sra", a, sh, sra32(a, sh)) )
  return asm


