from multiprocessing import shared_memory
import numpy as np
import time

def chunkReader(shm_name):
    existing_shm = shared_memory.SharedMemory(name=shm_name)

    while True:
        print("ITERATION")
        print("=============")
        arr = np.ndarray((10,), dtype=np.int16, buffer=existing_shm.buf)

        print(arr)
        print("\n")
        time.sleep(2)

    existing_shm.close() # closes access to the shm for this program

    # we should not be calling unlink here; this would delete the entire shm
    # we reserve unlink to be called once in the accumulator
    return 1

if __name__ == '__main__':
    chunkReader("mem123")