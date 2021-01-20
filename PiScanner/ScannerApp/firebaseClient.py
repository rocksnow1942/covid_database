from threading import Thread
import requests
import time

class Firebase:
    def __init__(self,username,password,url):
        self.username = username
        self.pwd = password
        self._url = url
        self.expire = 0
        self.token=""
        self.stopRefresh = False
        self.refreshThread = None
        
    @property
    def headers(self):
        return {'Authorization':f'Bearer {self.token}'}

    def url(self,sub):
        return f"{self._url}{sub}"

    def fetchToken(self):
        try:
            res = requests.post(self.url('/user/login'),json={'email':self.username,'password':self.pwd})
            if res.status_code == 200:
                self.token = res.json()['token']
                self.expire = time.time() + 60 * 55 # each token is valid for 55 minutes.
            else:
                self.token=""
        except:
            self.token=''            
        
    def refreshToken(self):
        "refreshtoken every 1hour"        
        while True:
            if self.stopRefresh:
                break
            if self.expire < time.time() or self.token=="":
                self.fetchToken()
            time.sleep(1)

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
        return requests.put(url,*args,**kwargs,headers=self.headers)
 