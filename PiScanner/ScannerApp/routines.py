

class SpecimenRoutine():
    _pages = ['DTMXPage','DTMXPage','SavePage']
    def __init__(self,master):
        self.master = master
        self.pages = [
             self.master.pages[i] for i in self._pages
        ]
        self.results = [None for i in self._pages]
        self.currentPage = 0

    def startRoutine(self):
        "start"
        self.currentPage = 0
        self.results = [None for i in self._pages]
        self.pages[0].showPage()

    def resetAllPages(self):
        'reset all pages of this routine.'
        for p in self.pages:
            p.resetState()

    def prevPage(self):
        print('calling prevPage :', self.currentPage)
        if self.currentPage == 0:
            self.resetAllPages()
            self.master.showHomePage()
            return 
        self.pages[self.currentPage - 1].setResult(self.results[self.currentPage - 1])
        self.pages[self.currentPage - 1].showPage()
        self.currentPage -= 1

    def nextPage(self):
        print('calling nextPage :', self.currentPage)
        self.results[self.currentPage] = self.pages[self.currentPage].readResult()
        if self.results[self.currentPage+1]:
            self.pages[self.currentPage+1].setResult(self.results[self.currentPage+1])
        self.pages[self.currentPage+1].showPage()
        self.currentPage += 1
    
    