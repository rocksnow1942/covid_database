from .utils import warnImplement
import time
from .logger import Logger
import requests
from .validators import selectPlateLayout

class Routine(Logger):
    "routine template"
    _pages = []
    _titles = []
    _msgs = []
    btnName = 'Routine'
    def __init__(self,master):
        self.master = master
        super().__init__(self.__class__.__name__,
        logLevel=self.master.LOGLEVEL,
        fileHandler=self.master.fileHandler)
        # self.pages = [
        #      self.master.pages[i] for i in self._pages
        # ]
        self.currentPage = 0
    
    @property
    def pages(self,):
        return [self.master.pages[i] for i in self._pages]
    
    def startRoutine(self):
        "define how to start a routine"
        self.currentPage = 0
        self.results = [i.resultType() for i in self.pages]
        self.pages[0].setResult(self.results[0])
        self.pages[0].showPage(title=self._titles[0],msg=self._msgs[0])
        
    def returnHomePage(self):
        self.pages[self.currentPage].closePage()
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
        self.currentPage = np
        self.results[cp] = self.pages[cp].readResult()
        self.pages[np].setResult(self.results[np])
        self.pages[cp].closePage()
        self.pages[np].showPage(title = self._titles[np],msg=self._msgs[np])
        

    def validateResult(self,result):
        """this method is called by routine's pages when they need to validate result.
        normally return True/False, a message, and whether bypass the error check.
        """
        warnImplement('validateResult',self)
        return (True, 'validation not implemented',False)

    def displayResult(self):
        "return formatted display of all current results"
        warnImplement('displayResult',self)
        return str(self.results)
    def saveResult(self):
        "save results to database"
        warnImplement('saveResult',self)
        yield 'not implement saveResult'

class SampleToLyse(Routine):
    _pages = ['BarcodePage','DTMXPage','BarcodePage','SavePage']
    _titles = ['Scan Sample Plate Barcode',
                'Place Plate on reader',
                'Scan Lyse Plate Barcode',
                'Save Result']
    _msgs = ['Scan barcode on the side of sample plate.',
             'Click Read to scan sample IDs',
             'Scan barcode on the side of blue plate.',
             'Review the results and click Save']
    btnName = 'Sample'
    # control filter return true if the sample is a control. x is the 0 based index, posi is from A1-A2...
    
    def __init__(self, master):
        super().__init__(master)
        
        self.plate = None

    def validateResult(self,code,):
        "provide feedback to each step's scan results"
        pageNbr = self.currentPage
        # page = self.pages[pageNbr]
        if pageNbr == 0:
            plate = selectPlateLayout(self.master.validate(code,'samplePlate'))
            if plate:
                self.plate = plate(self)
                return True, f"Plate ID valid. Layout: {plate.__name__}",False
            else:
                self.plate = None
                return False, f"Plate ID < {code} > is invalid.", False
        elif pageNbr == 1:            
            return self.validateSpecimen(code)
        elif pageNbr == 2:
            valid = self.master.validate(code,'lyse')
            return valid, 'Lyse plate ID valid.' if valid else 'Invalid Lyse plate barcode.', False
    def returnHomePage(self):
        self.plate = None
        return super().returnHomePage()
        
    def displayResult(self):
        sPlate = self.results[0]
        lp = self.results[2]
        total = self.plate.totalSample
        msg = [f"Specimen plate ID: {sPlate}.",f"Lysis plate ID: {lp}",f"Total patient sample: {total}."]
        return '\n'.join(msg)

    def validateSpecimen(self,toValidate):
        # use validator on selected plate to validate the datamatrix result.
        if self.plate:
            return self.plate(toValidate)
        else:
            return [False]*len(toValidate),'Read Sample Plate ID first.', False

    def compileResult(self):
        "combine the result to json."
        sPlate = self.results[0]
        wells = self.results[1]
        lp = self.results[2]
        
        plate = {
            'plateId':lp,
            'step':'lyse',
            'layout':self.plate.__class__.__name__,
            'wells':self.plate.compileWells(wells)
        }

        samples = [{'sampleId':id, 'sPlate':sPlate,'sWell': sWell} 
                for sWell,id in self.plate.compileSampleIDs(wells)]
        return plate, samples

    def saveResult(self):
        "save results to database"
        plateurl = self.master.URL + '/plates'
        sampleurl = self.master.URL + '/samples'
        plate,samples = self.compileResult()
        yield 'Results compiled.'
        yield 'Saving plate results...'        
        res = requests.post(plateurl,json=plate)

        if res.status_code == 200:
            self.info(f'Saved plate: <{plate["plateId"]}> to database.')
            yield 'Plate result saved.'
        else:
            self.error(f'Error saving plate: <{plate["plateId"]}>.')
            raise RuntimeError (f"Saving plate result error: {res.status_code}, {res.json()}")
        
        yield 'Saving sample results...'

        res = requests.put(sampleurl,json=samples)

        if res.status_code == 200:
            # check if result have the same amount
            savedcount = sum(bool(i) for i in res.json())
            assert savedcount == len(samples) , f'Saved sample count {savedcount} != to save sample count {len(samples)}.'
            self.info(f'Saved < {len()} > samples to database.')
            yield 'Sample result saved.'
        else:
            raise RuntimeError (f"Saving sample result error: {res.status_code}, {res.json()}")    
        yield 'Done saving, return to home page in 2 seconds.'
        time.sleep(2)
        self.returnHomePage()
        
class CreateSample(Routine):
    ""
    _pages = ['DTMXPage','SavePage']
    _titles = ['Scan Sample Plate barcoe','Save Sample IDs to database']
    _msgs = ['Scan Sample Plate barcoe','Review the results and click Save']
    btnName = 'Create'
    def validateResult(self, wells):
        validlist = [self.master.validate(id,'sample') for (wn,id) in wells]
        msg = f'{sum(validlist)} / {len(validlist)} valid sample IDs found.'
        return validlist, msg ,True
    
    def displayResult(self,):
        wells = self.results[0]
        total = len(wells)
        valid = [None]
        invalid = [None]
        for (wn,id) in wells:
            if self.master.validate(id,'sample'):
                valid.append(f"{wn} : {id}" )
            else:
                invalid.append(f"{wn} : {id}")
        valid[0] = f"Total Valid Sample IDs: {len(valid)-1} / {total}"
        invalid[0] = f"Total Invalid Sample IDs: {len(invalid)-1} / {total}"
        return '\n'.join(invalid+valid)

    def saveResult(self):
        sampleurl = self.master.URL + '/samples'
        wells = self.results[0]
        valid = [{'sampleId':id} for (wn,id) in wells if self.master.validate(id,'sample')]
        yield f'Saving {len(valid)} samples to database...'
        res = requests.post(sampleurl,json=valid)
        if res.status_code == 200:
            yield 'Samples saved successfully.'
        else:
            raise RuntimeError(f"Saving error: server respond with {res.status_code}, {res.json()}")
        yield 'Done Saving, return to home page in 2 seconds.'
        time.sleep(2)
        self.returnHomePage()

class DeleteSample(Routine):
    ""
    _pages = ['DTMXPage','SavePage']
    _titles = ['Scan Sample Plate barcoe','Save Sample IDs to database']
    _msgs = ['Scan Sample Plate barcoe','Review the results and click Save']
    btnName = 'Create'
    def validateResult(self, wells):
        validlist = [self.master.validate(id,'sample') for (wn,id) in wells]
        msg = f'{sum(validlist)} / {len(validlist)} valid sample IDs found.'
        return validlist, msg ,True
    
    def displayResult(self,):
        wells = self.results[0]
        total = len(wells)
        valid = [None]
        invalid = [None]
        for (wn,id) in wells:
            if self.master.validate(id,'sample'):
                valid.append(f"{wn} : {id}" )
            else:
                invalid.append(f"{wn} : {id}")
        valid[0] = f"Total Valid Sample IDs: {len(valid)-1} / {total}"
        invalid[0] = f"Total Invalid Sample IDs: {len(invalid)-1} / {total}"
        return '\n'.join(invalid+valid)

    def saveResult(self):
        sampleurl = self.master.URL + '/samples'
        wells = self.results[0]
        valid = [{'sampleId':id} for (wn,id) in wells if self.master.validate(id,'sample')]
        yield f'Saving {len(valid)} samples to database...'
        res = requests.post(sampleurl,json=valid)
        if res.status_code == 200:
            yield 'Samples saved successfully.'
        else:
            raise RuntimeError(f"Saving error: server respond with {res.status_code}, {res.json()}")
        yield 'Done Saving, return to home page in 2 seconds.'
        time.sleep(2)
        self.returnHomePage()



class LyseToLAMP(Routine):
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
    SampleToLyse,
    LyseToLAMP,
    AddStorageRoutine,
    GetStorageRoutine,
    CreateSample,
    DeleteSample
]