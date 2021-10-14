import tkinter as tk
from threading import Thread
from . import BaseViewPage
from ..utils import convertTubeID



class DTMXPage(BaseViewPage):
    resultType = dict
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
        self.bypassErrorCheck = False
        self.reScanAttempt = 0 #to keep track how many times have been rescaned.
        self.master = master
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
        self.create_widgets()
        self.camera = master.camera
        self.initKeyboard()
        self.state = ['specimenError','bypassErrorCheck','reScanAttempt']
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'

    def resetState(self):
        self.result=self.resultType()
        self.reScanAttempt = 0
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
        
    def showPage(self,title="Default DataMatrix Page",msg="Place plate on reader and click read.",color='black'):
        self.setTitle(title,color)
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.camera.drawOverlay(self.specimenError)         
        self.displaymsg(msg)
        self.showPrompt()

    def closePage(self):
        self.master.camera.stop()
        #clean off keystrokes
        self.keySequence = []
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'

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
        olderror = self.specimenError
        oldresult = self.result
        self._prevBtn['state'] = 'disabled'
        self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = [0]
        self.result = []

        def read():
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            # this is the total number of samples on plate, from A-H then 1-12.
            needToVerify = self.master.currentRoutine.totalSampleCount
            for i, res in enumerate(self.camera.scanDTMX(olderror,oldresult,self.reScanAttempt,needToVerify)):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                convertedTubeID  = convertTubeID(res)
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i+1:3} / {total:3} {"."*(i%4)}')
                self.result.append((position,convertedTubeID))
                self.displayInfo(f"{position} : {convertedTubeID}")
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
         
