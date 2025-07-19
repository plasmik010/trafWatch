#!/usr/bin/python3

import tomllib
import requests
import getopt
import sys , os
from typing import Dict
from enum import Enum
# from datetime import datetime

CONFIGFILE = "config.toml"
CONFIGFILE2 = "secrets.toml"
DEBUG = True

class Conf:
    def __init__(self):
        self.baseUrl:str = ""
        self.botToken = ""
    def eval(self):
        conf.readToml(CONFIGFILE)
        conf.readToml(CONFIGFILE2)
        conf.getCliArgs(sys.argv[1:])
        conf.getEnvValues()
    def readToml(self, fname:str):
        with open(fname, "rb") as f:
            tomlTable = tomllib.load(f)
            if "baseUrl" in tomlTable:
                self.baseUrl = tomlTable["baseUrl"]
            if "bot_token" in tomlTable:
                self.botToken = tomlTable["bot_token"]
            if "chat_id" in tomlTable:
                self.chat_id = tomlTable["chat_id"]
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
        fullUrl = f"{conf.baseUrl}?attribute={dir.value}&detail={dtl}"
        try:
            response = requests.get(fullUrl, auth=('user', 'password'))
        except requests.exceptions.ConnectionError:
            print("\nConnection to Keenetic failed! Network problem or server is down")
            return
        j = response.json()
        # print(j["t"])
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
            mac =  f"{j["type"]}"
        t = self.records.get(mac)
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
        result = ""
        for rec in self.records.values():
            val = rec.getSummMiB()
            if val > threshMiB:
                violators.append(rec.mac)
        for vio in violators:
            rec = self.records[vio]
            # result += f"{vio} aka \"{rec.name}\" wasted {rec.getSummMiB():.2f} MiB" + f" ({rec.traf[Dir.Tx]/1024/1024:.1f}|{rec.traf[Dir.Rx]/1024/1024:.1f})" + "\n"
            result += f"{rec.getSummMiB():.1f}Mb wasted by '{rec.name}'\n"
        return result
    def report(self, period:Per, thresh:int, DoNotDisturb=False):
        app.restGetRecords(Dir.Rx, period.value)
        app.restGetRecords(Dir.Tx, period.value)
        app.summRecords()
        # Get violators list as text
        msg = app.blameViolators(thresh)
        if DoNotDisturb and not msg:
            print("no violators and donotDisturb, so stay quiet")
            return
        if not msg:
            msg = "None"
        # Add header line
        msg = f"{period.name} violators [>{thresh}mb]:\n" + msg
        if DEBUG: print("DEBUG", msg)
        teleg.sendMsgAll(msg)
        print()

class Teleg:
    def __init__(self):
        self.chatIds = set()
        self.getChatIds()
    def clear(self):
        self.chatIds.clear()
    def sendMsgAll(self, msg):
        print(f"Gonna send msg to {len(self.chatIds)} chats")
        for chat in self.chatIds:
            self.sendMessage(chat, msg)
    def getChatIds(self):
        url = f'https://api.telegram.org/bot{conf.botToken}/getUpdates'
        response = requests.get(url).json()
        if DEBUG: print(response)
        for result in response['result']:
            chat = result.get('message', {}).get('chat')
            if chat:
                self.chatIds.add(chat['id'])
    def sendMessage(self, chatID, message):
        url = f"https://api.telegram.org/bot{conf.botToken}/sendMessage"
        payload = {
            "chat_id": chatID,
            "text": message,
            # "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Message sent successfully")
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")


if __name__ == "__main__":
    conf = Conf()
    conf.eval()
    if DEBUG: conf.showAll()

    app = App()

    teleg = Teleg()

    if DEBUG: teleg.clear() # Prevent bot send message

    app.report(Per.OneHour, 500, True)
    app.report(Per.ThreeHour, 300)
    app.report(Per.OneDay, 900)

    sys.exit(0)

    # exCode:int = not ok
    # sys.exit(exCode) # exit with 0 if Ok


