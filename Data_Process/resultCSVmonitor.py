"for monitor the exported csv file and upload results"
import time
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import shutil
import requests
import json,os,glob
from collections import deque
from threading import Lock


TARGET_FOLDER= r"C:\Users\hui\Desktop\testfolder"
LOG_FILE = './csv_monitor.log'
LOG_LEVEL = 'debug'
CSV_JSON_LOG = './csv_log.json'

class MyLogger():
    "write logs to file."
    def debug(self, x): return 0
    def info(self, x): return 0
    def warning(self, x): return 0
    def error(self, x): return 0
    def critical(self, x): return 0
    def __init__(self, filename=None, logLevel=None, ):
        print(filename,logLevel)
        self.LOGLEVEL = logLevel
        fh = RotatingFileHandler( filename, maxBytes=2**23, backupCount=10)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s|%(name)-11s|%(levelname)-8s: %(message)s', datefmt='%m/%d %H:%M:%S'
        ))
        self.fh = fh
    
    def attachLogger(self,name,instance):
        "attach logging to an instance"
        level = getattr(logging,self.LOGLEVEL.upper(),20)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(self.fh)
        logger.setLevel(level)
        _log_level = ['debug', 'info', 'warning', 'error', 'critical']
        
        for i in _log_level:
            setattr(instance, i, getattr(logger, i))


class CsvHandler(PatternMatchingEventHandler):
    def __init__(self,logger,filehandler):        
        super().__init__(patterns=['*.csv'],ignore_patterns=['*~$*','*Conflict*','*!INVALID_FILENAME*'],
                ignore_directories=False,case_sensitive=True)
        logger.attachLogger('CsvHandler',self)
        self.handler = filehandler
    
    def on_created(self, event):
        file = event.src_path
        self.debug(f'{datetime.now()} on create file: ' + file)

    def on_deleted(self,event):
        file = event.src_path
        self.debug(f'{datetime.now()} on delete file: ' + file)
    
    def on_modified(self, event):
        file = event.src_path
        self.debug(f'{datetime.now()} on modify file: ' + file)

    def on_moved(self, event):
        file = event.src_path
        self.debug(f'{datetime.now()} on move file: ' + file)

class Analyzer():
    def __init__(self,targetFoler, logger, jsonlog):
        ""
        logger.attachLogger('Analyzer',self)
        self.tf = targetFoler
        self.jsonlog = jsonlog
        self.fileHistory = {}
        self.staged = deque()
        self.initialize()
    
    def initialize(self):
        "scan the target folder and compare with json log content"
        files = glob.glob(self.tf + r'\*.csv')
        if not os.path.exists(self.jsonlog):
            with open(self.jsonlog,'wt') as f:
                json.dump(self.fileHistory,f,indent=2)
        with open(self.jsonlog,'rt') as f:
            self.fileHistory = json.load(f)
        
        for file in files:
            if file not in self.fileHistory:
                self.fileHistory[file] = {'uploaded':False}
                self.staged.append(file)
        
        for file in list(self.fileHistory.keys()):
            if file not in files:
                self.fileHistory.pop(file)
        self.debug('Initialize done.')

    def close(self):
        "save the current status to log file"
        with open(self.jsonlog,'wt') as f:
            json.dump(self.fileHistory,f,indent=2)

    def create(self,file):
        "add a file to analyzer"
        self.staged.append(file)
        self.fileHistory[file] = {'uploaded':False}

    def sync(self):
        "synchronize the staged files to cloud."
        

    def upload(self,file):
        "upload data in a file to cloud."

         
    

def main():
    target_folder = TARGET_FOLDER
    
    logger = MyLogger(filename=LOG_FILE,logLevel=LOG_LEVEL)
    analyzer = Analyzer(target_folder,logger,CSV_JSON_LOG)
    handler = CsvHandler(logger,analyzer)
    observer = Observer()
    observer.schedule(handler,path=target_folder,recursive=True)
    observer.start()
    handler.debug('Monitor started.')
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            analyzer.close()
            handler.debug('Hander exit due to keybaord interrupt.')
            break
 
if __name__ == "__main__":
    main()
