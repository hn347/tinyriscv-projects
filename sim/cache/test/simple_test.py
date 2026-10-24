#=========================================================================
# simple_test.py
#=========================================================================
# This is primarily just for playing around with little transaction
# sequences.

from pymtl3.stdlib.test_utils import run_sim

from cache.test.harness    import req, resp, TestHarness
from cache.CacheFL         import CacheFL
from cache.CacheBase       import CacheBase
from cache.CacheAlt        import CacheAlt

#----------------------------------------------------------------------
# test
#----------------------------------------------------------------------

def test( cmdline_opts ):

  msgs = [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in',  0x0, 0,   0,  0          ),
  ]

  th = TestHarness( CacheFL() )

  th.set_param("top.src.construct",  msgs=msgs[::2]  )
  th.set_param("top.sink.construct", msgs=msgs[1::2] )

  run_sim( th, cmdline_opts, duts=['cache'] )
  # run_sim( CacheSimple, cmdline_opts, duts=['cache'] )


