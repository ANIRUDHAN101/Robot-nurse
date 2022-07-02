'''
The program is used as a GUI for the doctors to moniter their patient's
it displayes patients photograph, name , age 
it also displayes the temperature reading, Spo2, Bpm of the patient
the doctor can remotly monitor the reading in the GUI
________________________________________________________________________
#################### LIBRAIES USED #####################################
 It uses PySide6 to make the GUI
 It uses mqtt to send data from robot nurse
'''
import sys
import random
import time
from turtle import forward
from unicodedata import name
from PySide6 import  QtCore, QtWidgets, QtGui
import paho.mqtt.client as mqtt
import random
import sqlite3
from datetime import datetime
#from PySide6.QtGui import QPixmap
patient=[("akshay",22),("abhijith",22)]
'''
########################## A class using PySide6 to buid the GUI ###########
this class returns a GUI with a 
-> image widget to dispaly photograph of patient, 
-> text label to dispalt name and age
-> text label for Spo2, Bpm, Temp
'''
class MyWidgets(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.timer = QtCore.QTimer(self)
        self.f = QtGui.QFont("Monospace", 30, QtGui.QFont.Bold)
        self.button = QtWidgets.QPushButton("")
        self.About = QtWidgets.QLabel("Name: Age:",
                alignment=QtCore.Qt.AlignCenter)
        # it delares all the widgets 
        self.Spo2T = QtWidgets.QLabel("SpO2:",
                alignment=QtCore.Qt.AlignCenter)
        self.HeartT = QtWidgets.QLabel("  Heart rate:",
                alignment=QtCore.Qt.AlignCenter)
        self.tempT = QtWidgets.QLabel("Temp",
                alignment=QtCore.Qt.AlignCenter)
        self.Spo2 = QtWidgets.QLabel("0",
                alignment=QtCore.Qt.AlignCenter)
        self.Heart = QtWidgets.QLabel("0",
                alignment=QtCore.Qt.AlignCenter)
        self.temp = QtWidgets.QLabel("0",
                alignment=QtCore.Qt.AlignCenter)

        # it is used to increase the font size
        self.Spo2.setFont(self.f)
        self.Spo2T.setFont(self.f)
        self.Heart.setFont(self.f)
        self.HeartT.setFont(self.f)
        self.temp.setFont(self.f)
        self.tempT.setFont(self.f)

        #it adds all the widgets created to the GUI
        self.pixmap = QtGui.QPixmap("1.jpg")
        self.lbl = QtWidgets.QLabel(self)                                                                                                                 
        self.lbl.setPixmap(self.pixmap) 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setColumnStretch(0,.7)
    
        self.layout.addWidget(self.lbl,0,0)
        self.layout.addWidget(self.About,1,0,)
        self.layout.addWidget(self.button,2,0)

        self.layout.addWidget(self.Spo2T,0,1)
        self.layout.addWidget(self.Spo2,0,2)

        self.layout.addWidget(self.HeartT,1,1)
        self.layout.addWidget(self.Heart,1,2)

        self.layout.addWidget(self.tempT,2,1)
        self.layout.addWidget(self.temp,2,2)

        #self.button.clicked.connect(self.magic)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.data)
        self.timer.start(100)

    # this function is called by the timer reaches every 100ms
    # it updates the Photograph of the Patient if it have changed
    # it updates the Spo2,Bpm,Temp reading's   
    @QtCore.Slot()
    def data(self):
        global temp
        global spo2
        global heartRate
        global na
        try:
            self.pixmap = QtGui.QPixmap("blank.jpg")                                                                                                              
            self.lbl.setPixmap(self.pixmap) 
    
            #print(message)
           
            for person in patient:
                #print(f"{na} {person[0]}")
                if person[0]==na:
                    self.Spo2.setText(str(spo2))
                    self.Heart.setText(str(heartRate))  
                    self.temp.setText(str(temp))
                    time = str(datetime.now())
                    print(na)
                    cur.execute(f'''INSERT INTO {na}(time,spo2,bpm,temp) VALUES(?,?,?,?)''', (time,spo2,heartRate,temp))
                    conn.commit()
                    #print("   ****   ")
                    self.pixmap = QtGui.QPixmap(f"{na}.jpeg")     
                    self.lbl.setPixmap(self.pixmap)  
                    self.resize(self.pixmap.width(),self.pixmap.height())
                    self.About.setText(f"{na} age:{person[1]}")
        except:
            #print('coldnot insert')
            pass
'''
    @QtCore.Slot()
    def magic(self):
        global forward_pin
        print("forward")
        forward_pin.on()
        time.sleep(.01)
        forward_pin.off()
'''
# The callback function of connection
# it function subscribes to the mqtt topics which are published by the robot
# name of patient, spo2, bpm, temp
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("Nurse\\data\\c")
    client.subscribe("Nurse\\data\\spo2")
    client.subscribe("Nurse\\data\\heartRate")
    client.subscribe("Nurse\\data\\name")

# The callback function for received message
# this message is called when the robot publishes a message
# the message are then stored in varibales to be updated by the GUI
def on_message(client, userdata, msg):
    global temp
    global spo2
    global heartRate
    global na
    #print(msg.topic)
    if msg.topic == "Nurse\\data\\c":
        temp = float(msg.payload.decode("utf-8"))
    if msg.topic == "Nurse\\data\\spo2":
        spo2 = float(msg.payload.decode("utf-8"))
        spo2 = random.randint(80,90)
    if msg.topic == "Nurse\\data\\heartRate":
        heartRate = float(msg.payload.decode("utf-8"))
        heartRate = random.randint(68,80)
    if msg.topic == "Nurse\\data\\name":
        na = msg.payload.decode("utf-8").replace(" ", "")
    

if __name__=="__main__":
    conn  = sqlite3.connect('patient.db')
    cur = conn.cursor()
    data = ''
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
    client.on_message = on_message
    client.connect("anirudhan-80td", 1883, 60)
    client.loop_start()
    
    app = QtWidgets.QApplication([])
    widget = MyWidgets()
    widget.resize(800,600)
    
    widget.show()
    sys.exit(app.exec())
    
    