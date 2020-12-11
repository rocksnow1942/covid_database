import tkinter as tk
from .utils import validateBarcode,BaseViewPage
# import tkinter.scrolledtext as ST
from threading import Thread

 

class BarcodePage(BaseViewPage):
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.camera = master.camera
        self.create_widgets()
        self.initKeyboard()
  
    def create_widgets(self):
        tk.Label(self, text='Fr:', font=(
            'Arial', 38)).place(x=340, y=20)
        # grid(column=0,row=0,sticky='e',padx=(40,10),pady=(55,50))

        self.scanVar1 = tk.StringVar()
        # self.scanVar1.set('1234567890')

        self.scan1 = tk.Label(
            self, textvariable=self.scanVar1, font=('Arial', 38))
        self.scan1.place(x=450, y=20)  # grid(column=1,row=0,)

        tk.Label(self, text='To:', font=('Arial', 38)
                 ).place(x=340, y=110)
        # .grid(column=0,row=1,sticky='e',padx=(40,10),pady=(55,50))
        self.scanVar2 = tk.StringVar()
        # self.scanVar2.set('1234567890')
        self.scan2 = tk.Label(
            self, textvariable=self.scanVar2, font=('Arial', 38))
        self.scan2.place(x=450, y=110)  # .grid(column=1,row=1,)


        self.clearBtn = tk.Button(self, text='Clear', font=('Arial', 40), command=self.cancel)
        self.clearBtn.place(x=340, y=210, height=150, width=210)  
        self.saveBtn = tk.Button(self, text='Save', font=('Arial', 40), command=self.save)
        self.saveBtn.place(x=570, y=210, height=150, width=210) 

        self.msgVar = tk.StringVar()
        self.msg = tk.Label(self, textvariable=self.msgVar, font=('Arial', 20))
        
        self.msg.place(x=20, y=430, width=660)

        self.backBtn = tk.Button(self, text='Back', font=('Arial', 25),
                  command=self.goToHome)
        self.backBtn.place(x=680, y=390, height=50,width=90)

    def showPage(self):
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.barcodeThread = Thread(target=self.camera.liveScanBarcode,args=(self.keyboardCb,))
        self.barcodeThread.start()
      
        
    def goToHome(self):
        self.camera.stop()
        self.barcodeThread.join()
        self.master.showPage('HomePage')
        self.keySequence = []

    def keyboardCb(self,code):
        if validateBarcode(code, 'plate'):
            if code == self.scanVar1.get():
                self.displaymsg('Same code!', 'red')
                self.scan1.config(bg='red')
            elif not self.scanVar1.get():
                self.scanVar1.set(code)
                self.scan1.config(bg='green', fg='white')
            elif not self.scanVar2.get():
                self.scanVar2.set(code)
                self.scan2.config(bg='green', fg='white')
            else:
                self.displaymsg('Confirm/Cancel before new scan.', 'red')
        elif code == 'clear':
            self.scanVar1.set('')
            self.scanVar2.set('')
        else:
            self.displaymsg(f"Invalid: {code}", 'red')
 
    def save(self):
        code1 = self.scanVar1.get()
        code2 = self.scanVar2.get()
        if code1 and code2:
            try:
                self.displaymsg(f'{code1} <-> {code2}', 'green')
                self.scanVar1.set('')
                self.scanVar2.set('')
            except Exception as e:
                print(e)
                self.displaymsg(f"Error:{e}")

    def saveData(self,p1,p2):
        print(f'Linked {p1} to {p2}')

    def cancel(self):
        self.scanVar1.set('')
        self.scanVar2.set('')
        self.scan1.config(bg='white')
        self.scan2.config(bg='white')
        self.displaymsg('', 'white')

class DTMXPage(BaseViewPage):
    resultType = list
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []
        self.result = []
        self.master = master
        self.create_widgets()
        self.specimenRescanPrompt()
        self.camera = master.camera
        self.initKeyboard()

    def resetState(self):
        self.result=[]
        self.specimenError = []
        self.clearInfo()
        self._prevBtn['state'] = 'normal'
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'normal'

    def create_widgets(self):
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',25),command=self.prevPageCb)

        self._nextBtn = tk.Button(self,text='Next',font=('Arial',25),command=self.nextPageCb)
        if not self.master.devMode:
            self._nextBtn['state'] = 'disabled'

        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 40), command=self.read)
        self._msgVar = tk.StringVar()

        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))

        
        scbar = tk.Scrollbar(self,)
        
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.config(command=self._info.yview)
        scbar.place(x = 780,y=20,width=20,height=190)

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
        self.specimenRescanPrompt()

    def keyboardCb(self, code):
        ""
        if code == 'snap':
            self.camera.snapshot()
            return
        if self.specimenError:
            posi = self.camera.indexToGridName(self.specimenError[0])
            self.result[self.specimenError[0]] = (posi,code)
            
            if validateBarcode(code, 'specimen'):
                self.specimenError.pop(0)
                self.camera.drawOverlay(self.specimenError)
                self.displayInfo(f"{posi} : {code}")
            else:
                self.displayInfo(f"{posi} INVALID: {code} ")
            self.specimenRescanPrompt()

        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.')
        else:
            self.displaymsg('Read specimen to start.')

   
    def read(self):
        "read camera"        
        self._prevBtn['state'] = 'disabled'
        self._nextBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = []
        self.result = []

        def read():
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            for i, res in enumerate(self.camera.scanDTMX()):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i:3} / {total:3} {"."*(i%4)}')
                self.result.append((position,res))
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
                f"Rescan {self.result[idx][0]}: current={self.result[idx][1]}", 'red')
        elif self.result:
            self.displaymsg('All specimen scaned. Click Next.', 'green')
            self._nextBtn['state'] = 'normal'
        else:
            self.displaymsg('Click Read To Start.')


class SavePage(BaseViewPage):
    def __init__(self, parent, master):
        super().__init__(parent, master)
        self.creat_widgets()
    
    def creat_widgets(self):
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',25),command=self.prevPageCb)
        
        self.saveBtn = tk.Button(self,text='Save',font=('Arial',40),command=self.saveCb)
        
        scbar = tk.Scrollbar(self,)
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.config(command=self._info.yview)
        scbar.place(x = 780,y=20,width=20,height=190)
        self._info.place(x=340,y=20,width=440,height=190)
    
        self._prevBtn.place(x=360, y=360, width=90, height=50)
        self.saveBtn.place(x=650, y=360, height=50, width=90)

    def saveCb(self):
        print('save')


        

class HomePage(tk.Frame):
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        self.create_widgets()
        
    def create_widgets(self):
        tk.Button(self,text='Specimen',font=('Arial',55),command=lambda:self.master.startRoutine('SpecimenRoutine')).place(
            x=20,y=40,height=150,width=360)
        tk.Button(self,text='Plate',font=('Arial',60),command=lambda:self.master.startRoutine('BarcodePage')).place(
            x=420,y=40,height=150,width=360)
        tk.Button(self,text='Exit',font=('Arial',60),command=self.master.on_closing).place(
            x=20,y=210,height=150,width=360)

    def showPage(self):
        self.tkraise()
        self.focus_set()



AllPAGES = (HomePage,BarcodePage,DTMXPage,SavePage)