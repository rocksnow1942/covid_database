import tkinter as tk
from .pages import AllPAGES
from .camera import Camera,Mock
from .routines import Routines
import configparser
from .logger import createFileHandler,Logger
from .validators import BarcodeValidator

class ScannerApp(tk.Tk,Logger):
    def __init__(self):
        super().__init__()
        self.config =  self.loadConfig()
        self.validator = BarcodeValidator(self)
        # initialzie loggger
        self.fileHandler = createFileHandler('ScannerApp.log')
        Logger.__init__(self,'ScannerApp',logLevel=self.LOGLEVEL,
            fileHandler=self.fileHandler)
        self.title('Scanner App')
        self.resizable(0,0)

        if self.devMode:
            self.geometry('800x480+100+30')#-30
        else:
            self.geometry('800x480+0+-30')#-30

        if self.hasCamera:
            self.camera = Camera(config=self.cameraConfig)
        else:
            self.camera = Mock()
        

        container = tk.Frame(self)
    
        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # load routine first without initialize
        self.routine = {}
        for rName in self.enabledRoutine:
            self.routine[rName] = Routines[rName]

        # load pages
        self.pages = {}
        
        for F in AllPAGES:
            self.pages[F.__name__] = F(parent=container,master=self)
            self.pages[F.__name__].grid(row=0, column=0, sticky="nsew")
        
        # initialize routines        
        for rName in self.routine:
            self.routine[rName] = Routines[rName](master=self)

        self.showHomePage()
    
    # config properties delegated to properties, instead of directly access
    # So that when altering config.ini structure, only need to change it here.
    @property
    def URL(self):
        return self.config['appConfig']['databaseURL']
    @property
    def cameraConfig(self):
        return self.config['cameraConfig']
    @property
    def devMode(self):
        return self.config['debugConfig']['appMode'] == 'dev'
    @property
    def LOGLEVEL(self):
        return self.config['debugConfig']['LOGLEVEL']
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
        return self.config['debugConfig']['hasCamera']
    @property
    def codeValidationRules(self):
        return self.config['codeValidation']

    def plateColor(self,plateType):
        return self.config['plateColors'].get(plateType,('',''))


    def validate(self,code,codeType=None):
        return self.validator(code,codeType)
    
    def validateInDatabase(self,code,codeType,validationType=None):
        return self.validator.validateInDatabase(code,codeType,validationType)

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
    

