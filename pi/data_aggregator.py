# data accumulation for sensors & microcontrollers [ALPHA]
# Alex Lee
# 10/1/2024

import multiprocessing
from multiprocessing import shared_memory
import numpy as np
import time

def create_shared_memory(size:int):
    # initialize shared memory block
    # "mem123" is the "password" for this chunk of memory
    shm = shared_memory.SharedMemory(create=True, size=size * 8, name="mem123")
    return shm

if __name__ == '__main__':
    shm = create_shared_memory(12) # 12 * 8 bytes - tested up to a gigabyte size chunk
    print(f"Shared memory block created with name: {shm.name}")
    print("Press Ctrl+C to end shared memory instance")
   
    # store some initial arbitrary data to the shm
    # this is for testing purposes only!
    a = np.array(range(10))
    # create a NumPy array backed by shared memory
    b = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
    b[:] = a[:]  # copy the original data into shared memory

    try:
        # keep the shared memory alive
        # other programs can utilize the shm at this time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Cleaning up shared memory...")
        shm.close()
        
        # once the last process closes its shm instance it gets deleted
        shm.unlink() # queues shm cleanup
    
