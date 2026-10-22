#include <stdio.h>
#include <cuda_runtime.h>
#include <stdio.h>
#include <cuda_runtime.h>

#define WARMUP_ITERATIONS 100
#define TOTAL_OPERATIONS 1024
#define MEASURED_ITERATIONS 100

__global__ void fp32_latency_kernel(float *out) {
    float x = 1.0001f;

    // Prevent loop unrolling
    #pragma unroll 1
    for (int i = 0; i < TOTAL_OPERATIONS; i++) {
        // Execute PTX as is
        asm volatile("add.f32 %0, %0, %0;" : "+f"(x));
    }

    // Store result to prevent compiler optimization
    if (threadIdx.x == 0) {
        out[0] = x;
    }
}


int main(){
    float *d_out;
    cudaMalloc(&d_out, sizeof(float));

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    // Warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        fp32_latency_kernel<<<1, 1>>>(d_out);
    }
    cudaDeviceSynchronize();

    // Measure — single thread, single block to isolate latency
    cudaEventRecord(start);
    for (int i = 0; i < MEASURED_ITERATIONS; i++) {
        fp32_latency_kernel<<<1, 1>>>(d_out);
    }
    cudaEventRecord(stop);
    cudaDeviceSynchronize();

    float ms = 0;
    cudaEventElapsedTime(&ms, start, stop);

    // Get clock rate for cycle conversion
    int clock_khz;
    cudaDeviceGetAttribute(&clock_khz, cudaDevAttrClockRate, 0);
    float clock_ghz = clock_khz / 1e6f;

    float total_ops = (float)TOTAL_OPERATIONS * MEASURED_ITERATIONS;
    float ns_per_op = (ms * 1e6f) / total_ops;
    float cycles_per_op = ns_per_op * clock_ghz;


    printf("P32 FADD latency microbenchmark\n");
    printf("\tClock Speed:\t%.2f GHz\n", clock_ghz);
    printf("\tTotal Operations:\t%d\n", TOTAL_OPERATIONS);
    printf("\nMeasured Iterations:\t%d\n", MEASURED_ITERATIONS);
    printf("nanosecs per op:\t%.2f\n", ns_per_op);
    printf("cycles per op:\t%.2f\n", cycles_per_op);

    cudaFree(d_out);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    return 0;
}
