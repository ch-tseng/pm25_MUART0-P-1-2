import time
import RPi.GPIO as GPIO
#from libraryCH.database.sqlite import sqlitedb
from libraryCH.device.air import G3
from libraryCH.device.lcd import ILI9341

#Configurable
debug=0
pinDevice = 2

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

#Setup
lcd = ILI9341(LCD_size_w=240, LCD_size_h=320, LCD_Rotate=0)
lcd.displayImg("pmbg.jpg")
time.sleep(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pinDevice ,GPIO.OUT)
GPIO.output(pinDevice, GPIO.LOW)

#pm25db = sqlitedb()
#pm25db.connectDB("pm25db.sqlite")
#pm25db.createTable("pmdata", "(id INTEGER PRIMARY KEY AUTOINCREMENT, datetime default current_timestamp,\
#    ioDoor BOOLEAN NOT NULL, pm10 INT, pm25 INT, pm100 INT)")

air=G3()
i = 0
while True:
    if(i % 2 == 0):
        GPIO.output(pinDevice, GPIO.LOW)
        G3device = 0

    else:
        GPIO.output(pinDevice, GPIO.HIGH)
        G3device = 1

    g3 = (air.read("/dev/ttyS0"))
    time.sleep(1)
    g3 = (air.read("/dev/ttyS0"))
    print ("device:{} --> pm1:{} pm2.5:{} pm10:{}".format(G3device, g3[3], g3[4], g3[5]))

    if(i % 2 == 0):
        pm10_a = g3[3]
        pm25_a = g3[4]
        pm100_a = g3[5]

    else:
        pm10_b = g3[3]
        pm25_b = g3[4]
        pm100_b = g3[5]


 #   columns = "ioDoor, pm10, pm25, pm100"
 #   datas = "{}, {}, {}, {}".format(G3device, g3[3], g3[4], g3[5])
 #   pm25db.insertData("pmdata", columns, datas )

    if(i % 2 != 0):
        lcd.printPMdata("e1.ttf", pm10=(pm10_a,pm10_b), pm25=(pm25_a,pm25_b), pm100=(pm100_a,pm100_b), imagePath="pmbg.jpg")


    i += 1
    time.sleep(3)

#    pm25db.sqlSelect("SELECT * FROM pmdata")
#    for row in pm25db.rows:
#        print (row)




