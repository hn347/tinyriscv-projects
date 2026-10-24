#=========================================================================
# NetMsgAdapters_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.mem import mk_mem_msg, MemMsgType

from multicore.NetMsgAdapters import \
(
  CacheReq2NetMsg,  NetMsg2CacheReq,
  CacheResp2NetMsg, NetMsg2CacheResp,
  MemReq2NetMsg,    NetMsg2MemReq,
  MemResp2NetMsg,   NetMsg2MemResp
)

#-------------------------------------------------------------------------
# Cache Message Types
#-------------------------------------------------------------------------

CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32  )

def creq( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return CacheReqType( type_, opaque, addr, len, data )

def cresp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return CacheRespType( type_, opaque, test, len, data )

#-------------------------------------------------------------------------
# CacheReqTestHarness
#-------------------------------------------------------------------------

class CacheReqTestHarness( Component ):

  def construct( s, src_id=0 ):

    # Instantiate models

    s.src  = StreamSourceFL( CacheReqType )
    s.c2n  = CacheReq2NetMsg()
    s.n2c  = NetMsg2CacheReq()
    s.sink = StreamSinkFL( CacheReqType )

    # Connect

    s.c2n.src_id  //= src_id
    s.src.ostream //= s.c2n.istream
    s.c2n.ostream //= s.n2c.istream
    s.n2c.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    net_msg_str = s.c2n.ostream.line_trace()
    return f"{s.src.line_trace()} > ({net_msg_str}) > {s.sink.line_trace()}"

#-------------------------------------------------------------------------
# test_cachereq
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "src_id", [0,1,2,3] )
def test_cachereq( src_id, cmdline_opts ):

  th = CacheReqTestHarness(src_id)

  # Put the source id into the top two bits of an 8-bit value. Then we
  # can just or this in with the expected opaque field.

  s = Bits8(0)
  s[6:8] = src_id

  msgs = [

    creq( 'rd', 0x00, 0x1000, 0, 0          ), creq( 'rd', s | 0x00, 0x1000, 0, 0          ),
    creq( 'rd', 0x00, 0x1010, 0, 0          ), creq( 'rd', s | 0x10, 0x1010, 0, 0          ),
    creq( 'rd', 0x00, 0x1020, 0, 0          ), creq( 'rd', s | 0x20, 0x1020, 0, 0          ),
    creq( 'rd', 0x00, 0x1030, 0, 0          ), creq( 'rd', s | 0x30, 0x1030, 0, 0          ),

    creq( 'rd', 0x0a, 0x1000, 0, 0          ), creq( 'rd', s | 0x0a, 0x1000, 0, 0          ),
    creq( 'rd', 0x0b, 0x1010, 0, 0          ), creq( 'rd', s | 0x1b, 0x1010, 0, 0          ),
    creq( 'rd', 0x0c, 0x1020, 0, 0          ), creq( 'rd', s | 0x2c, 0x1020, 0, 0          ),
    creq( 'rd', 0x0d, 0x1030, 0, 0          ), creq( 'rd', s | 0x3d, 0x1030, 0, 0          ),

    creq( 'wr', 0x00, 0x1000, 0, 0x0a0a0a0a ), creq( 'wr', s | 0x00, 0x1000, 0, 0x0a0a0a0a ),
    creq( 'wr', 0x00, 0x1010, 0, 0x0b0b0b0b ), creq( 'wr', s | 0x10, 0x1010, 0, 0x0b0b0b0b ),
    creq( 'wr', 0x00, 0x1020, 0, 0x0c0c0c0c ), creq( 'wr', s | 0x20, 0x1020, 0, 0x0c0c0c0c ),
    creq( 'wr', 0x00, 0x1030, 0, 0x0d0d0d0d ), creq( 'wr', s | 0x30, 0x1030, 0, 0x0d0d0d0d ),

    creq( 'wr', 0x0a, 0x1000, 0, 0x0a0a0a0a ), creq( 'wr', s | 0x0a, 0x1000, 0, 0x0a0a0a0a ),
    creq( 'wr', 0x0b, 0x1010, 0, 0x0b0b0b0b ), creq( 'wr', s | 0x1b, 0x1010, 0, 0x0b0b0b0b ),
    creq( 'wr', 0x0c, 0x1020, 0, 0x0c0c0c0c ), creq( 'wr', s | 0x2c, 0x1020, 0, 0x0c0c0c0c ),
    creq( 'wr', 0x0d, 0x1030, 0, 0x0d0d0d0d ), creq( 'wr', s | 0x3d, 0x1030, 0, 0x0d0d0d0d ),

  ]

  th.set_param( "top.src.construct",  msgs=msgs[::2]  )
  th.set_param( "top.sink.construct", msgs=msgs[1::2] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['c2n','n2c'] )

#-------------------------------------------------------------------------
# CacheRespTestHarness
#-------------------------------------------------------------------------

class CacheRespTestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.src  = StreamSourceFL( CacheRespType )
    s.c2n  = CacheResp2NetMsg()
    s.n2c  = NetMsg2CacheResp()
    s.sink = StreamSinkFL( CacheRespType )

    # Connect

    s.src.ostream //= s.c2n.istream
    s.c2n.ostream //= s.n2c.istream
    s.n2c.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    net_msg_str = s.c2n.ostream.line_trace()
    return f"{s.src.line_trace()} > ({net_msg_str}) > {s.sink.line_trace()}"

#-------------------------------------------------------------------------
# test_cacheresp
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "src_id", [0,1,2,3] )
def test_cacheresp( src_id, cmdline_opts ):

  th = CacheRespTestHarness()

  # Put the source id into the top two bits of an 8-bit value. Then we
  # can just or this in with the expected opaque field.

  s = Bits8(0)
  s[6:8] = src_id

  msgs = [

    cresp( 'rd', s | 0x00, 0, 0, 0x0a0a0a0a ), cresp( 'rd', 0x00, 0, 0, 0x0a0a0a0a ),
    cresp( 'rd', s | 0x10, 0, 0, 0x0b0b0b0b ), cresp( 'rd', 0x00, 0, 0, 0x0b0b0b0b ),
    cresp( 'rd', s | 0x20, 0, 0, 0x0c0c0c0c ), cresp( 'rd', 0x00, 0, 0, 0x0c0c0c0c ),
    cresp( 'rd', s | 0x30, 0, 0, 0x0d0d0d0d ), cresp( 'rd', 0x00, 0, 0, 0x0d0d0d0d ),

    cresp( 'rd', s | 0x0a, 1, 0, 0x0a0a0a0a ), cresp( 'rd', 0x0a, 1, 0, 0x0a0a0a0a ),
    cresp( 'rd', s | 0x1b, 1, 0, 0x0b0b0b0b ), cresp( 'rd', 0x0b, 1, 0, 0x0b0b0b0b ),
    cresp( 'rd', s | 0x2c, 1, 0, 0x0c0c0c0c ), cresp( 'rd', 0x0c, 1, 0, 0x0c0c0c0c ),
    cresp( 'rd', s | 0x3d, 1, 0, 0x0d0d0d0d ), cresp( 'rd', 0x0d, 1, 0, 0x0d0d0d0d ),

    cresp( 'wr', s | 0x00, 0, 0, 0          ), cresp( 'wr', 0x00, 0, 0, 0          ),
    cresp( 'wr', s | 0x10, 0, 0, 0          ), cresp( 'wr', 0x00, 0, 0, 0          ),
    cresp( 'wr', s | 0x20, 0, 0, 0          ), cresp( 'wr', 0x00, 0, 0, 0          ),
    cresp( 'wr', s | 0x30, 0, 0, 0          ), cresp( 'wr', 0x00, 0, 0, 0          ),

    cresp( 'wr', s | 0x0a, 1, 0, 0          ), cresp( 'wr', 0x0a, 1, 0, 0          ),
    cresp( 'wr', s | 0x1b, 1, 0, 0          ), cresp( 'wr', 0x0b, 1, 0, 0          ),
    cresp( 'wr', s | 0x2c, 1, 0, 0          ), cresp( 'wr', 0x0c, 1, 0, 0          ),
    cresp( 'wr', s | 0x3d, 1, 0, 0          ), cresp( 'wr', 0x0d, 1, 0, 0          ),

  ]

  th.set_param( "top.src.construct",  msgs=msgs[::2]  )
  th.set_param( "top.sink.construct", msgs=msgs[1::2] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['c2n','n2c'] )

#-------------------------------------------------------------------------
# Memory Message Types
#-------------------------------------------------------------------------

MemReqType, MemRespType   = mk_mem_msg( 8, 32, 128 )

def mreq( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemReqType( type_, opaque, addr, len, data)

def mresp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemRespType( type_, opaque, test, len, data )

#-------------------------------------------------------------------------
# MemReqTestHarness
#-------------------------------------------------------------------------

class MemReqTestHarness( Component ):

  def construct( s, src_id=0 ):

    # Instantiate models

    s.src  = StreamSourceFL( MemReqType )
    s.c2n  = MemReq2NetMsg()
    s.n2c  = NetMsg2MemReq()
    s.sink = StreamSinkFL( MemReqType )

    # Connect

    s.c2n.src_id  //= src_id
    s.src.ostream //= s.c2n.istream
    s.c2n.ostream //= s.n2c.istream
    s.n2c.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    net_msg_str = s.c2n.ostream.line_trace()
    return f"{s.src.line_trace()} > ({net_msg_str}) > {s.sink.line_trace()}"

#-------------------------------------------------------------------------
# test_memreq
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "src_id", [0,1,2,3] )
def test_memreq( src_id, cmdline_opts ):

  th = MemReqTestHarness(src_id)

  # Put the source id into the top two bits of an 8-bit value. Then we
  # can just or this in with the expected opaque field.

  s = Bits8(0)
  s[6:8] = src_id

  msgs = [

    mreq( 'rd', 0x00, 0x1000, 0, 0          ), mreq( 'rd', s | 0x00, 0x1000, 0, 0          ),
    mreq( 'rd', 0x00, 0x1010, 0, 0          ), mreq( 'rd', s | 0x00, 0x1010, 0, 0          ),
    mreq( 'rd', 0x00, 0x1020, 0, 0          ), mreq( 'rd', s | 0x00, 0x1020, 0, 0          ),
    mreq( 'rd', 0x00, 0x1030, 0, 0          ), mreq( 'rd', s | 0x00, 0x1030, 0, 0          ),

    mreq( 'rd', 0x0a, 0x1000, 0, 0          ), mreq( 'rd', s | 0x0a, 0x1000, 0, 0          ),
    mreq( 'rd', 0x0b, 0x1010, 0, 0          ), mreq( 'rd', s | 0x0b, 0x1010, 0, 0          ),
    mreq( 'rd', 0x0c, 0x1020, 0, 0          ), mreq( 'rd', s | 0x0c, 0x1020, 0, 0          ),
    mreq( 'rd', 0x0d, 0x1030, 0, 0          ), mreq( 'rd', s | 0x0d, 0x1030, 0, 0          ),

    mreq( 'wr', 0x00, 0x1000, 0, 0x0a0a0a0a ), mreq( 'wr', s | 0x00, 0x1000, 0, 0x0a0a0a0a ),
    mreq( 'wr', 0x00, 0x1010, 0, 0x0b0b0b0b ), mreq( 'wr', s | 0x00, 0x1010, 0, 0x0b0b0b0b ),
    mreq( 'wr', 0x00, 0x1020, 0, 0x0c0c0c0c ), mreq( 'wr', s | 0x00, 0x1020, 0, 0x0c0c0c0c ),
    mreq( 'wr', 0x00, 0x1030, 0, 0x0d0d0d0d ), mreq( 'wr', s | 0x00, 0x1030, 0, 0x0d0d0d0d ),

    mreq( 'wr', 0x0a, 0x1000, 0, 0x0a0a0a0a ), mreq( 'wr', s | 0x0a, 0x1000, 0, 0x0a0a0a0a ),
    mreq( 'wr', 0x0b, 0x1010, 0, 0x0b0b0b0b ), mreq( 'wr', s | 0x0b, 0x1010, 0, 0x0b0b0b0b ),
    mreq( 'wr', 0x0c, 0x1020, 0, 0x0c0c0c0c ), mreq( 'wr', s | 0x0c, 0x1020, 0, 0x0c0c0c0c ),
    mreq( 'wr', 0x0d, 0x1030, 0, 0x0d0d0d0d ), mreq( 'wr', s | 0x0d, 0x1030, 0, 0x0d0d0d0d ),

  ]

  th.set_param( "top.src.construct",  msgs=msgs[::2]  )
  th.set_param( "top.sink.construct", msgs=msgs[1::2] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['c2n','n2c'] )

#-------------------------------------------------------------------------
# MemRespTestHarness
#-------------------------------------------------------------------------

class MemRespTestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.src  = StreamSourceFL( MemRespType )
    s.c2n  = MemResp2NetMsg()
    s.n2c  = NetMsg2MemResp()
    s.sink = StreamSinkFL( MemRespType )

    # Connect

    s.src.ostream //= s.c2n.istream
    s.c2n.ostream //= s.n2c.istream
    s.n2c.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    net_msg_str = s.c2n.ostream.line_trace()
    return f"{s.src.line_trace()} > ({net_msg_str}) > {s.sink.line_trace()}"

#-------------------------------------------------------------------------
# test_memresp
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "src_id", [0,1,2,3] )
def test_memresp( src_id, cmdline_opts ):

  th = MemRespTestHarness()

  # Put the source id into the top two bits of an 8-bit value. Then we
  # can just or this in with the expected opaque field.

  s = Bits8(0)
  s[6:8] = src_id

  msgs = [

    mresp( 'rd', s | 0x00, 0, 0, 0x0a0a0a0a ), mresp( 'rd', 0x00, 0, 0, 0x0a0a0a0a ),
    mresp( 'rd', s | 0x00, 0, 0, 0x0b0b0b0b ), mresp( 'rd', 0x00, 0, 0, 0x0b0b0b0b ),
    mresp( 'rd', s | 0x00, 0, 0, 0x0c0c0c0c ), mresp( 'rd', 0x00, 0, 0, 0x0c0c0c0c ),
    mresp( 'rd', s | 0x00, 0, 0, 0x0d0d0d0d ), mresp( 'rd', 0x00, 0, 0, 0x0d0d0d0d ),

    mresp( 'rd', s | 0x0a, 1, 0, 0x0a0a0a0a ), mresp( 'rd', 0x0a, 1, 0, 0x0a0a0a0a ),
    mresp( 'rd', s | 0x0b, 1, 0, 0x0b0b0b0b ), mresp( 'rd', 0x0b, 1, 0, 0x0b0b0b0b ),
    mresp( 'rd', s | 0x0c, 1, 0, 0x0c0c0c0c ), mresp( 'rd', 0x0c, 1, 0, 0x0c0c0c0c ),
    mresp( 'rd', s | 0x0d, 1, 0, 0x0d0d0d0d ), mresp( 'rd', 0x0d, 1, 0, 0x0d0d0d0d ),

    mresp( 'wr', s | 0x00, 0, 0, 0          ), mresp( 'wr', 0x00, 0, 0, 0          ),
    mresp( 'wr', s | 0x00, 0, 0, 0          ), mresp( 'wr', 0x00, 0, 0, 0          ),
    mresp( 'wr', s | 0x00, 0, 0, 0          ), mresp( 'wr', 0x00, 0, 0, 0          ),
    mresp( 'wr', s | 0x00, 0, 0, 0          ), mresp( 'wr', 0x00, 0, 0, 0          ),

    mresp( 'wr', s | 0x0a, 1, 0, 0          ), mresp( 'wr', 0x0a, 1, 0, 0          ),
    mresp( 'wr', s | 0x0b, 1, 0, 0          ), mresp( 'wr', 0x0b, 1, 0, 0          ),
    mresp( 'wr', s | 0x0c, 1, 0, 0          ), mresp( 'wr', 0x0c, 1, 0, 0          ),
    mresp( 'wr', s | 0x0d, 1, 0, 0          ), mresp( 'wr', 0x0d, 1, 0, 0          ),

  ]

  th.set_param( "top.src.construct",  msgs=msgs[::2]  )
  th.set_param( "top.sink.construct", msgs=msgs[1::2] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['c2n','n2c'] )

