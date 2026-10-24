#=========================================================================
# extra multicore memory tests
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < {0x00002000,0x00002004,0x00002008,0x0000200c}
    csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}

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
    csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}

    .data
    .word 0x01020304
    .word 0x11121314
    .word 0x21222324
    .word 0x31323334
  """

#-------------------------------------------------------------------------
# gen_cross_bank_test
#-------------------------------------------------------------------------

def gen_cross_bank_test():
  return """
    csrr x1, mngr2proc < {0x00002010,0x00002020,0x00002030,0x00002040}
    csrr x2, mngr2proc < {0x11110001,0x22220002,0x33330003,0x44440004}

    sw   x2, 0(x1)
    nop
    nop
    nop

    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x11110001,0x22220002,0x33330003,0x44440004}

    .data
    .word 0xaaaaaaaa
    .word 0xbbbbbbbb
    .word 0xcccccccc
    .word 0xdddddddd
  """

#-------------------------------------------------------------------------
# gen_bank_conflict_test
#-------------------------------------------------------------------------

def gen_bank_conflict_test():
  return """
    csrr x1, mngr2proc < {0x00002050,0x00002054,0x00002058,0x0000205c}
    csrr x2, mngr2proc < {0xaaaa0001,0xbbbb0002,0xcccc0003,0xdddd0004}

    sw   x2, 0(x1)
    nop
    nop

    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0xaaaa0001,0xbbbb0002,0xcccc0003,0xdddd0004}

    .data
    .word 0xffffffff
    .word 0xffffffff
    .word 0xffffffff
    .word 0xffffffff
  """

#-------------------------------------------------------------------------
# gen_interleave_rw_test
#-------------------------------------------------------------------------

def gen_interleave_rw_test():
  return """
    csrr x1, mngr2proc < {0x00002060,0x00002064,0x00002068,0x0000206c}
    csrr x2, mngr2proc < {0x10100010,0x20200020,0x30300030,0x40400040}

    # Initial load (from .data or reset value)
    lw   x3, 0(x1)
    nop

    # Overwrite data
    sw   x2, 0(x1)
    nop
    nop

    # Load back new value
    lw   x4, 0(x1)
    csrw proc2mngr, x4 > {0x10100010,0x20200020,0x30300030,0x40400040}

    .data
    .word 0x00000001
    .word 0x00000002
    .word 0x00000003
    .word 0x00000004
  """

#-------------------------------------------------------------------------
# gen_mixed_stride_test
#-------------------------------------------------------------------------

def gen_mixed_stride_test():
  return """
    csrr x1, mngr2proc < {0x00002070,0x00002078,0x00002080,0x00002088}
    csrr x2, mngr2proc < {0xabc00111,0xabc00222,0xabc00333,0xabc00444}

    sw   x2, 0(x1)
    nop
    nop

    lw   x3, 0(x1)
    lw   x3, 0(x1)
    lw   x3, 0(x1)

    csrw proc2mngr, x3 > {0xabc00111,0xabc00222,0xabc00333,0xabc00444}

    .data
    .word 0x55555555
    .word 0x66666666
    .word 0x77777777
    .word 0x88888888
  """

#-------------------------------------------------------------------------
# gen_reverse_order_test
#-------------------------------------------------------------------------

def gen_reverse_order_test():
  return """
    csrr x1, mngr2proc < {0x0000209c,0x00002098,0x00002094,0x00002090}
    csrr x2, mngr2proc < {0xff001122,0xee002233,0xdd003344,0xcc004455}

    sw   x2, 0(x1)
    nop
    nop
    nop

    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0xff001122,0xee002233,0xdd003344,0xcc004455}

    .data
    .word 0x12341234
    .word 0x56785678
    .word 0x9abc9abc
    .word 0xdef0def0
  """

#-------------------------------------------------------------------------
# gen_random_multiline_test
#-------------------------------------------------------------------------

def gen_random_multiline_test():
  random.seed(12345)

  base = 0x000020a0
  # Four addresses in a small range, each 4-byte aligned
  addrs = [ base + random.randint(0,3)*16 + i*4 for i in range(4) ]
  vals  = [ random.randint(0,0xffffffff) for _ in range(4) ]

  addr_str = ",".join(hex(a) for a in addrs)
  val_str  = ",".join(hex(v) for v in vals)

  return f"""
    csrr x1, mngr2proc < {{{addr_str}}}
    csrr x2, mngr2proc < {{{val_str}}}

    sw   x2, 0(x1)
    nop
    nop

    lw   x3, 0(x1)
    lw   x3, 0(x1)
    lw   x3, 0(x1)

    csrw proc2mngr, x3 > {{{val_str}}}

    .data
    .word 0
    .word 0
    .word 0
    .word 0
  """

#-------------------------------------------------------------------------
# gen_random_dualop_test
#-------------------------------------------------------------------------

def gen_random_dualop_test():
  random.seed(999)

  base = 0x000020e0
  addrs = [ base + i*4 for i in range(4) ]
  init_vals = [ random.randint(0,0xffff) for _ in range(4) ]
  adds      = [ random.randint(1,15)     for _ in range(4) ]

  results = [ (v + a) & 0xffffffff for v,a in zip(init_vals,adds) ]

  a_str   = ",".join(hex(a) for a in addrs)
  v_str   = ",".join(hex(v) for v in init_vals)
  add_str = ",".join(hex(a) for a in adds)
  r_str   = ",".join(hex(r) for r in results)

  return f"""
    csrr x1, mngr2proc < {{{a_str}}}
    csrr x2, mngr2proc < {{{v_str}}}
    csrr x3, mngr2proc < {{{add_str}}}

    # Write initial values
    sw   x2, 0(x1)
    nop
    nop

    # Read back, compute new value, store result
    lw   x4, 0(x1)
    add  x5, x4, x3
    sw   x5, 0(x1)
    nop

    # Verify by loading result
    lw   x6, 0(x1)
    csrw proc2mngr, x6 > {{{r_str}}}

    .data
    .word 0
    .word 0
    .word 0
    .word 0
  """
