import smbus2
import time
import movement
import numpy
import csv

def northSTUP():
    mag = smbus2.SMBus(1)									#i2c bus call  =  mag
    mag.write_byte_data(0x1e,0x20,0b11111100, force=None)	#writes to reg20h Temp = on, ultrahighperformance, 80Hz data rate
    mag.write_byte_data(0x1e,0x21,0b00000000, force=None)	#writes to reg21h full scale config +- 4 gauss
    mag.write_byte_data(0x1e,0x22,0b00000000, force=None)	#writes to reg22h lowpower off, spi off, continuous mode on
    #stat = mag.read_byte_data(0x1e, 0x27, force=None)		#code to read status reg for debugging
    #print (stat)
    
def north():
    mag = smbus2.SMBus(1)
    reads = 0
    readings = []
    while reads < 50:										#while loop to take 50 samples
        time.sleep(0.01)									#timing to not exceed 80 reads ber second
        low = mag.read_byte_data(0x1e, 0x28, force=None)	#Values read the same ans the accelerometer
        high = mag.read_byte_data(0x1e, 0x29, force=None)
        high = (high<<8)
        total = str(format((high+low), '16b'))
        running = 0
        for i in range(0, len(total)):
            if i == 0 and (total[i]) == "1":
                running = (-1*(2**15))
            elif i >= 1 and total[i] == "1":
                running = (running + (2**(15-i)))
            else:
                running = (running * 1)
        readings.append(running)							#append read of accelerometer to data set 
        reads = reads + 1									#increment while loop counter
    std_dev = numpy.std(readings)							#take standard deviation of the data set of 50 reads
    ave = numpy.mean(readings)								#find average of ddata set
    readings_weeded = []									#list of readings which will be within one standard dev of mean
    for i in readings:										#loop through list of readings
        if i > (ave - std_dev) and i < (ave + std_dev):		# if reading falls inside of one standard dev 
            readings_weeded.append(i)						#append to weeded list
    readings_weeded.sort()
    ave = numpy.median(readings_weeded)
    #ave = round(numpy.mean(readings_weeded),2)				#return average of the weeded list
    return(ave)												#return the average value to find_north()
            

def find_north():  
    northSTUP()									#call setup
    deg = 0										#sets initial position as zero
    pos = []									#position list (degrees)
    xatpos = []									#value at position
    while deg <= 45:							#while degree steps are less than or equal to 45
        pos.append(deg)							#append degree value to pos list
        xatpos.append(north())					#append result of north function to x at position list
        deg = deg + 0.5							#increment degree value
        movement.Movement(0.5,0)				#rotate one degree clockwise 
    movement.Movement(-90,0)					#when loop complete rotate 90 degree counter clockwise
    deg = -45									#set degree value to -45 degrees
    while deg < 0:								#while dregree steps are less than 0 (start at -45)
        pos.append(deg)							#append degree value to pos list
        xatpos.append(north())					#append result of north function to x at position list
        deg = deg + 0.5							#increment degree value
        movement.Movement(0.5,0)				#rotate one degree clockwise
    print(xatpos)
    max_index = xatpos.index(max(xatpos))		#find list index of the highest value of x
    movement.Movement(pos[max_index], 0)		#move to that position which is at the same index in pos list
    return()
        
   

find_north()
