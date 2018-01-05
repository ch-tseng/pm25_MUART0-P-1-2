import time
import RPi.GPIO as GPIO
#from libraryCH.database.sqlite import sqlitedb
from libraryCH.device.air import G3
from libraryCH.device.lcd import ILI9341
from subprocess import call

call(["amixer", "sset", "PCM,0", "5%"])

#Configurable
debug=0
pinDevice = 2
pinPIR = 4
pinOutdoor = 21
pinIndoor = 20

numData = 46

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
indoorPM1 = []
indoorPM25 = []
indoorPM10 = []
outdoorPM1 = []
outdoorPM25 = []
outdoorPM10 = []
displayMode = 0  #0(default), 1 (outdoor), 2(indoor)
displayScreen = 0  #for displayMode=1 or 2, 0: pm1, 1: pm25, 2: pm10

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

def collectData(pmType, dataInsert):
    global indoorPM1, indoorPM25, indoorPM10, outdoorPM1, outdoorPM25, outdoorPM10

    if(pmType == 0):
        indoorPM1.append(dataInsert)
        if(len(indoorPM1)>numData):
            indoorPM1.pop(0)
    elif (pmType == 1):
        indoorPM25.append(dataInsert)
        if(len(indoorPM25)>numData):
            indoorPM25.pop(0)

    elif (pmType == 2):
        indoorPM10.append(dataInsert)
        if(len(indoorPM10)>numData):
            indoorPM10.pop(0)

    elif (pmType == 3):
        outdoorPM1.append(dataInsert)
        if(len(outdoorPM1)>numData):
            outdoorPM1.pop(0)

    elif (pmType == 4):
        outdoorPM25.append(dataInsert)
        if(len(outdoorPM25)>numData):
            outdoorPM25.pop(0)

    elif (pmType == 5):
        outdoorPM10.append(dataInsert)
        if(len(outdoorPM10)>numData):
            outdoorPM10.pop(0)


air=G3()
i = 0
while True:

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
    print ("device:{} --> pm1:{} pm2.5:{} pm10:{}".format(G3device, g3[3], g3[5], g3[4]))

    if(i % 2 == 0):
        pm10_a = g3[3]
        pm25_a = g3[5]
        pm100_a = g3[4]

        collectData(0, pm10_a)
        collectData(1, pm25_a)
        collectData(2, pm100_a)

    else:
        pm10_b = g3[3]
        pm25_b = g3[5]
        pm100_b = g3[4]
        collectData(3, pm10_b)
        collectData(4, pm25_b)
        collectData(5, pm100_b)

    if(i % 2 != 0):
        if(displayMode==0):
            lcd.printPMdata("e1.ttf", pm10=(pm10_a,pm10_b), pm25=(pm25_a,pm25_b), pm100=(pm100_a,pm100_b), imagePath="pmbg.jpg")

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

    i += 1




