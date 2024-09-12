import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)                           
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_UP)

   
def alt(steps):
    GPIO.output(11, GPIO.LOW)			#enable pin
    if steps < 0:						#set direction down
        GPIO.output(13, GPIO.HIGH)
    elif steps > 0:						#set direction up
        GPIO.output(13, GPIO.LOW)
    else:
        return(0)						# if zero steps no movement
    time.sleep(0.01)
    steps = abs(steps)					#remove sign from steps value
    steps1 = 0
    while steps1 < steps:				#loop through number of steps
        GPIO.output(15, GPIO.HIGH) 		#step
        time.sleep(0.005)				#100 steps per second
        GPIO.output(15, GPIO.LOW)
        time.sleep(0.005)
        steps1 = steps1 + 1
    return()
    
    
def az(steps):
    GPIO.output(31, GPIO.LOW)			#enable pin
    if steps < 0:				#set direction left
        GPIO.output(33, GPIO.HIGH)
    elif steps > 0 :	#set direction right
        GPIO.output(33, GPIO.LOW)
    else:
        return(0)
    time.sleep(0.01)
    steps = abs(steps)
    steps1 = 0    
    while steps1 < steps:
        GPIO.output(35, GPIO.HIGH) 		#step
        time.sleep(0.001)
        GPIO.output(35, GPIO.LOW)
        time.sleep(0.001)
        steps1 = steps1 + 1
    return()

def Movement(Rotate, Tilt):
    
    altstep = int(round((Tilt*88.889), 0))				#degrees*steps per. rounded to nearest step
    azstep = int(round((Rotate*426.667), 0))
    t1 = threading.Thread(target=az, args=(azstep,))	#define threads
    t2 = threading.Thread(target=alt, args=(altstep,))

    t1.start()											#call threads
    t2.start()
    t1.join()											#join threads
    t2.join()
