#=========================================================================
# NetMsgAdapters PyMTL3 Wrappers
#=========================================================================

from os import path

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from pymtl3.stdlib.mem import mk_mem_msg
from multicore.NetMsg   import mk_net_msg

#-------------------------------------------------------------------------
# CacheReq2NetMsg
#-------------------------------------------------------------------------

class CacheReq2NetMsg( VerilogPlaceholder, Component ):
  def construct( s ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )
    NetMsgType = mk_net_msg( CacheReqType.nbits )

    s.src_id  = InPort(2)
    s.istream = IStreamIfc( CacheReqType )
    s.ostream = OStreamIfc( NetMsgType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# NetMsg2CacheReq
#-------------------------------------------------------------------------

class NetMsg2CacheReq( VerilogPlaceholder, Component ):
  def construct( s ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )
    NetMsgType = mk_net_msg( CacheReqType.nbits )

    s.istream = IStreamIfc( NetMsgType )
    s.ostream = OStreamIfc( CacheReqType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# CacheResp2NetMsg
#-------------------------------------------------------------------------

class CacheResp2NetMsg( VerilogPlaceholder, Component ):
  def construct( s ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )
    NetMsgType = mk_net_msg( CacheRespType.nbits )

    s.istream = IStreamIfc( CacheRespType )
    s.ostream = OStreamIfc( NetMsgType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# NetMsg2CacheResp
#-------------------------------------------------------------------------

class NetMsg2CacheResp( VerilogPlaceholder, Component ):
  def construct( s ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )
    NetMsgType = mk_net_msg( CacheRespType.nbits )

    s.istream = IStreamIfc( NetMsgType )
    s.ostream = OStreamIfc( CacheRespType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# MemReq2NetMsg
#-------------------------------------------------------------------------

class MemReq2NetMsg( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )
    NetMsgType = mk_net_msg( MemReqType.nbits )

    s.src_id  = InPort(2)
    s.istream = IStreamIfc( MemReqType )
    s.ostream = OStreamIfc( NetMsgType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# NetMsg2MemReq
#-------------------------------------------------------------------------

class NetMsg2MemReq( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )
    NetMsgType = mk_net_msg( MemReqType.nbits )

    s.istream = IStreamIfc( NetMsgType )
    s.ostream = OStreamIfc( MemReqType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# MemResp2NetMsg
#-------------------------------------------------------------------------

class MemResp2NetMsg( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )
    NetMsgType = mk_net_msg( MemRespType.nbits )

    s.istream = IStreamIfc( MemRespType )
    s.ostream = OStreamIfc( NetMsgType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

#-------------------------------------------------------------------------
# NetMsg2MemResp
#-------------------------------------------------------------------------

class NetMsg2MemResp( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )
    NetMsgType = mk_net_msg( MemRespType.nbits )

    s.istream = IStreamIfc( NetMsgType )
    s.ostream = OStreamIfc( MemRespType )

    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/NetMsgAdapters.v' )

