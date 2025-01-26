# reads buffered array from shared memory every 1 ms 
#
# Alex Lee
# 10/25/2024
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from globals import *

def chunkReader(shm_name):
    existing_shm = shared_memory.SharedMemory(name=shm_name)

    while True:
        try:
            arr = np.ndarray(shape=SHMEM_NMEM, dtype=SHMEM_DTYPE, buffer=existing_shm.buf)

            print(arr)
            print("\n")
            time.sleep(0.5)
        except KeyboardInterrupt:
            existing_shm.close() # closes access to the shm for this program
            break

    # we should not be calling unlink here; this would delete the entire shm
    # we reserve unlink to be called once in the accumulator

if __name__ == '__main__':
    chunkReader("mem123")