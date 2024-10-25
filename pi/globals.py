# global variable and import suite for aggregator and client programs to use
#
# Alex Lee, Robi
# 10/25/2024
from multiprocessing import shared_memory
import time
import atexit
import serial

import numpy as np

# GLOBAL VARS

# name of shm instance stored in aggregator
SHMEM_NAME = "mem123"
# length of sensor data array stored in shm
SHMEM_NMEM = 10
# datatype of sensor readings to be stored in shm
SHMEM_DTYPE = np.int64
SHMEM_MEMB_SIZE = np.dtype(SHMEM_DTYPE).itemsize
SHMEM_TOTAL_SIZE = SHMEM_NMEM * SHMEM_MEMB_SIZE