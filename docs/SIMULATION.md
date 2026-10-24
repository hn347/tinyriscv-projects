# Simulation and testing

## Environment

The simulation framework requires Python, PyMTL3, and pytest. RTL models use Verilator and a C++ toolchain through PyMTL3's Verilog backend. Exact compatible versions were not recorded in the source, so the inherited course environment is the best starting point; the commands below are usage examples for an already configured environment, not a verified installation procedure.

Building application binaries additionally requires a compatible RISC-V cross compiler. The application configuration includes `riscv64-unknown-elf` and `riscv64-unknown-linux-gnu` targets with RV32IM/Zicsr and ILP32 compiler flags. The processor supports TinyRV2, so binaries must use instructions supported by that subset.

## Keep generated files separate

From the repository root:

```bash
mkdir -p sim/build
cd sim/build
```

Run the remaining commands from this directory. The four project directories depend on one another through Python imports and Verilog includes; retain the complete `sim/` tree.

## Existing test suites

```bash
python -m pytest ../imul
python -m pytest ../processor
python -m pytest ../cache
python -m pytest ../multicore
```

There are 4 multiplier, 23 processor, 5 cache, and 17 multicore/network test modules. These counts describe source files, not the number of parametrized test cases or passing results.

## Standalone simulators

```bash
# Multiplier: same workload, two implementations
python ../imul/imul-sim --impl base --input small --stats
python ../imul/imul-sim --impl alt --input small --stats

# Processor: run and verify a vector-addition microbenchmark
python ../processor/proc-sim --impl alt --input vvadd-unopt --verify --stats

# Cache: run a synthetic access pattern
python ../cache/mem-sim --impl alt --input loop1 --stats
```

The multiplier, processor, and cache drivers support `fl`, `base`, and `alt` implementations: functional reference, baseline RTL, and alternative RTL. Use `--help` to inspect supported inputs and tracing options. `--stats` provides workload-specific statistics; no example output or speedup is asserted here because these commands have not been rerun in the current environment.

## Integrated system simulation

[`sys-sim`](../sim/multicore/sys-sim) takes a TinyRV2 ELF binary. It does not accept the assembly workload names used by `proc-sim`.

```bash
python ../multicore/sys-sim --help
```

Implementation choices are `score-fl` (single-core functional), `mcore-fl` (multicore functional), `base` (single-core RTL), and `alt` (multicore RTL). The `app/` tree supplies application source, runtime support, Autoconf configuration, and linker scripts. Generated binaries and build directories are excluded.

## Validation recorded for this repository

After replacing the original numbered project namespaces with `imul`, `processor`, `cache`, and `multicore`:

- 135 Python source files and simulator scripts passed syntax parsing.
- 275 project-local Python imports resolved to files or packages.
- 167 active Verilog include references resolved to local files.
- The prepared source and initial uploaded repository had identical Git tree hashes.

These are static packaging checks. They do not establish hardware correctness, test-suite success, synthesis results, timing, area, or benchmark performance. Hardware simulations still need to be rerun in a configured environment.
