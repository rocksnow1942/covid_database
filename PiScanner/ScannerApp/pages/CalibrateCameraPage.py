import tkinter as tk
from threading import Thread
from . import BaseViewPage
from ..utils import convertTubeID



class CalibratePage(BaseViewPage):
    resultType = dict
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
        self.bypassErrorCheck = False
        self.reScanAttempt = 0 #to keep track how many times have been rescaned.
        self.master = master
                
        self.create_widgets()
        self.camera = master.camera
        self.initKeyboard()
        self.state = ['specimenError','bypassErrorCheck','reScanAttempt']
        self.currentSelection = 0
        

    def resetState(self):
        self.result=self.resultType()
        self.reScanAttempt = 0
        self.specimenError = []
        self.currentSelection = 0
        self.clearInfo()
        self._prevBtn['state'] = 'normal'        
        self.readBtn['state'] = 'normal'
        self.bypassErrorCheck = False

    def create_widgets(self):
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._msg.place(x=20, y=430, width=740)
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._title.place(x=40,y=20,width=720,height=30)
        self._prevBtn = tk.Button(self,text='Back',font=('Arial',32),command=self.prevPageCb)
        self._prevBtn.place(x=640, y=300,  height=90 ,width=130,)



        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 32), command=self.read)
        self.readBtn .place(x=495, y=300, height=90, width=130)
        self.saveBtn = tk.Button(self, text='Save', font=(
            'Arial', 32), command=self.read)
        self.readBtn .place(x=350, y=300, height=90, width=130)
        
        X = 340
        Y = 100
        btnSize = 50
        self.upBtn = tk.Button(self, text='↑',    font=('Arial', 20), command=self.moveSelection('up'))
        self.downBtn = tk.Button(self, text='↓',  font=('Arial', 20), command=self.moveSelection('down'))
        self.leftBtn = tk.Button(self, text='←',  font=('Arial', 20), command=self.moveSelection('left'))
        self.rightBtn = tk.Button(self, text='→', font=('Arial', 20), command=self.moveSelection('right'))
        self.upBtn   .place(x=X,y=Y,width=btnSize,height=btnSize)
        self.downBtn .place(x=X,y=Y + btnSize * 2,width=btnSize,height=btnSize)
        self.leftBtn .place(x=X - btnSize,y=Y + btnSize,width=btnSize,height=btnSize)
        self.rightBtn.place(x=X + btnSize,y=Y + btnSize,width=btnSize,height=btnSize)

        X = X + btnSize * 3 + 20
        Y = 100
        btnSize = 50
        self.upBtn2 = tk.Button(self, text='↑',    font=('Arial', 20), command=self.moveSelection('up',2))
        self.downBtn2 = tk.Button(self, text='↓',  font=('Arial', 20), command=self.moveSelection('down',2))
        self.leftBtn2 = tk.Button(self, text='←',  font=('Arial', 20), command=self.moveSelection('left',2))
        self.rightBtn2 = tk.Button(self, text='→', font=('Arial', 20), command=self.moveSelection('right',2))
        self.upBtn2   .place(x=X,y=Y,width=btnSize,height=btnSize)
        self.downBtn2 .place(x=X,y=Y + btnSize * 2,width=btnSize,height=btnSize)
        self.leftBtn2 .place(x=X - btnSize,y=Y + btnSize,width=btnSize,height=btnSize)
        self.rightBtn2.place(x=X + btnSize,y=Y + btnSize,width=btnSize,height=btnSize)

        tk.Label(self,text='Brightness',font=('Arial',16)).place(x=X + btnSize * 2 + 20,y=Y)
        tk.Button(self, text='+', font=('Arial',20),command=self.adjustBrightness('+')).place(x=X + btnSize * 2 + 20,y=Y + btnSize, height=btnSize, width=btnSize)
        tk.Button(self, text='-', font=('Arial',20),command=self.adjustBrightness('-')).place(x=X + btnSize * 2 + 20,y=Y + btnSize * 2, height=btnSize, width=btnSize)
        
        
    def showPage(self,title="Calibrate Camera",msg="Place plate on reader and click read.",color='black'):
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

    def validateResult(self):
        "send the result to routein for validation"
        newerror = []        
        validlist,msg,bypass = self.master.currentRoutine.validateResult(self.result)
        # valid list is a boolean list to indicate if a well is valid or not
        # it can also be a string, = 'valid', 'invalid', 'non-exist', 'conflict'
        for i,valid in enumerate(validlist):
            if not valid:
                newerror.append((i,'red','invalid'))                
        
        self.specimenError = newerror
        self.bypassErrorCheck = bypass
        
    def read(self,):
        "read camera"
        olderror = self.specimenError
        oldresult = self.result
        self._prevBtn['state'] = 'disabled'
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
            self.validateResult()
            self.currentSelection =self.specimenError[0][0] if self.specimenError else None
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()
            self._prevBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
            
        Thread(target=read,).start()

    def showPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            # idx = self.specimenError[0][0]
            idx = self.currentSelection
            text = 'valid'
            for error in self.specimenError:
                if idx == error[0]:
                    text = error[2]
                    break
            self.displaymsg(
                f"Rescan {self.result[idx][0]} {text}: current={self.result[idx][1]}", 'green' if text == 'valid' else 'red')
             
        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.', 'green')
            
         

    def moveSelection(self,direction,corner=0):
        def cb():
            ''
            if direction == 'left':
                self.camera.adjustScanWindow(0,5,0,5)
            elif direction == 'right':
                self.camera.adjustScanWindow(0,-5,0,-5)
            elif direction == 'up':
                self.camera.adjustScanWindow(-5,0,-5,0)
            elif direction == 'down':
                self.camera.adjustScanWindow(5,0,5,0)
            
            self.camera.drawOverlay(self.specimenError)
        return cb