# Repo for Sensors Microcontrollers Team Tufts Electric Racing

## DOCUMENTATION GUIDELINES
1. Use descriptive file names
2. All files should have a header comment describing their purpose/function,
   including their relation to the other files, and if applicable, the set-up of any relevant physical parts

## REPOSITORY GUIDELINES
- TODO
### Navigating the raspberry pi
- To ssh (need wifi): ```ssh racing@172.16.9.130```
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
