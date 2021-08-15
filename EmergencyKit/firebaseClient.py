from threading import Thread
import requests
import time
from getpass import getpass

prodURL = 'https://us-central1-ams-clia.cloudfunctions.net/api'
devURL = 'http://localhost:5000/ams-clia/us-central1/api'


class Firebase:
    def __init__(self,username='user@ams.com',password='',mode='prod'):
        self.username = username        
        self._url = devURL if mode=='dev' else prodURL
        self.expire = 0
        self.token=""
        self.stopRefresh = False
        self.refreshThread = None
        if password:
            self.pwd = password
        else:
            self.pwd = getpass(f'Enter password for {username}')
        self.start()
        
    def __repr__(self):
        return f"Firebase User: {self.username}"
    @property
    def headers(self):
        return {'Authorization':f'Bearer {self.token}'}

    def url(self,sub):
        return f"{self._url}{sub}"

    def fetchToken(self):        
        res = requests.post(self.url('/user/login'),json={'email':self.username,'password':self.pwd})
        if res.status_code == 200:
            self.token = res.json()['token']
            self.expire = time.time() + 60 * 55 # each token is valid for 55 minutes.
        else:
            self.token=""
            raise Exception(f'Cannot Fetch Token {res.status_code}, {res.text}')
        
    
    def refreshToken(self):
        "refreshtoken every 1hour"        
        while True:
            if self.stopRefresh:
                break
            if self.expire < time.time():
                self.fetchToken()            
            time.sleep(0.5)

    def start(self):        
        if self.refreshThread and self.refreshThread.is_alive():
            self.refreshThread.join()
        self.stopRefresh = False
        self.refreshThread = Thread(target=self.refreshToken,daemon=True)
        self.refreshThread.start()
        
    def stop(self):
        self.stopRefresh = True
        # if self.refreshThread:
        #     self.refreshThread.join()

    def post(self,url,*args,**kwargs):    
        return requests.post(self.url(url),*args,**kwargs,headers=self.headers)

    def get(self,url,*args,**kwargs):
        return requests.get(self.url(url),*args,**kwargs,headers=self.headers)
    
    def delete(self,url,*args,**kwargs):
        return requests.delete(self.url(url),*args,**kwargs,headers=self.headers)

    def put(self,url,*args,**kwargs):
        return requests.put(self.url(url),*args,**kwargs,headers=self.headers)
 