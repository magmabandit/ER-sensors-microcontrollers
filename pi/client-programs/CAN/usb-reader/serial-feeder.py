# Simulates what a standard CAN frame may look like from canusb.c
# 
#

import time
import os
import random

def randomize_bytes():
    return os.urandom(8)

start = time.time()
# configure number of frame ids / weights if needed
fids = ["0001", "0036", "00A0", "00A1", "00A2", "00A3", "00A4", "00A5", "00A6", "00A7", "00A8", "00A9", "00AA", "00AB", "00AC", "00AD", "00AE", "00AF"]
weights = [1, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

while True:
    bytes = randomize_bytes()
    b = ' '.join(f'{byte:02x}' for byte in list(bytes))
    fid = random.choices(fids, weights=weights)[0]
    print(f"{time.time() - start} Frame ID: {fid}, Data: {b}")
    time.sleep(0.005)
