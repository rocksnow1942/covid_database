from http.server import HTTPServer,BaseHTTPRequestHandler
import json

class DispatchMeta(type):
    """
    NOT USED ANYMORE
    enable dispatch class function to a new name using dispatch."""
    def __new__(meta,name,bases,dct):
        for k in list(dct.keys()):
            item = dct[k]
            if getattr(item,'isDispatchMethod',None):
                dct[item.__name__] = dct.pop(k)
        return super(DispatchMeta, meta).__new__(meta, name, bases, dct)

        
def dispatch(instance,path,):
    """
    NOT USED ANYMORE
    msg format: {
        action: methodName/tag1/tag2,
        other key:value pairs will also be passed to method.
    }
    route an action to instance dispatchers
    """
    methodName = path
    method = getattr(instance,methodName,None)
    if method==None: 
        raise KeyError(f'Method <{methodName}> was not found on <{instance.__class__.__name__}>.')
    return method()

class SimpleHandler(BaseHTTPRequestHandler,):
 
    def json(self):
        "return json dict or empty dict"
        if self.headers['Content-Length']:
            return json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode())
        return {} 

    def abort404(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('<h1>PAGE NOT FOUND.</h1>'.encode())

    def sendData(self,data,header,cache=True):
        self.send_response(200)
        self.send_header("Content-type", header)
        # FIXME: remove dev testing.
        self.end_headers()
        self.wfile.write(data)

    def sendCSS(self,css):
        self.sendData(css,'text/css')
    def sendHTML(self,html):
        self.sendData(html,'text/html')
    def sendJS(self,js):
        self.sendData(js,'application/javascript')
    def sendMAP(self,js):
        self.sendData(js,'application/json')

    def do_GET(self):
        """Respond to a GET request."""
        # display LED flash.

        try:
            # redirect / to /index
            path = self.path.strip('/') or 'index'
            print(path)
            print(self.json())
            self.sendHTML('hello world',)
        except:
            # if not defined, try to look for raw html pate.
            self.sendFileOr404(path)

    def do_POST(self):
        "respond to post request"
        self.logger.main.peripheral.led.show('wifi',[50,1],1,)

        try:
            # redirect / to /index
            path = self.path.strip('/') or 'index'
            dispatch(self,path=path)
        except:
            # if not defined, try to look for raw html pate.
            self.sendFileOr404(path)

    def sendFileOr404(self,filePath,mode='html'):
       return self.abort404()
       
       
       
serverAddress=('127.0.0.1',8000)
HTTPServer(serverAddress,SimpleHandler ).serve_forever()
 