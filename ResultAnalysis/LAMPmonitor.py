"for monitor the exported csv file and upload results"
import time
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import requests
import json,os
from collections import deque
from threading import Lock,Thread
import threading
import numpy as np
from dateutil import parser
from dateutil import tz
import sys
import time
import sys
import psutil
import subprocess

# start the script mannually with 
# python LAMPmonitor.py a 
# will print all errors



with open('./config.json','rt') as f:
    config = json.load(f)


# folder to monitor csv saved from qPCR
TARGET_FOLDER=  config['TARGET_FOLDER'] 

# foler to output plate ratio result.
TABLE_OUTPUT_FOLDER =  config['TABLE_OUTPUT_FOLDER'] 


LOG_FILE = './csv_monitor.log'
LOG_LEVEL = 'debug'
SUPERVISOR_LOG_FILE = './supervisor.log'

CSV_JSON_LOG = './csv_log.json'
DATABASE_URL = 'http://192.168.1.200:8001'




os.makedirs(TARGET_FOLDER,exist_ok=True)
os.makedirs(TABLE_OUTPUT_FOLDER,exist_ok=True)


class MyLogger():
    "write logs to file."
    def debug(self, x): return 0
    def info(self, x): return 0
    def warning(self, x): return 0
    def error(self, x): return 0
    def critical(self, x): return 0
    def __init__(self, filename=None, logLevel=None, ):        
        self.LOGLEVEL = logLevel
        fh = RotatingFileHandler( filename, maxBytes=2**23, backupCount=10)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s|%(name)-11s|%(levelname)-8s: %(message)s', datefmt='%m/%d %H:%M:%S'
        ))
        self.fh = fh
    
    def attachLogger(self,name,instance=None):
        "attach logging to an instance"
        level = getattr(logging,self.LOGLEVEL.upper(),20)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(self.fh)
        logger.setLevel(level)
        _log_level = ['debug', 'info', 'warning', 'error', 'critical']
        
        if instance:
            for i in _log_level:
                setattr(instance, i, getattr(logger, i))


class CsvHandler(PatternMatchingEventHandler):
    def __init__(self,logger,filehandler):        
        super().__init__(patterns=['*.csv'],ignore_patterns=['*~$*','*Conflict*','*!INVALID_FILENAME*'],
                ignore_directories=False,case_sensitive=True)
        if sys.argv[-1] == '-m':
            logger.attachLogger('CsvHandler',self)
        else:
            self.debug = self.error = self.info =  print        
        self.handler = filehandler
    
    def on_created(self, event):
        file = event.src_path
        self.debug('Create file: ' + file)
        time.sleep(0.5)
        self.handler.create(file)

    def on_deleted(self,event):
        file = event.src_path
        self.debug('Delete file: ' + file)
    
    def on_modified(self, event):
        file = event.src_path
        self.debug('Modify file: ' + file)

    def on_moved(self, event):
        file = event.src_path
        self.debug('Move file: ' + file)
        

class Analyzer():
    def __init__(self,targetFoler, logger, jsonlog):
        ""        
        if sys.argv[-1] == '-m':
            logger.attachLogger('Analyzer',self)
        else:
            self.debug = self.error = self.info =  print
        
        self.tf = targetFoler
        self.jsonlog = jsonlog
        self.fileHistory = {}
        self.staged = deque()
        self.initialize()
        self.lock = Lock()

    def url(self,sub):
        return DATABASE_URL+sub
    
    def initialize(self):
        "scan the target folder and compare with json log content"        
        files = [os.path.join(self.tf,i) for i in os.listdir(self.tf)]
        files = list(filter(lambda f:f.endswith('.csv') and os.path.isfile(f) , files))
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
        self.save()


    def save(self):
        "save the current status to log file"
        with open(self.jsonlog,'wt') as f:
            json.dump(self.fileHistory,f,indent=2)

    def create(self,file):
        "add a file to analyzer"
        # print(f'Create thread: {threading.get_ident()}')
        self.lock.acquire()
        self.staged.append(file)        
        self.fileHistory[file] = {'uploaded':False}
        self.save()
        self.lock.release()

    def sync(self):
        "synchronize the staged files to cloud."
        # print(f'Sync thread: {threading.get_ident()}')
        if not self.staged: return 'Nothing Synced.'
        self.lock.acquire()        
        file = self.staged.popleft()
        self.fileHistory[file].update(status='start sync')
        self.lock.release()
        
        try:
            id,wells = self.parseCSV(file)
        except Exception as e:
            self.error(f'sync->parseCSV error {e}')
            self.fileHistory[file].update(error='Parse CSV error')
            return
        
        plate = self.getPlate(id,file=file)
        if not plate:
            # plate is not in data base, still write to file.
            plate = self.getEmptyPlate(id)
            self.updatePlate(plate,wells)
            Thread(target=self.writeOnePlateToCSV,args=(plate,),).start()
            return
                
        # the plate information is here,update the date document.
        try:
            plate = self.updatePlate(plate,wells)
        except Exception as e:
            self.error(f'sync->updatePlate: {e}')
            self.fileHistory[file].update(error='update plate error')
            return
        
        #write te plate data to csv.
        Thread(target=self.writeOnePlateToCSV,args=(plate,),).start()

        # upload updated plate to server.
        status = self.uploadPlate(plate)
        if not status: 
            self.fileHistory[file].update(error='server error: Upload error')
            return
        
        # upload succeeded.
        self.fileHistory[file].pop('error',None)
        self.fileHistory[file].update(status='Uploaded.')
        self.fileHistory[file].update(uploaded=True)

        # if the plate have companion plate, try to see if that plate is done.
        if plate['companion']:
            companionPlate = self.getPlate(plate['companion'])
            if not companionPlate: return
            if companionPlate['step'] != 'read': # step != read means this plate havn't updated raw data.
                return
                        
            results = self.parseResult(plate,companionPlate)

            # send result to server.
            res = requests.post(self.url('/samples/results'),json=results)
            if res.status_code == 200:
                # write results to csv file after upload success.
                Thread(target=self.writeResultToCSV,args=([i['sampleId'] for i in results],),).start()
            else:
                self.error(f'Save results to server error {res.status_code}: {res.json()}')

    def writeOnePlateToCSV(self,plate):
        "write a plate to csv file"
        id = plate['plateId']
        pType = 'RP4' if plate['layout'].endswith('RP4Ctrl') else 'N7'
        file = os.path.join(TABLE_OUTPUT_FOLDER,f'{datetime.now().strftime("%Y%m%d %H%M")} {pType} {id}.csv')        
        col = ['']+[str(i) for i in range(1,13)]
        linesRatio = [','*12,f'{id} {pType} Normalized RFU Ratio'+','*12 ,','.join(col)]
        linesRaw = [f'{id} {pType} Raw RFU'+','*12 , ','.join(col)]
        wells = plate['wells']
        for row in 'ABCDEFGH':
            a = [row] # is ratio
            b = [row] # is raw
            for c in col[1:]:
                ratio = str(wells.get(f'{row}{c}',{}).get('ratio',''))
                raw = str(wells.get(f'{row}{c}',{}).get('raw',''))
                a.append(ratio)
                b.append(raw)
            linesRatio.append(','.join(a))
            linesRaw.append(','.join(b))
        with open(file,'wt') as f:
            f.write('\n'.join(linesRaw+linesRatio))
            f.write('\n')
    
    def getEmptyPlate(self,id='Unknown ID'):
        "return a mock plate to use"    
        return {
            'plateId': f"{id or 'Unknown ID'} Not In Server",
            'layout': 'Sample88_2NTC_3PTC_3IAB',
            'wells':{f"{R}{C}":{} for R in 'ABCDEFGH' for C in range(1,13)},
        }

    def parseISOtime(self,isoString):
        "turn mongo time stamp to python datetime object."
        dt = parser.parse(isoString)
        return dt.astimezone(tz.tzlocal())

    def writeResultToCSV(self,sampleIds):
        "write results to csv from a group of sample Ids"
        file = os.path.join(TABLE_OUTPUT_FOLDER,f'{datetime.now().strftime("%Y%m%d %H%M")} Diagnose Result.csv')
        cols=['Well','name','collectAt','result','N7','RP4','N7_NTC','N7_NTC_CV','N7_PTC','N7_PTC_CV','N7_NBC_CV',
                'RP4_NTC','RP4_NTC_CV','RP4_PTC','RP4_PTC_CV','RP4_NBC_CV','testStart','testEnd']
        toWrite = [','.join(cols)]
        try:
            
            res = requests.get(self.url(f'/samples?page=0&perpage={len(sampleIds)}'),json={'sampleId':{'$in':sampleIds}})
            if res.status_code == 200:
                samples = res.json()
                for s in samples:
                    t = []
                    t.append(s['sWell'])
                    t.append(s.get('meta',{}).get('name','unknown'))
                    t.append(self.parseISOtime(s['created']).strftime('%H:%M'))
                    for i in cols[3:]:
                        t.append(str(s['results'][-1].get(i,'')))
                    toWrite.append(','.join(t))
            else:
                self.error(f'writePlateToCSV error: {res.status_code}: {res.json()}')
        except Exception as e:
            self.error(f'writePlateToCSV error: {e}')
        
        with open(file,'wt') as f:
            f.write('\n'.join(toWrite))
            f.write('\n')

    def callResult(self,res,NTCs=[]):
        """
        call based on individual well result
        """
        # if res['N7_NTC'] >= 5: return 'Invalid:N7NTC'
        # if res['RP4_NTC'] >= 5: return 'Invalid:RP4NTC'

        if any([i> 5 for i in NTCs['N7']]): return 'Invalid:N7NTC'
        if any([i> 5 for i in NTCs['RP4']]): return 'Invalid:RP4NTC'
        if res['N7_NBC_CV'] > 5:return 'Invalid:N7CV'
        if res['RP4_NBC_CV'] > 5:return 'Invalid:RP4CV'
        if res['N7_PTC'] < 1.8: return 'Invalid:N7PTC'
        if res['RP4_PTC'] < 1.8: return 'Invalid:RP4PTC'
        if res['N7']>5:return 'Positive'
        if res['RP4']<5:return 'Invalid:RP4'
        return 'Negative'

    def parseResult(self,p1,p2):
        "give the document of two plate, update their final result to server"
        if p1['layout'].endswith('RP4Ctrl'):
            N = p2
            RP = p1
        else:
            N= p1
            RP = p2
        # need to do if plate.layout == Sample88_2NTC_3PTC_3IAB in the future if we have other types.
        layout = N['layout']
        if (layout.startswith('Sample88_2NTC_3PTC_3IAB') or 
            layout.startswith('VariableSample_2NTC_3PTC_3IAB')):
            Nwells = N['wells']
            RPwells = RP['wells']
            Nres = N['result']
            RPres = RP['result']

            _r = {'N7':Nres,'RP4':RPres}
            control = { f"{p}{t}":_r[p][f"{p}{t}"] for p in ['N7','RP4'] 
                            for t in ['_NTC','_PTC','_NTC_CV','_PTC_CV','_NBC_CV']}
            
            control.update(
                testStart=N['created'],
                plateId=[N['plateId'],RP['plateId']],
                comment='',            
            )

            # get all 4 NTC positions. assuming the plate layout here.
            NTCs = {n:[i[w]['ratio'] for w in ['A12','B12']] for (n,i) in [('N7',Nwells),('RP4',RPwells)]}
            results =[]
            for well in Nwells.keys():
                n = Nwells[well]
                r = RPwells[well]
                if not n['sampleId']: # bypass control wells.
                    continue
                result = control.copy()            
                result.update(
                    N7 = n['ratio'],                
                    RP4 = r['ratio'],              
                )
                result['result'] = self.callResult(result,NTCs)

                results.append(dict(
                    sampleId=n['sampleId'],
                    results=[result]
                ))
            return results

        raise RuntimeError('Plate not defined in parseResult')


    def getPlate(self,id,file=None):
        "get plateId = id plate data from server."
        try:
            res = requests.get(self.url('/plates/?page=0&perpage=1'),json={'plateId':id})
            if res.status_code == 200:
                if res.json():
                    plate = res.json()[0]
                    return plate
                else:
                    self.error(f'sync->getPlate plate ID {id} not in database')
                    if file:
                        self.fileHistory[file].update(error=f'plate ID {id} not in database')
                    return None
            else:
                if file:
                    self.fileHistory[file].update(error=f'server error: {res.status_code}')
                self.error(f'sync->getPlate server response {res.status_code}:{res.json()}')
                return None          
        except Exception as e:
            if file:self.fileHistory[file].update(error='server error: can not request.')
            self.error(f'sync->getPlate error {e}')
            return None
        

    def uploadPlate(self,plate):
        "upload the plate data to plate collection in ams"
        try:
            res = requests.put(self.url('/plates'),json=plate)
            if res.status_code==200:                
                return True
            else:
                self.error(f'sync:uploadPlate server response {res.status_code},{res.json()}')
        except Exception as e:
            self.error(f'sync:uploadPlate error: {e}')

    def calcMetrics(self,wells,labels):
        "calculate average, cv"
        vals = [wells[l] for l in labels]
        return round(np.mean(vals),1),round(np.std(vals,ddof=1)*100/np.mean(vals),2),
    
    def calcRatioGenerator(self,NBCavg,PTCavg):
        def wrap(raw):
            return round((raw-NBCavg)/(PTCavg-NBCavg) * 9 + 1,2)
        return wrap


    def updatePlate(self,plate,wells):
        "fill in the raw data and analysis result based on plate layout and wells raw data."
        layout = plate['layout']
        if (layout.startswith('Sample88_2NTC_3PTC_3IAB') or 
            layout.startswith('VariableSample_2NTC_3PTC_3IAB')):
            # this also includes the '-RP4Ctrl' plate
            # calculate the controls 
            primer = 'RP4' if layout.endswith('RP4Ctrl') else 'N7'
            NTCavg,NTCcv = self.calcMetrics(wells,['A12','B12'])
            PTCavg,PTCcv = self.calcMetrics(wells,['C12','D12','E12'])
            NBCavg,NBCcv = self.calcMetrics(wells,['F12','G12','H12'])
            calc = self.calcRatioGenerator(NBCavg,PTCavg)
            for well,item in plate['wells'].items():
                raw = wells[well]
                item['raw']=raw
                item['ratio'] = calc(raw)
            plate['result']={
                f'{primer}_NTC':calc(NTCavg),
                f'{primer}_NTC_CV': NTCcv,
                f'{primer}_PTC': round(PTCavg/NBCavg,2),
                f'{primer}_PTC_CV': PTCcv,
                f'{primer}_NBC_CV': NBCcv,                
            }
            plate['step'] = 'read'
            return plate
        
        raise RuntimeError('plate layout is not defined in updatePlate')


    def parseCSV(self,file):
        "read and return structured data from CSV file."
        with open(file,'rt') as f:
            data = f.readlines()
        id=""
        wells = {}
        wellStart = False
        for line in data:
            if wellStart:                
                ss =  line.strip().split(',')
                if len(ss)!=2 or (not ss[1]):
                    continue
                well,value = ss              
                # turn A01 to A1
                well = f"{well[0]}{int(well[1:])}"
                wells[well] = int(float(value))
            elif line.startswith('ID'):
                id = line.strip().split(',')[1]
            elif line.startswith('Well,'):
                wellStart = True        
        return id, wells

 

def startMonitor():
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
            res = analyzer.sync()
            time.sleep(10)
            if res != 'Nothing Synced.':
                analyzer.save()
        except KeyboardInterrupt:
            analyzer.save()
            handler.debug('Hander exit due to keybaord interrupt.')
            break
        except Exception as e:
            analyzer.error(f'Sync Analyzer Error.{e}')
            continue



def start_script():
    result = subprocess.Popen(
        [sys.executable, sys.argv[0], '-m'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result


def startSupervisor():   
    logger = MyLogger(filename=SUPERVISOR_LOG_FILE,logLevel=LOG_LEVEL) 
    logger.attachLogger('SUPERVISOR',logger)
    monitorpid = start_script()
    logger.info('Supervisor started script')
    while 1:
        try:
            pids = [p.pid for p in psutil.process_iter()]
            if monitorpid.pid not in pids:  # restart if process is gone.
                logger.error('Monitor stopped. restart...')
                try:
                    monitorpid = start_script()
                    logger.info('Script restarted.')      
                except Exception as e:
                    logger.error(f'Script restart failed {e}')
                    pass
            # check every 600 seconds if the monitor service is running.
            time.sleep(600)   
        except KeyboardInterrupt as e:
            logger.info('Stopped supervisor by keybaord interrupt.')
            exit(0)      
        except:           
            time.sleep(30)
            continue
        

if __name__ == '__main__':
    if sys.argv[-1] in ('-m','a'):
        startMonitor()    
    else:
        startSupervisor()    