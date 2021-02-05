import requests
from . import Routine

class CreateSample(Routine):
    """Scan a rack of samples and store the valid sample tube IDs to database."""
    _pages = ['DTMXPage','SavePage']
    _titles = ['Place Plate on reader','Save Sample IDs to database']
    _msgs = ['Click Read to scan sample IDs','Review the results and click Save']
    btnName = 'Create'
    requireAuthorization = 'reception'
    @property
    def totalSampleCount(self):
        "return totoal exptected sample count"        
        return 96
    
    def validateResult(self, wells):
        self.toUploadSamples = []
        validlist = [self.master.validate(id,'sample') for (wn,id) in wells]
        res = self.master.db.get('/samples',json={'sampleId':{'$in':[i[1] for i in wells]}})
       

        if res.status_code == 200:
            conflictSample = [] # samples that is not created by batchDownload, this will mean the sample is already preexist in database.
            validexist = [] # sample created by batchDownlaod 
            for s in res.json():
                if s.get('meta',{}).get('from',None) == 'batchDownload' and (not s.get('sPlate',None)):
                    validexist.append(s.get('sampleId'))
                    
                else:
                    conflictSample.append(s.get('sampleId'))
            for idx , (wn,id) in wells:
                if id in conflictSample:
                    validlist[idx] = False
                  
            msg = f'{sum(validlist)} / {len(validlist)} valid sample IDs found. \n\
{len(validlist)}  / {len(validlist)} sampleIDs are downloaded from app\n\
{len(conflictSample)} / {len(validlist)} samples have conflict with existing sampleIDs',                
        
            self.toUploadSamples = [i for i,v in zip(wells,validlist) if (v and (i[1] not in validexist))]
            return validlist, msg ,len(conflictSample)==0
        else:
            return [False]*len(wells),f'Server Response {res.status_code}',False
        
        
    
    def displayResult(self,): 
        return f"Total Valid Sample IDs: {len(self.validatedWells)}."

    def saveResult(self):
        
        # valid = self.validatedWells
        valid = [{'sampleId':id} for (wn,id) in self.toUploadSamples]
        yield f'Saving {len(valid)} samples to database...'
        

        res = self.master.db.post('/samples',json=valid)
        if res.status_code == 200:
            yield 'Samples saved successfully.'
        else:
            raise RuntimeError(f"Saving error: server respond with {res.status_code}, {res.json()}")
        yield from self.goHomeDelay(3)
