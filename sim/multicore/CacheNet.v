//========================================================================
// Cache Network
//========================================================================
// This network conects the four processor data memory interfaces to the
// four data cache banks. It includes a network for the requests, a
// network for the responses, and appropriate adapters to convert memory
// messages into network messages.

`ifndef MULTICORE_CACHE_NET_V
`define MULTICORE_CACHE_NET_V

`include "vc/mem-msgs.v"
`include "vc/net-msgs.v"
`include "vc/trace.v"

`include "multicore/Net.v"
`include "multicore/NetMsgAdapters.v"

module multicore_CacheNet
(
  input  logic          clk,
  input  logic          reset,

  // Processor <-> Net Interface

  input  mem_req_4B_t   proc2net_reqstream_msg   [4],
  input  logic          proc2net_reqstream_val   [4],
  output logic          proc2net_reqstream_rdy   [4],

  output mem_resp_4B_t  proc2net_respstream_msg  [4],
  output logic          proc2net_respstream_val  [4],
  input  logic          proc2net_respstream_rdy  [4],

  // Net <-> Cache Interface

  output mem_req_4B_t   net2cache_reqstream_msg  [4],
  output logic          net2cache_reqstream_val  [4],
  input  logic          net2cache_reqstream_rdy  [4],

  input  mem_resp_4B_t  net2cache_respstream_msg [4],
  input  logic          net2cache_respstream_val [4],
  output logic          net2cache_respstream_rdy [4]
);

  //----------------------------------------------------------------------
  // CacheReq2NetMsg Adapters
  //----------------------------------------------------------------------

  localparam cachereqnet_msg_size = 12+$bits(mem_req_4B_t);

  logic [cachereqnet_msg_size-1:0] cachereq2netmsg_ostream_msg [4];
  logic                            cachereq2netmsg_ostream_val [4];
  logic                            cachereq2netmsg_ostream_rdy [4];

  genvar i;
  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: CACHEREQ2NETMSG

    multicore_CacheReq2NetMsg cachereq2netmsg
    (
      .src_id      (i[1:0]),

      .istream_msg (proc2net_reqstream_msg[i]),
      .istream_val (proc2net_reqstream_val[i]),
      .istream_rdy (proc2net_reqstream_rdy[i]),

      .ostream_msg (cachereq2netmsg_ostream_msg[i]),
      .ostream_val (cachereq2netmsg_ostream_val[i]),
      .ostream_rdy (cachereq2netmsg_ostream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // CacheReqNet
  //----------------------------------------------------------------------

  logic [cachereqnet_msg_size-1:0] cachereqnet_ostream_msg [4];
  logic                            cachereqnet_ostream_val [4];
  logic                            cachereqnet_ostream_rdy [4];

  multicore_Net
  #(
    .p_msg_nbits (cachereqnet_msg_size)
  )
  cachereqnet
  (
    .clk         (clk),
    .reset       (reset),

    .istream_msg (cachereq2netmsg_ostream_msg),
    .istream_val (cachereq2netmsg_ostream_val),
    .istream_rdy (cachereq2netmsg_ostream_rdy),

    .ostream_msg (cachereqnet_ostream_msg),
    .ostream_val (cachereqnet_ostream_val),
    .ostream_rdy (cachereqnet_ostream_rdy)
  );

  //----------------------------------------------------------------------
  // NetMsg2CacheReq Adapters
  //----------------------------------------------------------------------

  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: NETMSG2CACHEREQ

    multicore_NetMsg2CacheReq netmsg2cachereq
    (
      .istream_msg (cachereqnet_ostream_msg[i]),
      .istream_val (cachereqnet_ostream_val[i]),
      .istream_rdy (cachereqnet_ostream_rdy[i]),

      .ostream_msg (net2cache_reqstream_msg[i]),
      .ostream_val (net2cache_reqstream_val[i]),
      .ostream_rdy (net2cache_reqstream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // CacheResp2NetMsg Adapters
  //----------------------------------------------------------------------

  localparam cacherespnet_msg_size = 12+$bits(mem_resp_4B_t);

  logic [cacherespnet_msg_size-1:0] cacheresp2netmsg_ostream_msg [4];
  logic                             cacheresp2netmsg_ostream_val [4];
  logic                             cacheresp2netmsg_ostream_rdy [4];

  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: CACHERESP2NETMSG

    multicore_CacheResp2NetMsg cacheresp2netmsg
    (
      .istream_msg (net2cache_respstream_msg[i]),
      .istream_val (net2cache_respstream_val[i]),
      .istream_rdy (net2cache_respstream_rdy[i]),

      .ostream_msg (cacheresp2netmsg_ostream_msg[i]),
      .ostream_val (cacheresp2netmsg_ostream_val[i]),
      .ostream_rdy (cacheresp2netmsg_ostream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // CacheRespNet
  //----------------------------------------------------------------------

  logic [cacherespnet_msg_size-1:0] cacherespnet_ostream_msg [4];
  logic                             cacherespnet_ostream_val [4];
  logic                             cacherespnet_ostream_rdy [4];

  multicore_Net
  #(
    .p_msg_nbits (cacherespnet_msg_size)
  )
  cacherespnet
  (
    .clk         (clk),
    .reset       (reset),

    .istream_msg (cacheresp2netmsg_ostream_msg),
    .istream_val (cacheresp2netmsg_ostream_val),
    .istream_rdy (cacheresp2netmsg_ostream_rdy),

    .ostream_msg (cacherespnet_ostream_msg),
    .ostream_val (cacherespnet_ostream_val),
    .ostream_rdy (cacherespnet_ostream_rdy)
  );

  //----------------------------------------------------------------------
  // NetMsg2CacheResp Adapters
  //----------------------------------------------------------------------

  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: NETMSG2CACHERESP

    multicore_NetMsg2CacheResp netmsg2cacheresp
    (
      .istream_msg (cacherespnet_ostream_msg[i]),
      .istream_val (cacherespnet_ostream_val[i]),
      .istream_rdy (cacherespnet_ostream_rdy[i]),

      .ostream_msg (proc2net_respstream_msg[i]),
      .ostream_val (proc2net_respstream_val[i]),
      .ostream_rdy (proc2net_respstream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    vc_trace.append_str( trace_str, "{" );
    cachereqnet.line_trace( trace_str );
    vc_trace.append_str( trace_str, "}{" );
    cacherespnet.line_trace( trace_str );
    vc_trace.append_str( trace_str, "}" );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* MULTICORE_NET_V */
