#!/usr/bin/python3

import tomllib
import requests
import io
import time
import getopt
import sys , os
from typing import Self
from datetime import datetime

CONFIG_NAME = "config.toml"
# TICK_S = 0.3j

class Conf:
    def __init__(self):
        self.baseUrl:str = ""
        self.detail1per = 0
        self.detail2per = 0
        self.detail3per = 0
        self.readToml(CONFIG_NAME)
    def readToml(self, fname:str):
        with open(fname, "rb") as f:
            tomlTable = tomllib.load(f)
            if "detail1_period_it" in tomlTable:
                self.detail1per = tomlTable["detail1_period_it"]
            if "detail2_period_it" in tomlTable:
                self.detail2per = tomlTable["detail2_period_it"]
            if "detail3_period_it" in tomlTable:
                self.detail3per = tomlTable["detail3_period_it"]
            if "baseUrl" in tomlTable:
                self.baseUrl = tomlTable["baseUrl"]
    def getCliArgs(self, argv):
       try:
          opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
       except getopt.GetoptError:
          print ('Bad invocation')
          sys.exit(2)
       for opt, arg in opts:
          if opt == '-h':
             print ("NO HELP! ha-ha")
             sys.exit()
          elif opt in ("-i", "--ifile"):
             print("now know i-file")
          elif opt in ("-o", "--ofile"):
             print("now know o-file")
    def getEnvValues(self):
        # Env has priority
        envApiKey = os.environ.get('trafWatchBaseUrl', None)
        if envApiKey: self.baseUrl = envApiKey
    def showAll(self):
        print("\nCurrent params:")
        for name, value in self.__dict__.items():
            print(f"    {name} = {value}")

from enum import Enum, auto

class Dir(Enum):
    Rx = auto()
    Tx = auto()

class trafRecord:
    def __init__(self, name:str, amount:float, dir:Dir):
        self.name:str = name
        self.amount:float = amount
        self.dir:Dir = dir
    @classmethod
    def fromJson(cls, s:str) -> Self:
        return trafRecord(s, 0, Dir.Rx)

class App:
    def __init__(self):
        self.freqs :list[trafRecord] = []
    def restGetRecords(self):
        pass
    def summRecords(self):
        pass
    def printViolators(self):
        print(f"Violators are {1,2,3}")

if __name__ == "__main__":
    conf = Conf()
    conf.readToml(CONFIG_NAME)
    conf.showAll()

    app = App()
    app.restGetRecords()
    app.summRecords()
    app.printViolators()

    print("Oneshot finished")
    # exCode:int = not ok
    # sys.exit(exCode) # exit with 0 if Ok


