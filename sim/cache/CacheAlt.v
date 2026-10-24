//=========================================================================
// Alt Blocking Cache
//=========================================================================

`ifndef CACHE_CACHE_ALT_V
`define CACHE_CACHE_ALT_V

`include "vc/mem-msgs.v"
`include "vc/trace.v"
`include "vc/muxes.v"
`include "vc/regs.v"

`include "cache/CacheAltCtrl.v"
`include "cache/CacheAltDpath.v"

module cache_CacheAlt
#(
  parameter p_num_banks = 1 // Total number of cache banks
)
(
  input  logic          clk,
  input  logic          reset,

  // Processor <-> Cache Interface

  input  mem_req_4B_t   proc2cache_reqstream_msg,
  input  logic          proc2cache_reqstream_val,
  output logic          proc2cache_reqstream_rdy,

  output mem_resp_4B_t  proc2cache_respstream_msg,
  output logic          proc2cache_respstream_val,
  input  logic          proc2cache_respstream_rdy,

  // Cache <-> Memory Interface

  output mem_req_16B_t  cache2mem_reqstream_msg,
  output logic          cache2mem_reqstream_val,
  input  logic          cache2mem_reqstream_rdy,

  input  mem_resp_16B_t cache2mem_respstream_msg,
  input  logic          cache2mem_respstream_val,
  output logic          cache2mem_respstream_rdy
);

  logic        cachereq_en;
  logic [3:0]  cachereq_type;
  logic        memresp_en; 
  logic        write_data_mux_sel;
  logic        wben_mux_sel;

  logic        data_array_ren;
  logic        data_array_wen;
  logic        tag_array_ren;
  logic        tag_array_wen_way0;
  logic        tag_array_wen_way1;
  logic [31:0] cachereq_addr;
  logic        read_data_reg_en;
  logic        read_data_zero_mux_sel;
  logic        evict_addr_reg_en;
  logic        mem_req_addr_mux_sel;
  logic [3:0]  cacheresp_type;
  logic        hit;
  logic [3:0]  memreq_type;
  
  // new alt control signals
  logic        way_sel;
  logic        tag_w0_match;
  logic        tag_w1_match;
  logic        victim;
  logic        victim_mux_sel;

  //----------------------------------------------------------------------
  // Control
  //----------------------------------------------------------------------

  cache_CacheAltCtrl
  #(
    .p_num_banks              (p_num_banks)
  )
  ctrl
  (
   .clk                      (clk),
   .reset                    (reset),
   // Processor <-> Cache Interface

   .proc2cache_reqstream_val  (proc2cache_reqstream_val),
   .proc2cache_reqstream_rdy  (proc2cache_reqstream_rdy),
   .proc2cache_respstream_val (proc2cache_respstream_val),
   .proc2cache_respstream_rdy (proc2cache_respstream_rdy),

   // Cache <-> Memory Interface

   .cache2mem_reqstream_val   (cache2mem_reqstream_val),
   .cache2mem_reqstream_rdy   (cache2mem_reqstream_rdy),
   .cache2mem_respstream_val  (cache2mem_respstream_val),
   .cache2mem_respstream_rdy  (cache2mem_respstream_rdy),

   // clk/reset/control/status signals
   .cachereq_type(cachereq_type),
   .cachereq_addr(cachereq_addr),
    
   // Outputs to datapath
   .cachereq_en(cachereq_en),
   .memresp_en(memresp_en), 
   .write_data_mux_sel(write_data_mux_sel),
   .wben_mux_sel(wben_mux_sel),
   .data_array_ren(data_array_ren),
   .data_array_wen(data_array_wen),
   .tag_array_ren(tag_array_ren),
   .tag_array_wen_way0(tag_array_wen_way0),
   .tag_array_wen_way1(tag_array_wen_way1),
   .read_data_reg_en(read_data_reg_en), 
   .read_data_zero_mux_sel(read_data_zero_mux_sel),
   .evict_addr_reg_en(evict_addr_reg_en),
   .mem_req_addr_mux_sel(mem_req_addr_mux_sel),
   .cacheresp_type(cacheresp_type),
   .hit(hit),
   .memreq_type(memreq_type),
   .way_sel(way_sel),
   .tag_w0_match(tag_w0_match),      
   .tag_w1_match(tag_w1_match),
   .victim(victim),              
   .victim_mux_sel(victim_mux_sel) 

  );

  //----------------------------------------------------------------------
  // Datapath
  //----------------------------------------------------------------------

  cache_CacheAltDpath
  #(
    .p_num_banks              (p_num_banks)
  )
  dpath
  (
   .clk                      (clk),
   .reset                    (reset),
   // Processor <-> Cache Interface

   .proc2cache_reqstream_msg  (proc2cache_reqstream_msg),
   .proc2cache_respstream_msg (proc2cache_respstream_msg),

   // Cache <-> Memory Interface

   .cache2mem_reqstream_msg   (cache2mem_reqstream_msg),
   .cache2mem_respstream_msg  (cache2mem_respstream_msg),

    // clk/reset/control/status signals

   .cachereq_type(cachereq_type),
   .cachereq_addr(cachereq_addr),
  //  .tag_match(tag_match),
    
   // Outputs to datapath
   .cachereq_en(cachereq_en),
   .memresp_en(memresp_en), 
   .write_data_mux_sel(write_data_mux_sel),
   .wben_mux_sel(wben_mux_sel),
   .data_array_ren(data_array_ren),
   .data_array_wen(data_array_wen),
   .tag_array_ren(tag_array_ren),
   .tag_array_wen_way0(tag_array_wen_way0),
   .tag_array_wen_way1(tag_array_wen_way1),
   .read_data_reg_en(read_data_reg_en), 
   .read_data_zero_mux_sel(read_data_zero_mux_sel),
   .evict_addr_reg_en(evict_addr_reg_en),
   .mem_req_addr_mux_sel(mem_req_addr_mux_sel),
   .cacheresp_type(cacheresp_type),
   .hit(hit),
   .memreq_type(memreq_type),
   .way_sel(way_sel),
   .tag_w0_match(tag_w0_match),      
   .tag_w1_match(tag_w1_match),
   .victim(victim),              
   .victim_mux_sel(victim_mux_sel)   
  );

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    // Minimal line trace - just show the state
    vc_trace.append_str( trace_str, "(" );
    
    case ( ctrl.state )
      ctrl.STATE_IDLE:              vc_trace.append_str( trace_str, "I " );
      ctrl.STATE_TAG_CHECK:         vc_trace.append_str( trace_str, "TC" );
      ctrl.STATE_INIT_DATA_ACCESS:  vc_trace.append_str( trace_str, "IN" );
      ctrl.STATE_READ_DATA_ACCESS:  vc_trace.append_str( trace_str, "RD" );
      ctrl.STATE_WRITE_DATA_ACCESS: vc_trace.append_str( trace_str, "WD" );
      ctrl.STATE_REFILL_REQUEST:    vc_trace.append_str( trace_str, "RR" );
      ctrl.STATE_REFILL_WAIT:       vc_trace.append_str( trace_str, "RW" );
      ctrl.STATE_REFILL_UPDATE:     vc_trace.append_str( trace_str, "RU" );
      ctrl.STATE_EVICT_PREPARE:     vc_trace.append_str( trace_str, "EP" );
      ctrl.STATE_EVICT_REQUEST:     vc_trace.append_str( trace_str, "ER" );
      ctrl.STATE_EVICT_WAIT:        vc_trace.append_str( trace_str, "EW" );
      ctrl.STATE_WAIT:              vc_trace.append_str( trace_str, "W " );
      default:                      vc_trace.append_str( trace_str, "? " );
    endcase
    
    vc_trace.append_str( trace_str, ")" );
  end
  `VC_TRACE_END

  // These trace modules are useful because they breakout all the
  // individual fields so you can see them in gtkwave

  vc_MemReqMsg4BTrace proc2cache_reqstream_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (proc2cache_reqstream_val),
    .rdy   (proc2cache_reqstream_rdy),
    .msg   (proc2cache_reqstream_msg)
  );

  vc_MemRespMsg4BTrace proc2cache_respstream_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (proc2cache_respstream_val),
    .rdy   (proc2cache_respstream_val),
    .msg   (proc2cache_respstream_msg)
  );

  vc_MemReqMsg16BTrace cache2mem_reqstream_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (cache2mem_reqstream_val),
    .rdy   (cache2mem_reqstream_rdy),
    .msg   (cache2mem_reqstream_msg)
  );

  vc_MemRespMsg16BTrace cache2mem_respstream_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (cache2mem_respstream_val),
    .rdy   (cache2mem_respstream_rdy),
    .msg   (cache2mem_respstream_msg)
  );

  `endif

endmodule

`endif
