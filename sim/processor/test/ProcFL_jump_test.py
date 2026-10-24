#=========================================================================
# ProcFL_jump_test.py
#=========================================================================
# We group all our test cases into a class so that we can easily reuse
# these test cases in our RTL tests. We can simply inherit from this test
# class, overload the setup_class method, and set the ProcType
# appropriately.

import pytest

from pymtl3 import *
from processor.test.harness import asm_test, run_test
from processor.ProcFL import ProcFL

from processor.test import inst_jal
from processor.test import inst_jalr

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcFL

  #-----------------------------------------------------------------------
  # jal
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jal.gen_basic_test        ) ,
    asm_test( inst_jal.gen_jal_quick_check_test ),
    asm_test( inst_jal.gen_jump_forward_basic_test ),
    asm_test( inst_jal.gen_jump_back_basic_test ),
    asm_test( inst_jal.gen_two_jumps_chain_test ),
    asm_test( inst_jal.gen_linkaddr_capture_test ),
    asm_test( inst_jal.gen_jal_data_hazard_test ),
    asm_test( inst_jal.gen_jal_src_dep_test ),
    asm_test( inst_jal.gen_jal_src_eq_dest_test ),
    asm_test( inst_jal.gen_random_test     ),
  ])

  def test_jal( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_jal_delays( s ):
    run_test( s.ProcType, inst_jal.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # jalr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jalr.gen_basic_test    ),
    asm_test( inst_jalr.gen_value_test ),
    asm_test( inst_jalr.gen_immediate_test ),
    asm_test( inst_jalr.gen_reg_test ),
    asm_test( inst_jalr.gen_negative_offset_test ),
    asm_test( inst_jalr.gen_dest_dep_test ),
    asm_test( inst_jalr.gen_srcs_dest_test ),
    asm_test( inst_jalr.gen_random_test ),
  ])

  def test_jalr( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_jalr_delays( s ):
    run_test( s.ProcType, inst_jalr.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

