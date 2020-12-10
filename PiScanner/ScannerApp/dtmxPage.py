import tkinter as tk
import tkinter.scrolledtext as ST
from .utils import validateBarcode,BaseViewPage
from threading import Thread

class DTMXPage(BaseViewPage):
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
        self.specimenResult = []
        self.master = master
        self.create_widgets()
        self.specimenRescanPrompt()
        self.camera = master.camera
        self.initKeyboard()
 

    def create_widgets(self):
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',25),command=self.prevPageCb)

        self._nextBtn = tk.Button(self,text='Next',font=('Arial',25),command=self.nextPageCb)
        self._nextBtn['state'] = 'disabled'

        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 40), command=self.read)
        self._msgVar = tk.StringVar()

        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))

        
        scbar = tk.Scrollbar(self,)
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.place(x = 475,y=20)

        # self._info = ST.ScrolledText(self,wrap=tk.WORD,font=('Arial',16),padx=3,pady=0)

        self._msg.place(x=20, y=430, width=660)
        self._prevBtn.place(x=360, y=360, width=90, height=50)
        self._nextBtn.place(x=650, y=360, height=50, width=90)
        self._info.place(x=340,y=20,width=440,height=190)
        self.readBtn.place(x=395, y=250, height=90, width=310)        

    def showPage(self):
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.camera.drawOverlay(self.specimenError)

    def keyboardCb(self, code):
        ""
        if code == 'snap':
            self.camera.snapshot()
            return
        if self.specimenError:
            posi = self.camera.indexToGridName(self.specimenError[0])
            self.specimenResult[self.specimenError[0]] = (posi,code)
            
            if validateBarcode(code, 'specimen'):
                self.specimenError.pop(0)
                self.camera.drawOverlay(self.specimenError)
                self.displayInfo(f"{posi} : {code}")
            else:
                self.displayInfo(f"{posi} INVALID: {code} ")
            self.specimenRescanPrompt()

        elif self.specimenResult:
            self.displaymsg('All specimen scaned. Click Next.')
        else:
            self.displaymsg('Read specimen to start.')

   
    def read(self):
        "read camera"        
        self._prevBtn['state'] = 'disabled'
        self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = []
        self.specimenResult = []

        def read():
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            for i, res in enumerate(self.camera.scanDTMX()):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i:3} / {total:3} {"."*(i%4)}')
                self.specimenResult.append((position,res))
                if not validateBarcode(res, 'specimen'):
                    self.specimenError.append(i)
                    self.displayInfo(f"{position} INVALID: {res}")
                else:
                    self.displayInfo(f"{position} : {res}")
                            
            self.camera.drawOverlay(self.specimenError)
            self.specimenRescanPrompt()
            self._prevBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
        Thread(target=read,).start()

    def specimenRescanPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            idx = self.specimenError[0]
            self.displaymsg(
                f"Rescan {self.camera.indexToGridName(idx)}: {self.specimenResult[idx]}", 'red')
        elif self.specimenResult:
            self.displaymsg('All specimen scaned. Click Next.', 'green')
        else:
            self.displaymsg('Click Read To Start.')
