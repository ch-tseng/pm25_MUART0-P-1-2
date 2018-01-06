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

air=G3()
air.debug = False
i = 0
while True:
    pirStatus = GPIO.input(pinPIR)

    if(GPIO.input(pinOutdoor)==1 and GPIO.input(pinIndoor)==0 ):
        print("pinOutdoor clicked")
        if(displayMode != 1):
            displayMode = 1
        else:
            displayScreen += 1
            if(displayScreen>2): displayScreen=0

    if(GPIO.input(pinIndoor)==1 and GPIO.input(pinOutdoor)==0):
        print("pinIndoor clicked")
        if(displayMode != 2):
            displayMode = 2
            displayScreen += 1
            if(displayScreen>2): displayScreen=0
        else:
            displayScreen += 1
            if(displayScreen>2): displayScreen=0

    if(GPIO.input(pinIndoor)==1 and GPIO.input(pinOutdoor)==1):
        print("2 buttons clicked")
        displayMode = 0


    if(i % 2 == 0):
        GPIO.output(pinDevice, GPIO.LOW)
        G3device = 0

    else:
        GPIO.output(pinDevice, GPIO.HIGH)
        G3device = 1

    g3 = (air.read("/dev/ttyS0"))
    time.sleep(0.5)
    g3 = (air.read("/dev/ttyS0"))

    if(i % 2 == 0):
        try:
            pm10_a = g3[3]
            pm10 = g3[3]
        except:
            pm10_a = 0
            pm10 = 0

        try:
            pm25_a = g3[5]
            pm25 = g3[5]
        except:
            pm25_a = 0
            pm25 = 0

        try:
            pm100_a = g3[4]
            pm100 = g3[4]
        except:
            pm100_a = 0
            pm100 = 0

        dataPM.dataInput("indoor_pm1", pm10_a)
        dataPM.dataInput("indoor_pm25", pm25_a)
        dataPM.dataInput("indoor_pm10", pm100_a)

    else:
        try:
            pm10_b = g3[3]
            pm10 = g3[3]
        except:
            pm10_b = 0
            pm10 = 0

        try:
            pm25_b = g3[5]
            pm25 = g3[5]
        except:
            pm25_b = 0
            pm25 = 0

        try:
            pm100_b = g3[4]
            pm100 = g3[4]
        except:
            pm100_b = 0
            pm100 = 0

        dataPM.dataInput("outdoor_pm1", pm10_b)
        dataPM.dataInput("outdoor_pm25", pm25_b)
        dataPM.dataInput("outdoor_pm10", pm100_b)

    print ("time:{} PIR:{} device:{} --> pm1:{} pm2.5:{} pm10:{}".format(round(time.time()-lastPlayVoice), pirStatus, G3device, pm10, pm25, pm100))

    if(i % 2 != 0):
        if(displayMode==0):
            lcd.printPMdata("e1.ttf", pm10=(pm10_a,pm10_b), pm25=(pm25_a,pm25_b), pm100=(pm100_a,pm100_b), imagePath="pics/pmbg.jpg")

        elif(displayMode==1):
            if(displayScreen==0):
                lcd.drawLineChart(outdoorPM1, "e1.ttf", "pics/outdoor_pm1.jpg")
            elif(displayScreen==1):
                lcd.drawLineChart(outdoorPM25, "e1.ttf", "pics/outdoor_pm25.jpg")
            elif(displayScreen==2):
                lcd.drawLineChart(outdoorPM10, "e1.ttf", "pics/outdoor_pm10.jpg")

        elif(displayMode==2):
            if(displayScreen==0):
                lcd.drawLineChart(indoorPM1, "e1.ttf", "pics/indoor_pm1.jpg")
            elif(displayScreen==1):
                lcd.drawLineChart(indoorPM25, "e1.ttf", "pics/indoor_pm25.jpg")
            elif(displayScreen==2):
                lcd.drawLineChart(indoorPM10, "e1.ttf", "pics/indoor_pm10.jpg")

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




