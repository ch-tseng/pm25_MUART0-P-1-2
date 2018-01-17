import time, os
import RPi.GPIO as GPIO
#from libraryCH.database.sqlite import sqlitedb
from libMUART.device.air import G3
from libMUART.device.lcd import ILI9341
from libMUART.app.MUART0P12 import pmDataCollect
from subprocess import call

#Set the volume to 100%
call(["amixer", "sset", "PCM,0", "100%"])

#Configurable, you can update the parameter's value below
debug=0  #change to 1 will display more messasge for debug
pinDevice = 2  #the GPIO pin which will switch RF Uart device #1 and #2
pinPIR = 4  #the GPIO pin for PIR module
pinOutdoor = 21  #the GPIO pin for the button of outdoor's pm25 display
pinIndoor = 20  #the GPIO pin for the button of indoor's pm25 display

numData = 46  #How many pm25 data will be displayed on the screen?
pirSensity = 10  #Sensity for the PIR, large number will delay the PIR sensity

#you don't have to change the values below
a_pm1 = [0, 0, 0, 0, 0, 0]
a_pm25 = [0, 0, 0, 0, 0, 0]
a_pm10 = [0, 0, 0, 0, 0, 0]
pm10_a = 0
pm25_a = 0
pm100_a = 0
pm10_b = 0
pm25_b = 0
pm100_b = 0
setVoice = True
setScreen = 0
#displayMode = 0  #0(default), 1 (outdoor), 2(indoor)
#displayScreen = 0  #for displayMode=1 or 2, 0: pm1, 1: pm25, 2: pm10
lastPlayVoice = 0
pirAccumulated = 0

#Setup
#You have to update the LCD's siae and rotation if the LCD is not 240x320 resolution
lcd = ILI9341(LCD_size_w=240, LCD_size_h=320, LCD_Rotate=0)
lcd.displayImg("pics/pmbg.jpg")
time.sleep(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pinDevice ,GPIO.OUT)
GPIO.output(pinDevice, GPIO.LOW)
GPIO.setup(pinPIR ,GPIO.IN)
GPIO.setup(pinOutdoor ,GPIO.IN)
GPIO.setup(pinIndoor ,GPIO.IN)

dataPM = pmDataCollect(lengthData=numData, debug=False)
#dataPM.displayMode = 0  #0(default), 1 (outdoor), 2(indoor)
#dataPM.displayScreen = 9  #for displayMode=1 or 2, 0: pm1, 1: pm25, 2: pm10

def readFromUart(delay=0.5):
    g3 = (air.read("/dev/ttyS0"))
    time.sleep(delay)
    g3 = (air.read("/dev/ttyS0"))

    try:
        pm1 = g3[3]
    except:
        pm1 = 0

    try:
        pm10 = g3[4]
    except:
        pm10 = 0

    try:
        pm25 = g3[5]
    except:
        pm25 = 0

    return (pm1, pm10, pm25)

air=G3()
air.debug = False
i = 0
while True:
    pirStatus = GPIO.input(pinPIR)
    btn1 = GPIO.input(pinOutdoor)
    btn2 = GPIO.input(pinIndoor)

    dataPM.btnSelect(btn1, btn2)
    if(dataPM.displayMode==0):
        lcd.printPMdata("e1.ttf", pm10=dataPM.getLiveData("pm1"), pm25=dataPM.getLiveData("pm25"), \
                pm100=dataPM.getLiveData("pm10"), imagePath="pics/pmbg.jpg")

    elif(dataPM.displayMode==1):
        if(dataPM.displayScreen==0):
            lcd.drawLineChart(dataPM.getData("outdoor_pm1"), "e1.ttf", "pics/outdoor_pm1.jpg")
        elif(dataPM.displayScreen==1):
            lcd.drawLineChart(dataPM.getData("outdoor_pm25"), "e1.ttf", "pics/outdoor_pm25.jpg")
        elif(dataPM.displayScreen==2):
            lcd.drawLineChart(dataPM.getData("outdoor_pm10"), "e1.ttf", "pics/outdoor_pm10.jpg")

    elif(dataPM.displayMode==2):
        if(dataPM.displayScreen==0):
            lcd.drawLineChart(dataPM.getData("indoor_pm1"), "e1.ttf", "pics/indoor_pm1.jpg")
        elif(dataPM.displayScreen==1):
            lcd.drawLineChart(dataPM.getData("indoor_pm25"), "e1.ttf", "pics/indoor_pm25.jpg")
        elif(dataPM.displayScreen==2):
            lcd.drawLineChart(dataPM.getData("indoor_pm10"), "e1.ttf", "pics/indoor_pm10.jpg")

    if(dataPM.voiceFile != ""): 
        os.system('omxplayer --no-osd ' + dataPM.voiceFile )
        dataPM.voiceFile  = ""


    if(i % 2 == 0):
        GPIO.output(pinDevice, GPIO.LOW)
        G3device = 0
        liveData = readFromUart(0.5)

        dataPM.dataInput("indoor_pm1", liveData[0])
        dataPM.dataInput("indoor_pm25", liveData[2])
        dataPM.dataInput("indoor_pm10", liveData[1])
    else:
        GPIO.output(pinDevice, GPIO.HIGH)
        G3device = 1
        liveData = readFromUart(0.5)

        dataPM.dataInput("outdoor_pm1", liveData[0])
        dataPM.dataInput("outdoor_pm25", liveData[2])
        dataPM.dataInput("outdoor_pm10", liveData[1])

    print ("time:{} PIR:{} BTN1:{} BTN2:{} device:{} --> pm1:{} pm2.5:{} pm10:{}".format(round(time.time()-lastPlayVoice),\
            pirStatus, btn1, btn2, G3device, liveData[0], liveData[2], liveData[1]))

    print(liveData)

    if(pirStatus==1): 
        pirAccumulated += 1
    else:
        pirAccumulated = 0

    if(pirAccumulated>pirSensity and i>0 and time.time()-lastPlayVoice>60):
        pirAccumulated = 0

        if(pm25_a<=50):
            wav = 'pm25_1.wav'
        elif(pm25_a>50 and pm25_a<=100):
            wav = 'pm25_2.wav'
        elif(pm25_a>100 and pm25_a<=150):
            wav = 'pm25_3.wav'
        elif(pm25_a>150 and pm25_a<=200):
            wav = 'pm25_4.wav'
        elif(pm25_a>200 and pm25_a<=300):
            wav = 'pm25_5.wav'
        elif(pm25_a>300):
            wav = 'pm25_6.wav'

        os.system('omxplayer --no-osd wav/' + wav)
        lastPlayVoice = time.time()

    i += 1
