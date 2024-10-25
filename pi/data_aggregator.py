# beginnings of a data accumulator script: instantiates pool of shared
# memory of a specified size (see consts) and frees it on exit
#
# Alex Lee, Robi
# 10/19/2024

from multiprocessing import shared_memory
import numpy as np
import time
import atexit

SHMEM_NAME = "mem123"
SHMEM_NMEM = 10
SHMEM_DTYPE = np.int64
SHMEM_MEMB_SIZE = np.dtype(SHMEM_DTYPE).itemsize
SHMEM_TOTAL_SIZE = SHMEM_NMEM * SHMEM_MEMB_SIZE

# Basically our destructor
def cleanup_shmem(shared_mem_inst):
    print("Cleaning up shared memory...")
    shared_mem_inst.close()
    shared_mem_inst.unlink()

shm = shared_memory.SharedMemory(
    create=True, size=SHMEM_TOTAL_SIZE, name=SHMEM_NAME
)
atexit.register(cleanup_shmem, shared_mem_inst=shm)

# create a NumPy array backed by shared memory
shm_handle = np.ndarray(shape=SHMEM_NMEM, dtype=SHMEM_DTYPE, buffer=shm.buf)

print(f"Shared memory block created with name \"{shm.name}\" of size {SHMEM_MEMB_SIZE}")
print("Will be free'd on program exit")

# store some initial arbitrary data to the shm
# this is for testing purposes only!
writebuf = np.array(range(SHMEM_NMEM))

shm_handle[:] = writebuf[:]  # copy the original data into shared memory

# Do nothing; host shared memory

while True:
    time.sleep(1)
