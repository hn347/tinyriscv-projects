#=========================================================================
# jal
#=========================================================================

from pymtl3 import *
from processor.test.inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0     # 0x0200
                        #
    nop                 # 0x0204
    nop                 # 0x0208
    nop                 # 0x020c
    nop                 # 0x0210
    nop                 # 0x0214
    nop                 # 0x0218
    nop                 # 0x021c
    nop                 # 0x0220
                        #
    jal   x1, label_a   # 0x0224
    addi  x3, x3, 0b01  # 0x0228

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
    csrw  proc2mngr, x1 > 0x0228

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3 > 0b10

  """

def gen_jal_quick_check_test():
  return """
    # smallest jal check
    jal  x1, T1
    nop
  T1:
    csrw proc2mngr, x1 > 0x00000204
    nop
  """

def gen_jump_forward_basic_test():
  return """
    # jump forward to label
    jal x3, FWD
    # if jal fails we’d hit this
    addi x4, x0, 0xbad

  FWD:
    # x3 should hold link addr, x4 still zero
    csrw proc2mngr, x3 > 0x00000204
    csrw proc2mngr, x4 > 0
  """

def gen_jump_back_basic_test():
  return """
    # quick backwards jump
    addi x1, x0, 0x100

  START:
    jal x0, TGT
    # skipped if jal works
    addi x2, x0, 0xbad

  TGT:
    # we should land here
    csrw proc2mngr, x1 > 0x100
    addi x3, x0, 0x123
    csrw proc2mngr, x3 > 0x123
  """

def gen_two_jumps_chain_test():
  return """
    # two jal’s in a row
    jal x2, A
    nop
  A:
    jal x3, B
    nop
  B:
    # check both link addresses
    csrw proc2mngr, x2 > 0x00000204
    csrw proc2mngr, x3 > 0x0000020c
  """

def gen_linkaddr_capture_test():
  return """
    # capture link addresses twice
    jal x5, T1
  T1:
    csrw proc2mngr, x5 > 0x00000204

    jal x6, T2
  T2:
    csrw proc2mngr, x6 > 0x0000020c
  """

def gen_jal_data_hazard_test():
  return """
    # make sure regs survive jal
    addi x10, x0, 0x100
    jal  x12, HZ
    nop
  HZ:
    csrw proc2mngr, x12 > 0x00000208
    csrw proc2mngr, x10 > 0x100
  """

def gen_jal_src_dep_test():
  return """
    # use src reg after jump
    addi x1, x0, 5
    jal  x2, LAB
    nop
  LAB:
    addi x3, x1, 3
    csrw proc2mngr, x2 > 0x00000208
    csrw proc2mngr, x3 > 8
  """

def gen_jal_src_eq_dest_test():
  return """
    # src == dest, should hold link addr
    addi x5, x0, 100
    jal  x5, LAB
    nop
  LAB:
    csrw proc2mngr, x5 > 0x00000208
  """

def gen_random_test():
  progs = []
  for i in range(20):
    progs.append(f"""
    addi  x3, x0, 0

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    jal   x0, L_JAL_{i}
    addi  x3, x3, 1
    addi  x3, x3, 4

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  L_JAL_{i}:
    nop
    nop
    nop
    addi  x3, x3, 2
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

    csrw  proc2mngr, x3 > 2

    nop
    """)
  return progs

