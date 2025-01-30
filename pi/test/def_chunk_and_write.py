# Data aggregator test program
# Manually injects data into aggregator
# Alex Lee, Jackie, Jishnu
# 10/1/2024

import multiprocessing
from multiprocessing import shared_memory
import numpy as np
import time
import fileinput

def writer(shm_name): 
    try:
        while True:
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            # store array buffer from shm to array
            arr = np.ndarray((32,), dtype=np.int32, buffer=existing_shm.buf)
            data = int(input("Please input data: "))
            arrayIndex = int(input("Input index 0-9: "))
            arr[arrayIndex] = data
            existing_shm.close()
    except KeyboardInterrupt:
        print("Closing Writer...")

    return 0


# data accumulator program MUST BE RUNNING for this to work
if __name__ == '__main__':
    writer("mem123")
    
