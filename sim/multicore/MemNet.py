#=========================================================================
# MemNet PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.mem.ifcs import MemRequesterIfc, MemResponderIfc
from pymtl3.stdlib.mem      import mk_mem_msg

class MemNet( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )

    s.cache2net = [ MemResponderIfc( MemReqType, MemRespType ) for _ in range(4) ]
    s.net2mem   = MemRequesterIfc( MemReqType, MemRespType )

