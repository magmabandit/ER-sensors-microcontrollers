# sample program that writes data to shared memory
# Alex Lee
# 10/1/2024
from multiprocessing import shared_memory
import numpy as np
import random
import time
from datetime import datetime


def writer(shm_name):

    try:
        while True:
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            # store array buffer from shm to array
            arr = np.ndarray((10,), dtype=np.int64, buffer=existing_shm.buf)

            # write to the array randomly
            if random.randint(0, 4) == 1:
                print(datetime.now().strftime("%H:%M:%S"), " - RANDOM WRITE!")
                arr[0] = random.randint(0, 100)
            time.sleep(1)
            existing_shm.close()
    except KeyboardInterrupt:
        print("Closing Writer...")

    return 0


# data accumulator program MUST BE RUNNING for this to work
if __name__ == "__main__":
    writer("mem123")
