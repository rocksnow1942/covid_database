import tkinter as tk
from .utils import validateBarcode, PageMixin
from threading import Thread

class DTMXPage(tk.Frame, PageMixin):
    def __init__(self, parent, master):
        super().__init__(parent)
        self.specimenError = []
        self.specimenResult = []
        self.master = master
        self.create_widgets()
        self.camera = master.camera
        self.initKeyboard()

    def create_widgets(self):
        tk.Label(self, text='LP:', font=(
            'Arial', 40)).place(x=340, y=20, )
        # grid(column=0,row=0,sticky='e',padx=(40,10),pady=(55,50))

        self.scanVar1 = tk.StringVar()
        # self.scanVar1.set('1234567890')

        self.scan1 = tk.Label(
            self, textvariable=self.scanVar1, font=('Arial', 40))
        self.scan1.place(x=440, y=20)  # grid(column=1,row=0,)

        tk.Label(self, text='SP:', font=('Arial', 40)
                 ).place(x=340, y=110)
        # .grid(column=0,row=1,sticky='e',padx=(40,10),pady=(55,50))
        self.scanVar2 = tk.StringVar()
        # self.scanVar2.set('1234567890')
        self.scan2 = tk.Label(
            self, textvariable=self.scanVar2, font=('Arial', 40))
        self.scan2.place(x=440, y=110)  # .grid(column=1,row=1,)

        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 40), command=self.read)
        self.readBtn.place(x=340, y=210, height=150, width=210)
        self.saveBtn = tk.Button(self, text='Save', font=(
            'Arial', 40), command=self.save)
        self.saveBtn.place(x=570, y=210, height=150, width=210)
        self.saveBtn['state'] = 'disabled'

        self.msgVar = tk.StringVar()
        self.msg = tk.Label(self, textvariable=self.msgVar, font=('Arial', 20))

        self.msg.place(x=20, y=430, width=660)

        self.backBtn = tk.Button(self, text='Back', font=('Arial', 25),
                                 command=self.goToHome)
        self.backBtn.place(x=680, y=390, height=50, width=90)

        self.specimenRescanPrompt()

    def showPage(self):
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.camera.drawOverlay(self.specimenError)

    def goToHome(self):
        self.camera.stop()
        self.master.showPage('HomePage')
        self.keySequence = []

    def keyboardCb(self, code):
        ""
        if code == 'snap':
            self.camera.snapshot()
            return
        if self.specimenError:
            self.specimenResult[self.specimenError[0]] = code
            if validateBarcode(code, 'specimen'):
                self.specimenError.pop(0)
                self.camera.drawOverlay(self.specimenError)
            self.specimenRescanPrompt()

        elif self.specimenResult:
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
                    self.saveBtn['state'] = 'normal'
                else:
                    self.displaymsg('Save before new scan.', 'red')
            elif code == 'clear':
                self.scanVar1.set('')
                self.scanVar2.set('')
                self.saveBtn['state'] = 'disabled'
            else:
                self.displaymsg(f"Invalid: {code}", 'red')
        else:
            self.displaymsg('Read specimen to start.')

    def displayScan(self, code):
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

    def save(self):
        code1 = self.scanVar1.get()
        code2 = self.scanVar2.get()
        sL = len(self.specimenResult)
        if code1 and code2 and sL:
            try:
                self.saveData(self.specimenResult, code1, code2)
                self.displaymsg(f'{code1}/{code2} <-> {sL} specimen', 'green')
                self.scanVar1.set('')
                self.scanVar2.set('')
                self.saveBtn['state'] = 'disabled'
                self.specimenResult = []
            except Exception as e:
                print(e)
                self.displaymsg(f"Error:{e}")

    def saveData(self, specimen, p1, p2):
        "save data to server"
        print(specimen)
        print(f'Saved to {p1},{p2}')

    def read(self):
        "read camera"
        self.scanVar1.set('')
        self.scanVar2.set('')
        self.backBtn['state'] = 'disabled'
        self.saveBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = []
        self.specimenResult = []

        def read():
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]
            for i, res in enumerate(self.camera.scanDTMX()):
                self.displaymsg(
                    f'{"."*(i%4)} Reading {i:3} / {total:3} {"."*(i%4)}')
                self.specimenResult.append(res)
            self.specimenError = []
            for idx, res in enumerate(self.specimenResult):
                if not validateBarcode(res, 'specimen'):
                    self.specimenError.append(idx)
            self.camera.drawOverlay(self.specimenError)
            self.specimenRescanPrompt()
            self.backBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
        Thread(target=read,).start()

    def specimenRescanPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            idx = self.specimenError[0]
            self.displaymsg(
                f"Rescan {self.camera.indexToName(idx)}: {self.specimenResult[idx]}", 'red')
        elif self.specimenResult:
            self.displaymsg('All specimen correct. Scan Plate.', 'green')
        else:
            self.displaymsg('Read Specimen To Start.')
