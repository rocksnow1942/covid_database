from threading import Thread, Lock
import requests
import time
from datetime import date, timedelta
import json
import os


class NoDispatchMethod(Exception):
    pass


class Response:
    "Mock response for offline use."

    def __init__(self, code=200):
        self.status_code = code
        self._json = None

    def json(self, data='!!_NOT_SUPPLIED_!!'):
        """
        if json is called without argument, will return the self._json, 
        otherwise set the _json to data provided.
        """
        if data == '!!_NOT_SUPPLIED_!!':
            return self._json
        else:
            self._json = data
            return self


def resolve(func):
    """
    decorator to turn original method to a two stage method.
    for a post or get request, try use requests.post or get.
    if not able to do that, use offline dispatch.
    if the dispatch Method is not implemented,
    will raise original request error.
    """

    def wrap(self, url, *args, **kwargs):
        try:
            return func(self, url, *args, **kwargs)
        except Exception as e:
            try:
                return self.dispatch(func.__name__, url, *args, **kwargs)
            except NoDispatchMethod:
                raise e
            except Exception as dispatchException:
                raise dispatchException
    return wrap


class HeaderManager:
    def __init__(self, url, offlineDataFile) -> None:
        self._url = url
        self.offline = False
        self.offlineDataFile = offlineDataFile
        self.offlineData = {}
        self.loadOfflineData()

    @property
    def headers(self):
        return {}

    @property
    def timeout(self):
        """
        the offline property is set by pollServer thread in HomePage.
        every 10 seconds, it is updated by checking either ping to google.com
        or our mongodb server.
        if offline, then request time out set to 0.01 second to save time.
        """
        return 0.01 if self.offline else 5

    def loadOfflineData(self):
        if os.path.exists(self.offlineDataFile):
            with open(self.offlineDataFile, 'rt') as f:
                self.offlineData = json.load(f)
        else:
            self.saveOfflineData()

    def saveOfflineData(self):
        with open(self.offlineDataFile, 'wt') as f:
            json.dump(self.offlineData, f, indent=2)

    def url(self, sub):
        return f"{self._url}{sub}"

    def requests(self, method: str, url: str, *args, **kwargs):
        """
        Add default timeout and header to request method call,
        if the timeout and header is not provided in method call kwargs.
        """
        timeout = kwargs.pop('timeout', None) or self.timeout
        headers = kwargs.pop('headers', None) or self.headers
        return getattr(requests, method)(self.url(url), *args, **kwargs, timeout=timeout, headers=headers)

    @resolve
    def post(self, url, *args, **kwargs):
        return self.requests('post', url, *args, **kwargs)

    @resolve
    def get(self, url, *args, **kwargs):
        return self.requests('get', url, *args, **kwargs)

    @resolve
    def delete(self, url, *args, **kwargs):
        return self.requests('delete', url, *args, **kwargs)

    @resolve
    def put(self, url, *args, **kwargs):
        return self.requests('put', url, *args, **kwargs)

    def getDispathMethod(self, method, url):
        "return a method based on method and url"
        return None

    def dispatch(self, method, url, *args, **kwargs):
        """
        dispatch a method a url to certain offline method call
        if the dispatch method is implemented, return call result.
        if not, raise NoDisptchMethod error,
        so that the resolver will raise origianal requests call error.
        """
        dispatch = self.getDispathMethod(method, url)
        if dispatch:
            return dispatch(method, url, *args, **kwargs)
        else:
            raise NoDispatchMethod


class Firebase(HeaderManager):
    def __init__(self, username, password, url):
        super().__init__(url, './ScannerApp/logs/firebaseDataFile.json')
        self.username = username
        self.pwd = password
        self.expire = 0
        self.token = ""

        self.requestStorage = OfflineRequestStorage(
            file='./ScannerApp/logs/FirebaseRequests.json')

        Thread(target=self.loadBooking, daemon=True).start()

        Thread(target=self.saveOfflineRequests, daemon=True).start()

    def fetchToken(self):
        "fetch a auth token from firebase, and set expire time and token"
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

    @property
    def headers(self):
        "set the auth header for firebase. "
        if self.expire < time.time() or self.token == "":
            self.fetchToken()
        return {'Authorization': f'Bearer {self.token}'}

    def saveOfflineRequests(self):
        """
        save the offline requests to firebase,once it is online.
        """
        while True:
            time.sleep(10)
            saved = []
            if not self.offline and self.requestStorage:
                for idx, (method, url, args, kwargs) in enumerate(self.requestStorage):
                    time.sleep(1)
                    try:
                        res = self.requests(method, url, *args, **kwargs)
                        if res.status_code == 200:
                            saved.append(idx)
                    except Exception as e:
                        print(e)
                if saved:
                    self.requestStorage.remove(saved)

    def loadBooking(self):
        """
        load booking calendar, during first app start up, 3 days ago and 14 days ahead.
        """
        if self.offlineData.get('booking', None) is None:
            self.offlineData['booking'] = []
        try:
            res = self.requests('post', '/booking/getCalendar',
                                json={'startDate': (date.today() + timedelta(days=-3)).strftime('%Y-%m-%d'),
                                      'endDate': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d')})
            if res.status_code == 200:
                self.offlineData['booking'] = res.json()
                self.saveOfflineData()
        except Exception as e:
            print(e)

    def getDispathMethod(self, method, url):
        parts = url.split('/')
        if len(parts) > 2 and parts[2] == 'info':
            tempurl = '/booking/info'
        else:
            tempurl = url
        return {
            ('post', '/booking/query'): self.bookingQuery,
            ('get', '/booking/info'): self.bookingInfo,
            ('post', '/booking/checkin'): self.checkInPatient,
        }.get((method, tempurl), None)

    def checkInPatient(self, method, url, *args, **kwargs):
        docID = kwargs.get('json').get('docID')
        for book in self.offlineData.get('booking', []):
            if book.get('docID', None) == docID:
                book['checkin'] = True
                self.saveOfflineData()
                break
        self.requestStorage.save(method, url, args, kwargs)
        return Response(200)

    def bookingQuery(self, method, url, *args, **kwargs):
        similar = []
        firstName = kwargs.get('json', {}).get('firstName', '')
        lastName = kwargs.get('json', {}).get('lastName', '')
        checkName = (firstName+lastName).replace(' ', '').lower()
        for book in self.offlineData.get('booking', []):
            name = book.get('name').lower().replace(' ', '')
            if checkName in name:
                similar.append(book)
        if similar:
            return Response(200).json(similar)
        else:
            return Response(404).json({'error': 'Name not found in Local booking data.'})

    def bookingInfo(self, method, url, *args, **kwargs):
        id = url.replace('/booking/info', '')
        for book in self.offlineData.get('booking', []):
            if id == book.get('docID', None):
                return Response(200).json(book)
        return Response(404).json({'error': 'Not found in local booking data.'})


class AMS_Database(HeaderManager):
    def __init__(self, url) -> None:
        super().__init__(url, './ScannerApp/logs/mongoDBDataFile.json')
        self.username = 'default user'
        self.storage = OfflineRequestStorage(
            file='./ScannerApp/logs/MongoDBRequests.json')
        Thread(target=self.loadUsers, daemon=True).start()
        Thread(target=self.saveOfflineRequests, daemon=True).start()

    def saveOfflineRequests(self):
        while True:
            time.sleep(10)
            saved = []
            if not self.offline and self.storage:
                for idx, (method, url, args, kwargs) in enumerate(self.storage):
                    try:
                        res = getattr(requests, method)(
                            self.url(url), *args, **kwargs, timeout=self.timeout)
                        if res.status_code == 200:
                            saved.append(idx)
                    except Exception as e:
                        print(e)
                if saved:
                    self.storage.remove(saved)

    def loadUsers(self,):
        if self.offlineData.get('users', None) is None:
            self.offlineData['users'] = []
        try:
            res = self.requests('post', '/user/all')
            if res.status_code == 200:
                self.offlineData['users'] = res.json()
                self.saveOfflineData()
        except Exception as e:
            print(e)

    def setUser(self, userObj):
        "userObj is the document received from server."
        self.username = userObj.get('username', 'Unauthorized')

    def resetUser(self,):
        "reset username and etc."
        self.username = 'default user'

    @property
    def headers(self):
        return {'Authorization': json.dumps({'username': self.username}, separators=(',', ':'))}

    def getDispathMethod(self, method, url):
        parts = url.split('/')
        if len(parts) > 2 and parts[1] == 'user':
            tempurl = '/user'
        else:
            tempurl = url
        return {
            ('post', '/samples'): self.saveToLocal,
            ('get', '/user'): self.getUser
        } .get((method, tempurl), None)

    def getUser(self, method, url, *args, **kwargs):
        token = url.split('/')[2]
        for user in self.offlineData.get('users', []):
            if user.get('token', None) == token:
                return Response(200).json(user)
        return Response(400)

    def saveToLocal(self, method, url, *args, **kwargs):
        kwargs.update(headers=self.headers)
        self.storage.save(method, url, args, kwargs)
        return Response(200)


class OfflineRequestStorage:
    def __init__(self, file) -> None:
        self.file = file
        self.requests = []
        self.lock = Lock()
        self.load()

    def __bool__(self):
        return bool(self.requests)

    def __iter__(self):
        return iter(self.requests)

    def save(self, method, url, args, kwargs):
        self.lock.acquire()
        self.requests.append([method, url, args, kwargs])
        self.saveJson()
        self.lock.release()

    def load(self,):
        self.lock.acquire()
        if os.path.exists(self.file):
            with open(self.file, 'rt') as f:
                self.requests = json.load(f)
        else:
            self.requests = []
        self.lock.release()

    def saveJson(self):
        with open(self.file, 'wt') as f:
            json.dump(self.requests, f, indent=2)

    def remove(self, toRemoveIdx):
        self.lock.acquire()
        self.requests = [i for k, i in enumerate(
            self.requests) if k not in toRemoveIdx]
        self.saveJson()
        self.lock.release()
