from ..validators import Sample88_2NTC_3PTC_3IAB
from . import Routine


class ValidateSample(Routine):
    """
    This is to validate all samples on the plate matches existing sample barcode in the database.
    currently forced to validate the 88 sample layout.
    """
    _pages=['DTMXPage']
    _titles = ['Place Samples on Reader']
    _msgs = ['Click read to start.']
    btnName = 'Validate'
    def __init__(self, master):
        super().__init__(master)
        self.plate = Sample88_2NTC_3PTC_3IAB(self)
    
    @property
    def totalSampleCount(self):        
        return 96

    
    def nextPage(self):
        self.pages[0].resetState()
        self.showNewPage(cp=0,np=0)

    def validateResult(self, result):
        return self.plate.validateSpecimen(result)


