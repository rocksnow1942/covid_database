from .utils import warnImplement
import time
from .utils import validateBarcode

class Routine():
    "routine template"
    _pages = []
    _titles = []
    _msgs = []
    def __init__(self,master):
        self.master = master
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
    _pages = ['DTMXPage','BarcodePage','SavePage']
    _titles = ['dtmx page','barcoe page','save result']
    _msgs = ['scan barcoe','scan barcode','save result']
    
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
    _titles = ['barcoe page','barcoe page','save result']
    _msgs = ['scan barcoe','scan barcode','save result']
    def validateResult(self, result):
        return super().validateResult(result)
    


Routines = {
    'Specimen': SpecimenRoutine,
    'Plate':PlateLinkRoutine,
}