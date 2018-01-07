import time, os
import RPi.GPIO as GPIO
#from libraryCH.database.sqlite import sqlitedb
from libMUART.device.air import G3
from libMUART.device.lcd import ILI9341
from libMUART.app.MUART0P12 import pmDataCollect
from subprocess import call

call(["amixer", "sset", "PCM,0", "100%"])

#Configurable
debug=0
pinDevice = 2
pinPIR = 4
pinOutdoor = 21
pinIndoor = 20

numData = 46  #How many data point will display on the screen?
pirSensity = 10  #Sensity for the PIR, large number will delay the PIR senssity

#Fixed
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
displayMode = 0  #0(default), 1 (outdoor), 2(indoor)
displayScreen = 0  #for displayMode=1 or 2, 0: pm1, 1: pm25, 2: pm10
lastPlayVoice = 0
pirAccumulated = 0

#Setup
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

def modeSelect(btn1, btn2):
    global displayMode, displayScreen

    voiceFile = ""
    if(btn1==1 and btn2==0 ):
        print("pinOutdoor clicked")
        if(displayMode != 1):
            displayMode = 1
        else:
            displayScreen += 1
            if(displayScreen>2): displayScreen=0

        if(displayScreen==0):
            voiceFile = "wav/pm1-outdoor.wav"
        elif(displayScreen==1):
            voiceFile = "wav/pm25-outdoor.wav"
        elif(displayScreen==2):
            voiceFile = "wav/pm10-outdoor.wav"

    if(btn1==0 and btn2==1):
        print("pinIndoor clicked")
        if(displayMode != 2):
            displayMode = 2
            displayScreen += 1
            if(displayScreen>2): displayScreen=0
        else:
            displayScreen += 1
            if(displayScreen>2): displayScreen=0

        if(displayScreen==0):
            voiceFile = "wav/pm1-indoor.wav"
        elif(displayScreen==1):
            voiceFile = "wav/pm25-indoor.wav"
        elif(displayScreen==2):
            voiceFile = "wav/pm10-indoor.wav"

    if(btn1==1 and btn2==1):
        print("2 buttons clicked")
        displayMode = 0
        voiceFile = "wav/pmstatus.wav"

    if(displayMode==0):
        lcd.printPMdata("e1.ttf", pm10=dataPM.getLiveData("pm1"), pm25=dataPM.getLiveData("pm25"), pm100=dataPM.getLiveData("pm10"), imagePath="pics/pmbg.jpg")

    elif(displayMode==1):
        if(displayScreen==0):
            lcd.drawLineChart(dataPM.getData("outdoor_pm1"), "e1.ttf", "pics/outdoor_pm1.jpg")
        elif(displayScreen==1):
            lcd.drawLineChart(dataPM.getData("outdoor_pm25"), "e1.ttf", "pics/outdoor_pm25.jpg")
        elif(displayScreen==2):
            lcd.drawLineChart(dataPM.getData("outdoor_pm10"), "e1.ttf", "pics/outdoor_pm10.jpg")

    elif(displayMode==2):
        if(displayScreen==0):
            lcd.drawLineChart(dataPM.getData("indoor_pm1"), "e1.ttf", "pics/indoor_pm1.jpg")
        elif(displayScreen==1):
            lcd.drawLineChart(dataPM.getData("indoor_pm25"), "e1.ttf", "pics/indoor_pm25.jpg")
        elif(displayScreen==2):
            lcd.drawLineChart(dataPM.getData("indoor_pm10"), "e1.ttf", "pics/indoor_pm10.jpg")

    if(voiceFile != ""): os.system('omxplayer --no-osd ' + voiceFile )


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
    modeSelect(btn1, btn2)

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
