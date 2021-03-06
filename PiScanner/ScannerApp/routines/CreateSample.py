from . import Routine
from datetime import datetime


class CreateSample(Routine):
    """Scan a rack of samples and store the valid sample tube IDs to database."""
    _pages = ['BarcodePage', 'DTMXPage', 'SavePage']
    _titles = ['Scan Reception Barcode',
               'Place Plate on reader', 'Save Sample IDs to database']
    _msgs = ["Scan Reception Barcode", 'Click Read to scan sample IDs',
             'Review the results and click Save']
    btnName = 'Create'
    requireAuthorization = 'reception'
    @property
    def totalSampleCount(self):
        "return totoal exptected sample count"
        return 96

    def validateResult(self, result):
        if self.currentPage == 0:
            res = self.master.db.get('/batch', json={'_id': result})
            if res.status_code == 200:
                return True, 'Batch Reception Barcode Scanned', True
            else:
                return False, 'Batch Reception Barcode is inValid', False
        else:
            wells = result
            self.toUploadSamples = []
            self.toUpdateSamples = []
            validlist = [self.master.validate(
                id, 'sample') for (wn, id) in wells]
            res = self.master.db.get(
                '/samples', json={'sampleId': {'$in': [i[1] for i in wells]}})
            if res.status_code == 200:
                # samples that is not created by batchDownload, this will mean the sample is already preexist in database.
                conflictSample = []
                validexist = []  # sample created by batchDownlaod
                for s in res.json():
                    # if the sample is not create by appCreated, or if the sample already have a well ID,
                    # that means the sample is already scanned and in our system before.
                    # then this sample is going to have conflict.
                    if s.get('meta', {}).get('from', None) == 'appCreated' and (not s.get('sWell', None)):
                        validexist.append(s.get('sampleId'))
                    else:
                        conflictSample.append(s.get('sampleId'))
                for idx, (wn, id) in enumerate(wells):
                    if id in conflictSample:
                        validlist[idx] = False

                msg = f'{sum(validlist)} / {len(validlist)} valid sample IDs found. \n\
    {len(validexist)}  / {len(validlist)} sampleIDs are downloaded from app\n\
    {len(conflictSample)} / {len(validlist)} samples have conflict with existing sampleIDs'

                self.toUploadSamples = [i for i, v in zip(
                    wells, validlist) if (v and (i[1] not in validexist))]
                self.toUpdateSamples = [i for i, v in zip(
                    wells, validlist) if (v and (i[1] in validexist))]
                return validlist, msg, len(conflictSample) == 0
            else:
                return [False]*len(wells), f'Server Response {res.status_code}', False

    def displayResult(self,):
        return f"Total Valid Sample IDs: {len(self.toUploadSamples)}."

    def saveResult(self):
        username = self.master.currentUser
        receptionCode = self.results[0]
        # don't need 'handler':username in the meta, because when posting, 
        # handler is set by the request header. 
        meta = {"receptionBatchId": receptionCode,}
        # valid = self.validatedWells
        valid = [{'sampleId': id, 'receivedAt': datetime.now().isoformat(
        ), 'sWell': wn, 'meta': meta} for (wn, id) in self.toUploadSamples]
        update = [{'sampleId': id, 'receivedAt': datetime.now().isoformat(
        ), 'sWell': wn, 'meta.receptionBatchId': receptionCode, 'meta.handler':username} for (wn, id) in self.toUpdateSamples]
        yield f'Saving {len(valid)} samples to database...'

        # update the count of reception in this batch
        res = self.master.db.post(
            '/batch/addsample', json={'id': receptionCode, "count": len(valid) + len(update)})
        if res.status_code == 200:
            yield f"Successfully updated batch reception."
        else:
            raise RuntimeError(
                f'Update batch reception error, response: {res.status_code},{res.json()}')

        if valid:
            res = self.master.db.post('/samples', json=valid)
            if res.status_code == 200:
                yield f'Successfully created {len(valid)} new samples.'
            else:
                raise RuntimeError(
                    f"Create Sample error: server respond with {res.status_code}, {res.json()}")

        if update:
            res = self.master.db.put('/samples', json=update)
            if res.status_code == 200:
                yield f'Successfully updated {len(update)} samples.'
            else:
                raise RuntimeError(
                    f"Update Sample error: server respond with {res.status_code}, {res.json()}")

        yield from self.goHomeDelay(3)
