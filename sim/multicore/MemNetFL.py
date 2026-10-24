#=========================================================================
# MemNetFL
#=========================================================================

from collections import deque

from pymtl3 import *

from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream      import IStreamDeqAdapterFL, OStreamEnqAdapterFL
from pymtl3.stdlib.mem.ifcs    import MemRequesterIfc, MemResponderIfc
from pymtl3.stdlib.mem         import mk_mem_msg

from processor.ProcFL import ProcFL
from cache.CacheFL import CacheFL

class MemNetFL( Component ):

  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )

    # Interface

    s.responders = [ MemResponderIfc( MemReqType, MemRespType ) for _ in range(4) ]
    s.requester  = MemRequesterIfc( MemReqType, MemRespType )

    # Cache Adapters

    s.cache_req_qs  = [ IStreamDeqAdapterFL( MemReqType ) for _ in range(4) ]
    s.cache_resp_qs = [ OStreamEnqAdapterFL( MemRespType ) for _ in range(4) ]

    for responder,cache_req_q in zip(s.responders,s.cache_req_qs):
      connect( responder.reqstream, cache_req_q.istream )

    for responder,cache_resp_q in zip(s.responders,s.cache_resp_qs):
      connect( responder.respstream, cache_resp_q.ostream )

    # Memory Adapters

    s.mem_req_q  = OStreamEnqAdapterFL( MemReqType )
    s.mem_resp_q = IStreamDeqAdapterFL( MemRespType )

    connect( s.requester.reqstream,  s.mem_req_q.ostream  )
    connect( s.requester.respstream, s.mem_resp_q.istream )

    # Helper state tracking

    dest_q   = deque() # track where responses should go
    priority = [ 0, 1, 2, 3 ]

    # Logic

    @update_once
    def logic():

      for idx in priority:
        if s.cache_req_qs[idx].deq.rdy() and s.mem_req_q.enq.rdy():
          s.mem_req_q.enq( s.cache_req_qs[idx].deq() )
          dest_q.append(idx)
          priority.remove(idx)
          priority.append(idx)

      if s.mem_resp_q.deq.rdy():
        dest_idx = dest_q[0]
        if s.cache_resp_qs[dest_idx].enq.rdy():
          s.cache_resp_qs[dest_idx].enq( s.mem_resp_q.deq() )
          dest_q.popleft()

