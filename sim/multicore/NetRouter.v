//========================================================================
// Network Router
//========================================================================

`ifndef MULTICORE_NET_ROUTER_V
`define MULTICORE_NET_ROUTER_V

`include "vc/net-msgs.v"
`include "vc/trace.v"
`include "vc/queues.v"

`include "multicore/NetRouterRouteUnit.v"
`include "multicore/NetRouterSwitchUnit.v"

module multicore_NetRouter
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Router id (which router is this in the network?)

  input  logic     [1:0]         router_id,

  // Input streams

  input  logic [p_msg_nbits-1:0] istream_msg [3],
  input  logic                   istream_val [3],
  output logic                   istream_rdy [3],

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [3],
  output logic                   ostream_val [3],
  input  logic                   ostream_rdy [3]
);

  // ---------- Input Queue 0 ----------
  logic [2:0] inq0_num_free_entries;
  logic [p_msg_nbits-1:0] inputstream0_deq_msg;
  logic inputstream0_deq_val;
  logic inputstream0_deq_rdy;

  vc_Queue#( `VC_QUEUE_NORMAL, p_msg_nbits, 4) inputstream0(
    .clk(clk),
    .reset(reset),

    .enq_val(istream_val[0]),
    .enq_rdy(istream_rdy[0]),
    .enq_msg(istream_msg[0]),

    .deq_val(inputstream0_deq_val),
    .deq_rdy(inputstream0_deq_rdy),
    .deq_msg(inputstream0_deq_msg),

    .num_free_entries(inq0_num_free_entries)
  );

  // ---------- Input Queue 1 ----------
  logic [2:0] inq1_num_free_entries;
  logic [p_msg_nbits-1:0] inputstream1_deq_msg;
  logic inputstream1_deq_val;
  logic inputstream1_deq_rdy;

  vc_Queue#( `VC_QUEUE_NORMAL, p_msg_nbits, 4) inputstream1(
    .clk(clk),
    .reset(reset),

    .enq_val(istream_val[1]),
    .enq_rdy(istream_rdy[1]),
    .enq_msg(istream_msg[1]),

    .deq_val(inputstream1_deq_val),
    .deq_rdy(inputstream1_deq_rdy),
    .deq_msg(inputstream1_deq_msg),

    .num_free_entries(inq1_num_free_entries)
  );

  // ---------- Input Queue 2 ----------
  logic [2:0] inq2_num_free_entries;
  logic [p_msg_nbits-1:0] inputstream2_deq_msg;
  logic inputstream2_deq_val;
  logic inputstream2_deq_rdy;

  vc_Queue#( `VC_QUEUE_NORMAL, p_msg_nbits, 4) inputstream2(
    .clk(clk),
    .reset(reset),

    .enq_val(istream_val[2]),
    .enq_rdy(istream_rdy[2]),
    .enq_msg(istream_msg[2]),

    .deq_val(inputstream2_deq_val),
    .deq_rdy(inputstream2_deq_rdy),
    .deq_msg(inputstream2_deq_msg),

    .num_free_entries(inq2_num_free_entries)
  );

  // ---------- Route Unit 0 ----------
  logic [p_msg_nbits-1:0] routeunit0_ostream_msg[3];
  logic routeunit0_ostream_val[3];
  logic routeunit0_ostream_rdy[3];
 
  multicore_NetRouterRouteUnit#(p_msg_nbits) runit0(
    .clk(clk),
    .reset(reset),
    
    .router_id(router_id),

    .istream_msg(inputstream0_deq_msg),
    .istream_val(inputstream0_deq_val),
    .istream_rdy(inputstream0_deq_rdy),

    .ostream_msg(routeunit0_ostream_msg),
    .ostream_val(routeunit0_ostream_val),
    .ostream_rdy(routeunit0_ostream_rdy)
  );

  // ---------- Route Unit 1 ----------
  logic [p_msg_nbits-1:0] routeunit1_ostream_msg[3];
  logic routeunit1_ostream_val[3];
  logic routeunit1_ostream_rdy[3];

  multicore_NetRouterRouteUnit#(p_msg_nbits) runit1(
    .clk(clk),
    .reset(reset),

    .router_id(router_id),

    .istream_msg(inputstream1_deq_msg),
    .istream_val(inputstream1_deq_val),
    .istream_rdy(inputstream1_deq_rdy),

    .ostream_msg(routeunit1_ostream_msg),
    .ostream_val(routeunit1_ostream_val),
    .ostream_rdy(routeunit1_ostream_rdy)
  );

  // ---------- Route Unit 2 ----------
  logic [p_msg_nbits-1:0] routeunit2_ostream_msg[3];
  logic routeunit2_ostream_val[3];
  logic routeunit2_ostream_rdy[3];

  multicore_NetRouterRouteUnit#(p_msg_nbits) runit2(
    .clk(clk),
    .reset(reset),

    .router_id(router_id),

    .istream_msg(inputstream2_deq_msg),
    .istream_val(inputstream2_deq_val),
    .istream_rdy(inputstream2_deq_rdy),

    .ostream_msg(routeunit2_ostream_msg),
    .ostream_val(routeunit2_ostream_val),
    .ostream_rdy(routeunit2_ostream_rdy)
  ); 
  
  // ---------- Switch Unit 0 ----------
  multicore_NetRouterSwitchUnit#(p_msg_nbits) sunit0(
    .clk(clk),
    .reset(reset),

    .istream_msg('{routeunit0_ostream_msg[0], routeunit1_ostream_msg[0], routeunit2_ostream_msg[0]}),
    .istream_val('{routeunit0_ostream_val[0], routeunit1_ostream_val[0], routeunit2_ostream_val[0]}),
    .istream_rdy('{routeunit0_ostream_rdy[0], routeunit1_ostream_rdy[0], routeunit2_ostream_rdy[0]}),

    .ostream_msg(ostream_msg[0]),
    .ostream_val(ostream_val[0]),
    .ostream_rdy(ostream_rdy[0])
  );

  // ---------- Switch Unit 1 ----------
  multicore_NetRouterSwitchUnit#(p_msg_nbits) sunit1(
    .clk(clk),
    .reset(reset),

    .istream_msg('{routeunit0_ostream_msg[1], routeunit1_ostream_msg[1], routeunit2_ostream_msg[1]}),
    .istream_val('{routeunit0_ostream_val[1], routeunit1_ostream_val[1], routeunit2_ostream_val[1]}),
    .istream_rdy('{routeunit0_ostream_rdy[1], routeunit1_ostream_rdy[1], routeunit2_ostream_rdy[1]}),

    .ostream_msg(ostream_msg[1]),
    .ostream_val(ostream_val[1]),
    .ostream_rdy(ostream_rdy[1])
  );

  // ---------- Switch Unit 2 ----------
  multicore_NetRouterSwitchUnit#(p_msg_nbits) sunit2(
    .clk(clk),
    .reset(reset),

    .istream_msg('{routeunit0_ostream_msg[2], routeunit1_ostream_msg[2], routeunit2_ostream_msg[2]}),
    .istream_val('{routeunit0_ostream_val[2], routeunit1_ostream_val[2], routeunit2_ostream_val[2]}),
    .istream_rdy('{routeunit0_ostream_rdy[2], routeunit1_ostream_rdy[2], routeunit2_ostream_rdy[2]}),

    .ostream_msg(ostream_msg[2]),
    .ostream_val(ostream_val[2]),
    .ostream_rdy(ostream_rdy[2])
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  vc_NetMsgTrace#(p_msg_nbits) ostream0_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[0]),
    .val   (ostream_val[0]),
    .rdy   (ostream_rdy[0])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream1_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[1]),
    .val   (ostream_val[1]),
    .rdy   (ostream_rdy[1])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream2_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[2]),
    .val   (ostream_val[2]),
    .rdy   (ostream_rdy[2])
  );

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Line tracing for input queues

    case ( inq0_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( inq1_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( inq2_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    vc_trace.append_str( trace_str, "|" );

    // Line tracing for switch units

    sunit0.line_trace( trace_str );
    sunit1.line_trace( trace_str );
    sunit2.line_trace( trace_str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_V */
