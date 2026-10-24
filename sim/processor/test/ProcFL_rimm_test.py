#=========================================================================
# ProcFL_rimm_test.py
#=========================================================================
# We group all our test cases into a class so that we can easily reuse
# these test cases in our RTL tests. We can simply inherit from this test
# class, overload the setup_class method, and set the ProcType
# appropriately.

import pytest

from pymtl3 import *
from processor.test.harness import asm_test, run_test
from processor.ProcFL import ProcFL

from processor.test import inst_addi
from processor.test import inst_ori
from processor.test import inst_slti
from processor.test import inst_srai
from processor.test import inst_slli
from processor.test import inst_lui
from processor.test import inst_auipc
from processor.test import inst_andi
from processor.test import inst_xori
from processor.test import inst_srli

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcFL

  #-----------------------------------------------------------------------
  # addi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_addi.gen_basic_test        ) ,
    asm_test( inst_addi.gen_zero_imm_test     ),
    asm_test( inst_addi.gen_neg_imm_test      ),
    asm_test( inst_addi.gen_large_pos_imm_test),
    asm_test( inst_addi.gen_write_x0_test     ),
    asm_test( inst_addi.gen_chain_dep_test    ),
    asm_test( inst_addi.gen_random_test       ),
    asm_test( inst_addi.bypass_logic_test) ,
  ])
  def test_addi( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_addi_delays( s ):
    run_test( s.ProcType, inst_addi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # ori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_ori.gen_basic_test     ) ,
    asm_test( inst_ori.gen_dest_dep_test  ) ,
    asm_test( inst_ori.gen_src_dep_test   ) ,
    asm_test( inst_ori.gen_srcs_dest_test ) ,
    asm_test( inst_ori.gen_value_test     ) ,
    asm_test( inst_ori.gen_random_test    ) ,
  ])
  def test_ori( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_ori_delays( s ):
    run_test( s.ProcType, inst_ori.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # slti
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slti.gen_basic_test     ) ,
    asm_test( inst_slti.gen_equal_test        ),
    asm_test( inst_slti.gen_neg_vs_pos_test   ),
    asm_test( inst_slti.gen_neg_vs_more_neg_test ),
    asm_test( inst_slti.gen_signbit_src_test  ),
    asm_test( inst_slti.gen_write_x0_test     ),
    asm_test( inst_slti.gen_random_test       ),
  ])
  def test_slti( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_slti_delays( s ):
    run_test( s.ProcType, inst_slti.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )


  #-----------------------------------------------------------------------
  # srai
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srai.gen_basic_test     ) ,
    asm_test( inst_srai.gen_zero_shamt_test    ),
    asm_test( inst_srai.gen_max_shamt_pos_test ),
    asm_test( inst_srai.gen_max_shamt_neg_test ),
    asm_test( inst_srai.gen_pattern_test       ),
    asm_test( inst_srai.gen_random_test        ),
  ])
  def test_srai( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srai_delays( s ):
    run_test( s.ProcType, inst_srai.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # slli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slli.gen_basic_test     ) ,
    asm_test( inst_slli.gen_zero_shamt_test ),
    asm_test( inst_slli.gen_max_shamt_test  ),
    asm_test( inst_slli.gen_pattern_test    ),
    asm_test( inst_slli.gen_write_x0_test   ),
    asm_test( inst_slli.gen_random_test     ),
  ])
  def test_slli( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_slli_delays( s ):
    run_test( s.ProcType, inst_slli.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # lui
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lui.gen_basic_test    ) ,
    asm_test( inst_lui.gen_zero_imm_test     ),
    asm_test( inst_lui.gen_max_pos_imm_test  ),
    asm_test( inst_lui.gen_min_neg_imm_test  ),
    asm_test( inst_lui.gen_lower_bits_zero_test ),
    asm_test( inst_lui.gen_write_x0_test     ),
    asm_test( inst_lui.gen_random_test       ),
  ])
  def test_lui( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_lui_delays( s ):
    run_test( s.ProcType, inst_lui.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # auipc
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_auipc.gen_basic_test    ) ,
    asm_test( inst_auipc.gen_zero_imm_test    ),
    asm_test( inst_auipc.gen_max_pos_imm_test ),
    asm_test( inst_auipc.gen_min_neg_imm_test ),
    asm_test( inst_auipc.gen_write_x0_test    ),
    asm_test( inst_auipc.gen_random_test      ),
    asm_test( inst_auipc.gen_random_test_delays),
  ])
  def test_auipc( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_auipc_delays( s ):
    run_test( s.ProcType, inst_auipc.gen_random_test_delays, delays=True,
            cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # andi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_andi.gen_basic_test     ),
    asm_test( inst_andi.gen_dest_dep_test  ),
    asm_test( inst_andi.gen_src_dep_test   ),
    asm_test( inst_andi.gen_srcs_dest_test ),
    asm_test( inst_andi.gen_value_test     ),
    asm_test( inst_andi.gen_random_test    ),
  ])

  def test_andi( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_andi_delays( s ):
    run_test( s.ProcType, inst_andi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # xori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xori.gen_basic_test     ),
    asm_test( inst_xori.gen_dest_dep_test  ),
    asm_test( inst_xori.gen_src_dep_test   ),
    asm_test( inst_xori.gen_srcs_dest_test ),
    asm_test( inst_xori.gen_value_test     ),
    asm_test( inst_xori.gen_random_test    ),
  ])

  def test_xori( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_xori_delays( s ):
    run_test( s.ProcType, inst_xori.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srli.gen_basic_test     ),
    asm_test( inst_srli.gen_value_test     ),
    asm_test( inst_srli.gen_x0_test     ),
    asm_test( inst_srli.gen_hi_regs_edge_test     ),
    asm_test( inst_srli.gen_long_bypass_chain_test     ),
    asm_test( inst_srli.gen_random_test     ),
  ])

  def test_srli( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srli_delays( s ):
    run_test( s.ProcType, inst_srli.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )


