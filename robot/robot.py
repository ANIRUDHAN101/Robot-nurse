'''
The program is used to run the robot 
the program runs in the raspberypi
_________________________________________
########## Libraries used ##############
the program uses gpio for obstacle ditection
matt pacho for communication with mqtt brocker
mfrc522 library for reading rfid card
w1thermsensor for reading temperature
threading for running multiple functions at a time
'''
from gpiozero import DistanceSensor
from time import sleep
from os import system
from threading import Thread
import queue
import max30100
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time
import os
import random

# function used to stop robot if  an obstacle detected
#1xx
def motorStop_distance():
    GPIO.output(cont1, 1) 
# function used to stop robot if  a rfid card detected
#x1x
def motorStop_rfid():
    GPIO.output(cont2, 1) 
# function used to Run robot if  an is not obstacle detected
# 0xx
def motorRun_distance():
    GPIO.output(cont1, 0) 
# function used to stop robot if  a rfid card is not detected
# x0x
def motorRun_rfid():
    GPIO.output(cont2, 0) 
# the function is called when the mqtt client establishes connection
# with the brocker 
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
# this function is called to read the spo2, bpm and publish it to mqtt brocker
def Spo2():
    global max30
    mx30.read_sensor()
    mx30.ir, mx30.red

    hb = int(mx30.ir / 100)
    spo2 = int(mx30.red / 100)
    
                    
    if mx30.ir != mx30.buffer_ir :
        print("Pulse:",hb)
        client.publish('Nurse\\data\\heartRate', payload=hb, qos=0, retain=False)
    if mx30.red != mx30.buffer_red:
        print("SPO2:",spo2)
        client.publish('Nurse\\data\\spo2', payload=spo2, qos=0, retain=False)

# the function is used to read temperature and publish it to mqtt brocker
def Temp():
    global sensor
    temperature = tempSensor.get_temperature()
    
    client.publish('Nurse\\data\\c', payload=temperature, qos=0, retain=False)
    print("The temperature is %s celsius" % temperature)

# the function is used to measuere the obstacle distance and  stop the robot and play an audio along with it
# the function runs as an individual thread
def distance(mode):
    dist_thresh = 20
    ob = 0
    while True:
        distance = ultraSound.distance * 100
        #print('Distance: ', distance)
        
        if distance <=dist_thresh:
            motorStop_distance()      
            GPIO.output(led_left_red,1)
            GPIO.output(led_right_red,1)
            system("mpg123 obstacle_detected.mp3")
            ob = 1
        else:
            
            GPIO.output(led_left_red,0)
            GPIO.output(led_right_red,0)
            motorRun_distance()    
        sleep(.001)
 
# the function is used to read the rfid card 
#  the function runs as an individual thread
def rfid(mode):
    reader = SimpleMFRC522()
    old_id = None
    old_person_time = time.time()
    delay = 20
    led_old  = time.time()
    led_old  = time.time()
    delay_led =.19
    seq = [0,1,0,1]
    while True:
        try:
            id,text = reader.read_no_block()
            if  id!=None:
                motorStop_rfid()
                GPIO.output(led_left_red,0)
                GPIO.output(led_right_red,0)
                GPIO.output(led_left_green,1)
                GPIO.output(led_right_green,1)
                
                #id, text = reader.read()
                text = text.replace(" ","")
                print(f"ID: {id} name {text}")
                client.publish('Nurse\\data\\name', payload=text, qos=0, retain=False)
                audio = os.listdir('audio')
                system(f"mpg123 audio/{text}.mp3")  
                # the wile loop runs for a time(variable delay=10) withot using any delay
                # you can change the variable to adjust the time spend by the while loop
                old_person_time = time.time() 
                time.sleep(4)
                while time.time()-old_person_time<=delay:
                    random.shuffle(seq)
                    GPIO.output(led_left_green,seq[0])
                    GPIO.output(led_right_green,seq[1])
                    Spo2()
                    GPIO.output(led_left_green,seq[2])
                    GPIO.output(led_right_green,seq[3])
                    Temp()
                    print(time.time()-old_person_time)
                # the function checks if the card is still there 
                system(f"mpg123 audio/{text}_thank.mp3") 
                motorRun_rfid()
                time.sleep(1)
                while reader.read_id_no_block()!=None:
                    time.sleep(.19)
                 
            else:
                motorRun_rfid()
                
                  
                GPIO.output(led_left_red,1)
                GPIO.output(led_right_red,1)
                GPIO.output(led_left_green,0)
                GPIO.output(led_right_green,0)
       
        except KeyboardInterrupt:
            GPIO.cleanup()
            raise

if __name__=="__main__":
    '''
    initilize all the pins connected to the raspberry pi as output  
    '''
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD  
    cont1 = 16
    cont2 = 20
    cont3 = 21
    
    led_right_red = 19
    led_right_green = 26
    led_left_red = 6
    led_left_green = 13

    GPIO.setup(cont1, GPIO.OUT)# connected to A3 pin of arduino uno
    GPIO.setup(cont2, GPIO.OUT)# connected to A0 pin of arduino uno
    GPIO.setup(cont3, GPIO.OUT)# connected to A5 pin of arduino uno
    #GPIO.output(16, 1)       # set port/pin value to 1/GPIO.HIGH/True  
    GPIO.output(16, 0)       # set port/pin value to 0/GPIO.LOW/False  

    GPIO.setup(led_right_red, GPIO.OUT)
    GPIO.setup(led_right_green, GPIO.OUT)
    GPIO.setup(led_left_red, GPIO.OUT)
    GPIO.setup(led_left_green, GPIO.OUT)

    GPIO.output(led_left_red,0)
    GPIO.output(led_right_green,0)
    GPIO.output(led_right_red,0)
    GPIO.output(led_left_green,0)
    '''
    pwm_led_r_red = GPIO.PWM(led_right_red,1)
    pwm_led_r_green = GPIO.PWM(led_right_green,1)
    pwm_led_l_red = GPIO.PWM(led_left_green,1)
    pwm_led_l_green = GPIO.PWM(led_left_red,1)
    
    pwm_led_l_green.start(10)

    '''
    mode = queue.Queue(1)

    '''
    It estavlishes a connection between the mqtt brocker
    The brocker can be a free public brocker or brocker running local network
    we are using a local brocker connected to 1883 port
    Note: the port of the sytem in which the brocker running should be open for a client to connect
    if you are runing in a linux machine 
    run 
        sudo iptables -I INPUT -p tcp --dport 1883 -j ACCEPT
    if you are running on a windows machie
        enable it using windows fireWall
    '''
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("broker.emqx.io", 1883, 60)
    client.loop_start()
    oldPatinet=""
    '''
    initilize all the sensors 
    temp sensor
    ultrasound 
    pulseoxy meter
    rfid card reader
    '''
    ultraSound = DistanceSensor(echo=0, trigger=5)
    mx30 = max30100.MAX30100()
    mx30.enable_spo2()
    tempSensor = W1ThermSensor()

    reader = SimpleMFRC522()
    
    '''
    2 threads are used an rfid thread and distance sensor thread
    it is used to do 2 task's at the same time
    '''
    di = Thread(target=distance,args=[mode])
    rf = Thread(target=rfid,args=[mode]).start()
    #led  =Thread(target=led_indicator,args=[mode]).start()
    di.start()
    di.join()
    rf.join()
    led.join()
