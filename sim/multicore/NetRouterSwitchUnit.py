#=========================================================================
# NetRouterSwitchUnit PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from multicore.NetMsg import mk_net_msg

class NetRouterSwitchUnit( VerilogPlaceholder, Component ):
  def construct( s, p_msg_nbits=44 ):

    NetMsgType = mk_net_msg( p_msg_nbits-12 )

    s.istream = [ IStreamIfc( NetMsgType ) for _ in range(3) ]
    s.ostream = OStreamIfc( NetMsgType )

