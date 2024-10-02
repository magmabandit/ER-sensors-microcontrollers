# sample program that reads data from shared memory
# Alex Lee
# 10/1/2024
from multiprocessing import shared_memory
import numpy as np
import time

def reader(shm_name):
    existing_shm = shared_memory.SharedMemory(name=shm_name)

    for i in range(1,11):
        print("ITERATION", i)
        print("=============")
        arr = np.ndarray((10,), dtype=np.int64, buffer=existing_shm.buf)

        print(arr)
        print("\n")
        time.sleep(2)

    existing_shm.close() # closes access to the shm for this program

    # we should not be calling unlink here; this would delete the entire shm
    # we reserve unlink to be called once in the accumulator
    return 1

# data accumulator program MUST BE RUNNING for this to work
if __name__ == '__main__':
    reader("mem123")