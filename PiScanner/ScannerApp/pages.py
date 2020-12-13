import time
import tkinter as tk
from .utils import validateBarcode,BaseViewPage
from threading import Thread
from .routines import Routines

class BarcodePage(BaseViewPage):
    resultType = lambda x:'Not Scanned'
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.useCamera = self.master.config['BarcodePage']['useCamera']
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
        self.camera.start()
        if not self.useCamera:
            livebarcode = lambda _:""
        else:
            livebarcode = self.camera.liveScanBarcode
        self.barcodeThread = Thread(target=livebarcode,args=(self.keyboardCb,))
        self.barcodeThread.start()
        self.showPrompt()
        if msg:
            self.displaymsg(msg)
    
    def closePage(self):
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
        self.showPrompt()
        
    def showPrompt(self):
        code = self.result
        self.scanVar.set(code)
        if code == "Not Scanned":
            self.displaymsg("Scan plate ID")
            self.scan.config(fg='black')
            return
        valid,msg  = self.master.currentRoutine.validateResult(code)
        if valid:
            self.result = code
            self.scan.config(fg='green')
            self.displaymsg(msg,'green')
            self.enableNextBtn()
        else:
            self.scan.config(fg='red')
            self.displaymsg(msg, 'red')
            self.disableNextBtn()


class DTMXPage(BaseViewPage):
    resultType = list
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
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
        validlist,msg = self.master.currentRoutine.validateResult(self.result)
        for i,valid in enumerate(validlist):
            if not valid:
                newerror.append(i)
        self.displayInfo(msg)
        self.specimenError = newerror

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
        Thread(target=read,).start()

    def showPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            idx = self.specimenError[0]
            self.displaymsg(
                f"Rescan {self.result[idx][0]}: current={self.result[idx][1]}", 'red')
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
        pass

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
                print(e)
                self.displaymsg(f'Error in saving: {str(e)[0:10]}','red')
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
        self.create_widgets()
        
    def create_widgets(self):
        "4 buttons Maximum"
        routines = self.master.config['appConfig']['routines']
        rtBtnNames = {r.__name__:r.btnName for r in Routines}
        for i,rtName in enumerate(routines[0:3]):
            r = i//2
            c = i%2            
            tk.Button(self,text=rtBtnNames[rtName],font=('Arial',55),command=self.master.startRoutineCb(rtName)).place(
                x=20 + c*400,y=40+200*r,height=150,width=360)
        tk.Button(self,text='Exit',font=('Arial',60),command=self.master.on_closing).place(
            x=420,y=210,height=150,width=360)

    def showPage(self):
        self.tkraise()
        self.focus_set()



AllPAGES = (HomePage,BarcodePage,DTMXPage,SavePage)