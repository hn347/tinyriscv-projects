//=========================================================================
// Alt Blocking Cache Datapath
//=========================================================================

`ifndef CACHE_CACHE_ALT_DPATH_V
`define CACHE_CACHE_ALT_DPATH_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/srams.v"
`include "vc/mem-msgs.v"
`include "vc/regfiles.v"

module cache_CacheAltDpath
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

  input logic           data_array_ren,
  input logic           data_array_wen,
  input logic           tag_array_ren,
  input  logic          tag_array_wen_way0,
  input  logic          tag_array_wen_way1,
  output logic [31:0]   cachereq_addr,
  input  logic          read_data_reg_en, 
  input  logic          read_data_zero_mux_sel,
  input  logic          evict_addr_reg_en,
  input  logic          mem_req_addr_mux_sel,
  input  logic [3:0]    cacheresp_type,
  input  logic          hit,
  input  logic [3:0]    memreq_type,

  // new alt control signals
  input  logic           way_sel,
  output logic           tag_w0_match,
  output logic           tag_w1_match,
  input  logic           victim,
  input  logic           victim_mux_sel
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
// Address decode (tag/index/offset/bank)
//---------------------

logic [1:0]  bank_bits; // only for 4-bank
logic [2:0]  index; //set index (8 sets)
logic [3:0]  tag_word_offset; // byte offset 
logic [23:0] tag; // upper tag bits

assign tag_word_offset = cachereq_addr_reg_out[3:0];
assign bank_bits = (p_num_banks == 4) ? cachereq_addr_reg_out[5:4] : 2'b00;
assign index = (p_num_banks == 4) ? cachereq_addr_reg_out[8:6]: cachereq_addr_reg_out[6:4];
assign tag = (p_num_banks == 4) ? cachereq_addr_reg_out[31:9] : cachereq_addr_reg_out[31:7];

//---------------------
// Wben Mux
//---------------------

//select word
logic [15:0] wben_dec = 16'h000F << {cachereq_addr_reg_out[3:2], 2'b00};
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
logic [127:0] write_data_mux_out;
logic [127:0] cachereq_data_reg_out_repl;
assign cachereq_data_reg_out_repl = {4{cachereq_data_reg_out}};

vc_EnResetReg#(128) memresp_data_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (memresp_en),
  .d      (cache2mem_respstream_msg.data),
  .q      (memresp_data_reg_out)
);

vc_Mux2#(128) write_data_mux
(
  .in0  (cachereq_data_reg_out_repl),
  .in1  (memresp_data_reg_out),
  .sel  (write_data_mux_sel),
  .out  (write_data_mux_out)
);

//-----------------------------------
// Tag Array (two ways & compares)
//-----------------------------------

logic [23:0] tag_array0_out;
logic [23:0] tag_array1_out;

vc_CombinationalBitSRAM_1rw#(24,8) tag_array_way0
(
  .clk(clk),
  .reset(reset),
  .read_en(tag_array_ren),
  .read_addr(index),
  .read_data(tag_array0_out),
  .write_en(tag_array_wen_way0),
  .write_addr(index),
  .write_data(tag)
);

vc_CombinationalBitSRAM_1rw#(24,8) tag_array_way1
(
  .clk(clk),
  .reset(reset),
  .read_en(tag_array_ren),
  .read_addr(index),
  .read_data(tag_array1_out),
  .write_en(tag_array_wen_way1),
  .write_addr(index),
  .write_data(tag)
);

assign tag_w0_match = (tag_array0_out == tag);
assign tag_w1_match = (tag_array1_out == tag);

//-----------------------------------
// Build eviction/refill address
//-----------------------------------

// Choose which way before mk addr 
logic [23:0] tag_evict;
vc_Mux2#(24) mk_addr_mux
(
  .in0 (tag_array0_out),
  .in1 (tag_array1_out),
  .sel (victim),  
  .out (tag_evict)
);

// full evict address
logic [31:0] mk_addr_evict;
assign mk_addr_evict = (p_num_banks == 4) 
                    ? {tag_evict, index, bank_bits, 4'b0} 
                    : {tag_evict, index, 4'b0};

// full request line base
logic [31:0] mk_addr;
assign mk_addr = (p_num_banks == 4)
                ? {tag, index, bank_bits, 4'b0}
                : {tag, index, 4'b0};

logic [31:0] evict_addr_reg_out;
vc_EnResetReg#(32, 0) evict_addr_reg
(
  .clk    (clk),
  .reset  (reset),
  .en     (evict_addr_reg_en),
  .d      (mk_addr_evict),
  .q      (evict_addr_reg_out)
);

logic [31:0] memreq_addr_mux_out;
vc_Mux2#(32) memreq_addr_mux
(
  .in0  (evict_addr_reg_out),
  .in1  (mk_addr),
  .sel  (mem_req_addr_mux_sel),
  .out  (memreq_addr_mux_out)
);

//---------------------
// Data Array (two ways)
//---------------------

logic active_way;
// choose way: victim during evict/refill, else selected hit way
assign active_way = victim_mux_sel ? victim : way_sel;
logic [3:0] data_idx = { active_way, index[2:0] };

logic [127:0] data_array_out_0;
logic [127:0] data_array_out_1;
vc_CombinationalSRAM_1rw#(128,8) data_array_way0
(
  .clk(clk),
  .reset(reset),
  .read_en(data_array_ren),
  .read_addr(index),
  .read_data(data_array_out_0),
  .write_en(data_array_wen & ~active_way),
  .write_byte_en(wben_mux_out),
  .write_addr(index),
  .write_data(write_data_mux_out)
);

vc_CombinationalSRAM_1rw#(128,8) data_array_way1
(
  .clk(clk),
  .reset(reset),
  .read_en(data_array_ren),
  .read_addr(index),
  .read_data(data_array_out_1),
  .write_en(data_array_wen & active_way),
  .write_byte_en(wben_mux_out),
  .write_addr(index),
  .write_data(write_data_mux_out)
);

logic [127:0] data_array_read_data;
assign data_array_read_data = active_way ? data_array_out_1 : data_array_out_0;
logic [127:0] read_data_zero_mux_out;

vc_Mux2#(128) read_data_zero_mux
(
  .in0  (data_array_read_data),
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
