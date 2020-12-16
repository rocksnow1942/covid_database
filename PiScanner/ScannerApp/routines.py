from .utils import warnImplement
import time
from .logger import Logger
import requests
from .validators import selectPlateLayout,n7PlateToRP4Plate

class GetColorMixin:
    def getColorText(self,plate):
        return f'({self.master.plateColor(plate)[0].capitalize()})'*bool(self.master.plateColor(plate)[0])
    def getColor(self,plate):
        return self.master.plateColor(plate)[1].lower()

class Routine(Logger):
    "routine template"
    _pages = []
    _titles = []
    _msgs = []
    _colors = []
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
        self.results = [i.resultType() for i in self.pages]
        self.states = [{} for i in self.pages]
        self.showNewPage(None,0)
        
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
        
    def showNewPage(self,cp=None,np=None):
        "close current page and show next page"
            # if the next page already have result stored, update with current stored result.
        self.currentPage = np
        if cp is not None:
            self.results[cp],self.states[cp] = self.pages[cp].readResultState()
        self.pages[np].setResultState(self.results[np],self.states[np])
        if cp is not None:
            self.pages[cp].closePage()
        kwargs = {i[1:-1]:getattr(self,i)[np] for i in ['_titles','_msgs','_colors'] if getattr(self,i)}
        self.pages[np].showPage(**kwargs)
        
    def validateResult(self,result):
        """
        this method is called by routine's pages when they need to validate result.
        normally return True/False to indicate whether result is valid, 
        a message to display, 
        and whether bypass the error check (for example enable next button).
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
        for i in range(5):
            yield 'not implement saveResult'
            time.sleep(0.5)
        yield from self.goHomeDelay(3)
    
    def goHomeDelay(self,seconds):
        "go back to home page after seconds"
        yield f'Return to home page in {seconds} seconds.'
        for i in range(int(seconds)):
            time.sleep(1)
            yield f'Return in {seconds - i}s'
        yield f'Return Home.'
        self.returnHomePage()

class SampleToLyse(Routine,GetColorMixin):
    _pages = ['BarcodePage','DTMXPage','BarcodePage','SavePage']
    _msgs = ['Scan barcode on the side of sample plate.',
             'Click Read to scan sample IDs',
             'Scan barcode on the side of lyse plate.',
             'Review the results and click Save']
    btnName = 'Sample'
    
    # control filter return true if the sample is a control. x is the 0 based index, posi is from A1-A2...
    
    def __init__(self, master):
        super().__init__(master)
        self.plate = None
    @property
    def _colors(self):
        return ['black','black',self.getColor('lyse'),'black']
    @property
    def _titles(self):
        return ['Scan Sample Plate Barcode',
                'Place Plate on reader',
                f'Scan Lyse Plate Barcode {self.getColorText("lyse")}',
                'Save Result']

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
            return self.plate.validateSpecimen(toValidate)
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
            self.info(f'Saved < {savedcount} > samples to database.')
            yield 'Sample result saved.'
        else:
            raise RuntimeError (f"Saving sample result error: {res.status_code}, {res.json()}")    
        yield from self.goHomeDelay(10)
        
class CreateSample(Routine):
    ""
    _pages = ['DTMXPage','SavePage']
    _titles = ['Place Plate on reader','Save Sample IDs to database']
    _msgs = ['Click Read to scan sample IDs','Review the results and click Save']
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
        yield from self.goHomeDelay(3)

class DeleteSample(Routine):
    ""
    _pages = ['DTMXPage','SavePage']
    _titles = ['Scan Sample Plate barcode','Delete Sample IDs in database']
    _msgs = ['Scan Sample Plate barcode','Review the results and click Save']
    btnName = 'Delete'
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
        yield f'Deleting {len(valid)} samples in database...'
        res = requests.delete(sampleurl,json=valid)
        if res.status_code == 200:
            yield 'Samples successfully deleted.'
            yield str(res.json())
        else:
            raise RuntimeError(f"Saving error: server respond with {res.status_code}, {res.json()}")
        yield from self.goHomeDelay(3)

class LyseToLAMP(Routine,GetColorMixin):
    _pages = ['BarcodePage','BarcodePage','BarcodePage',"SavePage"]    
    _msgs = ['Scan barcode on the side of lyse plate.',
        'Scan barcode on the side of LAMP-N7 plate',
        'Scan barcode on the side of LAMP-RP4 plate',
        'Review results and click save']
    btnName = 'Plate'
    @property
    def _titles(self):
        return [f'Scan Barcode On Lyse Plate {self.getColorText("lyse")}',
        f'Scan Barcode On LAMP-N7 Plate {self.getColorText("lampN7")}',
        f'Scan Barcode On LAMP-RP4 Plate {self.getColorText("lampRP4")}',
        'Save Linked Plates']

    @property
    def _colors(self):
        return [self.getColor('lyse'),self.getColor('lampN7'),self.getColor('lampRP4'),'black']

    def displayResult(self):
        return f"Lyse plate: {self.results[0]} \nLAMP-N7 plate: {self.results[1]}\nLAMP-RP4 plate: {self.results[2]}"

    def saveResult(self):
        lyseId = self.results[0]
        n7Id = self.results[1]
        rp4Id = self.results[2]
        # save reulsts to server here:        
        yield 'Start saving...'
        
        res = requests.put(self.master.URL + '/plates/link',json={'oldId':lyseId,'step':'lamp','newId':n7Id,'companion':rp4Id}) 
        if res.status_code == 200:
            yield 'LAMP - N7 plate updated.'
        else:
            self.error(f'LyseToLAMP.saveResult server response <{res.status_code}>@N7: json: {res.json()}')
            raise RuntimeError(f'Server respond with {res.status_code} when saving LAMP-N7 plate.')
        rp4doc = res.json()
        rp4doc.update(companion=n7Id,plateId=rp4Id,wells=n7PlateToRP4Plate(rp4doc['wells']),layout=rp4doc['layout']+'-RP4Ctrl')
        res = requests.post(self.master.URL+'/plates',json=rp4doc)
        if res.status_code == 200:
            yield 'LAMP - RP4 plate saved.'
        else:
            self.error(f'LyseToLAMP.saveResult server response <{res.status_code}>@RP4: json: {res.json()}')
            raise RuntimeError(f'Server respond with {res.status_code} when saving LAMP-RP4 plate.')
        yield from self.goHomeDelay(3)

    def validationResultParse(self,valid,name):
        if valid is None: # server error
            return False, 'Validation failed, server error.', False
        else:
            return valid, f'{name.capitalize()} plate ID is ' + ('valid' if valid else 'invalid'),False


    def validateResult(self, result):
        page = self.currentPage
        if page == 0:
            valid = self.master.validateInDatabase(result,'lyse','exist')
            return self.validationResultParse(valid,'lyse')
        elif page == 1:
            valid = self.master.validateInDatabase(result,'lampN7','not-exist')
            return self.validationResultParse(valid,'LAMP-N7')
        elif page == 2:
            valid = self.master.validateInDatabase(result,'lampRP4','not-exist')
            return self.validationResultParse(valid,'LAMP-RP4')

class SaveStore(Routine):
    _pages = ['BarcodePage','BarcodePage','SavePage']
    _titles = ['Scan Barcode on Sample Plate','*','Save Plate Storage Location']
    _msgs =['Scan barcode on sample plate.',"*","Review the results then click save."]
    _colors = ['black','red','black']
    btnName = 'Store'
    def __init__(self, master):
        super().__init__(master)
        self.toRemove = None
        self.emptySpot = None
    def validateResult(self, result):
        if self.currentPage == 0:
            
            valid = self.master.validateInDatabase(result,'samplePlate','not-exist')
            if valid is None:
                return False, 'Validation failed, server error.', False
            elif valid:
                # then find an empty spot.
                try:
                    res = requests.get(self.master.URL + '/store/empty')
                    if res.status_code == 200:
                        self.emptySpot = res.json()['location']
                        return True, 'Sample Plate ID valid',False
                    elif res.status_code == 400: # no more empty position
                        res = requests.get(self.master.URL + '/store')
                        if res.status_code == 200:
                            self.toRemove = res.json()[0]['location']
                            return True, 'Sample Plate ID valid',False
                        else:
                            return False, "ID valid, cannot find empty spot", False
                except Exception as e:
                    self.error(f'AddStorageRoutine.validateResult error find empty: {e}')
                    return False, 'Error in looking for empty spot', False
            else:
                return valid, 'Sample plate ID is invalid',False
        elif self.currentPage == 1:
            try:
                res = requests.get(self.master.URL + '/store',json={'plateId':result})
                if res.json() and res.json()[0]['location'] == self.toRemove:
                    return True, 'Discard the sample plate to bioharzard container.',False
                elif res.json():
                    id = res.json()[0]['plateId']
                    loc = res.json()[0]['location']
                    return False, f'Found plate <{id}> @ <{loc}>. Re-check plate location / Re-Scan',False
                else:
                    return False, f"Plate {result} not in database,Re-check with Admin", True
            except Exception as e:
                self.error(f'AddStorageRoutine.validateResult error: {e}')
                return False, f'Error:{e}', False
    def returnHomePage(self):
        self.toRemove = None
        self.emptySpot = None
        return super().returnHomePage()
    def prevPage(self):
        cp = self.currentPage
        if self.toRemove is not None:
            np = self.currentPage - 1
        elif self.emptySpot is not None:
            np = self.currentPage - 2
        else:
            np = cp
        if self.currentPage == 0:
            self.returnHomePage()
            return
        self.showNewPage(cp,np)

    def nextPage(self,):
        cp = self.currentPage
        if self.toRemove is not None:
            np = self.currentPage + 1
        elif self.emptySpot is not None:
            np = self.currentPage + 2
        else:
            np = cp
        self.showNewPage(cp,np)
            
    def showNewPage(self, cp, np):
        self.currentPage = np
        if cp is not None:
            self.results[cp],self.states[cp] = self.pages[cp].readResultState()
        self.pages[np].setResultState(self.results[np],self.states[np])
        if cp is not None:
            self.pages[cp].closePage()
        kwargs = {i[1:-1]:getattr(self,i)[np] for i in ['_titles','_msgs','_colors'] if getattr(self,i)}
        if np == 1: # going to remove page
            kwargs['title'] = f'Remove plate from <{self.toRemove}>'
            kwargs['msg'] = f"Scan the plate removed from {self.toRemove}."
        
        self.pages[np].showPage(**kwargs)

    def displayResult(self):
        if self.emptySpot:
            return f"Place plate at location <{self.emptySpot}>.\nThen click save."
        elif self.toRemove:
            return f"Discard plate at location <{self.toRemove}>.\nPlace new plate at location <{self.toRemove}>.\nThen click save."
        else:
            return  'Unable to find storage location.\nPlease check with administrator.'
    
    def saveResult(self):
        sampleId = self.results[0]
        loc = self.toRemove or self.emptySpot
        if not loc:
            raise RuntimeError(f"Can't store plate <{sampleId}>. No storage location available.")
        yield f'Saving plate {sampleId} to location {loc}...'
        res = requests.put(self.master.URL + '/store',json={'location':loc,'plateId':sampleId,"removePlate":True})
        if res.status_code == 200:
            yield f'Saved plate to location{loc}\nResponse: {res.json()}.'
        else:
            yield "Save plate error."
            raise RuntimeError(f"Save plate failed, server response <{res.status_code}>, json:{res.json()}")
        yield from self.goHomeDelay(3)

class FindStore(Routine):
    _pages = ['BarcodePage','BarcodePage','SavePage']
    btnName = 'Find'
    def __init__(self, master):
        super().__init__(master)
        self.loc = None
        self.plate = None
    def returnHomePage(self):
        self.loc = None
        self.plate = None
        return super().returnHomePage()

    def validateResult(self, result):
        if self.currentPage == 0:            
            res = self.master.validator.samplePlateExist(result)
            if res is None:
                return False, f'Database Server Error.', False
            elif res == False:
                return False, f"Plate {result} not found,Re-check with Admin / Re-enter", False
            else:
                self.plate = result
                self.loc = res
                return True, f'Plate <{result}> found @ <{res}>',False
        elif self.currentPage == 1:            
            if result == self.plate:
                return True, f"Plate <{result}> matches query <{self.plate}>.", False
            else:
                res = self.master.validator.samplePlateExist(result)
                if res is None:
                    return False, f'Database Server Error.', False
                elif res == False:
                    return False, f"Found:<{result}> not in DB, query:<{self.plate}>,Re-check / Re-scan", False
                else:
                    return False, f'Plate <{result}> should be @ <{res}>, Re-Check',False
    @property
    def _msgs(self):
        return ['Scan Plate barcode or enter plate ID to start',
                f'Take plate from <{self.loc}> and Scan to confirm ID',
                f"Confirm Taking Out <{self.plate}> @ <{self.loc}> by click save"]
    @property
    def _titles(self):
        return ['Enter Plate ID to query',
                f'Take Plate <{self.plate}> from <{self.loc}>',
                f"Confirm Take <{self.plate}> from <{self.loc}>"]

    def displayResult(self):
        return f"Taking Out Plate: {self.plate}\nFrom location:{self.loc}"
    
    def saveResult(self):
        loc = self.loc
        if not loc:
            raise RuntimeError('No location provided.')
        yield f"Removing {self.plate} from {loc}..."
        res = requests.put(self.master.URL + '/store',json={'location':loc,'plateID':""})
        if res.status_code == 200:
            yield f"Removed {self.plate} from {loc}."
        else:
            yield "Save result error."
            raise RuntimeError(f'Save results failed server response {res.status_code},json:{res.json()}')
        yield from self.goHomeDelay(3)



Routines = {r.__name__:r for r in [
    SampleToLyse,
    LyseToLAMP,
    FindStore,
    SaveStore,
    CreateSample,
    DeleteSample
]}