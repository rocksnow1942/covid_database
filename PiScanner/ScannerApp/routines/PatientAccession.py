import time
from . import Routine
import requests


class PatientAccession(Routine):
    _pages =['AccessionPage']
    _titles =['Scan QR Code']
    btnName='Accession'

    def saveResult(self):
        result = self.pages[0].result
        yield 'Saving patient ID to databse...'
        res = requests.post(self.master.URL+'/patients',json=[result])
        if res.status_code == 200:
            yield 'Patient ID saved successfully.'
        else:
            self.error(f'PatientAccession.saveResult Patient ID server response {res.status_code}, json:{res.json()}')
            raise RuntimeError('Patient ID saving error')
        time.sleep(0.5)
        yield 'Saving sample ID to database...'
        sampleId = result['sampleIds'][0]
        res = requests.post(self.master.URL+'/samples',json=[{'sampleId':sampleId}])
        if res.status_code == 200:
            yield 'Sample ID saved successfully.'
        else:
            self.error(f'PatientAccession.saveResult  Sample ID server response {res.status_code}, json:{res.json()}')
            raise RuntimeError('Sample ID saving error')
        

