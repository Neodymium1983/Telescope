import RPi.GPIO as GPIO
import time
import threading
import serial

def handcontroller():
    ser = serial.Serial('/dev/ttyAMA0', 		#serial port setup
            baudrate = 38400,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS)

    time.sleep(0.001)

    x = ser.read_until(b'START')				#read and clear input buffer
    x = ser.read_until(b'END')					#read uptil END which is appended to each message.
    x = x.decode()								#decode binary to string
    ser.write(b'TY')							#write reply to say message recieved
    return(x)									#return message
