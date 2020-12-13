import tkinter as tk
from .pages import AllPAGES
from .camera import Camera,Mock
from .routines import Routines
import configparser
from .logger import createFileHandler,Logger

class ScannerApp(tk.Tk,Logger):
    def __init__(self):
        super().__init__()
        self.config =  self.loadConfig()

        # initialzie loggger
        self.fileHandler = createFileHandler('ScannerApp.log')
        Logger.__init__(self,'ScannerApp',logLevel=self.config['appConfig']['LOGLEVEL'],
            fileHandler=self.fileHandler)
        self.title('Scanner App')
        self.resizable(0,0)

        if self.devMode:
            self.geometry('800x480+100+30')#-30
        else:
            self.geometry('800x480+0+-30')#-30

        if self.hasCamera:
            self.camera = Camera(config=self.config)
        else:
            self.camera = Mock()
        

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
    
    # config properties
    @property
    def URL(self):
        return self.config['appConfig']['databaseURL']
    @property
    def devMode(self):
        return self.config['appConfig']['appMode'] != 'prod'
    @property
    def LOGLEVEL(self):
        return self.config['appConfig']['LOGLEVEL']
    @property
    def specimenDigits(self):
        return self.config['DataMatrix']['specimenDigits']
    @property
    def enabledRoutine(self):
        return self.config['appConfig']['routines']
    @property
    def useCamera(self):
        return self.config['BarcodePage']['useCamera']
    @property
    def hasCamera(self):
        return self.config['appConfig']['hasCamera']


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
    

