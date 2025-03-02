# data aggregator script: TEST INSTANCE ONLY
# should NOT be running at the same time as the official aggregator
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
print(sys.path)
sys.path.insert(0, parent_dir)

from globals import *

# Basically our destructor
def cleanup_shmem(shared_mem_inst):
    print("Cleaning up shared memory...")
    shared_mem_inst.close()
    shared_mem_inst.unlink()

# writes the value stored at idx in the handle to serial port of selected arduino.
# comma separated if there are multiple indices
def write_to_arduino(s: serial.Serial, shmem: np.ndarray[SHMEM_DTYPE], *indexes:int):
    msg = ""
    for i in indexes:
        msg += str(shmem[i]) + ","
    
    # remove trailing comma
    s.write(msg[-1].encode('utf-8'))

shm = shared_memory.SharedMemory(
    create=True, size=SHMEM_TOTAL_SIZE, name=SHMEM_NAME
)
atexit.register(cleanup_shmem, shared_mem_inst=shm)

# create a NumPy array backed by shared memory
shm_handle = np.ndarray(shape=SHMEM_NMEM, dtype=SHMEM_DTYPE, buffer=shm.buf)

print(f"Shared memory block created with name \"{shm.name}\" of size {SHMEM_TOTAL_SIZE}")
print("Will be free'd on program exit")

# store some initial arbitrary data to the shm
writebuf = np.zeros(shape=SHMEM_NMEM)

shm_handle[:] = writebuf[:]  # copy the original data into shared memory

# read serial output from arduinos and host shared memory
# threadify this?
while True:
    # sync every 1 ms
    time.sleep(.001)