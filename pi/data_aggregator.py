# data aggregator script: instantiates pool of shared
# memory of a specified size (see globals) and frees it on exit;
# handles writing to shared memory from arduino input, and writing values back
# to arduinos
# 
# must be connected to serial input to run
#
# Alex Lee, Robi
# 10/24/2024
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

i = 0
while True:
    i += 1
    try:
        ard1 = serial.Serial('COM6', 19200, timeout=0.001)  # Replace 'COM5' with Arduino's port
    except Exception as e: # or serialexception?
        time.sleep(0.01)
        if i == 100:
            print("log: serial disconnected, trying again")
            print("log: error: " + str(e))
            i = 0
        continue

# ard2 = serial.Serial('COM7', 19200, timeout=0.001)

# read serial output from arduinos and host shared memory
# threadify this?
while True:
    try:
        a1_data = ard1.readline().decode('utf-8').strip().split(',') # readings are comma separated
        # a2_data = ard2. ...
    except UnicodeDecodeError:
        continue
        #print("Log: decoding issue")
    
    
    # this arduino arbitrarily outputs just 2 pedal sensor readings
    # skip garbage vals for all readings in the array, make sure values are
    # updated only when values for both readings exist
    
    if (all(reading != '' and reading != '-' for reading in a1_data) and len(a1_data) == 2):
        shm_handle[0] = SHMEM_DTYPE(a1_data[0])
        shm_handle[1] = SHMEM_DTYPE(a1_data[1])

    write_to_arduino(ard1, shm_handle, 0)
    
    # sync every 1 ms
    time.sleep(.001)