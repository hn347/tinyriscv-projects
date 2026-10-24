//========================================================================
// Multi-Core System
//========================================================================

`ifndef MULTICORE_MULTI_CORE_SYS_V
`define MULTICORE_MULTI_CORE_SYS_V

`include "vc/mem-msgs.v"
`include "vc/trace.v"

`include "processor/ProcAlt.v"
`include "cache/CacheAlt.v"
`include "multicore/MultiCoreDataCache.v"

module multicore_MultiCoreSys
(
  input  logic          clk,
  input  logic          reset,

  // From mngr streaming ports

  input  logic [31:0]   mngr2proc_msg [4],
  input  logic          mngr2proc_val [4],
  output logic          mngr2proc_rdy [4],

  // To mngr streaming ports

  output logic [31:0]   proc2mngr_msg [4],
  output logic          proc2mngr_val [4],
  input  logic          proc2mngr_rdy [4],

  // Instruction Memory Request Port

  output mem_req_16B_t  imem_reqstream_msg,
  output logic          imem_reqstream_val,
  input  logic          imem_reqstream_rdy,

  // Instruction Memory Response Port

  input  mem_resp_16B_t imem_respstream_msg,
  input  logic          imem_respstream_val,
  output logic          imem_respstream_rdy,

  // Data Memory Request Port

  output mem_req_16B_t  dmem_reqstream_msg,
  output logic          dmem_reqstream_val,
  input  logic          dmem_reqstream_rdy,

  // Data Memory Response Port

  input  mem_resp_16B_t dmem_respstream_msg,
  input  logic          dmem_respstream_val,
  output logic          dmem_respstream_rdy,

  // stats output

  output logic          stats_en,
  output logic [3:0]    commit_inst,
  output logic [3:0]    icache_access,
  output logic [3:0]    icache_miss,
  output logic [3:0]    dcache_access,
  output logic [3:0]    dcache_miss
);

  //----------------------------------------------------------------------
  // Instruction Memory Network
  //----------------------------------------------------------------------

  mem_req_16B_t  icache2imemnet_reqstream_msg  [4];
  logic          icache2imemnet_reqstream_val  [4];
  logic          icache2imemnet_reqstream_rdy  [4];

  mem_resp_16B_t icache2imemnet_respstream_msg [4];
  logic          icache2imemnet_respstream_val [4];
  logic          icache2imemnet_respstream_rdy [4];

  multicore_MemNet imemnet
  (
    .clk                      (clk),
    .reset                    (reset),

    .cache2net_reqstream_msg  (icache2imemnet_reqstream_msg),
    .cache2net_reqstream_val  (icache2imemnet_reqstream_val),
    .cache2net_reqstream_rdy  (icache2imemnet_reqstream_rdy),

    .cache2net_respstream_msg (icache2imemnet_respstream_msg),
    .cache2net_respstream_val (icache2imemnet_respstream_val),
    .cache2net_respstream_rdy (icache2imemnet_respstream_rdy),

    .net2mem_reqstream_msg    (imem_reqstream_msg),
    .net2mem_reqstream_val    (imem_reqstream_val),
    .net2mem_reqstream_rdy    (imem_reqstream_rdy),

    .net2mem_respstream_msg   (imem_respstream_msg),
    .net2mem_respstream_val   (imem_respstream_val),
    .net2mem_respstream_rdy   (imem_respstream_rdy)
  );

  //----------------------------------------------------------------------
  // Instruction Caches
  //----------------------------------------------------------------------

  mem_req_4B_t  proc2icache_reqstream_msg  [4];
  logic         proc2icache_reqstream_val  [4];
  logic         proc2icache_reqstream_rdy  [4];

  mem_resp_4B_t proc2icache_respstream_msg [4];
  logic         proc2icache_respstream_val [4];
  logic         proc2icache_respstream_rdy [4];

  genvar i;
  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: ICACHE

    cache_CacheAlt icache
    (
      .clk                       (clk),
      .reset                     (reset),

      .proc2cache_reqstream_msg  (proc2icache_reqstream_msg[i]),
      .proc2cache_reqstream_val  (proc2icache_reqstream_val[i]),
      .proc2cache_reqstream_rdy  (proc2icache_reqstream_rdy[i]),

      .proc2cache_respstream_msg (proc2icache_respstream_msg[i]),
      .proc2cache_respstream_val (proc2icache_respstream_val[i]),
      .proc2cache_respstream_rdy (proc2icache_respstream_rdy[i]),

      .cache2mem_reqstream_msg   (icache2imemnet_reqstream_msg[i]),
      .cache2mem_reqstream_val   (icache2imemnet_reqstream_val[i]),
      .cache2mem_reqstream_rdy   (icache2imemnet_reqstream_rdy[i]),

      .cache2mem_respstream_msg  (icache2imemnet_respstream_msg[i]),
      .cache2mem_respstream_val  (icache2imemnet_respstream_val[i]),
      .cache2mem_respstream_rdy  (icache2imemnet_respstream_rdy[i])
    );

  end
  endgenerate

  //----------------------------------------------------------------------
  // Processors
  //----------------------------------------------------------------------

  mem_req_4B_t  proc2dcache_reqstream_msg  [4];
  logic         proc2dcache_reqstream_val  [4];
  logic         proc2dcache_reqstream_rdy  [4];

  mem_resp_4B_t proc2dcache_respstream_msg [4];
  logic         proc2dcache_respstream_val [4];
  logic         proc2dcache_respstream_rdy [4];

  logic         commit_insts [4];
  logic         stats_ens    [4];

  generate
  for ( i = 0; i < 4; i = i + 1 ) begin: PROC

    processor_ProcAlt
    #(
      .p_num_cores         (4)
    )
    proc
    (
      .clk                 (clk),
      .reset               (reset),

      // Manager <-> Proc Interface

      .mngr2proc_msg       (mngr2proc_msg[i]),
      .mngr2proc_val       (mngr2proc_val[i]),
      .mngr2proc_rdy       (mngr2proc_rdy[i]),

      .proc2mngr_msg       (proc2mngr_msg[i]),
      .proc2mngr_val       (proc2mngr_val[i]),
      .proc2mngr_rdy       (proc2mngr_rdy[i]),

      // Processor <-> Instruction Cache Interface

      .imem_reqstream_msg  (proc2icache_reqstream_msg[i]),
      .imem_reqstream_val  (proc2icache_reqstream_val[i]),
      .imem_reqstream_rdy  (proc2icache_reqstream_rdy[i]),

      .imem_respstream_msg (proc2icache_respstream_msg[i]),
      .imem_respstream_val (proc2icache_respstream_val[i]),
      .imem_respstream_rdy (proc2icache_respstream_rdy[i]),

      // Processor <-> Data Cache Interface

      .dmem_reqstream_msg  (proc2dcache_reqstream_msg[i]),
      .dmem_reqstream_val  (proc2dcache_reqstream_val[i]),
      .dmem_reqstream_rdy  (proc2dcache_reqstream_rdy[i]),

      .dmem_respstream_msg (proc2dcache_respstream_msg[i]),
      .dmem_respstream_val (proc2dcache_respstream_val[i]),
      .dmem_respstream_rdy (proc2dcache_respstream_rdy[i]),

      // Stats

      .core_id             (i[1:0]),
      .stats_en            (stats_ens[i]),
      .commit_inst         (commit_insts[i])
    );

    assign commit_inst[i] = commit_insts[i];
  end
  endgenerate

  assign stats_en    = stats_ens[0];

  //----------------------------------------------------------------------
  // Data Cache
  //----------------------------------------------------------------------

  multicore_MultiCoreDataCache dcache
  (
    .clk                       (clk),
    .reset                     (reset),

    .proc2cache_reqstream_msg  (proc2dcache_reqstream_msg),
    .proc2cache_reqstream_val  (proc2dcache_reqstream_val),
    .proc2cache_reqstream_rdy  (proc2dcache_reqstream_rdy),

    .proc2cache_respstream_msg (proc2dcache_respstream_msg),
    .proc2cache_respstream_val (proc2dcache_respstream_val),
    .proc2cache_respstream_rdy (proc2dcache_respstream_rdy),

    .cache2mem_reqstream_msg   (dmem_reqstream_msg),
    .cache2mem_reqstream_val   (dmem_reqstream_val),
    .cache2mem_reqstream_rdy   (dmem_reqstream_rdy),

    .cache2mem_respstream_msg  (dmem_respstream_msg),
    .cache2mem_respstream_val  (dmem_respstream_val),
    .cache2mem_respstream_rdy  (dmem_respstream_rdy)
  );

  //----------------------------------------------------------------------
  // Stats
  //----------------------------------------------------------------------
  // Eventually we need to figure out how to handle these.

  generate 
    for( i = 0; i < 4; i = i + 1 ) begin: STATS
      assign icache_access[i] = proc2icache_reqstream_val[i]  & proc2icache_reqstream_rdy[i];
      assign icache_miss[i]   = proc2icache_respstream_val[i] & proc2icache_respstream_rdy[i] & ~proc2icache_respstream_msg[i].test[0];
      assign dcache_access = proc2dcache_reqstream_val[i]  & proc2dcache_reqstream_rdy[i];
      assign dcache_miss   = proc2dcache_respstream_val[i] & proc2dcache_respstream_rdy[i] & ~proc2dcache_respstream_msg[i].test[0];
    end
  endgenerate

  //----------------------------------------------------------------------
  // Line Traceing
  //----------------------------------------------------------------------
  // If you use different instance names for your processor and caches,
  // you may need to update the line tracing logic.

  `ifndef SYNTHESIS

  `VC_TRACE_BEGIN
  begin

    vc_trace.append_str( trace_str, "(" );
    ICACHE[0].icache.line_trace( trace_str );
    vc_trace.append_str( trace_str, ") " );
    PROC[0].proc.line_trace( trace_str );

    vc_trace.append_str( trace_str, " " );

    vc_trace.append_str( trace_str, "(" );
    ICACHE[1].icache.line_trace( trace_str );
    vc_trace.append_str( trace_str, ") " );
    PROC[1].proc.line_trace( trace_str );

    vc_trace.append_str( trace_str, " " );

    vc_trace.append_str( trace_str, "(" );
    ICACHE[2].icache.line_trace( trace_str );
    vc_trace.append_str( trace_str, ") " );
    PROC[2].proc.line_trace( trace_str );

    vc_trace.append_str( trace_str, " " );

    vc_trace.append_str( trace_str, "(" );
    ICACHE[3].icache.line_trace( trace_str );
    vc_trace.append_str( trace_str, ") " );
    PROC[3].proc.line_trace( trace_str );

    vc_trace.append_str( trace_str, " " );

    dcache.line_trace( trace_str );
  end
  `VC_TRACE_END

   `endif /* SYNTHESIS */

endmodule

`endif /* MULTICORE_MULTI_CORE_SYS_V */
