import time
import serial

def get_latlong():
    ser = serial.Serial('/dev/ttyAMA3', 		#set serial port 3 up
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS)

    time.sleep(0.1)
    LL = []
    ll = []
    x = ser.read_until(b'GGA')					#read until start of string of interest 
    x = ser.read_until(b'GSA')					#read until rend of strinf of interest, discard previous.
    x = x.decode()								#decode from hex
    #Parse LAT + LONG
    LL.append((round(int(x[12:14])+(((int(x[14:16])+(int(x[17:21])/10000))/60)),5))) #list entry 0 = LAT
    LL.append((round(int(x[24:27])+(((int(x[27:29])+(int(x[30:34])/10000))/60)),5))) #list entry 1 = LONG
    if x[35] == "W": 							# loop to "sign" value depending on E or W
        LL[1] = 0-LL[1]
    return(LL)									#return list LL (LAT, LONG)
