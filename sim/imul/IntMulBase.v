//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef IMUL_INT_MUL_BASE_V
`define IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
`include "vc/regs.v"
`include "vc/regfiles.v"
`include "vc/muxes.v"
`include "vc/arithmetic.v"


//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module datapath
(
  input  logic        clk,
  input  logic        reset,

  // input  logic        istream_val,
  // output logic        istream_rdy,
  input  logic [63:0] istream_msg,

  // output logic        ostream_val,
  // input  logic        ostream_rdy,
  output logic [31:0] ostream_msg,

  input logic         b_mux_sel,
  input logic         a_mux_sel,
  input logic         result_mux_sel,
  output logic        b_lsb,
  input logic         result_en,
  input logic         add_mux_sel
);

  logic [31:0] b_reg_out, b_mux_output, b_mux_in0;
  logic [31:0] a_reg_out, a_mux_output, a_mux_in0;
  logic [31:0] result_mux_output;
  logic [31:0] add_mux_output;
  logic [31:0] adder_out;

  assign b_lsb = b_reg_out[0];

  vc_Reg#(32) b_reg ( 
    .clk(clk), 
    .q(b_reg_out), 
    .d(b_mux_output)
  );

  vc_Reg#(32) a_reg ( 
    .clk(clk), 
    .q(a_reg_out), 
    .d(a_mux_output)
  );

  vc_EnReg#(32) result_reg( 
    .clk(clk),
    .reset(reset),
    .q(ostream_msg), 
    .d(result_mux_output),
    .en(result_en)
  );

  vc_Mux2#(32) b_mux(
    .in0(b_mux_in0),
    .in1(istream_msg[31:0]),
    .sel(b_mux_sel),
    .out(b_mux_output)
  );

  vc_Mux2#(32) a_mux(
    .in0(a_mux_in0),
    .in1(istream_msg[63:32]),
    .sel(a_mux_sel),
    .out(a_mux_output)
  );
  
  vc_Mux2#(32) result_mux(
    .in0(add_mux_output),
    .in1(32'b0),
    .sel(result_mux_sel),
    .out(result_mux_output)
  );
  
  vc_Mux2#(32) add_mux(
    .in0(ostream_msg),
    .in1(adder_out),
    .sel(add_mux_sel),
    .out(add_mux_output)
  );
  
  vc_SimpleAdder#(32) adder(
    .in0(a_reg_out),
    .in1(ostream_msg),
    .out(adder_out)
  );

  vc_RightLogicalShifter#(32,1) right_shifter(
    .in (b_reg_out),
    .shamt (1'b1),
    .out (b_mux_in0)
  );

  vc_LeftLogicalShifter#(32,1) left_shifter(
    .in(a_reg_out),
    .shamt(1'b1),
    .out(a_mux_in0)
  );

endmodule

module fsm
(
  input  logic        clk,
  input  logic        reset,

  input  logic        istream_val,
  output logic        istream_rdy,

  output logic        ostream_val,
  input  logic        ostream_rdy,

  //control signals
  output logic         b_mux_sel,
  output logic         a_mux_sel,
  output logic         result_mux_sel,
  input logic          b_lsb,
  output logic         result_en,
  output logic         add_mux_sel,

  // iteration counter
  output logic        iter_clear,
  output logic        iter_inc
);


typedef enum logic [1:0] { STATE_IDLE, STATE_CALC, STATE_DONE } state_e;
state_e state, next_state;

// 32 counter
logic [5:0] iter_count;

always_ff @(posedge clk or posedge reset) begin

  if (reset) begin
    iter_count <= 6'd0;
  end else begin 
    if (iter_clear) iter_count <= 6'd0;
    else if (iter_inc) iter_count <= iter_count +6'd1;
  end
end

// sequential state register

always_ff @(posedge clk or posedge reset) begin
  if (reset) state <= STATE_IDLE;
  else       state <= next_state;
end

// state transition block
always_comb begin
  next_state = state;
  if (state == STATE_IDLE) begin
    if (istream_val) begin
      next_state = STATE_CALC;
    end
  end
  else if (state == STATE_CALC) begin
    if (iter_count == 6'd32) begin
      next_state = STATE_DONE;
    end
  end

  else if (state == STATE_DONE) begin
    if (ostream_rdy) begin
      next_state = STATE_IDLE;
    end
  end
end
  
// output block, blue text and ostream logics
always_comb begin

  // defaults
  istream_rdy     = 1'b0;
  ostream_val     = 1'b0;

  b_mux_sel       = 1'b0;  
  a_mux_sel       = 1'b0;
  result_mux_sel  = 1'b0;  
  add_mux_sel     = 1'b0;  
  result_en       = 1'b0;

  iter_clear      = 1'b0;
  iter_inc        = 1'b0;

  unique case (state)
    STATE_IDLE : begin istream_rdy = 1'b1;
                b_mux_sel = 1'b1; 
                a_mux_sel = 1'b1;
                result_mux_sel = 1'b1;
                result_en = istream_val & istream_rdy;
                iter_clear = istream_val & istream_rdy;
    end
    STATE_CALC :begin b_mux_sel = 1'b0;
                a_mux_sel = 1'b0;
                result_mux_sel = 1'b0;
                add_mux_sel = b_lsb; 
                result_en = 1'b1;
                iter_inc = 1'b1;
    end
    STATE_DONE :begin 
      ostream_val = 1'b1;
    end
  endcase
end

endmodule


module imul_IntMulBase
(
  input  logic        clk,
  input  logic        reset,

  input  logic        istream_val,
  output logic        istream_rdy,
  input  logic [63:0] istream_msg,

  output logic        ostream_val,
  input  logic        ostream_rdy,
  output logic [31:0] ostream_msg
);

  // control signals

  logic b_mux_sel, a_mux_sel, result_mux_sel, result_en, add_mux_sel;
  logic b_lsb;

  // datapath
  datapath dp (
    .clk            (clk),
    .reset          (reset),
    .istream_msg    (istream_msg),
    .ostream_msg    (ostream_msg),
    .b_mux_sel      (b_mux_sel),
    .a_mux_sel      (a_mux_sel),
    .result_mux_sel (result_mux_sel),
    .b_lsb          (b_lsb),
    .result_en      (result_en),
    .add_mux_sel    (add_mux_sel)
  );

  // fsm
  logic iter_clear, iter_inc;

  fsm ctrl (
    .clk            (clk),
    .reset          (reset),
    .istream_val    (istream_val),
    .istream_rdy    (istream_rdy),
    .ostream_rdy    (ostream_rdy),
    .ostream_val    (ostream_val),

    .b_mux_sel      (b_mux_sel),
    .a_mux_sel      (a_mux_sel),
    .result_mux_sel (result_mux_sel),
    .b_lsb          (b_lsb),
    .result_en      (result_en),
    .add_mux_sel    (add_mux_sel),

    .iter_clear     (iter_clear),
    .iter_inc       (iter_inc)
  );
  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", istream_msg );
    vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", ostream_msg );
    vc_trace.append_val_rdy_str( trace_str, ostream_val, ostream_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule


`endif /* IMUL_INT_MUL_BASE_V */

