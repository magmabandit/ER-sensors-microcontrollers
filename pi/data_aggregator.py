# data aggregator script: instantiates pool of shared
# memory of a specified size (see globals) and frees it on exit;
# handles writing to shared memory from CAN, and writing values back
# to arduinos
#
# must be connected to serial input to run
#
# Alex Lee, Robi
# 4/12/2025
from globals import *
import random
import signal  # ADDED: Safe exit handling
import sys  # ADDED: Needed for safe exit handling
import struct
import ast

from ctypes import *
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
    max_redis_reads_per_second=100000,
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
                time.sleep(0.05)


def as_json(message):
    data_bytes = message["data"]
    return ast.literal_eval(data_bytes.decode("utf-8"))


def write_to_shm(message, index, lock, shm):
    try:
        # Ensure only one process writes at a time
        with lock:
            data = as_json(message)["data"]
            # print(data)            
            # assume we are handling through canusb-reader, which grabs buffer
            # bytes along with ID
            idx_withbuf = as_json(message)["can_id"]
            hex_str = f"{idx_withbuf:08x}"
            can_id_bytes = bytes.fromhex(hex_str) 
            idx = can_id_bytes[1]    
            message = bytes(data)  # Store data in the array
            
            

            # Use below if its required to translate c-style char arrays
            # message = bytes((c_ubyte * 8) (data["data"])) 
            # print(f"{idx} recieved message: {message}")
            # HANDLE ALL VALUES BELOW AS LITTLE ENDIAN
            # the math to store the MC data in the shm is based on the number
            # of MC Messages offset by the readings taken from each message.
            # This makes it kind of horrible to add / remove readings since you
            # need to modify the offsets of preceeding/succeeding readings based
            # on the change, not to mention the cap of allocated MC indices in
            # the shm. A more dynamic strategy is needed for future iterations
            
            if len(message) == 8: # skip chopped redis messages
               # print(f"{idx} recieved message: {message}")
                match idx:
                    case 160: # 'A0' - template value
                        pass
                    case 161: # Temp 2
                        cb_temp = np.float32(struct.unpack('<H', message[0:2])[0])
                        shm[MOTOR_START_IDX + (idx - 160)] = cb_temp / 10
                    case 162: # Temp 3
                        cool_temp = np.float32(struct.unpack('<H', message[0:2])[0])
                        htspt_temp = np.float32(struct.unpack('<H', message[2:4])[0])
                        mot_temp = np.float32(struct.unpack('<H', message[4:6])[0])
                        shm[MOTOR_START_IDX + (idx - 160)] = cool_temp / 10
                        shm[MOTOR_START_IDX + (idx - 159)] = htspt_temp / 10
                        shm[MOTOR_START_IDX + (idx - 158)] = mot_temp / 10
                    case 163: # Analog Input
                        bit_string = ''.join(format(byte, '08b') for byte in message) # for bitops.
                        pedal1 = bit_string[-10:]
                        # this grabs the proper bits
                        pedal2 = bit_string[20:30]
                        pedal2 = float(int(pedal2, 2)) / 100
                        pedal2 += 1.03
                        print(pedal2)
                        shm[MOTOR_START_IDX + (idx - 158)] = pedal1
                        shm[MOTOR_START_IDX + (idx - 157)] = pedal2
                    case 164: # Dig. Input Status
                        pass
                    case 165: # Motor Pos.
                        motor_angle = np.float32(struct.unpack('<H', message[0:2])[0])
                        motor_speed = np.float32(struct.unpack('<H', message[2:4])[0])
                        shm[MOTOR_START_IDX + (idx - 158)] = motor_angle / 10
                        shm[MOTOR_START_IDX + (idx - 157)] = motor_speed
                    case 166: # Current Info
                        dc_curr = np.float32(struct.unpack('<H', message[6:])[0])
                        shm[MOTOR_START_IDX + (idx - 157)] = dc_curr / 10
                    case 167: # Voltage Info
                        dc_volt = np.float32(struct.unpack('<H', message[0:2])[0])
                        shm[MOTOR_START_IDX + (idx - 157)] = dc_volt / 10
                    case 170: # Internal States
                        vsm_state = np.float32(message[0])
                        inv_state = np.float32(message[2])
                        direction = np.float32(int(message[7] & 1))
                        shm[MOTOR_START_IDX + (idx - 159)] = vsm_state
                        shm[MOTOR_START_IDX + (idx - 158)] = inv_state
                        shm[MOTOR_START_IDX + (idx - 157)] = direction
                    case 172: # Torque / Timer
                        torque = np.float32(struct.unpack('<H', message[0:2])[0])
                        timer = np.float32(struct.unpack('<H', message[2:4])[0])
                        shm[MOTOR_START_IDX + (idx - 158)] = torque / 10
                        shm[MOTOR_START_IDX + (idx - 157)] = timer
                    case _:
                        # as of now, ids < A0 are exclusively from the BMS
                        if idx < 160:
                            int_res = np.float32(struct.unpack('<H', message[2:4])[0])
                            open_volt = np.float32(struct.unpack('<H', message[4:6])[0])
                            
                            # sample cells at random and take the averages in final
                            # BMS indices. Small chance for values from the same
                            # cell to end up in both sampling cells, but effects are
                            # negligible.
                            shm[BMS_START_IDX + random.randint(2,3)] = int_res
                            shm[BMS_START_IDX + random.randint(4,5)] = open_volt

                            avg_res = (shm[BMS_START_IDX + 2] + shm[BMS_START_IDX + 3]) / 2
                            avg_ov  = (shm[BMS_START_IDX + 4] + shm[BMS_START_IDX + 5]) / 2

                            shm[BMS_START_IDX + 6] = avg_res
                            shm[BMS_START_IDX + 7] = avg_ov
                        else:
                            # print(f"CAN ID {idx} not yet handled for message {message}")
                            pass

            # print(f"Stored {message} at index {idx}")
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
        ard1 = serial.Serial('/dev/ttyACM0', 19200, timeout=0.001)  # Replace 'COM6' with Arduino's port
        ard2 = serial.Serial('/dev/ttyACM1', 19200, timeout=0.001)
    except serial.SerialException:
        time.sleep(0.01)
        if i == 100:  # writes once every 100 attempts as to not flood the logs
            print("log: serial disconnected, trying again")
            #print("log: error: " + str(e)) #only needed if it's not handling a specific connection
            i = 0
        continue 

    # read serial output from arduinos and host shared memory
    while True:
        # handle non-CAN sensor data
        try:
            a1_data = (
                ard2.readline().decode("utf-8").strip().split(",")
            )  # readings are comma separated
            # a2_data = ard2. ...
        except UnicodeDecodeError:
            continue
            # print("Log: decoding issue")
        except serial.SerialException:
            break

        # if (
        #     all(reading != "" and reading != "-" for reading in a1_data)
        #     and len(a1_data) == 2
        # ):
        #     shm_handle[0] = SHMEM_DTYPE(a1_data[0])
        #     shm_handle[1] = SHMEM_DTYPE(a1_data[1])

        # Send motor temp, pedal
        write_to_arduino(ard1, shm_handle, MOTOR_START_IDX + 6)
        # Send VSM State
        write_to_arduino(ard2, shm_handle, MOTOR_START_IDX + 11)
        # sync every 1 ms
        
