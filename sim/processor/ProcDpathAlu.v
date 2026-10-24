//========================================================================
// Proc Datapath ALU
//========================================================================

`ifndef PROCESSOR_PROC_DPATH_ALU_V
`define PROCESSOR_PROC_DPATH_ALU_V

`include "vc/arithmetic.v"

module processor_ProcDpathAlu
(
  input  logic [31:0] in0,
  input  logic [31:0] in1,
  input  logic [ 3:0] fn,
  output logic [31:0] out,
  output logic        ops_eq,
  output logic        ops_lt,
  output logic        ops_ltu
);

  logic [4:0] shamt;
  assign shamt = in1[4:0];

  always_comb begin

    out = 32'b0;
    case ( fn )
      4'd0    : out = in0 + in1;                                  // ADD
      4'd11   : out = in0;                                        // CP OP0
      4'd12   : out = in1;                                        // CP OP1
      4'd1    : out = in0 - in1;                                  // SUB
      4'd2    : out = in0 & in1;                                  // AND
      4'd3    : out = in0 | in1;                                  // OR
      4'd4    : out = in0 ^ in1;                                  // XOR
      4'd5 : out = ($signed(in0) < $signed(in1)) ? 32'd1 : 32'd0; // SLT
      4'd6 : out = $signed(in0) >>> shamt;                        // SRA (shift right arithmetic)
      4'd7:  out = in0 >> shamt;                                  //SRL (shift right logical) keeps it unsigned
      4'd8:  out = in0 << shamt;                                  //SLL (shift left logical)
      default : out = 32'b0;
    endcase

  end

  // Calculate equality, zero, negative flags

  vc_EqComparator #(32) cond_eq_comp
  (
    .in0  (in0),
    .in1  (in1),
    .out  (ops_eq)
  );

  assign ops_lt = $signed(in0) < $signed(in1);
  assign ops_ltu = in0 < in1;

endmodule

`endif /* PROCESSOR_PROC_DPATH_ALU_V */

