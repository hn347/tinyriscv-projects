#=========================================================================
# MultiCoreSysFL
#=========================================================================

from pymtl3 import *

from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.mem.ifcs    import MemRequesterIfc
from pymtl3.stdlib.mem         import mk_mem_msg

from processor.ProcFL  import ProcFL
from cache.CacheFL  import CacheFL
from multicore.MemNetFL import MemNetFL

class MultiCoreSysFL( Component ):

  def construct( s ):

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 128 )

    # Interface

    s.mngr2proc     = [ IStreamIfc( Bits32 ) for _ in range(4) ]
    s.proc2mngr     = [ OStreamIfc( Bits32 ) for _ in range(4) ]
    s.imem          = MemRequesterIfc( MemReqType, MemRespType )
    s.dmem          = MemRequesterIfc( MemReqType, MemRespType )

    s.stats_en      = OutPort()
    s.commit_inst   = OutPort(4)
    s.icache_access = OutPort(4)
    s.icache_miss   = OutPort(4)
    s.dcache_access = OutPort(4)
    s.dcache_miss   = OutPort(4)

    # Instantiate four processors, icaches, and dcaches

    s.procs   = [ ProcFL(num_cores=4) for _ in range(4) ]
    s.icaches = [ CacheFL() for _ in range(4) ]
    s.dcaches = [ CacheFL() for _ in range(4) ]

    # Instantiate two memory networks

    s.imemnet = MemNetFL()
    s.dmemnet = MemNetFL()

    # Connect proc2mngr and mngr2proc interfaces

    for i in range(4):
      s.mngr2proc[i] //= s.procs[i].mngr2proc
      s.proc2mngr[i] //= s.procs[i].proc2mngr

    # Connect processors <-> caches

    for i in range(4):
      s.procs[i].imem //= s.icaches[i].proc2cache
      s.procs[i].dmem //= s.dcaches[i].proc2cache

    # Connect caches <-> net

    for i in range(4):
      s.icaches[i].cache2mem //= s.imemnet.responders[i]
      s.dcaches[i].cache2mem //= s.dmemnet.responders[i]

    # Connect net <-> memory

    s.imem //= s.imemnet.requester
    s.dmem //= s.dmemnet.requester

    # Set the core ids

    for i in range(4):
      s.procs[i].core_id //= Bits32(i)

    # Bring the stats enable up to the top level

    s.stats_en      //= s.procs[0].stats_en
    s.commit_inst[0] //= s.procs[0].commit_inst
    s.commit_inst[1] //= s.procs[1].commit_inst
    s.commit_inst[2] //= s.procs[2].commit_inst
    s.commit_inst[3] //= s.procs[3].commit_inst
    s.icache_access //= 0
    s.icache_miss   //= 0
    s.dcache_access //= 0
    s.dcache_miss   //= 0

  def line_trace( s ):
    return "|".join([ proc.line_trace() for proc in s.procs ])
