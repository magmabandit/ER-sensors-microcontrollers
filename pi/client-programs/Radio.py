from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import datetime
import threading,time,json
from queue import Queue
import pandas as pd
from globals import *

lock = threading.Lock()
ws = []
rh = []
t = []
curr = []
sensors = []
class MyServerClass(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path == '/'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            testStr=""
            with open("test.html",'rb') as file:
                self.wfile.write(file.read())
        elif(self.path == '/setup'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")#doesent really matter here
            self.end_headers()
            dataToSend = {"sensors":sensors,"numSensors":len(sensors)}
            stringToSend = json.dumps(dataToSend)
            self.wfile.write(bytes(stringToSend,'utf-8'))
        elif(self.path == '/data'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")#doesent really matter here
            self.end_headers()
            #while myQueue.qsize == 0:
                #print("YO")
        
            z = {
                "strID": curr[0],
                "Value": str(curr[1]),
               
            }
            jsonString = json.dumps(z)
            #print(jsonString)
            self.wfile.write(bytes(jsonString,'utf-8'))
            
 
theServer = HTTPServer(('localhost',8000),MyServerClass)

# change this to read from shared memory array
# curr stores a tuple(?) of sensor name / sensor reading
# sensors stores sensor type ~ keeps track of total # sensors
# "dictionary" stores key=sensor type, value=sensor reading, 
# and the current time as a key/val pair. To convert into excel file
def usbListener():
    # read from shm, put relevent data in curr, sensors, and dictionary,
    # let other parts of the code handle this data
    shm = shared_memory.SharedMemory(name=SHMEM_NAME)
    
    global curr
    global sensors

    # copy shm into array and store in sensors
    sensors = np.ndarray(size=SHMEM_TOTAL_SIZE, dtype=SHMEM_DTYPE, buffer=shm.buf)
    
    
    # store sensor value along with its name for each sensor
    # ex. dictionary["sensName"] = sensors[idx_of_sensor]


    curr = []

    try:
        while True:
            dictionary = {}
            for i in range(len(sensors)):
                dictionary[SENS_NAMES[i]] = sensors[i]
            # read & do stuff here
    except KeyboardInterrupt:
        df = pd.DataFrame.from_dict(dictionary)
        df.to_excel("ModularTest.xlsx")
        sensors = [] #????
        curr = []
        #IDK
        theServer.shutdown()
     
        theThread.join()



threading.Thread(target = usbListener).start()


# old usb listener code using tcp sockets to read from arduinos:

# ------------------------------------------------------------- #

    # global curr
    # global sensors
    # mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # mySocket.bind(("localhost",8084))
    # while True:
    #     mySocket.listen()
    #     theSock,retAddr = mySocket.accept()
    #     numSensors = theSock.recv(1)[0]
        
    #     freqs = []
    #     maxFreq = 0

    #     for z in range(0,numSensors):
    #         sizeToRec = theSock.recv(1)[0]
    #         print(sizeToRec)
    #         sensor = str(theSock.recv(sizeToRec),'utf-8')
    #         print(sensor)
    #         overflow = theSock.recv(1)[0]
    #         print(overflow)
    #         freq = overflow*256 + theSock.recv(1)[0]
    #         if freq > maxFreq:
    #             maxFreq = freq
            
    #         sensors.append(sensor)
    #         freqs.append(freq)
    #     dictionary = {}
    #     for i in sensors:
    #         dictionary[i] = [0]
    #     dictionary["time"] = [0]
    #     counter = 0

        
        
    #     theThread = threading.Thread(target = theServer.serve_forever, args=(5,))
    #     theThread.start()

    #     while True:
    #         try:
    #             print("HERHERHERHERH")
    #             sizeToRec = theSock.recv(1)
    #             part = str(theSock.recv(sizeToRec[0]),'utf-8')
    #             value = theSock.recv(1)[0]
    #             dictionary[part].append(value)
    #             for i in sensors:
    #                 if (i != part):
    #                     dictionary[i].append(dictionary[i][len(dictionary[i])-1])
    #             dictionary["time"].append(float(counter/maxFreq))
    #             with lock:
    #                 curr = [part, value]
    #             print(part)
    #             print(value)
    #             time.sleep(1/maxFreq)#freq/2?
    #             counter += 1
    #         except:
    #             print("THIS IS WHERE IT BROKE")
    #             break