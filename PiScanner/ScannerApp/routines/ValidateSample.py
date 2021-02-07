from ..utils.validators import Sample88_2NTC_3PTC_3IAB
from . import Routine


class ValidateSample(Routine):
    """
    This is to validate all samples on the plate matches existing sample barcode in the database.
    currently forced to validate the 88 sample layout.
    """
    _pages = ['BarcodePage', 'DTMXPage']
    _titles = ['Scan plate barcode', 'Place Samples on Reader']
    _msgs = ['Scan barcode first', 'Click read to start.']
    btnName = 'Validate'

    def __init__(self, master):
        super().__init__(master)
        self.plate = Sample88_2NTC_3PTC_3IAB(self)

    @property
    def totalSampleCount(self):
        return 96

    def nextPage(self):
        if self.currentPage == 0:
            return super().nextPage()
        else:
            self.pages[1].resetState()
            self.showNewPage(cp=1, np=1)

    def validateResult(self, result):
        validlist = [self.master.validate(id, 'sample') for (wn, id) in result]
        if not all(validlist):
            return validlist, 'Not all barcodes read. Keep reading plate.', False
        wells = [i[1] for i in result]
        res = self.master.db.get('/samples', json={'sampleId': {'$in': wells}})
        plateID = self.results[0]
        wellLabels = ['Barcode Read ERROR. Mark Down Codes']
        if res.status_code == 200:
            plateIds = {}
            for s in res.json():
                plateIds[s['sampleId']] = s['sPlate']
            for idx, (wn, id) in enumerate(result):
                serverID = plateIds.get(id, None)
                if serverID != plateID:
                    validlist[idx] = False
                    wellLabels.append(f"Wrong {wn} = {id}")
            if all(validlist):
                return validlist, 'All barcodes are valid.', True
            else:

                return validlist, '\n'.join(wellLabels), True
        else:
            return [False]*len(wells), f'Server Response {res.status_code}', False
