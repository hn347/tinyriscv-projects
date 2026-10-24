#=========================================================================
# CacheNet PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.mem.ifcs import MemRequesterIfc, MemResponderIfc
from pymtl3.stdlib.mem      import mk_mem_msg

class CacheNet( VerilogPlaceholder, Component ):
  def construct( s ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )

    s.proc2net  = [ MemResponderIfc( CacheReqType, CacheRespType ) for _ in range(4) ]
    s.net2cache = [ MemRequesterIfc( CacheReqType, CacheRespType ) for _ in range(4) ]

