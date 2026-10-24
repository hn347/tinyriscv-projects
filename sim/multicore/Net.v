//========================================================================
// Ring Network
//========================================================================

`ifndef MULTICORE_NET_V
`define MULTICORE_NET_V

`include "vc/net-msgs.v"
`include "vc/trace.v"
`include "vc/queues.v"

`include "multicore/NetRouter.v"

module multicore_Net
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Input streams

  input  logic [p_msg_nbits-1:0] istream_msg [4],
  input  logic                   istream_val [4],
  output logic                   istream_rdy [4],

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [4],
  output logic                   ostream_val [4],
  input  logic                   ostream_rdy [4]
);

  // Clockwise and counter-clockwise channels
  logic [p_msg_nbits-1:0] channels_cw_msg  [4];
  logic                   channels_cw_val  [4];
  logic                   channels_cw_rdy  [4];

  logic [p_msg_nbits-1:0] channels_ccw_msg [4];
  logic                   channels_ccw_val [4];
  logic                   channels_ccw_rdy [4];

  // ---------- Router 0 ----------
  multicore_NetRouter#(p_msg_nbits) router0(
    .clk(clk),
    .reset(reset),

    .router_id(2'd0),

    .istream_msg('{istream_msg[0], channels_cw_msg[3], channels_ccw_msg[0]}),
    .istream_val('{istream_val[0], channels_cw_val[3], channels_ccw_val[0]}),
    .istream_rdy('{istream_rdy[0], channels_cw_rdy[3], channels_ccw_rdy[0]}),

    .ostream_msg('{ostream_msg[0], channels_cw_msg[0], channels_ccw_msg[3]}),
    .ostream_val('{ostream_val[0], channels_cw_val[0], channels_ccw_val[3]}),
    .ostream_rdy('{ostream_rdy[0], channels_cw_rdy[0], channels_ccw_rdy[3]})
  );

  // ---------- Router 1 ----------
  multicore_NetRouter#(p_msg_nbits) router1(
    .clk(clk),
    .reset(reset),

    .router_id(2'd1),

    .istream_msg('{istream_msg[1], channels_cw_msg[0], channels_ccw_msg[1]}),
    .istream_val('{istream_val[1], channels_cw_val[0], channels_ccw_val[1]}),
    .istream_rdy('{istream_rdy[1], channels_cw_rdy[0], channels_ccw_rdy[1]}),

    .ostream_msg('{ostream_msg[1], channels_cw_msg[1], channels_ccw_msg[0]}),
    .ostream_val('{ostream_val[1], channels_cw_val[1], channels_ccw_val[0]}),
    .ostream_rdy('{ostream_rdy[1], channels_cw_rdy[1], channels_ccw_rdy[0]})
  );

  // ---------- Router 2 ----------
  multicore_NetRouter#(p_msg_nbits) router2(
    .clk(clk),
    .reset(reset),

    .router_id(2'd2),

    .istream_msg('{istream_msg[2], channels_cw_msg[1], channels_ccw_msg[2]}),
    .istream_val('{istream_val[2], channels_cw_val[1], channels_ccw_val[2]}),
    .istream_rdy('{istream_rdy[2], channels_cw_rdy[1], channels_ccw_rdy[2]}),

    .ostream_msg('{ostream_msg[2], channels_cw_msg[2], channels_ccw_msg[1]}),
    .ostream_val('{ostream_val[2], channels_cw_val[2], channels_ccw_val[1]}),
    .ostream_rdy('{ostream_rdy[2], channels_cw_rdy[2], channels_ccw_rdy[1]})
  );

  // ---------- Router 3 ----------
  multicore_NetRouter#(p_msg_nbits) router3(
    .clk(clk),
    .reset(reset),

    .router_id(2'd3),

    .istream_msg('{istream_msg[3], channels_cw_msg[2], channels_ccw_msg[3]}),
    .istream_val('{istream_val[3], channels_cw_val[2], channels_ccw_val[3]}),
    .istream_rdy('{istream_rdy[3], channels_cw_rdy[2], channels_ccw_rdy[3]}),

    .ostream_msg('{ostream_msg[3], channels_cw_msg[3], channels_ccw_msg[2]}),
    .ostream_val('{ostream_val[3], channels_cw_val[3], channels_ccw_val[2]}),
    .ostream_rdy('{ostream_rdy[3], channels_cw_rdy[3], channels_ccw_rdy[2]})
  );


  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  // Generate for loop to instantiate trace modules

  genvar j;
  generate
  for ( j = 0; j < 4; j = j + 1 ) begin: CHANNEL_TRACE

    vc_NetMsgMiniTrace#(p_msg_nbits) cw_trace
    (
      .clk   (clk),
      .reset (reset),
      .msg   (channels_cw_msg[j]),
      .val   (channels_cw_val[j]),
      .rdy   (channels_cw_rdy[j])
    );

    vc_NetMsgMiniTrace#(p_msg_nbits) ccw_trace
    (
      .clk   (clk),
      .reset (reset),
      .msg   (channels_ccw_msg[j]),
      .val   (channels_ccw_val[j]),
      .rdy   (channels_ccw_rdy[j])
    );

  end
  endgenerate

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Line tracing for clockwise channels

    CHANNEL_TRACE[0].cw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[1].cw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[2].cw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[3].cw_trace.line_trace( trace_str );

    vc_trace.append_str( trace_str, "I" );

    // Line tracing for counter clockwise channels

    CHANNEL_TRACE[0].ccw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[1].ccw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[2].ccw_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "|" );
    CHANNEL_TRACE[3].ccw_trace.line_trace( trace_str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* MULTICORE_NET_V */
