# beginnings of a data accumulator script: instantiates pool of shared
# memory of a specified size (see globals) and frees it on exit
# 
# must be connected to serial input to run
#
# Alex Lee, Robi
# 10/19/2024
from globals import *

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
writebuf = np.zeros(shape=SHMEM_NMEM)

shm_handle[:] = writebuf[:]  # copy the original data into shared memory


ser = serial.Serial('COM5', 9600, timeout=0.001)  # Replace 'COM5' with Arduino's port

# read serial output from arduinos and host shared memory
while True:
    # arduino 1
    pedal_sens = ser.readline().decode('utf-8').strip()

    # if one arduino prints from more than one sensor, we need to distinguish
    # the sensors here

    # skip garbage vals
    # TODO - sentinel value?
    if (pedal_sens != '' and pedal_sens != '-'):
        shm_handle[0] = SHMEM_DTYPE(pedal_sens)
    
    # sync every 1 ms
    time.sleep(.001)