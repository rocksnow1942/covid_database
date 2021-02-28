from threading import Thread
import requests
import time
import json
import os

class NoDispatchMethod(Exception):
    pass

class Response:
    def __init__(self,code=200) -> None:
        self.status_code = code

def resolve(func):
    def wrap(self,url,*args,**kwargs):
        try:
            return func(self,url,*args,**kwargs)
        except Exception as e:
            try:
                return self.dispatch(func.__name__,url,*args,**kwargs)
            except NoDispatchMethod:
                raise e
            except Exception as dispatchException:
                raise dispatchException            
        # try:
        #     dispatch = getattr(self,'dispatch',None)
        #     if dispatch:
        #         method=func.__name__
        #         return dispatch(method,url,*args,**kwargs)
        #     else:
        #         raise RuntimeError('Dispatch is not implemented.')
        # except Exception as e:
        #     print('dispatch error',e)
        #     return func(self,url,*args,**kwargs)            
    return wrap



class HeaderManager:
    def __init__(self, url) -> None:
        self._url = url
        self.offline=False

    @property
    def headers(self):
        return {}
    
    @property
    def timeout(self):
        return 0.1 if self.offline else 5

    def url(self, sub):
        return f"{self._url}{sub}"

    def requests(self,method,url,*args,**kwargs):        
        return getattr(requests,method)(self.url(url),*args,**kwargs,timeout=self.timeout,headers=self.headers)

    @resolve
    def post(self, url, *args, **kwargs):
        return self.requests('post',url,*args,**kwargs)

    @resolve
    def get(self, url, *args, **kwargs):
        return self.requests('get',url,*args,**kwargs)

    @resolve
    def delete(self, url, *args, **kwargs):
        return self.requests('delete',url,*args,**kwargs)

    @resolve
    def put(self, url, *args, **kwargs):
        return self.requests('put',url,*args,**kwargs)

    def getDispathMethod(self,method,url):
        return None

    def dispatch(self,method,url,*args,**kwargs):
        dispatch = self.getDispathMethod(method,url)
        if dispatch:
            dispatch(method,url,*args,**kwargs)
        else:
            raise NoDispatchMethod
    
class Firebase(HeaderManager):
    def __init__(self, username, password, url):
        super().__init__(url)
        self.username = username
        self.pwd = password        
        self.expire = 0
        self.token = ""
        self.stopRefresh = False
        self.refreshThread = None
        self.storage = OfflineRequestStorage(file='./FirebaseRequest.json')

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
        self.stopRefresh = True
        if self.refreshThread and self.refreshThread.is_alive():
            self.refreshThread.join()
        self.stopRefresh = False
        self.refreshThread = Thread(target=self.refreshToken, daemon=True)
        self.refreshThread.start()

    def stop(self):
        self.stopRefresh = True
        # if self.refreshThread:
        #     self.refreshThread.join()

    def getDispathMethod(self,method,url):
        parts = url.split('/')
        if len(parts) > 2 and parts[2] == 'info':
            tempurl = '/booking/info'
        else:
            tempurl = url
        return {
            ('post','/booking/query'):self.saveToLocal,
            ('get','/booking/info'):self.saveToLocal,
            ('post','/booking/checkin'):self.saveToLocal
        }.get((method,tempurl),None)
        

    def saveToLocal(self,method,url,*args,**kwargs):
        self.storage.save(method,url,args,kwargs)

    



class AMS_Database(HeaderManager):
    def __init__(self, url) -> None:
        super().__init__(url)
        self.username = 'default user'        
        self.storage = OfflineRequestStorage(file='./MongoDBRequests.json')        
        self.loadUsers()
    
    def loadUsers(self,):
        mongoDataFile = './mongoDBDataFile.json'
        if os.path.exists(mongoDataFile):
            with open(mongoDataFile,'rt') as f:
                self.users = json.load(f)
        else:
            self.users = {}
        try:
            res = self.requests('post','/user/all')
            if res.status_code == 200:
                users = res.json()
                print(users)
                self.users = users
                with open(mongoDataFile,'wt') as f:
                    json.dump(self.users,f,indent=2)
            else:
                print(res.status_code)
                print(res.json())
        except Exception as e:
            print(e)
        

    def setUser(self, userObj):
        "userObj is the document received from server."
        self.username = userObj.get('username','Unauthorized')

    def resetUser(self,):
        "reset username and etc."
        self.username = 'default user'

    @property
    def headers(self):
        return {'Authorization': json.dumps({'username': self.username}, separators=(',', ':'))}
   
    def getDispathMethod(self,method,url):
        parts = url.split('/')
        if len(parts) > 2 and parts[1] == 'user':
            tempurl = '/user'
        else:
            tempurl = url
        return {
            ('post','/samples'):self.saveToLocal,
            ('get','/user') : self.getUser
        } .get((method,tempurl),None)
    
    def getUser(self,method,url,*args,**kwargs):
        print(method,url,args,kwargs)
        return 

    def saveToLocal(self,method,url,*args,**kwargs):
        self.storage.save(method,url,args,kwargs)
        return Response(200)

        

class OfflineRequestStorage:
    def __init__(self,file) -> None:
        self.file=file
        self.requests = []
    def __iter__(self):
        return iter(self.requests)
        
    def save(self,method,url,args,kwargs):
        self.requests.append([method,url,args,kwargs])
        with open(self.file,'wt') as f:
            json.dump(self.requests,f,indent=2)
    def load(self,):
        if os.path.exists(self.file):
            with open(self.file,'rt') as f:
                self.requests = json.load(f)
        else:
            self.requests = []
        
