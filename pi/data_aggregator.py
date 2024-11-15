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

# writes the value stored at idx in the handle to serial port of selected arduino
def write_to_arduino(s: serial.Serial, idx:int, shmem: np.ndarray[SHMEM_DTYPE]):
    s.write(str(shmem[idx]).encode('utf-8'))

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


ard1 = serial.Serial('COM5', 9600, timeout=0.001)  # Replace 'COM5' with Arduino's port

# read serial output from arduinos and host shared memory
while True:
    # each arduino reads more than one sensor, so we need to distinguish each
    # reading using an array
    
    a1_data = ard1.readline().decode('utf-8').strip().split(',') # readings are comma separated
    # ard2 = ser2. ...
    
    # this arduino arbitrarily outputs just 2 pedal sensor readings
    # will probably need to change later

    # skip garbage vals
    # TODO - sentinel value?
    if (a1_data != '' and a1_data != '-'):
        shm_handle[0] = SHMEM_DTYPE(a1_data[0])
        shm_handle[1] = SHMEM_DTYPE(a1_data[1])

    write_to_arduino(ard1, 0, shm_handle)
    
    # sync every 1 ms
    time.sleep(.001)