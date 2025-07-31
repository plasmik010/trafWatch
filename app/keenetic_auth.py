
# Original code from ancientGlider@github

"""
Данные с адресом, логином, паролем хранятся в конфигурационном файле следующего вида:

[Router]
baseUrl = 192.168.1.1:8080
login = log
passw = pas

"""

import configparser
import requests
import hashlib
import sys

def onAuthFail():
    print("Keenetic Auth failed. Exiting.")
    sys.exit(1)

class KeenTalker:
    def __init__(self, credentials, baseUrl:str, needAuth:bool = True):
        self.session = requests.session()  # заводим сессию глобально чтобы отрабатывались куки
        self.login, self.passw = credentials
        self.baseUrl = baseUrl
        self.needAuth:bool = needAuth

        self.maybeAuth()

    def maybeAuth(self):
        if self.needAuth:
            self.auth()
    def auth(self):        # авторизация на роутере
        response = self.request("auth")
        if response.status_code == 403:
            print("Router respond 403")
            onAuthFail()
        elif response.status_code == 401:
            print("Gonna re-auth")
            md5 = self.login + ":" + response.headers["X-NDM-Realm"] + ":" + self.passw
            md5 = hashlib.md5(md5.encode('utf-8'))
            sha = response.headers["X-NDM-Challenge"] + md5.hexdigest()
            sha = hashlib.sha256(sha.encode('utf-8'))
            load = {"login": self.login, "password": sha.hexdigest()}
            response = self.request("auth", load)
            if response.status_code == 200:
                print("Auth success")
            else:
                onAuthFail()
        elif response.status_code == 200:
            print("Auth success")
        else:
            print("Router respond {response.status_code}")
            onAuthFail()

# Отправка запросов на роутер
    def request(self, query, post = None):
        url = self.baseUrl + "/" + query
# Если есть данные для запроса POST, делаем POST, иначе GET
        if post:
            return self.session.post(url, json=post)
        else:
            return self.session.get(url)


if __name__ == "__main__":
    CONFIG_FILE_NAME = "config.toml"
    import tomllib

    with open(CONFIG_FILE_NAME, "rb") as f:
        tomlTable = tomllib.load(f)
    rr = tomlTable["Router"]

    keen = KeenTalker(rr["credent"], baseUrl = rr["baseUrl"], needAuth = rr["doAuth"])

    keen.session.verify = True
    response = keen.request("rci/show/interface/WifiMaster0");
    print(111, response.text)
    response = keen.request("rci/show/ip/hotspot/summary?attribute=rxbytes");
    print(222, response.status_code)
    pass


