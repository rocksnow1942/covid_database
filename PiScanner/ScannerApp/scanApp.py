import tkinter as tk
from .pages import AllPAGES
from .camera import Camera
from .routines import Routines
import configparser


class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config =  self.loadConfig()
        self.title('Scanner App')
        self.resizable(0,0)

        if self.config['appConfig']['appMode'] != 'prod':
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
        

        self.routine = {}
        for routine in Routines:
            self.routine[routine.__name__] = routine(master=self)
        self.showHomePage()
    
    def loadConfig(self):
        "load configuration from .ini"
        config = configparser.ConfigParser()
        config.optionxform = str # to perserve cases in option names.
        config.read('./config.ini')
        configdict = {}
        for section in config.sections():
            configdict[section]={}
            for key in config[section].keys():
                configdict[section][key] = eval(config[section][key])
        return configdict

    def showHomePage(self):
        self.currentRoutine = None
        self.pages['HomePage'].showPage()
    
    def startRoutineCb(self, routineName):
        def cb():
            self.currentRoutine = self.routine[routineName]
            self.currentRoutine.startRoutine()
        return cb
 
    def on_closing(self):
        self.destroy()
    

