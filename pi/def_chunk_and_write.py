# data accumulation for sensors & microcontrollers [ALPHA]
# Alex Lee
# 10/1/2024

import multiprocessing
from multiprocessing import shared_memory
import numpy as np
import time
import fileinput

<<<<<<< HEAD:pi/def_chunk_and_write.py
def writer(shm_name): 
=======

def writer(shm_name):

>>>>>>> main:pi/sample_writer.py
    try:
        while True:
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            # store array buffer from shm to array
<<<<<<< HEAD:pi/def_chunk_and_write.py
            arr = np.ndarray((10,), dtype=np.int16, buffer=existing_shm.buf)
            data = int(input("Please input data: "))
            arrayIndex = int(input("Input index 0-9: "))
            arr[arrayIndex] = data
=======
            arr = np.ndarray((10,), dtype=np.int64, buffer=existing_shm.buf)

            # write to the array randomly
            if random.randint(0, 4) == 1:
                print(datetime.now().strftime("%H:%M:%S"), " - RANDOM WRITE!")
                arr[0] = random.randint(0, 100)
            time.sleep(1)
>>>>>>> main:pi/sample_writer.py
            existing_shm.close()
    except KeyboardInterrupt:
        print("Closing Writer...")

    return 0


# data accumulator program MUST BE RUNNING for this to work
<<<<<<< HEAD:pi/def_chunk_and_write.py
if __name__ == '__main__':
    writer("mem123")
    
=======
if __name__ == "__main__":
    writer("mem123")
>>>>>>> main:pi/sample_writer.py
