#=========================================================================
# extra multicore csr tests
#=========================================================================

from pymtl3 import *

#-------------------------------------------------------------------------
# Test proc2mngr and mngr2proc with lists of values
#-------------------------------------------------------------------------

def gen_proc2mngr_sinks_test():
  return """
    csrr x2, mngr2proc < 1
    csrw proc2mngr, x2 > {1,1,1,1}
  """

def gen_proc2mngr_srcs_test():
  return """
    csrr x2, mngr2proc < {1,1,1,1}
    csrw proc2mngr, x2 > 1
  """

def gen_proc2mngr_srcs_sinks_test():
  return """
    csrr x2, mngr2proc < {1,2,3,4}
    csrw proc2mngr, x2 > {1,2,3,4}
  """

#-------------------------------------------------------------------------
# Test numcores and coreid
#-------------------------------------------------------------------------

def gen_core_stats_test():
  return """

    # Turn on stats here
    csrr x1, mngr2proc < 1
    csrw stats_en, x1

    # Check numcores/coreid
    csrr x2, numcores
    csrw proc2mngr, x2 > 4
    csrr x2, coreid
    csrw proc2mngr, x2 > {0,1,2,3}

    # Turn off stats here
    csrw stats_en, x0
    nop
    nop
    csrr x1, mngr2proc < 1
    csrw proc2mngr, x1 > 1
    nop
    nop
    nop
  """

