#!/usr/bin/python3

import tomllib
import requests
import getopt
import sys, os
from typing import Dict, Set
from enum import Enum
import copy

from keenetic_auth import KeenTalker

CONFIGFILE_COMMON = "config.toml"
#CONFIGFILE_SECRET = "secrets.toml"
DEBUG = False

class Conf:
    def __init__(self):
        self.baseUrl:str = ""
        self.botToken = ""
        self.keenLogin = ""
        self.keenPassw = ""
        self.doAuth = False # Для соединения c роутером по локальной сети - False 
        self.manualChats:Set[str] = set()
        self.dtl:Per|None = None
        self.thresh:int|None = None
        self.noDisturb:bool|None = None
    def eval(self):
        # Every next input has higher merit
        self.readToml(CONFIGFILE_COMMON)
        #self.readToml(CONFIGFILE_SECRET)
        self.getEnvValues()
        self.getCliArgs(sys.argv[1:])
    def oneShotParamsReady(self):
        return (self.dtl and self.thresh)
    
    def readToml(self, fname:str):
        global DEBUG
        with open(fname, "rb") as f:
            tomlTable = tomllib.load(f)
            def readTomlValue(tomlChapter, tomlvalueName, classmemberName):
                if tomlvalueName in tomlTable[tomlChapter]:
                    setattr(self, classmemberName, tomlTable[tomlChapter][tomlvalueName])
            readTomlValue("Router", "baseUrl", "baseUrl")
            readTomlValue("Router", "doAuth", "doAuth")
            readTomlValue("Telega", "botToken", "botToken")
            if "credent" in tomlTable["Router"]:
                self.keenLogin, self.keenPassw = tomlTable["Router"]["credent"]
            if "manualChats" in tomlTable["Telega"]:
                for chatID in tomlTable["Telega"]["manualChats"]:
                    conf.manualChats.add(str(chatID))
            if "Debug" in tomlTable["General"]:
                DEBUG = tomlTable["General"]["Debug"]

    def getCliArgs(self, argv):
       global DEBUG
       try:
          opts, args = getopt.getopt(argv, "hd:t:q", ["detail=", "thresh=", "semi-quiet", "debug", "no-debug"])
       except getopt.GetoptError:
          print ('Bad program invocation')
          sys.exit(2)
       for opt, arg in opts:
          if opt == '-h':
             print ("NO HELP! ha-ha")
             sys.exit(2)
          elif opt in ("-d", "--detail"):
              self.dtl = Per[arg]
          elif opt in ("-t", "--thresh"):
              self.thresh = int(arg)
          elif opt in ("-q", "--semi-quiet"):
              self.noDisturb = True
          elif opt in ("--debug"):
              DEBUG = True
          elif opt in ("-q", "--no-debug"):
              DEBUG = False

    def getEnvValues(self):
        def getEnvParam(envName, classmemberName):
            if not hasattr(self, classmemberName):
                print(f"Bad code! No attribute {classmemberName} in class!")
                sys.exit(1)
            envValue = os.environ.get(envName, None)
            if envValue:
                # It is python..
                setattr(self, classmemberName, envValue)
                return 1
            return 0
        getEnvParam("trafWatchBaseUrl", "baseUrl")
        getEnvParam("keenLogin", "keenLogin")
        getEnvParam("keenPassw", "keenPassw")
        getEnvParam("botToken", "botToken")

    def showAll(self):
        print("\nCurrent params:")
        for name, value in self.__dict__.items():
            if name in ["keenPassw", "botToken"]:
                if value != "":
                    print(f"    {name} is empty")
                else:
                    print(f"    {name} has value")
            else:
                print(f"    {name} = {value}")

class Dir(Enum):
    Rx = 'rxbytes'
    Tx = 'txbytes'
    Dual = 'total_bytes'

class Per(Enum):
    OneHour = "1"
    ThreeHour = "2"
    OneDay = "3"

class trafRecord:
    nonamers_cnt:int = 0
    def __init__(self, mac:str, name:str):
        self.mac:str = mac
        self.name:str = name
        self.traf:Dict[Dir, float] = {Dir.Rx:0, Dir.Tx:0, Dir.Dual:0}
    def update(self, amount:float, dir:Dir):
        self.traf[dir] = amount
    def updSumm(self):
        self.traf[Dir.Dual] = self.traf[Dir.Rx] + self.traf[Dir.Tx]
    def getSummMiB(self) -> float:
        return self.traf[Dir.Dual] / 1024 / 1024
    @classmethod
    def incNonamers(cls) -> int:
        cls.nonamers_cnt += 1
        return cls.nonamers_cnt

class App:
    def __init__(self):
        self.records :Dict[str, trafRecord] = {}
    def clear(self):
        self.records.clear()
    def restGetRecords(self, dir:Dir, dtl):
        query = f"rci/show/ip/hotspot/summary?attribute={dir.value}&detail={dtl}"
        try:
            response = keen.request(query);
            if DEBUG: print(response.text)
        except requests.exceptions.ConnectionError:
            print("\nConnection to Keenetic failed! Network problem or server is down")
            return
        try:
            j = response.json()
        except requests.exceptions.JSONDecodeError:
            print("\nError! Keenetic did not respond with proper json")
            print(response)
            return
        self.records.clear()
        for host in j["host"]:
            self.collectJsonRecord(host, dir)

    def collectJsonRecord(self, j, dir:Dir):
        amount = j[dir.value]
        if amount==0:
            return
        if j.get("mac"):
            mac = j["mac"]
        else:
            print("got special entry", j)
            # mac =  f"{j["type"]}_{trafRecord.incNonamers()}"
            mac =  f'{j["type"]}'
        t:trafRecord|None = self.records.get(mac)
        name = j.get("name") or j["type"]
        if not t:
            t = trafRecord(mac, name)
            self.records[mac] = t
        t.update(amount, dir)
    def summRecords(self):
        for rec in self.records.values():
            rec.updSumm()
    def blameViolators(self, threshMiB:float):
        violators = []
        for rec in self.records.values():
            val = rec.getSummMiB()
            if val > threshMiB:
                violators.append(f"{val:.1f}MiB wasted by '{rec.name}'")
        return violators
    def report(self, period:Per|None, thresh:int|None, DoNotDisturb=False):
        if not (period and thresh):
            print("Error. Detail level and threshold value are necessary!")
            sys.exit(1)
        app.restGetRecords(Dir.Rx, period.value)
        app.restGetRecords(Dir.Tx, period.value)
        app.summRecords()
        # Get violators list as text
        violators = app.blameViolators(thresh)
        if DoNotDisturb and len(violators) == 0:
            print("zero-violators and DoNotDisturb, so don't send message")
            return
        if len(violators) == 0:
            # msg = f"Zero violators of {thresh}MiB limit for {period.name}"
            msg = f"{period.name} violators [>{thresh}MiB]: \n😇 Nobody 😇"
        else:
            msg = "\n".join([f"{period.name} violators [>{thresh}MiB]:"] + violators)
        # Add header line
        if DEBUG: print("DEBUG", msg)
        teleg.sendMsgAll(msg)
        print()

class Teleg:
    def __init__(self):
        self.chatIds:Set[str] = set()
        self.reset()
        self.getChatIds()
    def clear(self):
        self.chatIds.clear()
    def reset(self):
        self.chatIds = copy.deepcopy(conf.manualChats)
    def sendMsgAll(self, msg):
        print(f"Gonna send msg to {len(self.chatIds)} chats")
        for chat in self.chatIds:
            self.sendMessage(chat, msg)
    def getChatIds(self):
        url = f'https://api.telegram.org/bot{conf.botToken}/getUpdates'
        botState = requests.get(url).json()
        if DEBUG: print("DEBUG:botState:", botState)
        for result in botState["result"]:
            chat = result.get("message", {}).get("chat")
            if chat:
                self.chatIds.add(chat["id"])
        print(f"Now have list of {len(self.chatIds)} chats")
    def sendMessage(self, chatID, message):
        url = f"https://api.telegram.org/bot{conf.botToken}/sendMessage"
        payload = {
            "chat_id": chatID,
            "text": message,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Message sent successfully to chat {chatID}")
        else:
            print(f"❌ Failed to send message to chat:{chatID}: {response.status_code} - {response.text}")


if __name__ == "__main__":
    conf = Conf()
    conf.eval()
    print(f"Debug is {DEBUG}")
    if DEBUG: conf.showAll()

    app = App()

    keen = KeenTalker((conf.keenLogin, conf.keenPassw), conf.baseUrl, conf.doAuth)
    teleg = Teleg()

    if DEBUG:
        # teleg.clear() # Prevent bot send message
        app.report(Per.OneHour, 200, True)
        app.report(Per.ThreeHour, 300)
        app.report(Per.OneDay, 300)
        sys.exit(0)

    app.report(conf.dtl, conf.thresh, conf.noDisturb or False)
    sys.exit(0)

