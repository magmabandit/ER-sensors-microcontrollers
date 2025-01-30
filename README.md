# Repo for Sensors Microcontrollers Team Tufts Electric Racing

## DOCUMENTATION GUIDELINES
1. Use descriptive file names
2. All files should have a header comment describing their purpose/function,
   including their relation to the other files, and if applicable, the set-up of any relevant physical parts

## REPOSITORY GUIDELINES
- Not super important as of this semester, but it is generally best practice to
  do your work on a branch separate from main. Consult the 
  [Git book](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
  for more on this. That way if you accidentally break something, it does not
  break the main branch code.
- Try to avoid having 2+ people working on the same file separately, this may cause
  merge conflicts, and has the potential to be a massive pain in the ass
- Push your work often, and **remember to pull before you start doing any work!!!**
  
### Navigating the raspberry pi
- To ssh (need wifi): ```ssh racing@172.16.9.248```
    - Or connect via usb (see RPI documentation in the Google Drive)
- Password: ```504BostonAve```
- **Important Commands**
    - ```hostname -I``` - get device IP
    - ```touch <filename>``` - create a file
    - ```mkdir <filename>``` - create a directory
        - ```rmdir <filename>``` - remove a directior
    - ```cd <path>``` - navigate to a directory located at path
        - ```cd ..``` - navigate backwards 1 directory
        - ```cd ~``` - navigate to root directory
    - ```ls``` - view all files/subdirectories in directory
    - ```cat <file>``` - view contents of a file
    - ```pwd``` - view path of directory you are in

    - ```sudo [COMMAND]``` - "Super do"; grants permissions to do stuff like file IO etc.
    - ```i2cdetect -y 1``` - Get I2C devices connected
    - ```sudo apt-get install``` - install something to the PI
### Data Aggregator
The aggregator is in charge of continuously storing sensor readings by the
milisecond and sending relevant data back to arduinos responsible for
controlling something (ie. break light, startup sound, etc). Client programs may
read (**not write**) from the aggregator array to their liking 
**Below are the relevant agreements made between arduinos and aggregator.**
- Ardunios read from multiple sensors, sending the data as a comma-delineated
  sequence through serial. For example, a sensor with 3 readings, *r1, r2, r3*
  would write the string "r1,r2,r3" to serial. The aggregator is responsible
  with appropriately splicing this data.
- Our *current* **aggregator array** stores the sensor readings as follows:

| **Index**  | 0             | 1         | 2         | 3         | 4         | 5         | 6         | 7         | ...  |
|------------|--------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|------|
| **Reading** | SteeringWheel | IMUAccelX | IMUAccelY | IMUAccelZ | IMUGyroX  | IMUGyroY  | IMUGyroZ  | IMUMagnetX | ...  |
| **From**   | Ard1         | Ard1      | Ard1      | Ard1      | Ard1      | Ard1      | Ard1      | Ard2      | ...  |

| **Index**  | 8         | 9         | 10         | 11         | 12        | 13        | 14      | 15      | ...  |
|------------|-----------|-----------|-----------|-----------|----------|----------|--------|--------|------|
| **Reading** | IMUMagnetY | IMUMagnetZ | WSFrontLeft | WSFrontRight | WSBackLeft | WSBackRight | Motor1 | Motor2 | ...  |
| **From**   | Ard2      | Ard2      | TBD      | TBD      | TBD     | TBD     | CAN   | CAN   | ...  |

| **Index**  | 16      | 17      | 18      | 19      | 20      | 21      | 22      | 23      | ...  |
|------------|--------|--------|--------|--------|--------|--------|--------|--------|------|
| **Reading** | Motor3 | Motor4 | Motor5 | Motor6 | Motor7 | Motor8 | Motor9 | Motor10 | ...  |
| **From**   | CAN   | CAN   | CAN   | CAN   | CAN   | CAN   | CAN   | CAN    | ...  |

| **Index**  | 24      | 25      | 26      | 27      | 28      | 29      | 30      | 31      | ...  |
|------------|--------|--------|--------|--------|--------|--------|--------|--------|------|
| **Reading** | Motor11 | Motor12 | Motor13 | Motor14 | Motor15 | Motor16 | BMS1 | BMS2 | ...  |
| **From**   | CAN    | CAN    | CAN    | CAN    | CAN    | CAN    | CAN | CAN | ...  |

| **Index**  | 32    | 33    | 34    | 35    | 36    | 37    |
|------------|------|------|------|------|------|------|
| **Reading** | BMS3 | BMS4 | BMS5 | BMS6 | BMS7 | BMS8 |
| **From**   | CAN | CAN | CAN | CAN | CAN | CAN |
