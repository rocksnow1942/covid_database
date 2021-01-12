import tkinter as tk
from threading import Thread
from . import BaseViewPage


class NumberInputPage(BaseViewPage):
    resultType = int
    def __init__(self,parent,master) -> None:
        
        super().__init__(parent,master)
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
    
    @property
    def inputValue(self):
        return self.numberVar.get()

    def placeDefaultWidgets(self):        
        self._msg.place(x=20, y=430, width=740)        
        self._prevBtn.place(x=340 , y=300,  height=90 ,width=130,)
        self._nextBtn.place(x=650 , y=300, height=90, width=130)
        self._title.place(x= 0,y=20,width=800,height=30)

        self.numberVar = tk.IntVar()
        self.numberVar.set(30)
        tk.Label(self,textvariable=self.numberVar,font=('Arial',65)).place(x=350,y=100,width=100)
        tk.Button(self,text='-',font=('Arial',65),command=lambda : self.numberVar.set(self.numberVar.get()-1))\
            .place(x=100,y=100,width=150,height=100)
        tk.Button(self,text='+',font=('Arial',65),command=lambda : self.numberVar.set(self.numberVar.get()+1))\
            .place(x=550,y=100,width=150,height=100)

    def showPage(self,title='Number input page',msg='Enter a number',color='green'):
        self.setTitle(title,color)
        self.tkraise()
        self.focus_set()
        self.displaymsg(msg,color)

    def closePage(self):
        pass

    def resetState(self):        
        pass

