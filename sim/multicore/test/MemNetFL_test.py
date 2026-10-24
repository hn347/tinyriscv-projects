#=========================================================================
# MemNetFL_test
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.mem import MemoryFL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.test_utils import run_sim

from multicore.MemNetFL import MemNetFL

#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

MemReqType, MemRespType   = mk_mem_msg( 8, 32, 128 )

def req( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemReqType( type_, opaque, addr, len, data)

def resp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemRespType( type_, opaque, test, len, data )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )

    # Instantiate models

    s.srcs  = [ StreamSourceFL( MemReqType ) for _ in range(4) ]
    s.sinks = [ StreamSinkFL( MemRespType ) for _ in range(4) ]
    s.net   = MemNetFL()
    s.mem   = MemoryFL( 1, [(MemReqType,MemRespType)] )

    # Connect

    for src,responder in zip(s.srcs,s.net.responders):
      connect( src.ostream, responder.reqstream )

    for sink,responder in zip(s.sinks,s.net.responders):
      connect( sink.istream, responder.respstream )

    s.net.requester //= s.mem.ifc[0]

  def done( s ):

    for src,sink in zip(s.srcs,s.sinks):
      if not src.done() or not sink.done():
        return False

    return True

  def line_trace( s ):

    src_linetrace  = "|".join([src.line_trace()  for src  in s.srcs  ])
    sink_linetrace = "|".join([sink.line_trace() for sink in s.sinks ])

    return src_linetrace + " > " + s.mem.line_trace() + " > " + sink_linetrace

#----------------------------------------------------------------------
# test
#----------------------------------------------------------------------

def test( cmdline_opts ):

  msgs0 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'wr',  0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
  ]

  msgs1 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x1, 0x2000, 0, 0xdeadbeef ), resp( 'wr',  0x1, 0,   0,  0          ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
  ]

  msgs2 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x2, 0x3000, 0, 0xdeadbeef ), resp( 'wr',  0x2, 0,   0,  0          ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
  ]

  msgs3 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x3, 0x3000, 0, 0xdeadbeef ), resp( 'wr',  0x3, 0,   0,  0          ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
  ]

  th = TestHarness()

  th.set_param("top.srcs[0].construct",  msgs=msgs0[::2]  )
  th.set_param("top.sinks[0].construct", msgs=msgs0[1::2] )
  th.set_param("top.srcs[1].construct",  msgs=msgs1[::2]  )
  th.set_param("top.sinks[1].construct", msgs=msgs1[1::2] )
  th.set_param("top.srcs[2].construct",  msgs=msgs2[::2]  )
  th.set_param("top.sinks[2].construct", msgs=msgs2[1::2] )
  th.set_param("top.srcs[3].construct",  msgs=msgs3[::2]  )
  th.set_param("top.sinks[3].construct", msgs=msgs3[1::2] )

  run_sim( th, cmdline_opts, duts=['net'] )

#----------------------------------------------------------------------
# test_arbitration
#----------------------------------------------------------------------

def test_arbitration( cmdline_opts ):

  msgs0 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'wr',  0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd',  0x0, 0,   0,  0xdeadbeef ),
  ]

  msgs1 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x1, 0x2000, 0, 0xdeadbeef ), resp( 'wr',  0x1, 0,   0,  0          ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x2000, 0, 0          ), resp( 'rd',  0x1, 0,   0,  0xdeadbeef ),
  ]

  msgs2 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x2, 0x3000, 0, 0xdeadbeef ), resp( 'wr',  0x2, 0,   0,  0          ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x3000, 0, 0          ), resp( 'rd',  0x2, 0,   0,  0xdeadbeef ),
  ]

  msgs3 = [
    #    type  opq  addr    len data                type  opq  test len data
    req( 'wr', 0x3, 0x3000, 0, 0xdeadbeef ), resp( 'wr',  0x3, 0,   0,  0          ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x3000, 0, 0          ), resp( 'rd',  0x3, 0,   0,  0xdeadbeef ),
  ]

  th = TestHarness()

  th.set_param("top.srcs[0].construct",  msgs=msgs0[::2]  )
  th.set_param("top.sinks[0].construct", msgs=msgs0[1::2] )
  th.set_param("top.srcs[1].construct",  msgs=msgs1[::2]  )
  th.set_param("top.sinks[1].construct", msgs=msgs1[1::2] )
  th.set_param("top.srcs[2].construct",  msgs=msgs2[::2]  )
  th.set_param("top.sinks[2].construct", msgs=msgs2[1::2] )
  th.set_param("top.srcs[3].construct",  msgs=msgs3[::2]  )
  th.set_param("top.sinks[3].construct", msgs=msgs3[1::2] )

  run_sim( th, cmdline_opts, duts=['net'] )

