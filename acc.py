import smbus2
import time
import math
import decimal


def tilt():
    acc = smbus2.SMBus(1)									#setup i2c bus as acc object
    acc.write_byte_data(0x6b,0x10,0b10110110, force=None)	#accelerometer on (sensor address, register, value)
    acc.write_byte_data(0x6b,0x0a,0b00000110, force=None)	#first in first out off
    low = acc.read_byte_data(0x6b, 0x28, force=None)		#read X axis low byte (sensor add, register)
    high = acc.read_byte_data(0x6b, 0x29, force=None)		#read X axis high byte
    high = (high<<8)										#bitshift high byte 8 bits
    total = str(format((high+low), '16b'))					#add high and lot together (binary add)
    #following code converts 2s compliment to signed decimal.
    running = 0
    for i in range(0, len(total)):
        if i == 0 and total[i] == "1":						#if most significant bit is 1
            running = (-1*(2**15))							#running total is -1 * 2^15
        elif i >= 1 and total[i] == "1":					#elif next bit is 1
            running = (running + (2**(15-i)))				#rinning total is 2^(bit position)
        else:
            running = (running * 1)							#if bit is zero running doesnt change
    X_accel = running

    low = acc.read_byte_data(0x6b, 0x2c, force=None)		#read Z axis low byte (sensor add, register)
    high = acc.read_byte_data(0x6b, 0x2d, force=None)		#read Z axis high byte
    high = (high<<8)
    total = str(format((high+low), '16b'))
    #following code converts 2s compliment to signed decimal.
    running = 0
    Z_accel = 0
    while Z_accel == 0:									#while loop to prevent divide by zero
        for i in range(0, len(total)):
            if i == 0 and total[i] == "1":
                running = (-1*(2**15))
            elif i >= 1 and total[i] == "1":
                running = (running + (2**(15-i)))
            else:
                running = (running * 1)
        Z_accel = running       

    tilt = math.atan((X_accel)/(Z_accel)) 					#calculate tilt andle from the X and Z axis values
    tilt = -1 * round(tilt * (180/(math.pi)), 2)			#multiply by -1 to make the value easier to deal with.
    return(tilt)
