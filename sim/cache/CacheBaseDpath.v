//=========================================================================
// Base Blocking Cache Datapath
//=========================================================================

`ifndef CACHE_CACHE_BASE_DPATH_V
`define CACHE_CACHE_BASE_DPATH_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/srams.v"
`include "vc/mem-msgs.v"
`include "vc/regfiles.v"

module cache_CacheBaseDpath
#(
  parameter p_num_banks = 1
)
(
  input  logic          clk,
  input  logic          reset,

  // Processor <-> Cache Interface

  input  mem_req_4B_t   proc2cache_reqstream_msg,
  output mem_resp_4B_t  proc2cache_respstream_msg,

  // Cache <-> Memory Interface

  output mem_req_16B_t  cache2mem_reqstream_msg,
  input  mem_resp_16B_t cache2mem_respstream_msg,

  // Control Signals (ctrl->dpath)
  input  logic          cachereq_en,
  output logic [3:0]    cachereq_type,
  input  logic          memresp_en, 
  input  logic          write_data_mux_sel,
  input  logic          wben_mux_sel,
  input  logic          tag_array_ren,
  input  logic          tag_array_wen,
  input  logic          data_array_ren,
  input  logic          data_array_wen,
  output logic [31:0]   cachereq_addr,
  input  logic          read_data_reg_en, 
  input  logic          read_data_zero_mux_sel,
  output logic          tag_match,
  input  logic          evict_addr_reg_en,
  input  logic          mem_req_addr_mux_sel,
  input  logic [3:0]    cacheresp_type,
  input  logic [1:0]    hit,
  input  logic [3:0]    memreq_type
);

//---------------------
// Cache Request
//---------------------

logic [7:0] cachereq_opaque_reg_out;
vc_EnResetReg#(8) cachereq_opaque_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (cachereq_en),
  .d      (proc2cache_reqstream_msg.opaque),
  .q      (cachereq_opaque_reg_out)
);

logic [3:0]  cachereq_type_reg_out;
assign cachereq_type = cachereq_type_reg_out; 
vc_EnResetReg#(4) cachereq_type_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (cachereq_en),
  .d      (proc2cache_reqstream_msg.type_),
  .q      (cachereq_type_reg_out)
);

logic [31:0] cachereq_addr_reg_out;
assign cachereq_addr = cachereq_addr_reg_out;
vc_EnResetReg#(32,0) cachereq_addr_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (cachereq_en),
  .d      (proc2cache_reqstream_msg.addr),
  .q      (cachereq_addr_reg_out)
);

logic [31:0] cachereq_data_reg_out;
vc_EnResetReg#(32,0) cachereq_data_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (cachereq_en),
  .d      (proc2cache_reqstream_msg.data),
  .q      (cachereq_data_reg_out)
);

//---------------------
// Adress decode
//---------------------

logic [1:0]  bank_bits; //only for 4-bank
logic [3:0]  index; //set index (8 sets)
logic [3:0]  tag_word_offset; // byte offset
logic [23:0] tag; // upper tag bits
logic [23:0] tag_array_out;

assign tag_word_offset = cachereq_addr_reg_out[3:0];
assign bank_bits = (p_num_banks == 4) ? cachereq_addr_reg_out[5:4] : 2'b00;
assign index = (p_num_banks == 4) ? cachereq_addr_reg_out[9:6]: cachereq_addr_reg_out[7:4];
assign tag = (p_num_banks == 4) ? cachereq_addr_reg_out[31:10] : cachereq_addr_reg_out[31:8];

//---------------------
// Wben Mux
//---------------------

logic [15:0] wben_dec = 16'h000F << (tag_word_offset[3:2] * 4);
logic [15:0] wben_mux_out;

vc_Mux2#(16) wben_mux
(
  .in0  (wben_dec),
  .in1  (16'b1111111111111111),
  .sel  (wben_mux_sel),
  .out  (wben_mux_out)
);

//---------------------
// Mem Response
//---------------------

logic [127:0] memresp_data_reg_out;
vc_EnResetReg#(128) memresp_data_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (memresp_en),
  .d      (cache2mem_respstream_msg.data),
  .q      (memresp_data_reg_out)
);

logic [127:0] write_data_mux_out;
logic [127:0] cachereq_data_reg_out_repl;
assign cachereq_data_reg_out_repl = {4{cachereq_data_reg_out}};

vc_Mux2#(128) write_data_mux
(
  .in0  (cachereq_data_reg_out_repl),
  .in1  (memresp_data_reg_out),
  .sel  (write_data_mux_sel),
  .out  (write_data_mux_out)
);

//---------------------
// Tag Array 
//---------------------

vc_CombinationalBitSRAM_1rw#(24,16) tag_array
(
  .clk(clk),
  .reset(reset),
  .read_en(tag_array_ren),
  .read_addr(index),
  .read_data(tag_array_out),
  .write_en(tag_array_wen),
  .write_addr(index),
  .write_data(tag)
);

// Comparator
assign tag_match = (tag == tag_array_out);

//-----------------------------------
// Build eviction/refill address
//-----------------------------------

logic [31:0] evict_addr_input;

assign evict_addr_input = (p_num_banks == 4)
                      ? {tag_array_out, index, bank_bits, 4'b0}
                      : {tag_array_out, index, 4'b0};

logic [31:0] evict_addr_reg_out;
vc_EnResetReg#(32) evict_addr_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (evict_addr_reg_en),
  .d      (evict_addr_input),
  .q      (evict_addr_reg_out)
);

logic [31:0] memreq_addr_mux_in1;
assign memreq_addr_mux_in1 = (p_num_banks == 4)
                            ? {tag, index, bank_bits, 4'b0} 
                            : {tag, index, 4'b0};
logic [31:0] memreq_addr_mux_out;

vc_Mux2#(32) memreq_addr_mux
(
  .in0  (evict_addr_reg_out),
  .in1  (memreq_addr_mux_in1),
  .sel  (mem_req_addr_mux_sel),
  .out  (memreq_addr_mux_out)
);

//---------------------
// Data Array 
//---------------------

logic [127:0] data_array_out;
vc_CombinationalSRAM_1rw#(128,16) data_array
(
  .clk(clk),
  .reset(reset),
  .read_en(data_array_ren),
  .read_addr(index),
  .read_data(data_array_out),
  .write_en(data_array_wen),
  .write_byte_en(wben_mux_out),
  .write_addr(index),
  .write_data(write_data_mux_out)
);

// logic read_data_zero_mux_sel;
logic [127:0] read_data_zero_mux_out;
vc_Mux2#(128) read_data_zero_mux
(
  .in0  (data_array_out),
  .in1  (128'b0),
  .sel  (read_data_zero_mux_sel),
  .out  (read_data_zero_mux_out)
);

logic [127:0] read_data_reg_out;
vc_EnResetReg#(128) read_data_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (read_data_reg_en),
  .d      (read_data_zero_mux_out),
  .q      (read_data_reg_out)
);

logic [31:0] read_data_bit_sel_out;
vc_Mux4#(32) read_data_bit_sel_mux
(
  .in0  (read_data_reg_out[31:0]),
  .in1  (read_data_reg_out[63:32]),
  .in2  (read_data_reg_out[95:64]),
  .in3  (read_data_reg_out[127:96]),
  .sel  (tag_word_offset[3:2]),
  .out  (read_data_bit_sel_out)
);

//---------------------
// Cache Response
//---------------------

assign proc2cache_respstream_msg.opaque = cachereq_opaque_reg_out;
assign proc2cache_respstream_msg.type_ = cacheresp_type;
assign proc2cache_respstream_msg.len = 2'b0;
assign proc2cache_respstream_msg.test = hit;
assign proc2cache_respstream_msg.data = (cachereq_type_reg_out == 4'd1) ? 32'b0: read_data_bit_sel_out;

//---------------------
// Mem Request
//---------------------

assign cache2mem_reqstream_msg.opaque = 8'b0;
assign cache2mem_reqstream_msg.data = read_data_reg_out;
assign cache2mem_reqstream_msg.addr = memreq_addr_mux_out;
assign cache2mem_reqstream_msg.len = 4'b0;
assign cache2mem_reqstream_msg.type_ = memreq_type;



endmodule

`endif
