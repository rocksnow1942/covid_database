 
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
            self.info(f'Saved patient {result.get("name","no name")} - {result["extId"]} to database.')
            yield 'Patient ID saved successfully.'
        else:
            self.error(f'{res.status_code},PatientAccession.saveResult Patient ID server response  json:{res.json()}')
            raise RuntimeError('Patient ID saving error')      
        yield 'Saving sample ID to database...'
        sampleId = result['sampleIds'][0]
        # save one sample to samples collection
        res = requests.post(self.master.URL+'/samples',
            json=[{'sampleId':sampleId,"extId":result['extId'], "meta":{ "name": result['name'] } }])
        if res.status_code == 200:
            self.info(f'Saved Sample {sampleId} to database.')
            yield 'Sample ID saved successfully.'
        else:
            self.error(f'{res.status_code}, PatientAccession.saveResult  Sample ID server response, json:{res.json()}')
            raise RuntimeError('Sample ID saving error')
        

    def validateResult(self,code):
        "validate the barcode code scanned."
        valid = self.master.validator(code,'sample')
        if not valid:
            return False, 'Invalid sample barcode, rescan.'
        notExist = self.master.validateInDatabase(code,'sample','not-exist')
        if notExist:
            return True,''
        elif notExist is None:
            return False,"Mongo Server is down. Can't validate barcode."
        else:
            return False, "Barcode already exists mongo server."

