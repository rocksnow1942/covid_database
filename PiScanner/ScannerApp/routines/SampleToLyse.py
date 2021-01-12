import requests
from ..validators import selectPlateLayout,VariableSample_2NTC_3PTC_3IAB
from . import Routine,GetColorMixin

class SampleToLyse(Routine,GetColorMixin):
    """
    this routine is for transfer samples from storage rack to lyse plate.
    This routine will first scan barcode on storage rack,
    Then scan tube datamatrix on sample tubes.
    Then scan barcode on the lyse plate.
    The samples in database will update with storage rack barcode,
    The lyse plate layout will be created.
    """
    _pages = ['BarcodePage','NumberInputPage','DTMXPage','BarcodePage','SavePage']
    _msgs = ['Scan barcode on the side of sample plate.',
             'Enter how many patient samples on the plate.',
             'Click Read to scan sample IDs',
             'Scan barcode on the side of lyse plate.',
             'Review the results and click Save']
    btnName = 'Sample'
    
    # control filter return true if the sample is a control. x is the 0 based index, posi is from A1-A2...
    
    def __init__(self, master):
        super().__init__(master)
        self.plate = None
    @property
    def totalSampleCount(self):
        "return totoal sample count if the sample plate is variable sample plate."
        if isinstance(self.plate,VariableSample_2NTC_3PTC_3IAB):
            return self.pages[1].inputValue
        else:
            return 88

    @property
    def _colors(self):
        return ['black','green','black',self.getColor('lyse'),'black']
    @property
    def _titles(self):
        return ['Scan Sample Plate Barcode',
                'Enter Patient Sample Number',
                'Place Plate on reader',
                f'Scan Lyse Plate Barcode {self.getColorText("lyse")}',
                'Save Result']

    def prevPage(self):
        if not isinstance(self.plate,VariableSample_2NTC_3PTC_3IAB):
            # need to skip the page number 1, which is the number input page.            
            if self.currentPage == 2:
                cp = self.currentPage 
                self.results[cp],self.states[cp] = self.pages[cp].readResultState()
                self.currentPage-=1
        super().prevPage()            
        
    def nextPage(self):
        if not isinstance(self.plate,VariableSample_2NTC_3PTC_3IAB):
            # need to skip the page number 1, which is the number input page.
            if self.currentPage == 0:
                cp = self.currentPage 
                self.results[cp],self.states[cp] = self.pages[cp].readResultState()
                self.currentPage += 1                
        super().nextPage()

    def validateResult(self,code,):
        "provide feedback to each step's scan results"
        pageNbr = self.currentPage
        # page = self.pages[pageNbr]
        if pageNbr == 0:
            plate = selectPlateLayout(self.master.validate(code,'samplePlate') and code)
            if plate:
                self.plate = plate(self)
                return True, f"Plate ID valid. Layout: {plate.__name__}",False
            else:
                self.plate = None
                return False, f"Plate ID < {code} > is invalid.", False
        elif pageNbr == 2:
            return self.validateSpecimen(code)
        elif pageNbr == 3:
            valid = self.master.validate(code,'lyse')
            return valid, 'Lyse plate ID valid.' if valid else 'Invalid Lyse plate barcode.', False
    def returnHomePage(self):
        self.plate = None
        return super().returnHomePage()
        
    def displayResult(self):
        sPlate = self.results[0]
        lp = self.results[3]
        total = self.plate.totalSample
        msg = [f"Specimen plate ID: {sPlate}.",f"Lysis plate ID: {lp}",f"Total patient sample: {total}."]
        return '\n'.join(msg)

    def validateSpecimen(self,toValidate):
        # use validator on selected plate to validate the datamatrix result.
        if self.plate:
            return self.plate.validateSpecimen(toValidate,self.totalSampleCount)
        else:
            return [False]*len(toValidate),'Read Sample Plate ID first.', False

    def compileResult(self):
        "combine the result to json."
        sPlate = self.results[0]
        wells = self.results[2]
        lp = self.results[3]
        
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
            self.info(f'Saved < {savedcount} > samples to database.')
            yield 'Sample result saved.'
        else:
            raise RuntimeError (f"Saving sample result error: {res.status_code}, {res.json()}")    
        yield from self.goHomeDelay(10)
        