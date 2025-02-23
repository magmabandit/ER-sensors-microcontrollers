# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
from multiprocessing import shared_memory
import time
import atexit
import serial
#from ER-sensors-microcontrollers.pi.globals import *
import numpy as np

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
socketio = SocketIO(app)

# Reads the shared memory and creates an array called data that contains the
# first 4 elements of the shared memory array.
def read_shm():
    try:
        existing_shm = shared_memory.SharedMemory(name="mem123")
        arr = np.ndarray(shape=10, dtype=np.float32, buffer=existing_shm.buf)
        # Convert array to string for display
        data = [arr[i].tolist() for i  in range(4)]
        existing_shm.close()

        return data
    except FileNotFoundError:
        return ["Error: Read from Shared Memory Failed."]

# Emits the signal 'update_data' to the index.html file to run the javascript
# code in the file.
def background_thread():
    while True:
        shm_data = read_shm()
        socketio.emit('update_data', {'array_data': shm_data})
        time.sleep(1)

# Creates a background thread that continously updates the display with
# updated data from the shared memory.
thread = threading.Thread(target = background_thread, daemon = True)
thread.start()

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function. 
def hello_world():

    shm_data = read_shm()
    return render_template("index.html", array_data = shm_data)

# main driver function
if __name__ == '__main__':

    # Runs the app using socketio for real-time data updates from the
    # shared memory.
    socketio.run(app, debug = True)
