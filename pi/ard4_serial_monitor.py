# serial monitor in python
# 10/13/2024
import serial
import time

# 1000 ms
ser = serial.Serial('COM5', 9600, timeout=0.001)  # Replace 'COM5' with your Arduino's port
# # 7000 ms
# ser2 = serial.Serial('COM7', 9600)
# # 2000 ms
# ser3 = serial.Serial('COM6', 9600)


time.sleep(2)  # Allow time for the connection to establish

while True:
    try:
        # Read a line of data from the serial port
        data = ser.readline().decode('utf-8').strip()
        # data2 = ser2.readline().decode('utf-8').strip()
        # data3 = ser3.readline().decode('utf-8').strip()



        # Process the data
        print(data)

    except KeyboardInterrupt:
        # Exit the loop when Ctrl+C is pressed
        break

# Close the serial connection
ser.close()
