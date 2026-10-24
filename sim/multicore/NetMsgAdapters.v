//========================================================================
// Network Message Adapters
//========================================================================

`ifndef MULTICORE_NET_MSG_ADAPTERS_V
`define MULTICORE_NET_MSG_ADAPTERS_V

`include "vc/mem-msgs.v"
`include "vc/net-msgs.v"

//------------------------------------------------------------------------
// CacheReq2NetMsg
//------------------------------------------------------------------------
// Convert a 4B cache request into a network message. The size of the
// network message will be the payload size (i.e., the size of a 4B cache
// request message) plus 12 bits (2 bits for source field, 2 bits for
// destination field, and 8 bits for opaque field).

module multicore_CacheReq2NetMsg
(
  input  logic [1:0]                        src_id,

  // Input stream

  input  mem_req_4B_t                       istream_msg,
  input  logic                              istream_val,
  output logic                              istream_rdy,

  // Output stream

  output logic [12+$bits(mem_req_4B_t)-1:0] ostream_msg,
  output logic                              ostream_val,
  input  logic                              ostream_rdy
);
  // Build header for network message; use bank id bits as the destination

  net_msg_hdr_t ostream_msg_hdr;
  assign ostream_msg_hdr.src    = src_id;
  assign ostream_msg_hdr.dest   = istream_msg.addr[5:4];
  assign ostream_msg_hdr.opaque = 0;

  // Assign the header and payload to the network message

  always_comb begin
    ostream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_req_4B_t))] = ostream_msg_hdr;
    ostream_msg[$bits(mem_req_4B_t)-1:0] = istream_msg;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// NetMsg2CacheReq
//------------------------------------------------------------------------
// Convert a network message back into a 4B cache request. The size of
// the network message will be the payload size (i.e., the size of a 4B
// cache request message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field). We put the src
// and dest fields from the network message into the top opaque bits of
// the cache request so when we get the cache responses come back we know
// where to send it.

module multicore_NetMsg2CacheReq
(
  // Input stream

  input  logic [12+$bits(mem_req_4B_t)-1:0] istream_msg,
  input  logic                              istream_val,
  output logic                              istream_rdy,

  // Output stream

  output mem_req_4B_t                       ostream_msg,
  output logic                              ostream_val,
  input  logic                              ostream_rdy
);
  // Get the cache request msg from the payload bits of the net msg and
  // set the opaque bits to be the network msg src/dest fields

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_req_4B_t))];

  always_comb begin
    ostream_msg = istream_msg[$bits(mem_req_4B_t)-1:0];
    ostream_msg.opaque[7:6] = istream_msg_hdr.src;
    ostream_msg.opaque[5:4] = istream_msg_hdr.dest;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// CacheResp2NetMsg
//------------------------------------------------------------------------
// Convert a 4B cache response into a network message. The size of the
// network message will be the payload size (i.e., the size of a 4B cache
// response message) plus 12 bits (2 bits for source field, 2 bits for
// destination field, and 8 bits for opaque field). We get the original
// src and dest fields that were in the network message going over the
// request network and flip them around. So the source is now the
// destination and the destination is now the source.

module multicore_CacheResp2NetMsg
(
  // Input stream

  input  mem_resp_4B_t                       istream_msg,
  input  logic                               istream_val,
  output logic                               istream_rdy,

  // Output stream

  output logic [12+$bits(mem_resp_4B_t)-1:0] ostream_msg,
  output logic                               ostream_val,
  input  logic                               ostream_rdy
);
  // Build the header for the network message

  net_msg_hdr_t ostream_msg_hdr;
  assign ostream_msg_hdr.src    = istream_msg.opaque[5:4];
  assign ostream_msg_hdr.dest   = istream_msg.opaque[7:6];
  assign ostream_msg_hdr.opaque = 0;

  // Assign the header and payload to the network message

  always_comb begin
    ostream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_resp_4B_t))] = ostream_msg_hdr;
    ostream_msg[$bits(mem_resp_4B_t)-1:0] = istream_msg;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// NetMsg2CacheResp
//------------------------------------------------------------------------
// Convert a network message back into a 4B cache response. The size of
// the network message will be the payload size (i.e., the size of a 4B
// cache response message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field). Clear the top
// four bits of the opaque field before returning the response.

module multicore_NetMsg2CacheResp
(
  // Input stream

  input  logic [12+$bits(mem_resp_4B_t)-1:0] istream_msg,
  input  logic                               istream_val,
  output logic                               istream_rdy,

  // Output stream

  output mem_resp_4B_t                       ostream_msg,
  output logic                               ostream_val,
  input  logic                               ostream_rdy
);
  // Get the cache response msg from the payload bits of the net msg and
  // clear the top opaque bits

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_resp_4B_t))];

  always_comb begin
    ostream_msg = istream_msg[$bits(mem_resp_4B_t)-1:0];
    ostream_msg.opaque[7:4] = 0;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// MemReq2NetMsg
//------------------------------------------------------------------------
// Convert a 16B memory request into a network message. The size of the
// network message will be the payload size (i.e., the size of a 16B
// memory request message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field).

module multicore_MemReq2NetMsg
(
  input  logic [1:0]                         src_id,

  // Input stream

  input  mem_req_16B_t                       istream_msg,
  input  logic                               istream_val,
  output logic                               istream_rdy,

  // Output stream

  output logic [12+$bits(mem_req_16B_t)-1:0] ostream_msg,
  output logic                               ostream_val,
  input  logic                               ostream_rdy
);
  // Build the header for the network message; always send to dest 0

  net_msg_hdr_t ostream_msg_hdr;
  assign ostream_msg_hdr.src    = src_id;
  assign ostream_msg_hdr.dest   = 0;
  assign ostream_msg_hdr.opaque = 0;

  // Assign the header and payload to the network message

  always_comb begin
    ostream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_req_16B_t))] = ostream_msg_hdr;
    ostream_msg[$bits(mem_req_16B_t)-1:0] = istream_msg;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// NetMsg2MemReq
//------------------------------------------------------------------------
// Convert a network message back into a 16B memory request. The size of
// the network message will be the payload size (i.e., the size of a 16B
// cache request message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field). We put the src
// and dest fields from the network message into the top opaque bits of
// the memory request so when we get the memory responses come back we
// know where to send it.

module multicore_NetMsg2MemReq
(
  // Input stream

  input  logic [12+$bits(mem_req_16B_t)-1:0] istream_msg,
  input  logic                               istream_val,
  output logic                               istream_rdy,

  // Output stream

  output mem_req_16B_t                       ostream_msg,
  output logic                               ostream_val,
  input  logic                               ostream_rdy
);
  // Get the cache request msg from the payload bits of the net msg and
  // set the opaque bits to be the network msg src/dest fields

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_req_16B_t))];

  always_comb begin
    ostream_msg = istream_msg[$bits(mem_req_16B_t)-1:0];
    ostream_msg.opaque[7:6] = istream_msg_hdr.src;
    ostream_msg.opaque[5:4] = istream_msg_hdr.dest;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// MemResp2NetMsg
//------------------------------------------------------------------------
// Convert a 16B memory response into a network message. The size of the
// network message will be the payload size (i.e., the size of a 16B
// memory response message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field). We get the
// original src and dest fields that were in the network message going
// over the request network and flip them around. So the source is now
// the destination and the destination is now the source.

module multicore_MemResp2NetMsg
(
  // Input stream

  input  mem_resp_16B_t                       istream_msg,
  input  logic                                istream_val,
  output logic                                istream_rdy,

  // Output stream

  output logic [12+$bits(mem_resp_16B_t)-1:0] ostream_msg,
  output logic                                ostream_val,
  input  logic                                ostream_rdy
);
  // Build the header for the network message

  net_msg_hdr_t ostream_msg_hdr;
  assign ostream_msg_hdr.src    = istream_msg.opaque[5:4];
  assign ostream_msg_hdr.dest   = istream_msg.opaque[7:6];
  assign ostream_msg_hdr.opaque = 0;

  // Assign the header and payload to the network message

  always_comb begin
    ostream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_resp_16B_t))] = ostream_msg_hdr;
    ostream_msg[$bits(mem_resp_16B_t)-1:0] = istream_msg;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

//------------------------------------------------------------------------
// NetMsg2MemResp
//------------------------------------------------------------------------
// Convert a network message back into a 16B memory response. The size of
// the network message will be the payload size (i.e., the size of a 16B
// memory response message) plus 12 bits (2 bits for source field, 2 bits
// for destination field, and 8 bits for opaque field). Clear the top
// four bits of the opaque field before returning the response.

module multicore_NetMsg2MemResp
(
  // Input stream

  input  logic [12+$bits(mem_resp_16B_t)-1:0] istream_msg,
  input  logic                                istream_val,
  output logic                                istream_rdy,

  // Output stream

  output mem_resp_16B_t                       ostream_msg,
  output logic                                ostream_val,
  input  logic                                ostream_rdy
);
  // Get the cache response msg from the payload bits of the net msg and
  // clear the top opaque bits

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(12+$bits(mem_resp_16B_t))];

  always_comb begin
    ostream_msg = istream_msg[$bits(mem_resp_16B_t)-1:0];
    ostream_msg.opaque[7:4] = 0;
  end

  // Pass val/rdy signals through

  assign ostream_val = istream_val;
  assign istream_rdy = ostream_rdy;

endmodule

`endif /* MULTICORE_NET_MSG_ADAPTERS_V */
