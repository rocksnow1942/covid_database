import tkinter as tk
import tkinter.scrolledtext as ST
from warnings import warn
from .logger import Logger

def warnImplement(funcname,ins):
    warn(f"Implement <{funcname}> in {ins.__class__.__name__}")


def validateBarcode(code,digits = 10,):
    return len(code) == digits and code.isnumeric() 


def indexToGridName(index,grid=(12,8),direction='top'):
    "convert 0-95 index to A1-H12,"
    rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:grid[1]]
    rowIndex = rowIndex if direction == 'top' else rowIndex[::-1]
    row = index//grid[0] + 1
    col = index - (row-1) * grid[0] + 1
    rowM = rowIndex[row-1]
    return f"{rowM}{col}"


class BaseViewPage(tk.Frame,Logger):
    resultType = str
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        Logger.__init__(self,self.__class__.__name__,
        logLevel=self.master.config['appConfig']['LOGLEVEL'],
        fileHandler=self.master.fileHandler)
        self.result = self.resultType()
        
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

 