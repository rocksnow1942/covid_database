import tkinter as tk
from .pages import AllPAGES
from .camera import Camera
from .routines import SpecimenRoutine
import configparser


class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scanner App')
        
        self.resizable(0,0)
        
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')
        if self.config['appConfig']['appMode'] == 'dev':            
            self.geometry('800x480+100+30')#-30
            self.devMode = True
        else:
            self.devMode = False
            self.geometry('800x480+0+-30')#-30

        self.camera = Camera(config=self.config)
        

        container = tk.Frame(self)
    
        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    
        # load pages
        self.pages = {}
        
        for F in AllPAGES:
            self.pages[F.__name__] = F(parent=container,master=self)
            self.pages[F.__name__].grid(row=0, column=0, sticky="nsew")
        

        self.routine = routine = {}
        routine['HomePage'] = {
            'pages':[self.pages['HomePage']]
        }
        for r in (SpecimenRoutine,):
            self.routine[r.__name__] = r(master=self)

        self.showHomePage()
    
    def showHomePage(self):
        self.currentRoutine = None
        self.pages['HomePage'].showPage()
    
    def startRoutine(self, routineName):
        self.currentRoutine = self.routine[routineName]
        self.currentRoutine.startRoutine()
 
    def on_closing(self):
        self.destroy()
    

