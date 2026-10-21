# GASP Custom Benchmarks
This repo includes custom CUDA benchmarks we have prepared for development/experimentation


## Profiling

We can run a kernel to get the profile:

For example with the `vecadd.cu` program:

```sh
ncu --metrics gpu__time_duration.avg,smsp__inst_executed.sum,smsp__inst_executed_op_global_ld.sum,smsp__inst_executed_op_global_st.sum,l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum,l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum,lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum,lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum,sm__warps_active.avg.pct_of_peak_sustained_active --csv ./vecadd 1000000
```

This outputs csv, which we can convert to JSON with `./scripts/csv_to_json.py`

