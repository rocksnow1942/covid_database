import time
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import requests
import json
import os
from collections import deque
from threading import Lock, Thread
import threading
import numpy as np
from dateutil import parser
from dateutil import tz
import sys
import time
import sys
import psutil
import subprocess
import signal

class MyLogger():
    "write logs to file."

    def debug(self, x): return 0
    def info(self, x): return 0
    def warning(self, x): return 0
    def error(self, x): return 0
    def critical(self, x): return 0

    def __init__(self, filename=None, logLevel=None, ):
        self.LOGLEVEL = logLevel
        fh = RotatingFileHandler(filename, maxBytes=2**23, backupCount=10)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s|%(name)-11s|%(levelname)-8s: %(message)s', datefmt='%m/%d %H:%M:%S'
        ))
        self.fh = fh

    def attachLogger(self, name, instance=None):
        "attach logging to an instance"
        level = getattr(logging, self.LOGLEVEL.upper(), 20)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(self.fh)
        logger.setLevel(level)
        _log_level = ['debug', 'info', 'warning', 'error', 'critical']

        if instance:
            for i in _log_level:
                setattr(instance, i, getattr(logger, i))

logger = MyLogger(filename='./test signal log.log', logLevel='debug')

def receiveSignal(sigNum,frame,):
    print('received signal: ',sigNum)
    if sigNum == 2:
        print(frame)
        logger.exit=1
    return 

def main():
    
    logger.attachLogger('SUPERVISOR', logger)
    while 1:
        time.sleep(3)
        logger.debug(f'Running at {time.time()}')
        if getattr(logger,'exit',None):
            exit(0)
        







if __name__ == "__main__":
     # register the signals to be caught
    # signal.signal(signal.SIGHUP, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)
    # signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGILL, receiveSignal)
    # signal.signal(signal.SIGTRAP, receiveSignal)
    signal.signal(signal.SIGABRT, receiveSignal)
    # signal.signal(signal.SIGBUS, receiveSignal)
    signal.signal(signal.SIGFPE, receiveSignal)
    # signal.signal(signal.SIGKILL, receiveSignal)
    # signal.signal(signal.SIGUSR1, receiveSignal)
    signal.signal(signal.SIGSEGV, receiveSignal)
    # signal.signal(signal.SIGUSR2, receiveSignal)
    # signal.signal(signal.SIGPIPE, receiveSignal)
    # signal.signal(signal.SIGALRM, receiveSignal)
    signal.signal(signal.SIGTERM, receiveSignal)
    
    for i in ['SIGINT','SIGILL','SIGABRT']

    main()