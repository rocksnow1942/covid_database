from .utils import warnImplement
import time
class Routine():
    "routine template"
    _pages = []
    def __init__(self,master):
        self.master = master
        self.pages = [
             self.master.pages[i] for i in self._pages
        ]
        self.results = [None for i in self._pages]
        self.currentPage = 0
    def startRoutine(self):
        "define how to start a routine"
        self.currentPage = 0
        self.results = [None for i in self._pages]
        self.pages[0].showPage()
 
    def returnHomePage(self):
        for p in self.pages:
            p.resetState()
        self.master.showHomePage()

    def prevPage(self):
        if self.currentPage == 0:
            self.returnHomePage()
            return
        self.pages[self.currentPage - 1].setResult(self.results[self.currentPage - 1])
        self.pages[self.currentPage].closePage()
        self.pages[self.currentPage - 1].showPage()
        self.currentPage -= 1
    
    def nextPage(self):
        self.results[self.currentPage] = self.pages[self.currentPage].readResult()
    
        if self.results[self.currentPage+1]:
            # if the next page already have result stored, update with current stored result.
            self.pages[self.currentPage+1].setResult(self.results[self.currentPage+1])
        self.pages[self.currentPage].closePage()
        self.pages[self.currentPage+1].showPage()
        self.currentPage += 1

    def displayResult(self):
        warnImplement('displayResult',self)
        return str(self.results)
    def saveResult(self):
        warnImplement('saveResult',self)
        for i in range(10):
            time.sleep(0.3)
            yield f'saving step {i}...'
        yield 'Done saving, return to main page in 2 seconds'
        time.sleep(2)
        self.returnHomePage()

class SpecimenRoutine(Routine):
    _pages = ['DTMXPage','BarcodePage','SavePage']

    
    