import tkinter as tk
from .barcodePage import BarcodePage
from .dtmxPage import DTMXPage
from .camera import Camera
import configparser


class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scanner App')
        
        self.resizable(0,0)
        
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')
        if self.config['appConfig']['appMode'] == 'dev':            
            self.geometry('800x480+1200+-30')#-30
        else:
            self.geometry('800x480+0+-30')#-30

        self.camera = Camera(config=self.config)
        

        container = tk.Frame(self)
    
        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        # load pages
        self.pages = {}
        for F in (HomePage,BarcodePage,DTMXPage):
            self.pages[F.__name__] = F(parent=container,master=self)
            self.pages[F.__name__].grid(row=0, column=0, sticky="nsew")
        
        self.showPage('HomePage',0)
        
    def showPage(self,routineName, page):
        if page <0:
            self.homePage.showPage()
        
        self.routine[routineName][page].showPage()
        

    def on_closing(self):
        print('exit')
        self.destroy()
        

class HomePage(tk.Frame):
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        self.create_widgets()
        
        
    def create_widgets(self):
        tk.Button(self,text='Specimen',font=('Arial',55),command=lambda:self.master.showPage('DTMXPage')).place(
            x=20,y=40,height=150,width=360)
        tk.Button(self,text='Plate',font=('Arial',60),command=lambda:self.master.showPage('BarcodePage')).place(
            x=420,y=40,height=150,width=360)

        tk.Button(self,text='Exit',font=('Arial',60),command=self.master.on_closing).place(
            x=20,y=210,height=150,width=360)

    def showPage(self):
        self.tkraise()
        self.focus_set()
