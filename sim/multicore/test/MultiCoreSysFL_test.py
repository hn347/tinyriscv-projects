#=========================================================================
# MultiCoreSysFL_test.py
#=========================================================================
# We apply select tests from lab2 to the multi core system. Keep in mind
# that different cores should not load/store the same word! If two cores
# load, modify, store different values to the same address there is no
# guarantee what the final correct result should be. This is a "race
# condition". You may need to exclude some of your SW tests from lab 2 if
# you cannot guarantee that a LW always produces the same value
# regardless of what the other cores are doing.

import pytest

from pymtl3 import *

from multicore.test.harness import asm_test
from multicore.test.harness import run_mcore_test as run_test

from multicore.MultiCoreSysFL import MultiCoreSysFL

from processor.test import inst_csr
from processor.test import inst_add
from processor.test import inst_mul
from processor.test import inst_addi
from processor.test import inst_lw
from processor.test import inst_sw
from processor.test import inst_bne
from processor.test import inst_jal

from multicore.test  import inst_csr_mcore

# Imported additional files from processor.test
from processor.test import inst_and
from processor.test import inst_andi
from processor.test import inst_auipc
from processor.test import inst_beq 
from processor.test import inst_bge
from processor.test import inst_blt
from processor.test import inst_bltu
from processor.test import inst_jalr
from processor.test import inst_lui
from processor.test import inst_or
from processor.test import inst_ori
from processor.test import inst_sll
from processor.test import inst_slli
from processor.test import inst_slt
from processor.test import inst_slti
from processor.test import inst_sra
from processor.test import inst_srai
from processor.test import inst_srl
from processor.test import inst_srli
from processor.test import inst_sub
from processor.test import inst_xor
from processor.test import inst_xori

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.SysType = MultiCoreSysFL

  #-----------------------------------------------------------------------
  # csr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_csr.gen_basic_test      ),
    asm_test( inst_csr.gen_bypass_test     ),
    asm_test( inst_csr.gen_value_test      ),
    asm_test( inst_csr.gen_random_test     ),
  ])
  def test_csr( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_csr_delays( s ):
    run_test( s.SysType, inst_csr.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # csr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_csr_mcore.gen_proc2mngr_sinks_test ),
    asm_test( inst_csr_mcore.gen_proc2mngr_srcs_test ),
    asm_test( inst_csr_mcore.gen_proc2mngr_srcs_sinks_test ),
    asm_test( inst_csr_mcore.gen_core_stats_test ),
  ])
  def test_csr_mcore( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # add
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_add.gen_basic_test     ),
    asm_test( inst_add.gen_dest_dep_test  ),
    asm_test( inst_add.gen_src0_dep_test  ),
    asm_test( inst_add.gen_src1_dep_test  ),
    asm_test( inst_add.gen_srcs_dep_test  ),
    asm_test( inst_add.gen_srcs_dest_test ),
    asm_test( inst_add.gen_value_test     ),
    asm_test( inst_add.gen_random_test    ),
  ])
  def test_add( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_add_delays( s ):
    run_test( s.SysType, inst_add.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # mul
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mul.gen_basic_test     ),
    asm_test( inst_mul.gen_x0_test        ),
    asm_test( inst_mul.gen_value_test     ),
    asm_test( inst_mul.gen_long_bypass_chain_test     ),
    asm_test( inst_mul.gen_random_test    ),
  ])
  def test_mul( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_mul_delays(s):
    run_test(s.SysType, inst_mul.gen_random_test, delays=True,
             cmdline_opts=s.__class__.cmdline_opts)

  #-----------------------------------------------------------------------
  # addi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_addi.gen_basic_test     ) ,
    asm_test( inst_addi.gen_zero_imm_test     ),
    asm_test( inst_addi.gen_neg_imm_test      ),
    asm_test( inst_addi.gen_large_pos_imm_test),
    asm_test( inst_addi.gen_write_x0_test     ),
    asm_test( inst_addi.gen_chain_dep_test    ),
    asm_test( inst_addi.gen_random_test       ),
    asm_test( inst_addi.bypass_logic_test) ,
  ])
  def test_addi( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_addi_delays( s ):
    run_test( s.SysType, inst_addi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # lw
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lw.gen_basic_test     ) ,
    asm_test( inst_lw.gen_dest_dep_test  ) ,
    asm_test( inst_lw.gen_base_dep_test  ) ,
    asm_test( inst_lw.gen_srcs_dest_test ) ,
    asm_test( inst_lw.gen_addr_test      ) ,
    asm_test( inst_lw.gen_random_test    ) ,
  ])
  def test_lw( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_lw_delays( s ):
    run_test( s.SysType, inst_lw.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sw
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sw.gen_basic_test     ),
    asm_test( inst_sw.gen_basic_test     ),
    asm_test( inst_sw.gen_pos_offset_test ),
    asm_test( inst_sw.gen_neg_offset_test ),
    asm_test( inst_sw.gen_overwrite_same_addr_test ),
    asm_test( inst_sw.gen_random_test     ),
  ])
  def test_sw( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sw_delays( s ):
    run_test( s.SysType, inst_sw.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bne
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bne.gen_basic_test             ),
    asm_test( inst_bne.gen_src0_dep_taken_test    ),
    asm_test( inst_bne.gen_src0_dep_nottaken_test ),
    asm_test( inst_bne.gen_src1_dep_taken_test    ),
    asm_test( inst_bne.gen_src1_dep_nottaken_test ),
    asm_test( inst_bne.gen_srcs_dep_taken_test    ),
    asm_test( inst_bne.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bne.gen_src0_eq_src1_test      ),
    asm_test( inst_bne.gen_value_test             ),
    asm_test( inst_bne.gen_random_test            ),
  ])
  def test_bne( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bne_delays( s ):
    run_test( s.SysType, inst_bne.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # jal
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jal.gen_basic_test              ),
    asm_test( inst_jal.gen_jal_quick_check_test    ),
    asm_test( inst_jal.gen_jump_forward_basic_test ),
    asm_test( inst_jal.gen_jump_back_basic_test    ),
    asm_test( inst_jal.gen_two_jumps_chain_test    ),
    asm_test( inst_jal.gen_linkaddr_capture_test   ),
    asm_test( inst_jal.gen_jal_data_hazard_test    ),
    asm_test( inst_jal.gen_jal_src_dep_test        ),
    asm_test( inst_jal.gen_jal_src_eq_dest_test    ),
    asm_test( inst_jal.gen_random_test             ),
  ])

  def test_jal( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_jal_delays( s ):
    run_test( s.SysType, inst_jal.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # and
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_and.gen_basic_test       ),
    asm_test( inst_and.gen_dest_dep_test    ),
    asm_test( inst_and.gen_src0_dep_test    ),
    asm_test( inst_and.gen_src1_dep_test    ),
    asm_test( inst_and.gen_srcs_dep_test    ),
    asm_test( inst_and.gen_srcs_dest_test   ),
    asm_test( inst_and.gen_value_test       ),
    asm_test( inst_and.gen_random_test      ),
  ])
  def test_and( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_and_delays( s ):
    run_test( s.SysType, inst_and.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # andi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_andi.gen_basic_test       ),
    asm_test( inst_andi.gen_dest_dep_test    ),
    asm_test( inst_andi.gen_src_dep_test     ),
    asm_test( inst_andi.gen_srcs_dest_test   ),
    asm_test( inst_andi.gen_value_test       ),
    asm_test( inst_andi.gen_random_test      ),
  ])
  def test_andi( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_andi_delays( s ):
    run_test( s.SysType, inst_andi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # auipc
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_auipc.gen_basic_test       ),
    asm_test( inst_auipc.gen_zero_imm_test    ),
    asm_test( inst_auipc.gen_max_pos_imm_test ),
    asm_test( inst_auipc.gen_min_neg_imm_test ),
    asm_test( inst_auipc.gen_write_x0_test    ),
    asm_test( inst_auipc.gen_random_test      ),
  ])
  def test_auipc( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_auipc_delays( s ):
    run_test( s.SysType, inst_auipc.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # beq
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_beq.gen_basic_test             ),
    asm_test( inst_beq.gen_src0_dep_taken_test   ),
    asm_test( inst_beq.gen_src0_dep_nottaken_test),
    asm_test( inst_beq.gen_src1_dep_taken_test   ),
    asm_test( inst_beq.gen_src1_dep_nottaken_test),
    asm_test( inst_beq.gen_random_test           ),
  ])
  def test_beq( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_beq_delays( s ):
    run_test( s.SysType, inst_beq.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    

  #-----------------------------------------------------------------------
  # bge
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bge.gen_basic_test             ),
    asm_test( inst_bge.gen_src0_dep_taken_test    ),
    asm_test( inst_bge.gen_src0_dep_nottaken_test ),
    asm_test( inst_bge.gen_src1_dep_taken_test    ),
    asm_test( inst_bge.gen_src1_dep_nottaken_test ),
    asm_test( inst_bge.gen_value_test             ),
    asm_test( inst_bge.gen_random_test            ),
  ])
  def test_bge( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bge_delays( s ):
    run_test( s.SysType, inst_bge.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # blt
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_blt.gen_basic_test             ),
    asm_test( inst_blt.gen_src0_dep_taken_test   ),
    asm_test( inst_blt.gen_src0_dep_nottaken_test),
    asm_test( inst_blt.gen_src1_dep_taken_test   ),
    asm_test( inst_blt.gen_src1_dep_nottaken_test),
    asm_test( inst_blt.gen_value_test            ),
    asm_test( inst_blt.gen_random_test           ),
  ])
  def test_blt( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_blt_delays( s ):
    run_test( s.SysType, inst_blt.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # bltu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bltu.gen_basic_test             ),
    asm_test( inst_bltu.gen_src0_dep_taken_test    ),
    asm_test( inst_bltu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bltu.gen_src1_dep_taken_test    ),
    asm_test( inst_bltu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bltu.gen_value_test             ),
    asm_test( inst_bltu.gen_random_test            ),
  ])
  def test_bltu( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bltu_delays( s ):
    run_test( s.SysType, inst_bltu.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # jalr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jalr.gen_basic_test        ) ,
    asm_test( inst_jalr.gen_value_test ),
    asm_test( inst_jalr.gen_immediate_test ),
    asm_test( inst_jalr.gen_reg_test ),
    asm_test( inst_jalr.gen_negative_offset_test ),
    asm_test( inst_jalr.gen_dest_dep_test ),
    asm_test( inst_jalr.gen_srcs_dest_test ),
    asm_test( inst_jalr.gen_random_test ),

  ])

  def test_jalr( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_jalr_delays( s ):
    run_test( s.SysType, inst_jalr.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # lui
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lui.gen_basic_test        ) ,
    asm_test( inst_lui.gen_zero_imm_test     ),
    asm_test( inst_lui.gen_max_pos_imm_test  ),
    asm_test( inst_lui.gen_min_neg_imm_test  ),
    asm_test( inst_lui.gen_lower_bits_zero_test ),
    asm_test( inst_lui.gen_write_x0_test     ),
    asm_test( inst_lui.gen_random_test       ),
  ])

  def test_lui( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_lui_delays( s ):
    run_test( s.SysType, inst_lui.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # or
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_or.gen_basic_test     ),
    asm_test( inst_or.gen_dest_dep_test  ),
    asm_test( inst_or.gen_src0_dep_test  ),
    asm_test( inst_or.gen_src1_dep_test  ),
    asm_test( inst_or.gen_srcs_dep_test  ),
    asm_test( inst_or.gen_srcs_dest_test ),
    asm_test( inst_or.gen_value_test     ),
    asm_test( inst_or.gen_random_test    ),
  ])

  def test_or( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_or_delays( s ):
    run_test( s.SysType, inst_or.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # ori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_ori.gen_basic_test     ),
    asm_test( inst_ori.gen_dest_dep_test  ) ,
    asm_test( inst_ori.gen_src_dep_test   ) ,
    asm_test( inst_ori.gen_srcs_dest_test ) ,
    asm_test( inst_ori.gen_value_test     ) ,
    asm_test( inst_ori.gen_random_test    ) ,
  ])

  def test_ori( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_ori_delays( s ):
    run_test( s.SysType, inst_ori.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # sll
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sll.gen_basic_test     ),
    asm_test( inst_sll.gen_dest_dep_test  ),
    asm_test( inst_sll.gen_src0_dep_test  ),
    asm_test( inst_sll.gen_src1_dep_test  ),
    asm_test( inst_sll.gen_srcs_dep_test  ),
    asm_test( inst_sll.gen_srcs_dest_test ),
    asm_test( inst_sll.gen_value_test     ),
    asm_test( inst_sll.gen_random_test    ),
  ])

  def test_sll( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sll_delays( s ):
    run_test( s.SysType, inst_sll.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # slli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slli.gen_basic_test     ),
    asm_test( inst_slli.gen_zero_shamt_test ),
    asm_test( inst_slli.gen_max_shamt_test  ),
    asm_test( inst_slli.gen_pattern_test    ),
    asm_test( inst_slli.gen_write_x0_test   ),
    asm_test( inst_slli.gen_random_test     ),
  ])

  def test_slli( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_slli_delays( s ):
    run_test( s.SysType, inst_slli.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # slt
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slt.gen_basic_test     ),
    asm_test( inst_slt.gen_mixed_signs_test     ),
    asm_test( inst_slt.gen_threshold_count_test     ),
    asm_test( inst_slt.gen_equal_false_sweep_test     ),
    asm_test( inst_slt.gen_write_after_write_test     ),
    asm_test( inst_slt.gen_hi_regs_edge_test     ),
    asm_test( inst_slt.gen_random_test)
  ])

  def test_slt( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_slt_delays( s ):
    run_test( s.SysType, inst_slt.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # slti
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slti.gen_basic_test     ),
    asm_test( inst_slti.gen_equal_test        ),
    asm_test( inst_slti.gen_neg_vs_pos_test   ),
    asm_test( inst_slti.gen_neg_vs_more_neg_test ),
    asm_test( inst_slti.gen_signbit_src_test  ),
    asm_test( inst_slti.gen_write_x0_test     ),
    asm_test( inst_slti.gen_random_test       ),
  ])

  def test_slti( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_slti_delays( s ):
    run_test( s.SysType, inst_slti.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # sra
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sra.gen_basic_test     ),
    asm_test( inst_sra.gen_value_test     ),
    asm_test( inst_sra.gen_x0_test        ),
    asm_test( inst_sra.gen_alias_test     ),
    asm_test( inst_sra.gen_hi_regs_edge_test     ),
    asm_test( inst_sra.gen_random_test    ),
  ])

  def test_sra( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sra_delays( s ):
    run_test( s.SysType, inst_sra.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srai
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srai.gen_basic_test         ),
    asm_test( inst_srai.gen_zero_shamt_test    ),
    asm_test( inst_srai.gen_max_shamt_pos_test ),
    asm_test( inst_srai.gen_max_shamt_neg_test ),
    asm_test( inst_srai.gen_pattern_test       ),
    asm_test( inst_srai.gen_random_test        ),
  ])

  def test_srai( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srai_delays( s ):
    run_test( s.SysType, inst_srai.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # srl
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srl.gen_basic_test     ),
    asm_test(inst_srl.gen_value_test      ),
    asm_test(inst_srl.gen_x0_test         ),
    asm_test(inst_srl.gen_alias_test      ),
    asm_test(inst_srl.gen_hi_regs_edge_test),
    asm_test(inst_srl.gen_long_bypass_chain_test),
    asm_test(inst_srl.gen_random_test     ),
  ])

  def test_srl( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srl_delays( s ):
    run_test( s.SysType, inst_srl.gen_random_test, delays=True,
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
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srli_delays( s ):
    run_test( s.SysType, inst_srli.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    
  #-----------------------------------------------------------------------
  # sub
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sub.gen_basic_test        ),
    asm_test( inst_sub.gen_dest_dep_test     ),
    asm_test( inst_sub.gen_src0_dep_test     ),
    asm_test( inst_sub.gen_src1_dep_test     ),
    asm_test( inst_sub.gen_srcs_dep_test     ),
    asm_test( inst_sub.gen_x0_test           ),
    asm_test( inst_sub.gen_value_test        ),
    asm_test( inst_sub.gen_long_bypass_chain_test     ),
    asm_test( inst_sub.gen_random_test       ),
  ])

  def test_sub( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sub_delays( s ):
    run_test( s.SysType, inst_sub.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
    

  #-----------------------------------------------------------------------
  # xor
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xor.gen_basic_test     ),
    asm_test( inst_xor.gen_dest_dep_test  ),
    asm_test( inst_xor.gen_src0_dep_test  ),
    asm_test( inst_xor.gen_src1_dep_test  ),
    asm_test( inst_xor.gen_srcs_dep_test  ),
    asm_test( inst_xor.gen_srcs_dest_test ),
    asm_test( inst_xor.gen_value_test     ),
    asm_test( inst_xor.gen_random_test    ),
  ])

  def test_xor( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_xor_delays( s ):
    run_test( s.SysType, inst_xor.gen_random_test, delays=True,
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
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_xori_delays( s ):
    run_test( s.SysType, inst_xori.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
