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
import signal  # ADDED: Safe exit handling
import sys  # ADDED: Needed for safe exit handling
import struct
import serial
import redis
import multiprocessing as mp
import json
import time


# Basically our destructor
def cleanup_shmem(shared_mem_inst):
    print("Cleaning up shared memory...")
    shared_mem_inst.close()
    shared_mem_inst.unlink()


# ====== ADDED: Safe Exit Handling ======
def handle_exit(signum, frame):
    """Handles termination signals (SIGINT, SIGTERM) to clean up shared memory safely."""
    print("Received stop signal. Cleaning up...")
    cleanup_shmem(shm)  # Ensure shared memory is properly freed
    sys.exit(0)

# ========================================

# writes a message containing specified shm readings given an array of indices
# to a serial port of an arduino. 
# Message contains:
#   - Synchronization byte
#   - Reading quantity byte
#   - 4 bytes per specified reading * quanity of readings (currently a float32)
# Up to the arduino to handle messages, but they should assume reading quantity
# is no more than a byte (no more than 16 readings per message).
#
# Ideally, this should be executed less than once per ms (safely once per
# 5-10ms for most cases) to avoid flooding the serial buffer
def write_to_arduino(s: serial.Serial, shmem: np.ndarray[SHMEM_DTYPE], *indexes: int):
    sync = b'\xFF'
    length = bytes([len(indexes)])

    s.write(sync)
    s.write(length)
    for i in indexes:
        s.write(struct.pack('<f', shmem[i]))


def redis_subscriber(
    channel,
    index,
    counter_lock,
    shm,
    host="localhost",
    port=6379,
    max_redis_reads_per_second=10,
):
    r = redis.Redis(host=host, port=port, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe(channel)

    last_reset_time = time.time()
    message_count = 0

    print("Subscriber started. Waiting for messages...")
    for message in pubsub.listen():
        if message["type"] == "message":
            current_time = time.time()

            # Reset the counter every second
            if current_time - last_reset_time >= 1:
                message_count = 0
                last_reset_time = current_time

            # Depending on how the published messages evolve, this can be a rate per channel
            if message_count < max_redis_reads_per_second:
                write_to_shm(message, index, counter_lock, shm)
                message_count += 1
            else:
                time.sleep(0.1)


def as_json(message):
    data_bytes = message["data"]
    return data_bytes.decode("utf-8")


def write_to_shm(message, index, lock, shm):
    try:
        # Ensure only one process writes at a time
        with lock:
            data = as_json(message)
            idx = data["id"]
            shm[idx] = data["data"]  # Store data in the array
            print(f"Stored {message} at index {idx}")
            index.value += 1  # Move to next index
    except ValueError:
        print(f"Invalid data received: {message['data'].decode('utf-8')}")


if __name__ == "__main__":
    # Register signal handlers for safe exit
    signal.signal(signal.SIGTERM, handle_exit)  # Handles system termination (e.g., `sudo systemctl stop`)
    signal.signal(signal.SIGINT, handle_exit)  # Handles Ctrl+C termination

    shm = shared_memory.SharedMemory(
        create=True, size=SHMEM_TOTAL_SIZE, name=SHMEM_NAME
    )
    atexit.register(cleanup_shmem, shared_mem_inst=shm)

    # create a NumPy array backed by shared memory
    shm_handle = np.ndarray(shape=SHMEM_NMEM, dtype=SHMEM_DTYPE, buffer=shm.buf)

    print(
        f'Shared memory block created with name "{shm.name}" of size {SHMEM_TOTAL_SIZE}'
    )
    print("Will be free'd on program exit")

    # store some initial arbitrary data to the shm
    writebuf = np.zeros(shape=SHMEM_NMEM)

    shm_handle[:] = writebuf[:]  # copy the original data into shared memory

    # Shared index for write position
    index = mp.Value("i", 0)  # Shared integer for tracking position
    counter_lock = mp.Lock()  # Lock for synchronization

    # Start the Redis subscriber in a separate process
    redis_process = mp.Process(
        target=redis_subscriber, args=("canusb_data", index, counter_lock, shm_handle)
    )
    redis_process.start()

    # ====== ADDED: Serial Connection Error Handling ======

i = 0
while True:
    i += 1
    try:
        ard1 = serial.Serial('COM7', 19200, timeout=0.005)  # Replace 'COM6' with Arduino's port
        # ard2 = serial.Serial('COM7', 19200, timeout=0.001)
        break
    except serial.SerialException:
        time.sleep(0.01)
        if i == 100:  # writes once every 100 attempts as to not flood the logs
            print("log: serial disconnected, trying again")
            #print("log: error: " + str(e)) #only needed if it's not handling a specific connection
            i = 0
        continue

    # read serial output from arduinos and host shared memory
    # threadify this?
    while True:
        try:
            # TODO: we need to catch serial errors here as well to avoid the
            # aggregator crashing
            a1_data = (
                ard1.readline().decode("utf-8").strip().split(",")
            )  # readings are comma separated
            # a2_data = ard2. ...
        except UnicodeDecodeError:
            continue
            # print("Log: decoding issue")

        if (
            all(reading != "" and reading != "-" for reading in a1_data)
            and len(a1_data) == 2
        ):
            shm_handle[0] = SHMEM_DTYPE(a1_data[0])
            shm_handle[1] = SHMEM_DTYPE(a1_data[1])

    write_to_arduino(ard1, shm_handle, 0, 1)
    # sync every 1 ms
    time.sleep(.001)
