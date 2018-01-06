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

