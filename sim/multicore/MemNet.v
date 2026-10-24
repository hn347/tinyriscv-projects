//========================================================================
// Mem Network
//========================================================================
// This network conects the four memory interfaces from the caches (i.e.,
// for refill/eviction) to a single main memory interface. It includes a
// network for the requests, a network for the responses, and appropriate
// adapters to convert memory messages into network messages.

`ifndef MULTICORE_MEM_NET_V
`define MULTICORE_MEM_NET_V

`include "vc/mem-msgs.v"
`include "vc/net-msgs.v"
`include "vc/trace.v"

`include "multicore/Net.v"
`include "multicore/NetMsgAdapters.v"

module multicore_MemNet
(
  input  logic          clk,
  input  logic          reset,

  // Cache <-> Net Interface

  input  mem_req_16B_t  cache2net_reqstream_msg  [4],
  input  logic          cache2net_reqstream_val  [4],
  output logic          cache2net_reqstream_rdy  [4],

  output mem_resp_16B_t cache2net_respstream_msg [4],
  output logic          cache2net_respstream_val [4],
  input  logic          cache2net_respstream_rdy [4],

  // Net <-> Mem Interface

  output mem_req_16B_t  net2mem_reqstream_msg,
  output logic          net2mem_reqstream_val,
  input  logic          net2mem_reqstream_rdy,

  input  mem_resp_16B_t net2mem_respstream_msg,
  input  logic          net2mem_respstream_val,
  output logic          net2mem_respstream_rdy
);

  //----------------------------------------------------------------------
  // MemReq2NetMsg Adapters
  //----------------------------------------------------------------------

  localparam memreqnet_msg_size = 12+$bits(mem_req_16B_t);

  logic [memreqnet_msg_size-1:0] memreq2netmsg_ostream_msg [4];
  logic                          memreq2netmsg_ostream_val [4];
  logic                          memreq2netmsg_ostream_rdy [4];

  genvar i;
  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: MEMREQ2NETMSG

    multicore_MemReq2NetMsg memreq2netmsg
    (
      .src_id      (i[1:0]),

      .istream_msg (cache2net_reqstream_msg[i]),
      .istream_val (cache2net_reqstream_val[i]),
      .istream_rdy (cache2net_reqstream_rdy[i]),

      .ostream_msg (memreq2netmsg_ostream_msg[i]),
      .ostream_val (memreq2netmsg_ostream_val[i]),
      .ostream_rdy (memreq2netmsg_ostream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // MemReqNet
  //----------------------------------------------------------------------

  logic [memreqnet_msg_size-1:0] memreqnet_ostream_msg [4];
  logic                          memreqnet_ostream_val [4];
  logic                          memreqnet_ostream_rdy [4];

  multicore_Net
  #(
    .p_msg_nbits (memreqnet_msg_size)
  )
  memreqnet
  (
    .clk         (clk),
    .reset       (reset),

    .istream_msg (memreq2netmsg_ostream_msg),
    .istream_val (memreq2netmsg_ostream_val),
    .istream_rdy (memreq2netmsg_ostream_rdy),

    .ostream_msg (memreqnet_ostream_msg),
    .ostream_val (memreqnet_ostream_val),
    .ostream_rdy (memreqnet_ostream_rdy)
  );

  //----------------------------------------------------------------------
  // NetMsg2MemReq Adapter
  //----------------------------------------------------------------------

  multicore_NetMsg2MemReq netmsg2memreq
  (
    .istream_msg (memreqnet_ostream_msg[0]),
    .istream_val (memreqnet_ostream_val[0]),
    .istream_rdy (memreqnet_ostream_rdy[0]),

    .ostream_msg (net2mem_reqstream_msg),
    .ostream_val (net2mem_reqstream_val),
    .ostream_rdy (net2mem_reqstream_rdy)
  );

  // Hard code the remaining interfaces

  assign memreqnet_ostream_rdy[1] = 0;
  assign memreqnet_ostream_rdy[2] = 0;
  assign memreqnet_ostream_rdy[3] = 0;

  //----------------------------------------------------------------------
  // MemResp2NetMsg Adapter
  //----------------------------------------------------------------------

  localparam memrespnet_msg_size = 12+$bits(mem_resp_16B_t);

  logic [memrespnet_msg_size-1:0] memresp2netmsg_ostream_msg [4];
  logic                           memresp2netmsg_ostream_val [4];
  logic                           memresp2netmsg_ostream_rdy [4];

  multicore_MemResp2NetMsg memresp2netmsg
  (
    .istream_msg (net2mem_respstream_msg),
    .istream_val (net2mem_respstream_val),
    .istream_rdy (net2mem_respstream_rdy),

    .ostream_msg (memresp2netmsg_ostream_msg[0]),
    .ostream_val (memresp2netmsg_ostream_val[0]),
    .ostream_rdy (memresp2netmsg_ostream_rdy[0])
  );

  // Hard code the remaining interfaces

  assign memresp2netmsg_ostream_msg[1] = 0;
  assign memresp2netmsg_ostream_msg[2] = 0;
  assign memresp2netmsg_ostream_msg[3] = 0;

  assign memresp2netmsg_ostream_val[1] = 0;
  assign memresp2netmsg_ostream_val[2] = 0;
  assign memresp2netmsg_ostream_val[3] = 0;

  //----------------------------------------------------------------------
  // MemRespNet
  //----------------------------------------------------------------------

  logic [memrespnet_msg_size-1:0] memrespnet_ostream_msg [4];
  logic                           memrespnet_ostream_val [4];
  logic                           memrespnet_ostream_rdy [4];

  multicore_Net
  #(
    .p_msg_nbits (memrespnet_msg_size)
  )
  memrespnet
  (
    .clk         (clk),
    .reset       (reset),

    .istream_msg (memresp2netmsg_ostream_msg),
    .istream_val (memresp2netmsg_ostream_val),
    .istream_rdy (memresp2netmsg_ostream_rdy),

    .ostream_msg (memrespnet_ostream_msg),
    .ostream_val (memrespnet_ostream_val),
    .ostream_rdy (memrespnet_ostream_rdy)
  );

  //----------------------------------------------------------------------
  // NetMsg2MemResp Adapters
  //----------------------------------------------------------------------

  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: NETMSG2MEMRESP

    multicore_NetMsg2MemResp netmsg2memresp
    (
      .istream_msg (memrespnet_ostream_msg[i]),
      .istream_val (memrespnet_ostream_val[i]),
      .istream_rdy (memrespnet_ostream_rdy[i]),

      .ostream_msg (cache2net_respstream_msg[i]),
      .ostream_val (cache2net_respstream_val[i]),
      .ostream_rdy (cache2net_respstream_rdy[i])
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
    memreqnet.line_trace( trace_str );
    vc_trace.append_str( trace_str, "}{" );
    memrespnet.line_trace( trace_str );
    vc_trace.append_str( trace_str, "}" );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* MULTICORE_NET_V */
