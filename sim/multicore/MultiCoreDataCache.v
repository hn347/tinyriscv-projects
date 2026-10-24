//========================================================================
// MultiCoreDataCache
//========================================================================
// The cache provides four cache interfaces, one memory interface and
// includes a cache network, four data cache banks, and one memory
// network.

`ifndef MULTICORE_MULTI_CORE_DATA_CACHE_V
`define MULTICORE_MULTI_CORE_DATA_CACHE_V

`include "vc/mem-msgs.v"
`include "vc/net-msgs.v"
`include "vc/trace.v"

`include "multicore/CacheNet.v"
`include "multicore/MemNet.v"
`include "cache/CacheAlt.v"

module multicore_MultiCoreDataCache
(
  input  logic          clk,
  input  logic          reset,

  // Processor <-> Cache Interfaces

  input  mem_req_4B_t   proc2cache_reqstream_msg  [4],
  input  logic          proc2cache_reqstream_val  [4],
  output logic          proc2cache_reqstream_rdy  [4],

  output mem_resp_4B_t  proc2cache_respstream_msg [4],
  output logic          proc2cache_respstream_val [4],
  input  logic          proc2cache_respstream_rdy [4],

  // Cache <-> Mem Interface

  output mem_req_16B_t  cache2mem_reqstream_msg,
  output logic          cache2mem_reqstream_val,
  input  logic          cache2mem_reqstream_rdy,

  input  mem_resp_16B_t cache2mem_respstream_msg,
  input  logic          cache2mem_respstream_val,
  output logic          cache2mem_respstream_rdy
);

  //----------------------------------------------------------------------
  // CacheNet
  //----------------------------------------------------------------------

  mem_req_4B_t  cachenet2dcache_reqstream_msg  [4];
  logic         cachenet2dcache_reqstream_val  [4];
  logic         cachenet2dcache_reqstream_rdy  [4];

  mem_resp_4B_t cachenet2dcache_respstream_msg [4];
  logic         cachenet2dcache_respstream_val [4];
  logic         cachenet2dcache_respstream_rdy [4];

  multicore_CacheNet cachenet
  (
    .clk                      (clk),
    .reset                    (reset),

    .proc2net_reqstream_msg   (proc2cache_reqstream_msg),
    .proc2net_reqstream_val   (proc2cache_reqstream_val),
    .proc2net_reqstream_rdy   (proc2cache_reqstream_rdy),

    .proc2net_respstream_msg  (proc2cache_respstream_msg),
    .proc2net_respstream_val  (proc2cache_respstream_val),
    .proc2net_respstream_rdy  (proc2cache_respstream_rdy),

    .net2cache_reqstream_msg  (cachenet2dcache_reqstream_msg),
    .net2cache_reqstream_val  (cachenet2dcache_reqstream_val),
    .net2cache_reqstream_rdy  (cachenet2dcache_reqstream_rdy),

    .net2cache_respstream_msg (cachenet2dcache_respstream_msg),
    .net2cache_respstream_val (cachenet2dcache_respstream_val),
    .net2cache_respstream_rdy (cachenet2dcache_respstream_rdy)
  );

  //----------------------------------------------------------------------
  // Cache Banks
  //----------------------------------------------------------------------

  mem_req_16B_t  dcache2memnet_reqstream_msg  [4];
  logic          dcache2memnet_reqstream_val  [4];
  logic          dcache2memnet_reqstream_rdy  [4];

  mem_resp_16B_t dcache2memnet_respstream_msg [4];
  logic          dcache2memnet_respstream_val [4];
  logic          dcache2memnet_respstream_rdy [4];

  genvar i;
  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: DCACHE

    cache_CacheAlt
    #(
      .p_num_banks               (4)
    )
    dcache
    (
      .clk                       (clk),
      .reset                     (reset),

      .proc2cache_reqstream_msg  (cachenet2dcache_reqstream_msg[i]),
      .proc2cache_reqstream_val  (cachenet2dcache_reqstream_val[i]),
      .proc2cache_reqstream_rdy  (cachenet2dcache_reqstream_rdy[i]),

      .proc2cache_respstream_msg (cachenet2dcache_respstream_msg[i]),
      .proc2cache_respstream_val (cachenet2dcache_respstream_val[i]),
      .proc2cache_respstream_rdy (cachenet2dcache_respstream_rdy[i]),

      .cache2mem_reqstream_msg   (dcache2memnet_reqstream_msg[i]),
      .cache2mem_reqstream_val   (dcache2memnet_reqstream_val[i]),
      .cache2mem_reqstream_rdy   (dcache2memnet_reqstream_rdy[i]),

      .cache2mem_respstream_msg  (dcache2memnet_respstream_msg[i]),
      .cache2mem_respstream_val  (dcache2memnet_respstream_val[i]),
      .cache2mem_respstream_rdy  (dcache2memnet_respstream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // MemNet
  //----------------------------------------------------------------------

  multicore_MemNet memnet
  (
    .clk                      (clk),
    .reset                    (reset),

    .cache2net_reqstream_msg  (dcache2memnet_reqstream_msg),
    .cache2net_reqstream_val  (dcache2memnet_reqstream_val),
    .cache2net_reqstream_rdy  (dcache2memnet_reqstream_rdy),

    .cache2net_respstream_msg (dcache2memnet_respstream_msg),
    .cache2net_respstream_val (dcache2memnet_respstream_val),
    .cache2net_respstream_rdy (dcache2memnet_respstream_rdy),

    .net2mem_reqstream_msg    (cache2mem_reqstream_msg),
    .net2mem_reqstream_val    (cache2mem_reqstream_val),
    .net2mem_reqstream_rdy    (cache2mem_reqstream_rdy),

    .net2mem_respstream_msg   (cache2mem_respstream_msg),
    .net2mem_respstream_val   (cache2mem_respstream_val),
    .net2mem_respstream_rdy   (cache2mem_respstream_rdy)
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    cachenet.line_trace( trace_str );
    DCACHE[0].dcache.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    DCACHE[1].dcache.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    DCACHE[2].dcache.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    DCACHE[3].dcache.line_trace( trace_str );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* MULTICORE_MULTI_CORE_DATA_CACHE_V */
