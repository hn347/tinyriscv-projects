//=========================================================================
// Base Blocking Cache Control
//=========================================================================

`ifndef CACHE_CACHE_BASE_CTRL_V
`define CACHE_CACHE_BASE_CTRL_V

`include "vc/trace.v"
`include "vc/regfiles.v"
`include "vc/mem-msgs.v"


module cache_CacheBaseCtrl
#(
  parameter p_num_banks = 1
)
(
  input  logic        clk,
  input  logic        reset,

  // Processor <-> Cache Interface

  // CHECK the inputs, SET the outputs
  input  logic        proc2cache_reqstream_val, // request is valid
  output logic        proc2cache_reqstream_rdy, // cache ready for new signal

  output logic        proc2cache_respstream_val,
  input  logic        proc2cache_respstream_rdy,

  // Cache <-> Memory Interface

  output logic        cache2mem_reqstream_val,
  input  logic        cache2mem_reqstream_rdy,

  input  logic        cache2mem_respstream_val,
  output logic        cache2mem_respstream_rdy,

  // Control Signals (ctrl->dpath)

  // Inputs from datapath
  input  logic [3:0]  cachereq_type,
  input  logic [31:0] cachereq_addr,
  input  logic        tag_match,
  
  // Outputs to datapath
  output logic        cachereq_en,
  output logic        memresp_en, 
  output logic        write_data_mux_sel,
  output logic        wben_mux_sel,
  output logic        tag_array_ren,
  output logic        tag_array_wen,
  output logic        data_array_ren,
  output logic        data_array_wen,
  output logic        read_data_reg_en, 
  output logic        read_data_zero_mux_sel,
  output logic        evict_addr_reg_en,
  output logic        mem_req_addr_mux_sel,
  output logic [3:0]  cacheresp_type,
  output logic [1:0]  hit,
  output logic [3:0]  memreq_type
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE              = 5'd0;
  localparam STATE_TAG_CHECK         = 5'd1;
  localparam STATE_INIT_DATA_ACCESS  = 5'd2;
  localparam STATE_READ_DATA_ACCESS  = 5'd3;
  localparam STATE_WRITE_DATA_ACCESS = 5'd4;
  localparam STATE_REFILL_REQUEST    = 5'd5;
  localparam STATE_REFILL_WAIT       = 5'd6;
  localparam STATE_REFILL_UPDATE     = 5'd7;
  localparam STATE_EVICT_PREPARE     = 5'd8;
  localparam STATE_EVICT_REQUEST     = 5'd9;  
  localparam STATE_EVICT_WAIT        = 5'd10;
  localparam STATE_WAIT              = 5'd11;

  // store current and next FSM states
  logic [4:0] state;
  logic [4:0] next_state;

  logic is_valid;
  logic is_dirty;

  logic hit_TC;
  assign hit_TC = (state == STATE_TAG_CHECK) && is_valid && tag_match;

  always_ff @(posedge clk or posedge reset) begin
    if (reset) state <= STATE_IDLE;
    else       state <= next_state;
  end

  always_comb begin
    next_state = state;

    // STATE_IDLE
    if (state == STATE_IDLE) begin 
      if (!proc2cache_reqstream_val) begin
        next_state = STATE_IDLE;
      end
      else if (proc2cache_reqstream_val) begin
        next_state = STATE_TAG_CHECK;
      end
    end

    // STATE_TAG_CHECK
    if (state == STATE_TAG_CHECK) begin 
      if (cachereq_type == 4'd2) begin
        next_state = STATE_INIT_DATA_ACCESS;
      end
      else if (tag_match && is_valid) begin // cache hit
        if (cachereq_type == 4'd0) begin  // read
          next_state = STATE_READ_DATA_ACCESS;
        end 
        else if (cachereq_type == 4'd1) begin
          next_state = STATE_WRITE_DATA_ACCESS;
        end 
      end
      else if (is_valid && is_dirty) begin  //cache miss and need to evict
        next_state = STATE_EVICT_PREPARE;
      end
      else begin
        next_state = STATE_REFILL_REQUEST;
      end  
    end
    
    // STATE_WAIT
    if (state == STATE_WAIT) begin 
      if (!proc2cache_respstream_rdy) begin
        next_state = STATE_WAIT;
      end
      else if (proc2cache_respstream_rdy) begin
        next_state = STATE_IDLE;
      end
    end

    // STATE_INIT_DATA_ACCESS
    if (state == STATE_INIT_DATA_ACCESS) begin 
        next_state = STATE_WAIT;
    end

    // STATE_READ_DATA_ACCESS
    if (state == STATE_READ_DATA_ACCESS) begin 
      next_state = STATE_WAIT;
    end

    // STATE_WRITE_DATA_ACCESS
    if (state == STATE_WRITE_DATA_ACCESS) begin 
      next_state = STATE_WAIT;
    end

    // STATE_EVICT_PREPARE
    if (state == STATE_EVICT_PREPARE) begin
      next_state = STATE_EVICT_REQUEST;
    end 

    // STATE_EVICT_REQUEST
    if (state == STATE_EVICT_REQUEST) begin 
      if (!cache2mem_reqstream_rdy) begin 
        next_state = STATE_EVICT_REQUEST;
      end
      else if (cache2mem_reqstream_rdy) begin 
        next_state = STATE_EVICT_WAIT;
      end
    end

    // STATE_EVICT_WAIT
    if (state == STATE_EVICT_WAIT) begin 
      if (!cache2mem_respstream_val) begin 
        next_state = STATE_EVICT_WAIT;
      end 
      else if (cache2mem_respstream_val) begin 
        next_state = STATE_REFILL_REQUEST;
      end
    end

    // STATE_REFILL_REQUEST
    if (state == STATE_REFILL_REQUEST) begin 
      if (!cache2mem_reqstream_rdy) begin 
        next_state = STATE_REFILL_REQUEST;
      end 
      else if (cache2mem_reqstream_rdy) begin 
        next_state = STATE_REFILL_WAIT;
      end
    end

    // STATE_REFILL_WAIT
    if (state == STATE_REFILL_WAIT) begin 
      if (!cache2mem_respstream_val) begin 
        next_state = STATE_REFILL_WAIT;
      end 
      else if (cache2mem_respstream_val) begin 
        next_state = STATE_REFILL_UPDATE;
      end
    end

    // STATE_REFILL_UPDATE
    if (state == STATE_REFILL_UPDATE) begin 
      if (cachereq_type == 4'd0) begin  // read
        next_state = STATE_READ_DATA_ACCESS;
      end 
      else if (cachereq_type == 4'd1) begin //write
        next_state = STATE_WRITE_DATA_ACCESS;
      end
    end

  end

  // ----------------------------
  // Valid/Dirty 1r1w regfiles 
  // ----------------------------

  localparam int NUM_SETS   = 16;       

  // Regfile write controls (from FSM)
  logic valid_wen;
  logic dirty_wen;

  logic valid_wdata;
  logic dirty_wdata;

  // Index based on number of banks
  logic [3:0] index;
  assign index = (p_num_banks == 4) ? cachereq_addr[9:6] : cachereq_addr[7:4];

  vc_Regfile_1r1w #(1, 16) valid_bits (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_valid),
    .write_en   (valid_wen),
    .write_addr (index),
    .write_data (valid_wdata)
  );

  vc_Regfile_1r1w #(1, 16) dirty_bits (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_dirty),
    .write_en   (dirty_wen),
    .write_addr (index),
    .write_data (dirty_wdata)
  );

  // -----------
  // Hit Logic
  // -----------

  logic [1:0] hit_out;
  logic [1:0] hit_next;

  vc_EnResetReg#(2,0) Hit_reg
  (
    .clk (clk),
    .reset (reset),
    .en (1),
    .d (hit_next),
    .q (hit_out)
  );

  // Next hit state logic
  always_comb begin
    hit_next = hit_out; 
    
    if (state == STATE_TAG_CHECK) begin
      if (cachereq_type == 4'd2) begin // Init
        hit_next = 2'b00;
      end 
      else if (tag_match && is_valid) begin // Hit
        hit_next = 2'b01; 
      end
      else begin // Miss
        hit_next = 2'b00;
      end
    end

    if (state == STATE_IDLE ) begin 
      hit_next = 2'b00; // Reset for new request
    end

    if (state == STATE_REFILL_UPDATE) begin
      hit_next = 2'b00; //Clear after refill
    end
  
  end

  assign hit = hit_out;

  task cs
  (
    input logic        cs_req_rdy,
    input logic        cs_resp_val,
    input logic        cs_memreq_val,
    input logic        cs_memresp_rdy,

    // Dpath Control Signals
    input logic        cs_cachereq_en,
    input logic        cs_memresp_en, 
    input logic        cs_write_data_mux_sel,
    input logic        cs_wben_mux_sel,
    input logic        cs_tag_array_ren,
    input logic        cs_tag_array_wen,
    input logic        cs_data_array_ren,
    input logic        cs_data_array_wen,
    input logic        cs_read_data_reg_en, 
    input logic        cs_read_data_zero_mux_sel,
    input logic        cs_evict_addr_reg_en,
    input logic        cs_mem_req_addr_mux_sel,
    input logic [3:0]  cs_cacheresp_type,
    input logic [3:0]  cs_memreq_type,

    // Valid and Dirty Bits
    input logic cs_valid_wen,
    input logic cs_valid_wdata,
    input logic cs_dirty_wen,
    input logic cs_dirty_wdata,
  );    
    proc2cache_reqstream_rdy  = cs_req_rdy;
    proc2cache_respstream_val = cs_resp_val;
    cache2mem_reqstream_val   = cs_memreq_val;
    cache2mem_respstream_rdy  = cs_memresp_rdy;

    cachereq_en               = cs_cachereq_en;
    memresp_en                = cs_memresp_en;
    write_data_mux_sel        = cs_write_data_mux_sel;
    wben_mux_sel              = cs_wben_mux_sel;
    tag_array_ren             = cs_tag_array_ren;
    tag_array_wen             = cs_tag_array_wen;
    data_array_ren            = cs_data_array_ren;
    data_array_wen            = cs_data_array_wen;
    read_data_reg_en          = cs_read_data_reg_en;
    read_data_zero_mux_sel    = cs_read_data_zero_mux_sel;
    evict_addr_reg_en         = cs_evict_addr_reg_en;
    mem_req_addr_mux_sel      = cs_mem_req_addr_mux_sel;
    cacheresp_type            = cs_cacheresp_type;
    memreq_type               = cs_memreq_type;

    valid_wen                 = cs_valid_wen;
    valid_wdata               = cs_valid_wdata;
    dirty_wen                 = cs_dirty_wen;
    dirty_wdata               = cs_dirty_wdata;
  endtask

  // Control signals table
  always_comb begin

    casez ( state )

      //                             req_   resp_    memreq_  memresp_   cache     mem     wrd  wben    tag    tag    data  data   read     read   evict       mem  cache       mem      valid_  valid_  dirty_  dirty_
      //                             rdy     val       val      val      req_en  resp_en   sel   sel    ren    wen    ren   wen    reg_en   sel    reg_en      sel  resptype  req_type    wen     wdata   wen     wdata 

      STATE_IDLE              :cs(   1'b1 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b1  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );

      STATE_TAG_CHECK         :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b1,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );

      STATE_INIT_DATA_ACCESS  :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b1,  1'b0 , 1'b1 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd2,      4'd0    ,  1'b1,   1'b1,  1'b1,  1'b0  );
      STATE_READ_DATA_ACCESS  :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b1 , 1'b0 , 1'b1,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0   );
      STATE_WRITE_DATA_ACCESS :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b1 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd1,      4'd0    ,  1'b0,   1'b0,  1'b1,  1'b1  );

      STATE_EVICT_PREPARE     :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b1,  1'b0,  1'b1 , 1'b0 , 1'b1,   1'b0 ,  1'b1   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );
      STATE_EVICT_REQUEST     :cs(   1'b0 ,  1'b0 ,   1'b1 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd1    ,  1'b0,   1'b0,  1'b0,  1'b0  );
      STATE_EVICT_WAIT        :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b1  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );

      STATE_REFILL_REQUEST    :cs(   1'b0 ,  1'b0 ,   1'b1 ,   1'b1  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b1 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );
      STATE_REFILL_WAIT       :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b1  ,   1'b0  ,  1'b1 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b1 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0   );
      STATE_REFILL_UPDATE     :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b1,  1'b1,  1'b0,  1'b1,  1'b1 , 1'b1 , 1'b1,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b1,   1'b1,  1'b1,  1'b0  );

      STATE_WAIT              :cs(   1'b0 ,  1'b1 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , cachereq_type,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );

      default                 :cs(   1'b1 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b1  ,  1'b0 ,  1'b0,  1'b0,  1'b0,  1'b0,  1'b0 , 1'b0 , 1'b0,   1'b0 ,  1'b0   ,  1'b0 , 4'd0,      4'd0    ,  1'b0,   1'b0,  1'b0,  1'b0  );

    endcase
  end  

endmodule

`endif
