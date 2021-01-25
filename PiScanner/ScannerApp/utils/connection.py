from threading import Thread
import requests
import time
import json


class HeaderManager:
    def __init__(self, url) -> None:
        self._url = url

    @property
    def headers(self):
        return {}

    def url(self, sub):
        return f"{self._url}{sub}"

    def post(self, url, *args, **kwargs):
        return requests.post(self.url(url), *args, **kwargs, headers=self.headers)

    def get(self, url, *args, **kwargs):
        return requests.get(self.url(url), *args, **kwargs, headers=self.headers)

    def delete(self, url, *args, **kwargs):
        return requests.delete(self.url(url), *args, **kwargs, headers=self.headers)

    def put(self, url, *args, **kwargs):
        return requests.put(self.url(url), *args, **kwargs, headers=self.headers)


class Firebase(HeaderManager):
    def __init__(self, username, password, url):
        self.username = username
        self.pwd = password
        self._url = url
        self.expire = 0
        self.token = ""
        self.stopRefresh = False
        self.refreshThread = None

    @property
    def headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def fetchToken(self):
        try:
            res = requests.post(
                self.url('/user/login'), json={'email': self.username, 'password': self.pwd})
            if res.status_code == 200:
                self.token = res.json()['token']
                # each token is valid for 55 minutes.
                self.expire = time.time() + 60 * 55
            else:
                self.token = ""
        except:
            self.token = ''

    def refreshToken(self):
        "refreshtoken every 1hour"
        while True:
            if self.stopRefresh:
                break
            if self.expire < time.time() or self.token == "":
                self.fetchToken()
            time.sleep(1)

    def start(self):
        if self.refreshThread and self.refreshThread.is_alive():
            self.refreshThread.join()
        self.stopRefresh = False
        self.refreshThread = Thread(target=self.refreshToken, daemon=True)
        self.refreshThread.start()

    def stop(self):
        self.stopRefresh = True
        # if self.refreshThread:
        #     self.refreshThread.join()


class AMS_Database(HeaderManager):
    def __init__(self, url) -> None:
        self.username = 'default user'
        self._url = url

    def setUser(self, userObj):
        "userObj is the document received from server."
        self.username = userObj.get('username','Unauthorized')

    def resetUser(self,):
        "reset username and etc."
        self.username = 'default user'

    @property
    def headers(self):
        return {'Authorization': json.dumps({'username': self.username}, separators=(',', ':'))}
