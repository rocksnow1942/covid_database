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
        self.currentSelection = 0
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'

    def resetState(self):
        self.result=self.resultType()
        self.reScanAttempt = 0
        self.specimenError = []
        self.currentSelection = 0
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
        self._info.place(x=340,y=80,width=340,height=180)
        scbar.place(x = 680,y=80,width=20,height=180)

        self.upBtn = tk.Button(self, text='↑',    font=('Arial', 20), command=self.moveSelection())
        self.downBtn = tk.Button(self, text='↓',  font=('Arial', 20), command=self.moveSelection())
        self.leftBtn = tk.Button(self, text='←',  font=('Arial', 20), command=self.moveSelection())
        self.rightBtn = tk.Button(self, text='→', font=('Arial', 20), command=self.moveSelection())
        self.upBtn   .place(x=710,y= 80,width=70,height=40)
        self.downBtn .place(x=710,y=130,width=70,height=40)
        self.leftBtn .place(x=710,y=180,width=70,height=40)
        self.rightBtn.place(x=710,y=230,width=70,height=40)


        
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
            idx = self.currentSelection
            posi = self.camera.indexToGridName(idx)
            self.result[self.specimenError[0][0]] = (posi,code)            
            self.validateResult()
            self.currentSelection = self.specimenError[0][0] if self.specimenError else None
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()

        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.')
        else:
            self.displaymsg('Read specimen to start.')

    def validateResult(self):
        "send the result to routein for validation"
        newerror = []
        
        validlist,msg,bypass = self.master.currentRoutine.validateResult(self.result)
        # valid list is a boolean list to indicate if a well is valid or not
        # it can also be a string, = 'valid', 'invalid', 'non-exist', 'conflict'
        for i,valid in enumerate(validlist):
            if isinstance(valid,str):
                if valid == 'invalid':
                    newerror.append((i,'red'))
                elif valid == 'conflict':
                    newerror.append((i,'purple'))
                elif valid == 'non-exist':
                    newerror.append((i,'yellow'))
            else:
                if not valid:
                    newerror.append((i,'red'))
        self.displayInfo(msg)
        self.specimenError = newerror
        self.bypassErrorCheck = bypass
        
    def read(self,):
        "read camera"
        olderror = self.specimenError
        oldresult = self.result
        self._prevBtn['state'] = 'disabled'
        self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = []
        self.result = []

        def read():
            plateId = getattr(self.master.currentRoutine,'plateId','')
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            # this is the total number of samples on plate, from A-H then 1-12.            
            needToVerify = self.master.currentRoutine.totalSampleCount
            for i, res in enumerate(self.camera.scanDTMX(olderror,oldresult,self.reScanAttempt,needToVerify,plateId)):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                convertedTubeID  = convertTubeID(res)
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i+1:3} / {total:3} {"."*(i%4)}')
                self.result.append((position,convertedTubeID))
                self.displayInfo(f"{position} : {convertedTubeID}")
            self.displayInfo("Validating...")
            self.validateResult()
            self.currentSelection =self.specimenError[0][0] if self.specimenError else None
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()
            self._prevBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
            if self.master.devMode:
                self._nextBtn['state'] = 'normal'
        Thread(target=read,).start()

    def showPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            # idx = self.specimenError[0][0]
            idx = self.currentSelection
            self.displaymsg(
                f"Rescan {self.result[idx][0]}: current={self.result[idx][1]}", 'red')
            if self.bypassErrorCheck:
                self._nextBtn['state'] = 'normal'
        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.', 'green')
            self._nextBtn['state'] = 'normal'
         

    def moveSelection(self,direction):
        def cb():
            ''
            if self.currentSelection == None:
                self.currentSelection = 0
            if direction == 'up':
                self.currentSelection -= 8
            elif direction == 'down':
                self.currentSelection += 8
            elif direction == 'left':
                self.currentSelection -= 1
            elif direction == 'right':
                self.currentSelection += 1
            if self.currentSelection < 0:
                self.currentSelection = 96 + self.currentSelection
            elif self.currentSelection > 95:
                self.currentSelection = self.currentSelection - 95
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()
        return cb