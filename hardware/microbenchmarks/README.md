# Microbenchmarks
This are targeted CUDA programs for specific operation measurements

## Kernel Launch Overhead
Change the file paths and architecture arguments below as necessary.
To build:
* A100: nvcc -O3 -std=c++17 -arch=sm_80 launch_overhead_bench.cu -o launch_overhead_bench
* H100: nvcc -O3 -std=c++17 -arch=sm_90 launch_overhead_bench.cu -o launch_overhead_bench
* B200: nvcc -O3 -std=c++17 -arch=sm_100 launch_overhead_bench.cu -o launch_overhead_bench
* Then run the script ./run_launch_overhead.py. This runs 4 configurations on the GPU and collects metrics then makes a linear model. Results are printed to a JSON file in hardware/runs/.
