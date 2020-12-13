from .utils import warnImplement,validateBarcode
import time
from .logger import Logger
import requests

class Routine(Logger):
    "routine template"
    _pages = []
    _titles = []
    _msgs = []
    btnName = 'Routine'
    def __init__(self,master):
        self.master = master
        super().__init__(self.__class__.__name__,
        logLevel=self.master.config['appConfig']['LOGLEVEL'],
        fileHandler=self.master.fileHandler)
        self.pages = [
             self.master.pages[i] for i in self._pages
        ]
        self.currentPage = 0
        

    def startRoutine(self):
        "define how to start a routine"
        self.currentPage = 0
        self.results = [i.resultType() for i in self.pages]
        self.pages[0].setResult(self.results[0])
        self.pages[0].showPage(title=self._titles[0],msg=self._msgs[0])
        
    def returnHomePage(self):
        for p in self.pages:
            p.resetState()
        self.master.showHomePage()

    def prevPage(self):
        cp = self.currentPage
        np = self.currentPage -1
        if self.currentPage == 0:
            self.returnHomePage()
            return
        self.showNewPage(cp,np)
    
    def nextPage(self):
        cp = self.currentPage
        np = self.currentPage + 1
        
        self.showNewPage(cp,np)
        
    def showNewPage(self,cp,np):
        "close current page and show next page"
            # if the next page already have result stored, update with current stored result.
        self.results[cp] = self.pages[cp].readResult()
        self.pages[np].setResult(self.results[np])
        self.pages[cp].closePage()
        self.pages[np].showPage(title = self._titles[np],msg=self._msgs[np])
        self.currentPage = np

    def validateResult(self,result):
        warnImplement('validateResult',self)
        return (True, 'validation not implemented')

    def displayResult(self):
        "return formatted display of all current results"
        warnImplement('displayResult',self)
        return str(self.results)
    def saveResult(self):
        "save results to database"
        warnImplement('saveResult',self)
        yield 'not implement saveResult'

class SpecimenRoutine(Routine):
    _pages = ['BarcodePage','DTMXPage','BarcodePage','SavePage']
    _titles = ['dtmx page','barcoe page','save result']
    _msgs = ['scan barcoe','scan barcode','save result']
    btnName = 'Specimen'
    # sampleCount is the number of wells that have patient samples.
    sampleCount = 88
    def validateResult(self,code,):
        "provide feedback to each step's scan results"
        pageNbr = self.currentPage
        page = self.master.pages[self._pages[pageNbr]]
        if pageNbr == 0:
            return validateBarcode(code),'valid code'
        elif pageNbr == 1:
            return validateBarcode(code),'validbarcode'
        elif pageNbr == 2:
            return validateBarcode(code),'valid barcode'
    
    def validateSpecimen(self,result,sampleCount):
        # first valida locally until all samples are correct.
        toValidate = result[0:sampleCount]
        toValidateIds = [i[1] for i in toValidate]
        validlist = [True] * len(toValidateIds)
        duplicates = []
        invalids = []
        for index,id in enumerate(toValidateIds):
            if id and toValidateIds.count(id)>1:
                validlist[index] = False
                duplicates.append(toValidate[index])
            elif not validateBarcode(id,digits=self.master.config['DataMatrix']['specimenDigits']):
                validlist[index] = False
                invalids.append(toValidate[index])
        
        if not all(validlist):
            # not all valid by local criteria
            msg = []
            if duplicates:
                msg.append('Found duplicate IDs:')
                msg.append('\n'.join(duplicates))
            if invalids:
                msg.append('Found invalid IDs:')
                msg.append('\n'.join(invalids))
            return validlist, '\n'.join(msg)

        url = self.master.config['appConfig']['databaseURL'] + '/samples'
        try:
            res = requests.get(url,json={'sampleId':{'$in':toValidateIds}})
        except Exception as e:
            res = None
            self.error(f'{self.__class__.__name__}.validateSpecimen: Validation request failed: {e}')

        if (not res) or res.status_code != 200: #request problem
            self.error(f'{self.__class__.__name__}.validateSpecimen: Server respond with <{res.status_code}>.')
            return [False]*sampleCount,'Validation Server Error.'
        validIds =  { i.get('sampleId'):i.get('sPlate') for i in res.json()}
        for index,id in enumerate(toValidateIds):
            if id in validIds:
                if validIds[id]: # the sample is already in a sample well
                    duplicates.append(toValidate[index])
            else:
                # use validlist again for store Ids that were not found in database.
                validlist[index] = False
                invalids.append(toValidate[index])
        msg = []
        if duplicates:
            msg.append('These samples already in another plate:')
            msg.append('\n'.join(duplicates))
        if invalids:
            msg.append("These samples doesn't exist in database:")
            msg.append('\n'.join(invalids))
        if not msg:
            msg.append(f'{len(toValidateIds)} samples are all valid.')
        return validlist,'\n'.join(msg)


        

    def saveResult(self):
        "save results to database"
        for i in range(10):
            time.sleep(0.3)
            yield f'saving step {i}...'
        yield 'Done saving, return to main page in 2 seconds'
        time.sleep(2)
        self.returnHomePage()
        


class PlateLinkRoutine(Routine):
    _pages = ['BarcodePage','BarcodePage',"SavePage"]
    _titles = ['Scan From Plate','Scan To Plate','Save Linked Plates']
    _msgs = ['Scan ID on plate transfering from.',
        'Scan ID on plate transfering to','Review results and click save']
    btnName = 'Plate'
    def displayResult(self):
        fp = self.results[0]
        tp = self.results[1]
        return f"From plate: {fp} \nTo plate: {tp}\n"
    def saveResult(self):
        fp = self.results[0]
        tp = self.results[1]
        # save reulsts to server here:
        res = {}
        saveSuccess = True
        yield 'start saving...'
        time.sleep(1)
        if saveSuccess:
            yield 'save success'
            time.sleep(1)
            self.returnHomePage()
        else:
            yield 'save failed.'
            yield 'here is the reason: <insert server response here>'
            raise RuntimeError ('save failed')
        
    def validateResult(self, result):
        return super().validateResult(result)
    
class AddStorageRoutine(Routine):
    _pages = []
    _titles = []

class GetStorageRoutine(Routine):
    _pages = []

Routines = [
    SpecimenRoutine,
    PlateLinkRoutine,
    AddStorageRoutine,
    GetStorageRoutine
]