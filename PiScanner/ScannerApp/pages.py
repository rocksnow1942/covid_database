import tkinter as tk
from threading import Thread
from .logger import Logger
from .utils import warnImplement
import requests,time

class BaseViewPage(tk.Frame,Logger):
    resultType = str
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        Logger.__init__(self,self.__class__.__name__,
        logLevel=self.master.config['appConfig']['LOGLEVEL'],
        fileHandler=self.master.fileHandler)
        self.result = self.resultType()
        self._info = None
        
    def createDefaultWidgets(self):
        "creat title, prev and next button,msg box"
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',32),command=self.prevPageCb)
        self._nextBtn = tk.Button(self,text='Next',font=('Arial',32),command=self.nextPageCb)

    def placeDefaultWidgets(self):
        self._msg.place(x=20, y=430, width=740)
        self._prevBtn.place(x=340, y=300,  height=90 ,width=130,)
        self._nextBtn.place(x=650, y=300, height=90, width=130)
        self._title.place(x=340,y=20,width=440,height=30)

    def resetState(self):
        warnImplement('resetState',self)
        self.result  = self.resultType()
    
    def showPage(self,*args,**kwargs):
        warnImplement('showPage',self)
       
        self.tkraise()
        self.focus_set()
    
    def closePage(self):
        warnImplement('closePage',self)

         
    def setTitle(self,title,color='black'):
        self._titleVar.set(title)
        if color:
            self._title.config(fg=color)

    def readResult(self):
        return self.result

    def setResult(self,result):
        self.result = result
    
    def prevPageCb(self):
        "return to previous page in the current routine"
        self.master.currentRoutine.prevPage()
    
    def enableNextBtn(self):
        self._nextBtn['state'] = 'normal'
    def disableNextBtn(self):
        self._nextBtn['state'] = 'disabled'
    
    def nextPageCb(self):
        self.master.currentRoutine.nextPage()

    def displaymsg(self, msg, color='black'):
        self._msgVar.set(msg)
        if color:
            self._msg.config(fg=color)
    
    def displayInfo(self,info):
        self._info.configure(state='normal')
        self._info.insert('1.0',info+'\n')
        self._info.configure(state='disabled')
    
    def clearInfo(self):
        "clear scrolledtext"
        self._info.configure(state='normal')
        self._info.delete('1.0',tk.END)
        self._info.configure(state='disabled')

    def initKeyboard(self):
        self.bind("<Key>",self.scanlistener)
        self.keySequence = []

    def scanlistener(self,e):       
        char = e.char
        if char.isalnum():
            self.keySequence.append(char)
        else:
            if self.keySequence:
                self.keyboardCb(''.join(self.keySequence))
            self.keySequence=[]
        #return 'break' to stop keyboard event propagation.
        return 'break'

    def keyboardCb(self,code):
        warnImplement('keyboardCb',self)

class BarcodePage(BaseViewPage):
    resultType = lambda x:'Not Scanned'
    def __init__(self, parent, master):
        self.validationStatus = []
        super().__init__(parent,master)
        self.useCamera = self.master.useCamera
        self.offset = 0 if self.useCamera else -160
        self.camera = master.camera
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
        self.create_widgets()
        self.initKeyboard()

        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'
    
    def placeDefaultWidgets(self):
        
        self._msg.place(x=20, y=430, width=740)
        
        self._prevBtn.place(x=340 , y=300,  height=90 ,width=130,)
        self._nextBtn.place(x=650 , y=300, height=90, width=130)
        self._title.place(x=340+self.offset,y=20,width=440,height=30)

    def create_widgets(self):
        self.scanVar = tk.StringVar()
        # self.scanVar1.set('1234567890')
        self.scan = tk.Label(
            self, textvariable=self.scanVar, font=('Arial', 35))
        l1 = tk.Label(self, text='ID:', font=('Arial', 35)
                 )
        self.scan.place(x=460+self.offset, y=110)  # grid(column=1,row=0,)
        l1.place(x=340+self.offset, y=110)
       
    def showPage(self,title='Default Barcode Page',msg=None,color='black'):
        self.setTitle(title,color)
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        if self.useCamera:
            self.camera.start()
            self.barcodeThread = Thread(target=self.camera.liveScanBarcode,args=(self.keyboardCb,))
            self.barcodeThread.start()
        self.showPrompt()
        if msg:
            self.displaymsg(msg)
    
    def closePage(self):
        if self.useCamera:
            self.master.camera.stop()
            self.barcodeThread.join()
        self.keySequence = []

    def resetState(self):
        self.result  = self.resultType()
        self.scanVar.set("")
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'
     
    def keyboardCb(self,code):
        self.result = code
        self.validationStatus = self.master.currentRoutine.validateResult(code)
        self.showPrompt()
        
    def showPrompt(self):
        code = self.result
        self.scanVar.set(code)
        if code == "Not Scanned":
            self.displaymsg("Scan plate ID")
            self.scan.config(fg='black')
            return
        valid,msg,bypass = self.validationStatus
        if valid:
            self.result = code
            self.scan.config(fg='green')
            self.displaymsg(msg,'green')
            self.enableNextBtn()
        else:
            self.scan.config(fg='red')
            self.displaymsg(msg, 'red')
            if not bypass:
                self.disableNextBtn()

class DTMXPage(BaseViewPage):
    resultType = list
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
        self.bypassErrorCheck = False
        self.master = master
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
        self.create_widgets()
        self.camera = master.camera
        self.initKeyboard()
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'

    def resetState(self):
        self.result=self.resultType()
        self.specimenError = []
        self.clearInfo()
        self._prevBtn['state'] = 'normal'
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'normal'
        self.bypassErrorCheck = False

    def create_widgets(self):
        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 32), command=self.read)
        
        scbar = tk.Scrollbar(self,)
        
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.config(command=self._info.yview)
        self._info.configure(state='disabled')
        self._info.place(x=340,y=80,width=440,height=180)
        scbar.place(x = 780,y=80,width=20,height=180)
        self.readBtn.place(x=495, y=300, height=90, width=130)
        
    def showPage(self,title="Default DataMatrix Page",msg=None,color='black'):
        self.setTitle(title,color)
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.camera.drawOverlay(self.specimenError)
        self.showPrompt()
        if msg:
            self.displaymsg(msg)

    def closePage(self):
        self.master.camera.stop()
        #clean off keystrokes
        self.keySequence = []

    def keyboardCb(self, code):
        ""
        if code == 'snap':
            self.camera.snapshot()
            return
        if self.specimenError:
            posi = self.camera.indexToGridName(self.specimenError[0])
            self.result[self.specimenError[0]] = (posi,code)
            
            self.validateResult()
            self.camera.drawOverlay(self.specimenError)
            self.showPrompt()

        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.')
        else:
            self.displaymsg('Read specimen to start.')

    def validateResult(self):
        "send the result to routein for validation"
        newerror = []
        validlist,msg,bypass = self.master.currentRoutine.validateResult(self.result)
        for i,valid in enumerate(validlist):
            if not valid:
                newerror.append(i)
        self.displayInfo(msg)
        self.specimenError = newerror
        self.bypassErrorCheck = bypass
        

    def read(self):
        "read camera"        
        self._prevBtn['state'] = 'disabled'
        self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = [0]
        self.result = []

        def read():
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            for i, res in enumerate(self.camera.scanDTMX()):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i+1:3} / {total:3} {"."*(i%4)}')
                self.result.append((position,res))
                self.displayInfo(f"{position} : {res}")
            self.displayInfo("Validating...")
            self.validateResult()
            self.camera.drawOverlay(self.specimenError)
            self.showPrompt()
            self._prevBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
            if self.master.devMode:
                self._nextBtn['state'] = 'normal'
        Thread(target=read,).start()

    def showPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            idx = self.specimenError[0]
            self.displaymsg(
                f"Rescan {self.result[idx][0]}: current={self.result[idx][1]}", 'red')
            if self.bypassErrorCheck:
                self._nextBtn['state'] = 'normal'
        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.', 'green')
            self._nextBtn['state'] = 'normal'
        else:
            self.displaymsg('Place plate then click read.')

class SavePage(BaseViewPage):
    def __init__(self, parent, master):
        super().__init__(parent, master)
        self.creat_widgets()
    
    def creat_widgets(self):
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',32),command=self.prevPageCb)
        self.saveBtn = tk.Button(self,text='Save',font=('Arial',32),command=self.saveCb)
        scbar = tk.Scrollbar(self,)
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.config(command=self._info.yview)
        self._title.place(x=40,y=20,width=720,height=30)
        self._info.place(x=40,y=80,width=720,height=190)
        scbar.place(x = 760,y=80,width=20,height=190)
        self._prevBtn.place(x=80, y=300,  height=90 ,width=130,)
        self.saveBtn.place(x=590, y=300, height=90, width=130)
        self._msg.place(x=20, y=430, width=740)

    def closePage(self):
        self.clearInfo()
        

    def resetState(self):
        self.clearInfo()
        self._prevBtn['state'] = 'normal'
        self.saveBtn['state'] = 'normal'
        self.displaymsg("")

        
    def showPage(self,title="Default Save Result Page",msg=None,color='black'):
        self.setTitle(title,color)
        self.displaymsg('Check the result and click save.')
        self.displayInfo(self.master.currentRoutine.displayResult())
        self.tkraise()
        self.focus_set()
        if msg:
            self.displaymsg(msg)
        
    def saveCb(self):
        def save():
            try:
                for p in self.master.currentRoutine.saveResult():
                    self.displayInfo(p)
            except Exception as e:
                self.error(e)
                self.displaymsg(f'Error in saving: {str(e)[0:40]}','red')
            self._prevBtn['state'] = 'normal'
            self.saveBtn['state'] = 'normal'
        Thread(target=save,).start()
        self.displaymsg('Saving results...','green')
        self._prevBtn['state'] = 'disabled'
        self.saveBtn['state'] = 'disabled'

class HomePage(tk.Frame):
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        self.buttons = []
        self.currentPage = 0
        self.maxPage = len(self.master.enabledRoutine)//4 + bool(len(self.master.enabledRoutine) % 4)
        self.create_widgets()
        
    def create_widgets(self):
        "4 buttons Maximum"
        # rtBtnNames = {r.__name__:r.btnName for r in Routines}
        
        
        tk.Button(self,text='Exit',font=('Arial',35),command=self.master.on_closing).place(
            x=630,y=400,height=50,width=150)

        self.pageVar = tk.StringVar()
        self.pageVar.set(f'1 / {self.maxPage}')
        tk.Label(self,textvariable=self.pageVar,font=('Arial',25)).place(x=350,y=400,width=100,height=50)

        self.prevBtn = tk.Button(self,text='<',font=('Arial',40),command=self.prevPage)
        self.prevBtn.place(x=300,y=400,width=50,height=50)
        self.prevBtn['state'] = 'disabled'

        self.nextBtn = tk.Button(self,text='>',font=('Arial',40),command=self.nextPage)
        self.nextBtn.place(x=450,y=400,width=50,height=50)
        if self.maxPage ==1:
            self.nextBtn['state'] = 'disabled'

        self.serverVar = tk.StringVar()
        
        self.serverStatus = tk.Label(self,textvariable=self.serverVar,font=('Arial',20))
        self.serverStatus.place(x=50,y=400,width=200,height=50)
        # tk.Button(self,text='remove',command=self.remove).place(x=420,y=400)
        # tk.Button(self,text='restore',command=self.restore).place(x=490,y=400)

        self.showBtnPage(self.currentPage)
        
        Thread(target = self.pollServer,daemon=True).start()
    
    def pollServer(self):
        while True:
            try:
                res = requests.get(self.master.URL)
                if res.status_code == 200 and res.json().get('live',None):
                    self.serverVar.set('Connected')
                    self.serverStatus.config(fg='green')
                else:
                    self.serverVar.set('')
                    self.serverStatus.config(fg='red')
            except:
                self.serverVar.set('Disconnected')
            time.sleep(10)

    def showBtnPage(self,n):
        self.pageVar.set(f'{n+1} / {self.maxPage}')
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        for i,rtName in enumerate(self.master.enabledRoutine[n*4:n*4+4]):
            r = i//2
            c = i%2            
            btn = tk.Button(self,text=self.master.routine[rtName].btnName,font=('Arial',55),command=self.master.startRoutineCb(rtName))
            btn.place(x=20 + c*400,y=40+170*r,height=150,width=360)
            self.buttons.append(btn)

    def prevPage(self):
        self.currentPage -= 1
        self.showBtnPage(self.currentPage)
        if self.currentPage==0:
            self.prevBtn['state'] = 'disabled'
        if self.currentPage < self.maxPage -1:
            self.nextBtn['state'] = 'normal'

    def nextPage(self):
        self.currentPage +=1
        self.showBtnPage(self.currentPage)
        if self.currentPage==self.maxPage-1:
            self.nextBtn['state'] = 'disabled'
        if self.currentPage > 0:
            self.prevBtn['state'] = 'normal'
    
    def showPage(self):
        self.tkraise()
        self.focus_set()


AllPAGES = (HomePage,BarcodePage,DTMXPage,SavePage)