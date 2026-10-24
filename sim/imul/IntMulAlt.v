//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

`ifndef IMUL_INT_MUL_ALT_V
`define IMUL_INT_MUL_ALT_V

`include "vc/trace.v"
`include "vc/regs.v"
`include "vc/regfiles.v"
`include "vc/muxes.v"
`include "vc/arithmetic.v"

module priority_encoder(
  input logic [31:0] b, 
  output logic [4:0] shamt
);
  logic        b_zero;
  logic        b_lsb;
  logic [4:0]  k;

  always_comb begin
    b_zero = (b == 32'b0);
    b_lsb  = b[0];
    k      = 5'd0;
    shamt  = 5'd0;

    if (b_zero) begin
      shamt = 5'd0;
    end
    else if (b_lsb == 1'b1) begin
      shamt = 5'd1;
    end
    else begin
      if (b[0]  == 1'b0) begin k += 5'd1;
      if (b[1]  == 1'b0) begin k += 5'd1;
      if (b[2]  == 1'b0) begin k += 5'd1;
      if (b[3]  == 1'b0) begin k += 5'd1;
      if (b[4]  == 1'b0) begin k += 5'd1;
      if (b[5]  == 1'b0) begin k += 5'd1;
      if (b[6]  == 1'b0) begin k += 5'd1;
      if (b[7]  == 1'b0) begin k += 5'd1;
      if (b[8]  == 1'b0) begin k += 5'd1;
      if (b[9]  == 1'b0) begin k += 5'd1;
      if (b[10] == 1'b0) begin k += 5'd1;
      if (b[11] == 1'b0) begin k += 5'd1;
      if (b[12] == 1'b0) begin k += 5'd1;
      if (b[13] == 1'b0) begin k += 5'd1;
      if (b[14] == 1'b0) begin k += 5'd1;
      if (b[15] == 1'b0) begin k += 5'd1;
      if (b[16] == 1'b0) begin k += 5'd1;
      if (b[17] == 1'b0) begin k += 5'd1;
      if (b[18] == 1'b0) begin k += 5'd1;
      if (b[19] == 1'b0) begin k += 5'd1;
      if (b[20] == 1'b0) begin k += 5'd1;
      if (b[21] == 1'b0) begin k += 5'd1;
      if (b[22] == 1'b0) begin k += 5'd1;
      if (b[23] == 1'b0) begin k += 5'd1;
      if (b[24] == 1'b0) begin k += 5'd1;
      if (b[25] == 1'b0) begin k += 5'd1;
      if (b[26] == 1'b0) begin k += 5'd1;
      if (b[27] == 1'b0) begin k += 5'd1;
      if (b[28] == 1'b0) begin k += 5'd1;
      if (b[29] == 1'b0) begin k += 5'd1;
      if (b[30] == 1'b0) begin k += 5'd1;
      if (b[31] == 1'b0) begin k += 5'd1; end end end end end end end end
      end end end end end end end end end end end end end end end end end end end
      end end end end end
      shamt = k;
    end
  end
endmodule

module datapath
( 
  input  logic        clk,
  input  logic        reset,

  input  logic [63:0] istream_msg,
  output logic [31:0] ostream_msg,

  input logic         b_mux_sel,
  input logic         a_mux_sel,
  input logic         result_mux_sel,
  input logic         result_en,
  input logic         add_mux_sel,

  output logic        b_lsb,
  output logic        b_zero,

  output logic        next_b_zero
);

  logic [31:0] b_reg_out, b_mux_output, b_mux_in0;
  logic [31:0] a_reg_out, a_mux_output, a_mux_in0;
  logic [31:0] result_mux_output;
  logic [31:0] add_mux_output;
  logic [31:0] adder_out;

  assign b_lsb = b_reg_out[0];
  assign b_zero = (b_reg_out == 32'b0);

  logic [4:0] shamt;
  
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

  vc_RightLogicalShifter#(32,5) right_shifter (
    .in(b_reg_out),
    .shamt(shamt),
    .out(b_mux_in0)
  );

  vc_LeftLogicalShifter#(32,5) left_shifter (
    .in(a_reg_out),
    .shamt(shamt),
    .out(a_mux_in0)
  );

  priority_encoder pe (
    .b     ( b_reg_out ),
    .shamt ( shamt )
  );

  logic [31:0] next_b;
  assign next_b      = b_mux_in0;              
  assign next_b_zero = (next_b == 32'b0);
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
  output logic         result_en,
  output logic         add_mux_sel,

  input logic          b_lsb,
  input logic          b_zero,
  
  input logic         next_b_zero
);

typedef enum logic [1:0] { STATE_IDLE, STATE_CALC, STATE_DONE } state_e;
state_e state, next_state;

// sequential state register

always_ff @(posedge clk or posedge reset) begin
  if (reset) state <= STATE_IDLE;
  else       state <= next_state;
end

// state transition block
always_comb begin
  next_state = state;
  if (state == STATE_IDLE) begin
    if (istream_val & istream_rdy) begin
      next_state = STATE_CALC;
    end
  end
  else if (state == STATE_CALC) begin
    if (next_b_zero) begin
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

  unique case (state)
    STATE_IDLE : begin istream_rdy = 1'b1;
                b_mux_sel = istream_val & istream_rdy; 
                a_mux_sel = istream_val & istream_rdy;
                result_mux_sel = istream_val & istream_rdy;
                result_en = istream_val & istream_rdy;
  
    end
    STATE_CALC :begin b_mux_sel = 1'b0;
                a_mux_sel = 1'b0;
                result_mux_sel = 1'b0;
                add_mux_sel = b_lsb; 
                result_en = 1'b1;
    end
    STATE_DONE :begin 
      ostream_val = 1'b1;
      result_en = 1'b0;
    end
  endcase
end

endmodule


//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

module imul_IntMulAlt
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
  logic b_lsb, b_zero;
  logic next_b_zero;

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
    .b_zero         (b_zero),
    .result_en      (result_en),
    .add_mux_sel    (add_mux_sel),
    .next_b_zero    (next_b_zero)
  );



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
    .b_zero         (b_zero),
    .result_en      (result_en),
    .add_mux_sel    (add_mux_sel),
    .next_b_zero    (next_b_zero)
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

`endif /* IMUL_INT_MUL_ALT_V */

