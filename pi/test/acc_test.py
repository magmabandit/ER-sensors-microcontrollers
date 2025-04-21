import serial
import time

# Set the serial port to which Arduino is connected
# On Windows, it could be something like COM3 or COM4
# On Linux/Mac, it could be something like /dev/ttyUSB0
arduino = serial.Serial('COM5', 9600, timeout=1)  # Adjust 'COM3' to match your system
time.sleep(2)  # Give time for the connection to establish

# Initialize an empty array to store the incoming data
data_array = []

try:
    while True:
        if arduino.in_waiting > 0:  # If there's data available to read
            data = arduino.readline().decode('utf-8').strip()  # Read and decode the line
            print(f"Received: {data}")  # Print data to console (optional)
            
            # Add the data to the array
            data_array.append(int(data))  # Convert string data to integer and add it to the array
            
            # Optionally, print the current array (you can remove or limit this to avoid printing too often)
            print(f"Current Data Array: {data_array}")
        
        time.sleep(1)  # Wait for a short time before checking again

except KeyboardInterrupt:
    print("Data collection stopped.")
    # When you stop the program, you can print or process the collected data
    print(f"Final Data Array: {data_array}")