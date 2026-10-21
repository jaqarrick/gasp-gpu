"""
This module is not a true "simulator" as it does not actually run or emulate code
Rather, it estimates GPU occupancy and reps (i.e. scheduling repetitions), MWP, CWP

How many threads can run simultaneously on each SM, and how many rounds of execution (waves) are needed to process all threads.

Inputs:
- launch params
- hardware params
- registers/shared memory per thread & block


Function:
1. Active warps per SM: we can get this limit from our inputs
2. Get `num_reps` - `num_total_warps / number_active_sms`
3. Determine MWP (Memory warp parallelism) - using Sim et. al
4. Determine CWP (Compute Warp parallelism) - same as above

Outputs:
```
active_warps_per_sm
active_sms
total_warps (int)
num_reps (i.e N)
mwp
cwp (float)


This module is also probably where we will model cache, coalescence, and bank conflicts.
However, if we are attempting to plug in PICO for these numbers, it will probably be in a separate module
"""
