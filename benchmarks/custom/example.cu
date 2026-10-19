#include <stdio.h>
#include <stdlib.h>
#include <cuda.h>
#include <time.h>



__global__ void addvector(int *, int *, int *, int);

int main(int argc, char *argv[])
{

  int i;
  int num = 0; // number of elements in the arrays
  int * a, *b, *c; // arrays at host
  int * ad, *bd, *cd; // arrays at device
  int choice = 0; // 0 means CPU and 1 means GPU
  int THREADS = 0; // user decides number of threads per block  


  // to measure the time
  double time_taken = 0;
  clock_t start, end;

  if(argc != 4){
     	printf("usage: addvec numelements cpu_or_gpu num_threads\n");
     	printf("cpu_or_gpu:  0 = CPU, 1  = GPU\n");
	exit(1);
  }

  num = atoi(argv[1]);
  choice = atoi(argv[2]);
  THREADS = atoi(argv[3]);

  a = (int *)malloc(num*sizeof(int));
  if(!a){
     printf("Cannot allocate array a with %d elements\n", num);
     exit(1);	
  }


  b = (int *)malloc(num*sizeof(int));
  if(!b){
     printf("Cannot allocate array b with %d elements\n", num);
     exit(1);	
  }


  c = (int *)malloc(num*sizeof(int));
  if(!c){
     printf("Cannot allocate array c with %d elements\n", num);
     exit(1);	
  }


  //Fill out arrays a and b with some random numbers
  srand(time(0));
  for( i = 0; i < num; i++)
  {
    a[i] = rand() % num;
    b[i] = rand() % num; 
  }

  // The CPU version   
  
  start = clock(); // start measuring
  for( i = 0; i < num; i++)
	c[i] = a[i] + b[i];
  
  end = clock();  // end of measuring
  time_taken = ((double)(end-start)) / CLOCKS_PER_SEC;

  printf("CPU time = %lf secs\n", time_taken); 


  //Now zero C[] in preparation for GPU version
  for( i = 0; i < num; i++)
	c[i] = 0;
  

  // The GPU version
  if(choice){
      
      int numblocks;
      int threadsperblock;
 
      if( (num % THREADS) == 0 )
	numblocks =num / THREADS ;
      else 
      	numblocks = (num/THREADS)>0? (num/THREADS)+1:1 ;
      threadsperblock = THREADS;

      printf("GPU: %d blocks of %d threads each\n", numblocks, threadsperblock);     

      //assume a block can have THREADS threads
      dim3 grid(numblocks, 1, 1);
      dim3 block(threadsperblock, 1, 1);

      cudaMalloc((void **)&ad, num*sizeof(int));
      if(!ad)
	{ printf("cannot allocated array ad of %d elements\n", num);
	  exit(1);
        }


      cudaMalloc((void **)&bd, num*sizeof(int));
      if(!bd)
	{printf("cannot allocated array bd of %d elements\n", num);
	  exit(1);
        }


      cudaMalloc((void **)&cd, num*sizeof(int));
      if(!cd)
	{printf("cannot allocated array cd of %d elements\n", num);
	  exit(1);
        }


      start = clock(); //start measuring time for GPU
 
      //mov a and b to the device
      cudaMemcpy(ad, a, num*sizeof(int), cudaMemcpyHostToDevice);
      cudaMemcpy(bd, b, num*sizeof(int), cudaMemcpyHostToDevice);

      //Launch the kernel
      addvector<<<numblocks , threadsperblock>>>(ad, bd, cd, num);

      //bring data back 
      cudaMemcpy(c, cd, num*sizeof(int), cudaMemcpyDeviceToHost);
      
      end = clock();  // end of measuring
      time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;

      printf("GPU time = %lf secs\n", time_taken); 
  } 
  
  cudaDeviceSynchronize(); //block host till device is done.
  
  //check the result is correct
  if( choice)
   for(i = 0; i < num; i++)
	if(c[i] != (a[i]+b[i]) )
	   printf("Incorrect result for element c[%d] = %d\n", i, c[i]);


  free(a);
  free(b);
  free(c);
  
  if( choice ){
     cudaFree(ad);
     cudaFree(bd);
     cudaFree(cd); }


}


__global__  void addvector(int * a, int * b, int *c, int n)
{
   int index;

   index = (blockIdx.x * blockDim.x) + threadIdx.x;

   if (index < n )
	c[index] = a[index] + b[index];
 
}
