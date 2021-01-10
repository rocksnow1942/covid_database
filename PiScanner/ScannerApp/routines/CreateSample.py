import requests
from . import Routine

class CreateSample(Routine):
    """Scan a rack of samples and store the valid sample tube IDs to database."""
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
