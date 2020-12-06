import tkinter as tk
from .utils import validateBarcode,PageMixin
from threading import Thread
# https://pypi.org/project/keyboard/
 

class BarcodePage(tk.Frame,PageMixin):
    def __init__(self, parent, master):
        super().__init__(parent)
        self.master = master
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
