# Performance engineering

## Define the workload

Choose a user-relevant metric and a reproducible input: load time, typing latency,
scrolling/frame latency, throughput, memory, query count, build size or export time.
Record input size/distribution, machine, OS/runtime/compiler, build mode, cache
state, concurrency and measurement method. Keep private inputs out of public artifacts.

Measure before changing code. Warm up when the workload needs it. Collect repeated
samples and inspect median, spread and outliers; use tail latency where user impact
requires it. Avoid comparing debug against release, different hardware, smaller
inputs or warm-cache against cold-cache runs.

## Find the cause

Profile the actual operation. Separate CPU work, I/O waiting, allocations, memory
retention, network/query fan-out and UI invalidation/rendering. Trace the expensive
path to its callers. Prefer reducing unnecessary work and improving algorithms or
data access before introducing caches, background workers or new infrastructure.

Validate correctness while optimising. Cache invalidation, cancellation, stale
responses, thread ownership and partial failure can change behaviour. A faster
incorrect operation is a regression. Keep appropriate regression tests.

## Compare and report

Repeat the same workload under comparable conditions after the final changes.
Record both source snapshots and actual samples. Explain measurement overhead and
noise. Report a small uncertain difference as uncertain; do not invent a causal
performance claim from a single timing.

The optional `scripts/bench.py` collects process wall-clock samples. It includes
process startup/output capture and is unsuitable for direct internal typing,
frame-latency or memory claims. For those, use the host's profiler or an instrumented
workload and export the actual metric into the benchmark record format. `compare`
rejects mismatched identity, units, workload, direction and environment.

Examples from the application root:

```sh
python3 "<EVOLVE_ROOT>/scripts/bench.py" run --name import --workload fixture-1000 --machine "<runner identity>" --runtime "<actual runtime>" --mode release --output .evolve/import-before.json -- <command> <args>
# Run the same invocation after implementation with import-after.json.
python3 "<EVOLVE_ROOT>/scripts/bench.py" compare .evolve/import-before.json .evolve/import-after.json --max-regression 5
```

A regression threshold is workload/project-specific. The example's 5% is not a
universal acceptance target. Recheck neighbouring workloads and resource usage
when a speedup might trade memory, startup cost or correctness.
