//=========================================================================
// Alt Blocking Cache Control
//=========================================================================

`ifndef CACHE_CACHE_ALT_CTRL_V
`define CACHE_CACHE_ALT_CTRL_V

`include "vc/trace.v"
`include "vc/regfiles.v"
`include "vc/mem-msgs.v"

module cache_CacheAltCtrl
#(
  parameter p_num_banks = 1
)
(
  input  logic        clk,
  input  logic        reset,

  // Processor <-> Cache Interface

  input  logic        proc2cache_reqstream_val,
  output logic        proc2cache_reqstream_rdy,

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
  
  // Outputs to datapath
  output logic        cachereq_en,
  output logic        memresp_en, 
  output logic        write_data_mux_sel,
  output logic        wben_mux_sel,
  output logic        data_array_ren,
  output logic        data_array_wen,
  output logic        tag_array_ren,
  output logic        tag_array_wen_way0,
  output logic        tag_array_wen_way1,
  output logic        read_data_reg_en, 
  output logic        read_data_zero_mux_sel,
  output logic        evict_addr_reg_en,
  output logic        mem_req_addr_mux_sel,
  output logic [3:0]  cacheresp_type,
  output logic        hit,
  output logic [3:0]  memreq_type,

  // new alt control signals
  output logic        way_sel,
  input  logic        tag_w0_match,
  input  logic        tag_w1_match,
  output logic        victim,
  output logic        victim_mux_sel

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

  // is-valid and is-dirty bits for each way
  logic valid_way0;
  logic valid_way1;
  logic dirty_way0;
  logic dirty_way1;

  // FSM state update
  always_ff @(posedge clk or posedge reset) begin
    if (reset) state <= STATE_IDLE;
    else       state <= next_state;
  end

  // State FSM
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
      else if (hit_w0 || hit_w1) begin
        next_state = (cachereq_type==4'd0) ? STATE_READ_DATA_ACCESS
                                          : STATE_WRITE_DATA_ACCESS;
      end
      else begin
        // free way
        if (!valid_way0 || !valid_way1) begin
          next_state = STATE_REFILL_REQUEST; 
        end 
        else begin
          if ( (victim_sel==1'b0 && dirty_way0) || (victim_sel==1'b1 && dirty_way1) )
            next_state = STATE_EVICT_PREPARE; //dirty victim
          else
            next_state = STATE_REFILL_REQUEST; //clean victim
        end
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

  // valid/dirty write enables
  logic valid_wen_way0;
  logic valid_wen_way1;
  logic dirty_wen_way0;
  logic dirty_wen_way1;

  // valid/dirty regfiles
  logic valid_wdata_way0;
  logic valid_wdata_way1;
  logic dirty_wdata_way0;
  logic dirty_wdata_way1;

  // hit detection
  logic hit_w0;
  logic hit_w1;
  assign hit_w0 = tag_w0_match & valid_way0;
  assign hit_w1 = tag_w1_match & valid_way1;

  // sets index
  logic [2:0] index;
  assign index = (p_num_banks == 4) ? cachereq_addr[8:6] : cachereq_addr[6:4];

  vc_Regfile_1r1w #(1, 8) valid_bits_way0 (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (valid_way0),
    .write_en   (valid_wen_way0),
    .write_addr (index),
    .write_data (valid_wdata_way0)
  );

  vc_Regfile_1r1w #(1, 8) valid_bits_way1 (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (valid_way1),
    .write_en   (valid_wen_way1),
    .write_addr (index),
    .write_data (valid_wdata_way1)
  );

  vc_Regfile_1r1w #(1, 8) dirty_bits_way0 (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (dirty_way0),
    .write_en   (dirty_wen_way0),
    .write_addr (index),
    .write_data (dirty_wdata_way0)
  );

  vc_Regfile_1r1w #(1, 8) dirty_bits_way1 (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (dirty_way1),
    .write_en   (dirty_wen_way1),
    .write_addr (index),
    .write_data (dirty_wdata_way1)
  );

  // -----------
  // LRU
  // -----------
  logic use_bit_read;     
  logic use_bit_wdata;
  logic use_bit_wen;

  vc_Regfile_1r1w #(1, 8) use_bits (  
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),        
    .read_data  (use_bit_read), 
    .write_en   (use_bit_wen),
    .write_addr (index),
    .write_data (use_bit_wdata)
  );

  // -----------
  // Victim
  // -----------
  logic victim_sel;

  always_comb begin
    if (!valid_way0) begin
      victim_sel = 1'b0; // if way0 invalid -> use way0 as victim
    end
    else if (!valid_way1) begin 
      victim_sel = 1'b1; // if way1 invalid -> use way1 as victim
    end
    else begin 
      victim_sel = use_bit_read; // both valid -> use LRU
    end
  end

  assign victim = victim_sel; // send to dpath

  always_comb begin
    // default
    way_sel_next = victim_sel;

    if (cachereq_type == 4'd2) begin // INIT request 
      if (!valid_way0) begin 
        way_sel_next = 1'b0; // prefer empty way0
      end
      else if (!valid_way1) begin
        way_sel_next = 1'b1;  //empty way1
      end
      else begin
        way_sel_next = 1'b0; // both valid -> pick way0 for INIT
      end
    end
    else if (hit_w0) begin 
      way_sel_next = 1'b0; // read/write hit in way0 -> use way0
    end
    else if (hit_w1) begin 
      way_sel_next = 1'b1; // read/write hit in way1 -> use way1
    end
    else begin 
      way_sel_next = victim_sel; // miss -> use victim
    end
  end

  // -----------
  // Hit Logic
  // -----------

  logic hit_out;
  logic hit_next;

  vc_EnResetReg#(1,0) hit_reg
  (
    .clk (clk),
    .reset (reset),
    .en (1'b1),
    .d (hit_next),
    .q (hit_out)
  );

  // hit logic
  always_comb begin
    hit_next = hit_out; 
    
    if (state == STATE_TAG_CHECK) begin
      if (cachereq_type == 4'd2) begin // Init
        hit_next = 1'b0; // init does not count as hit
      end 
      else begin
        hit_next = (hit_w0 || hit_w1); // normal hit if either way matches and is valid
      end
    end
    if (state == STATE_IDLE) begin
      hit_next = 1'b0;  // clears when idle (new transcation coming)
    end
    if (state == STATE_REFILL_UPDATE) begin
      hit_next = 1'b0;  
    end
  end

  assign hit = hit_out; // send to dpath

  // ----------------------
  // Way select logic
  // ----------------------

  logic way_sel_reg_out;
  logic way_sel_next;

  vc_EnResetReg#(1,0) way_sel_reg 
  (
    .clk   (clk),
    .reset (reset),
    .en    (state == STATE_TAG_CHECK),
    .d     (hit_w1 ? 1'b1 :
            hit_w0 ? 1'b0 :
            way_sel_next), 
    .q     (way_sel_reg_out)
  );

  assign way_sel = way_sel_reg_out;

  assign victim_mux_sel = (state==STATE_EVICT_PREPARE) || (state==STATE_EVICT_REQUEST) || (state==STATE_EVICT_WAIT) || (state==STATE_REFILL_UPDATE);

  //-------------------------------------
  // Valid/Dirty/Tag/LRU State Updates
  //-------------------------------------

  always_comb begin
    // defaults
    valid_wen_way0 = 0; 
    valid_wen_way1 = 0; 
    dirty_wen_way0 = 0; 
    dirty_wen_way1 = 0;

    valid_wdata_way0 = 1; // valid -> 1
    valid_wdata_way1 = 1; 
    dirty_wdata_way0 = 0; // dirty -> cleared on refill/init
    dirty_wdata_way1 = 0; 

    tag_array_wen_way0 = 0; 
    tag_array_wen_way1 = 0;

    use_bit_wen = 0; 
    use_bit_wdata = 0;

    // INIT: allocate a line
    if (state == STATE_INIT_DATA_ACCESS) begin
      if (way_sel == 1'b0) begin
        valid_wen_way0 = 1;
        dirty_wen_way0 = 1; 
        dirty_wdata_way0 = 0; 
        tag_array_wen_way0 = 1;
      end
      else begin
        valid_wen_way1 = 1; 
        dirty_wen_way1 = 1; 
        dirty_wdata_way1 = 0; 
        tag_array_wen_way1 = 1;
      end
    end

    // READ hit: update LRU/use bit (non-hit way becomes LRU)
    if (state == STATE_READ_DATA_ACCESS && (hit_w0 || hit_w1)) begin
      use_bit_wen   = 1;
      use_bit_wdata = hit_w0 ? 1'b1 : 1'b0;
    end

    // WRITE hit: mark that line dirty and update LRU/use bit
    if (state == STATE_WRITE_DATA_ACCESS && (hit_w0 || hit_w1)) begin
      if (hit_w0) begin 
        dirty_wen_way0 = 1; 
        dirty_wdata_way0 = 1; end
      else begin 
        dirty_wen_way1 = 1; 
        dirty_wdata_way1 = 1; 
      end
      use_bit_wen   = 1;
      use_bit_wdata = hit_w0 ? 1'b1 : 1'b0;
    end

    // REFILL install: write tag, set valid=1, clear dirty
    // update LRU so the other way becomes LRU
    if (state == STATE_REFILL_UPDATE) begin
        if (way_sel == 1'b0) begin
          valid_wen_way0 = 1; 
          dirty_wen_way0 = 1; 
          dirty_wdata_way0 = 0;
          tag_array_wen_way0 = 1;
        end
        else begin
          valid_wen_way1 = 1; 
          dirty_wen_way1 = 1; 
          dirty_wdata_way1 = 0; 
          tag_array_wen_way1 = 1;
        end
        use_bit_wen   = 1;
        use_bit_wdata = ~way_sel; 
      end
  end


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
    input logic        cs_data_array_ren,
    input logic        cs_data_array_wen,
    input logic        cs_tag_array_ren,
    input logic        cs_read_data_reg_en, 
    input logic        cs_read_data_zero_mux_sel,
    input logic        cs_evict_addr_reg_en,
    input logic        cs_mem_req_addr_mux_sel,
    input logic [3:0]  cs_cacheresp_type,
    input logic [3:0]  cs_memreq_type,
  );    
    proc2cache_reqstream_rdy  = cs_req_rdy;
    proc2cache_respstream_val = cs_resp_val;
    cache2mem_reqstream_val   = cs_memreq_val;
    cache2mem_respstream_rdy  = cs_memresp_rdy;

    cachereq_en               = cs_cachereq_en;
    memresp_en                = cs_memresp_en;
    write_data_mux_sel        = cs_write_data_mux_sel;
    wben_mux_sel              = cs_wben_mux_sel;
    data_array_ren            = cs_data_array_ren;
    data_array_wen            = cs_data_array_wen;
    tag_array_ren             = cs_tag_array_ren;
    read_data_reg_en          = cs_read_data_reg_en;
    read_data_zero_mux_sel    = cs_read_data_zero_mux_sel;
    evict_addr_reg_en         = cs_evict_addr_reg_en;
    mem_req_addr_mux_sel      = cs_mem_req_addr_mux_sel;
    cacheresp_type            = cs_cacheresp_type;
    memreq_type               = cs_memreq_type;

  endtask

  always_comb begin

    casez ( state )

      //                             req_   resp_    memreq_  memresp_   cache     mem     wrd  wben    data  data   tag   read    read   evict   mem    cache       mem   
      //                             rdy     val       val      val      req_en  resp_en   sel   sel    ren   wen    ren   reg_en  sel    reg_en  sel    resptype  req_type

      STATE_IDLE              :cs(   1'b1 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b1  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0,   1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );

      STATE_TAG_CHECK         :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b1, 1'b0,   1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );

      STATE_INIT_DATA_ACCESS  :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b1,  1'b0, 1'b1,   1'b0,  1'b0,   1'b0,   4'd2,      4'd0  );
      
      STATE_WAIT              :cs(   1'b0 ,  1'b1 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0 ,  1'b0,  1'b0,   1'b0,cachereq_type,4'd0  );

      STATE_READ_DATA_ACCESS  :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b1, 1'b0,  1'b1, 1'b1,   1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );
      
      STATE_WRITE_DATA_ACCESS :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b1,  1'b1, 1'b0,   1'b0,  1'b0,   1'b0,   4'd1,      4'd0  );

      STATE_EVICT_PREPARE     :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b1, 1'b0,  1'b1, 1'b1,   1'b0,  1'b1,   1'b0,   4'd0,      4'd0  );
      
      STATE_EVICT_REQUEST     :cs(   1'b0 ,  1'b0 ,   1'b1 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0,   1'b0,  1'b0,   1'b0,   4'd0,      4'd1  );
      
      STATE_EVICT_WAIT        :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b1  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0,   1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );

      STATE_REFILL_REQUEST    :cs(   1'b0 ,  1'b0 ,   1'b1 ,   1'b1  ,   1'b0  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0,   1'b0,  1'b0,   1'b1,   4'd0,      4'd0  );
      
      STATE_REFILL_WAIT       :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b1  ,   1'b0  ,  1'b1 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0,   1'b0,  1'b0,   1'b1,   4'd0,      4'd0  );
      
      STATE_REFILL_UPDATE     :cs(   1'b0 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b0  ,  1'b0 ,  1'b1,  1'b1,  1'b1, 1'b1,  1'b0, 1'b1,   1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );

      default                 :cs(   1'b1 ,  1'b0 ,   1'b0 ,   1'b0  ,   1'b1  ,  1'b0 ,  1'b0,  1'b0,  1'b0, 1'b0,  1'b0, 1'b0 ,  1'b0,  1'b0,   1'b0,   4'd0,      4'd0  );

    endcase
  end  

endmodule

`endif
