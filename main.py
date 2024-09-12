import RPi.GPIO as GPIO
import time
import threading
import movement
import acc
import Handcontroller
import mag
from ser1 import get_latlong
from Coords import convertTOaltaz

#steps per degree alt = 88.889, az = 426.667
Tilt = 0
Rotate = 0
dire = ""


def Startup():
    global Rotate
    Position = get_latlong()									      #poll the GPS to get lat and long
    Tilt = acc.tilt()											          #check current tilt angle, need to make tilt angle horizontal
    if Tilt > -45:												          #if tilt angle greater than -45 degrees
        movement.Movement(0, (-1*Tilt))							#move up if angle is negative and down if positive
    elif Tilt < -45:											          #elif tilt angle less than -45 degree(TUBE OVER VERTICAL)
        movement.Movement(0, (-1*(Tilt+180)))				#move down 180d-tilt angle
    check_tilt = True
    while check_tilt:											          #at this point tilt should be close to zero following code refines to +-0.5
        Tilt = acc.tilt()
        if Tilt > 0.5 or Tilt < -0.5:
            Tilt = acc.tilt()
            movement.Movement(0, (0-Tilt))
        else:
            check_tilt = False
    mag.find_north()											          #metal optical tube clear of magnetometer(less interference)
    Rotate = 0													            #zeros global Rotate
    return(Position)											          #returns lat and long

def TT():														                #threaded function to concurrently check handcontroller
    run = True													            #value for loop
    global dire													            #import global string to issue direction commands
    while run == True:											        #loop to check if stop move command sent
        dire = Handcontroller.handcontroller()
        print(dire)
        if dire == "stop END":									    #stop movement terminate loop
            run = False

def Tt(R, T):													              #threaded function to concurrently move telescope
    global dire, Rotate, Tilt
    count = 0
    while dire != "stop END":									      #loop movement until global dire value = stop
        movement.Movement(R, 0-T)
        count = count+1											        #keep track of number of loops
    if R == -0.25:												          #keep track of where telescope is pointing
        Rotate = Rotate - (count*0.25)
    elif R == 0.25:
        Rotate = Rotate + (count*0.25)
    else:
        Tilt = acc.tilt()

        
def Jog():														                              #this function is called when the userselects joystick control
    global dire													                            #global string for desired telescope direction for use in other funcs
    action = True												                            #value for looping the jog function 
    while action == True:										                        #loop function until user sends stop command from hand controller
        dire = Handcontroller.handcontroller()					            #wait for direction input from handcontroller
        if dire == "up END":									                      #if desired direction is up
            T2 = threading.Thread(target=TT, args=())			          #thread to check handcontroller mssg(func TT()) concurrently with movement
            T1 = threading.Thread(target=Tt, args=(0,-0.25,))	      #thread to move 0.25 degrees up 
            T1.start()											                        #start thread one
            T2.start()											                        #start thread two
            T1.join()											                          #terminate threads when finished
            T2.join()
        elif dire == "down END":
            T2 = threading.Thread(target=TT, args=())
            T1 = threading.Thread(target=Tt, args=(0,0.25,))
            T1.start()
            T2.start()
            T1.join()
            T2.join()
        elif dire == "left END":
            T2 = threading.Thread(target=TT, args=())
            T1 = threading.Thread(target=Tt, args=(-0.25,0,))
            T1.start()
            T2.start()
            T1.join()
            T2.join()
        elif dire == "right END":
            T2 = threading.Thread(target=TT, args=())
            T1 = threading.Thread(target=Tt, args=(0.25,0,))
            T1.start()
            T2.start()
            T1.join()
            T2.join()
        elif dire == "Tstop END":							                              #mssg from handcontroller to stop jog function and break loop
            action = False

Position = Startup()										                                    #return value of startup is the lat long position of the telescope. 
    
while True:
    HC_mssg = Handcontroller.handcontroller()				                        #call handcontroller function return value =
        
    if HC_mssg == "jog END":								                                #if message from hand controller is jog (joystickcontrol)
        Jog()												                                        #call jog() function    
    elif HC_mssg == "COORDS END":							                              #if message from handcontroller is user wants to enter coords
        RADEC = Handcontroller.handcontroller()				                      #get coordinates from handcontroller
        RA = (RADEC[0:2]+"h"+ RADEC[3:5]+"m"+str(int(RADEC[6:7])*6)+".0s")	#strip RA value from handcontroller message
                                                                            #converting Decimal mins to seconds E.G. 42.1mins
                                                                            # = 42m 6.0s
        DECms = str(round((((int(RADEC[13:15]))/100)*60),4))				        #Dec entered as dedimal degrees needs to be deg:min:secs
                                                                            #line converts degree fractions to decimal mins
        DECms = DECms.split(".")											                      #splits value in to 2 element list [mins, min_parts]
        DEC = (RADEC[9]+str(RADEC[10:12])+"d"+str(DECms[0])+"m"+str((int(DECms[1])/10)*60)+"s")
                                                                            #converts rest of DEC in to deg:mins:secs
        altaz = convertTOaltaz(RA,DEC,Position[0],Position[1])				      #coordinate conversion function
        if (float(altaz[0])) > 0 and (float(altaz[0])) < 90:				        #check altitude is within movemet bounds of 0 - 90 degrees of tilt
            mov_tilt = float(altaz[0]) - acc.tilt()							            #generate movement in degrees for tilt
            m = float(altaz[1]) - Rotate									                  #generate movement in degrees for rotation
            if m > 180:														                          #this part to make sure the telescope doesnt tie itself up in power cord
                m = m-360
            elif m < -180:
                m = m + 360
            movement.Movement(m, mov_tilt)									                #movement command
            Rotate = round(float(altaz[1]), 2)								              #update rotate global to keep track of location
        track = Handcontroller.handcontroller()								              #wait for handcontroller response 
        while track != ("Tstop END"):										                    #if the hadcontroller doesnt send a stop command then loop
            altaz = convertTOaltaz(RA,DEC,Position[0],Position[1])			    #reconvert coordinates stored for new time
            track = Handcontroller.handcontroller()							            #check latest handcontroller message
            if (float(altaz[0])) > 0 and (float(altaz[0])) < 90:			      #generate movement command as before
                print (acc.tilt(), altaz[0])
                mov_tilt = float(altaz[0])-acc.tilt()#issue here
                m = float(altaz[1]) - Rotate
                if m > 180:
                    m = m-360
                elif m < -180:
                    m = m + 360
                movement.Movement(m, mov_tilt)
                Rotate = round(float(altaz[1]), 2)
