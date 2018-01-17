#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class pmDataCollect():
    def __init__(self, lengthData, debug=False):
        self.indoorPM1 = []
        self.indoorPM25 = []
        self.indoorPM10 = []
        self.outdoorPM1 = []
        self.outdoorPM25 = []
        self.outdoorPM10 = []
        self.numData = lengthData
        self.voiceFile = ""
        self.displayMode = 0  #0(default), 1 (outdoor), 2(indoor)
        self.displayScreen = 0  #for displayMode=1 or 2, 0: pm1, 1: pm25, 2: pm10

    def dataInput(self, pmType, dataInsert):

        if(pmType == "indoor_pm1"):
            self.indoorPM1.append(dataInsert)
            if(len(self.indoorPM1)>self.numData):
                self.indoorPM1.pop(0)
        elif (pmType == "indoor_pm25"):
            self.indoorPM25.append(dataInsert)
            if(len(self.indoorPM25)>self.numData):
                self.indoorPM25.pop(0)

        elif (pmType == "indoor_pm10"):
            self.indoorPM10.append(dataInsert)
            if(len(self.indoorPM10)>self.numData):
                self.indoorPM10.pop(0)

        elif (pmType == "outdoor_pm1"):
            self.outdoorPM1.append(dataInsert)
            if(len(self.outdoorPM1)>self.numData):
                self.outdoorPM1.pop(0)

        elif (pmType == "outdoor_pm25"):
            self.outdoorPM25.append(dataInsert)
            if(len(self.outdoorPM25)>self.numData):
                self.outdoorPM25.pop(0)

        elif (pmType == "outdoor_pm10"):
            self.outdoorPM10.append(dataInsert)
            if(len(self.outdoorPM10)>self.numData):
                self.outdoorPM10.pop(0)

    def getData(self, pmType):
        if(pmType == "indoor_pm1"):
            return self.indoorPM1

        elif (pmType == "indoor_pm25"):
            return self.indoorPM25

        elif (pmType == "indoor_pm10"):
            return self.indoorPM10

        elif (pmType == "outdoor_pm1"):
            return self.outdoorPM1

        elif (pmType == "outdoor_pm25"):
            return self.outdoorPM25

        elif (pmType == "outdoor_pm10"):
            return self.outdoorPM10

    def getLiveData(self, pmType):
        if(pmType=="pm1"):
            if(len(self.outdoorPM1)>0):
                return (self.outdoorPM1[-1], self.indoorPM1[-1])
            else:
                return (0,0)
        elif(pmType=="pm25"):
            if(len(self.outdoorPM25)>0):
                return (self.outdoorPM25[-1], self.indoorPM25[-1])
            else:
                return (0,0)
        elif(pmType=="pm10"):
            if(len(self.outdoorPM10)>0):
                return (self.outdoorPM10[-1], self.indoorPM10[-1])
            else:
                return (0,0)

    def btnSelect(self, btn1, btn2):
        self.voiceFile = ""
        if(btn1==1 and btn2==0 ):
            print("pinOutdoor clicked")
            if(self.displayMode != 1):
                self.displayMode = 1
            else:
                self.displayScreen += 1
                if(self.displayScreen>2): self.displayScreen=0

            if(self.displayScreen==0):
                self.voiceFile = "wav/pm1-outdoor.wav"
            elif(self.displayScreen==1):
                self.voiceFile = "wav/pm25-outdoor.wav"
            elif(self.displayScreen==2):
                self.voiceFile = "wav/pm10-outdoor.wav"

        if(btn1==0 and btn2==1):
            print("pinIndoor clicked")
            if(self.displayMode != 2):
                self.displayMode = 2
                self.displayScreen += 1
                if(self.displayScreen>2): self.displayScreen=0
            else:
                self.displayScreen += 1
                if(self.displayScreen>2): self.displayScreen=0

            if(self.displayScreen==0):
                self.voiceFile = "wav/pm1-indoor.wav"
            elif(self.displayScreen==1):
                self.voiceFile = "wav/pm25-indoor.wav"
            elif(self.displayScreen==2):
                self.voiceFile = "wav/pm10-indoor.wav"

        if(btn1==1 and btn2==1):
            print("2 buttons clicked")
            self.displayMode = 0
            self.voiceFile = "wav/pmstatus.wav"

