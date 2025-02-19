# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template
from multiprocessing import shared_memory
import time
import atexit
import serial
#from ER-sensors-microcontrollers.pi.globals import *
import numpy as np

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    existing_shm = shared_memory.SharedMemory(name="mem123")
    arr = np.ndarray(shape=10, dtype=np.int64, buffer=existing_shm.buf)
    # Convert array to string for display
    arr_string0 = str(arr[0].tolist())
    arr_string1 = str(arr[1].tolist())
    arr_string2 = str(arr[2].tolist())
    arr_string3 = str(arr[3].tolist())
    
    existing_shm.close()
    return render_template("index.html", array_data = [arr_string0, arr_string1, arr_string2, arr_string3])

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()
