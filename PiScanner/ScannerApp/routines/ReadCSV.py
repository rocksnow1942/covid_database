from . import Routine
from datetime import datetime
import os



class ReadCSV(Routine):
    """
    This routine is to read a plate with barcode,
    then read the sample tubes on the plate,
    the samples read are not verified against anything.
    then save the result to a flat txt file.    
    """
    _pages = ['BarcodePage','DTMXPage','SavePage']
    _msgs = ['Scan barcode on the side of sample plate.',             
             'Click Read to scan sample IDs',             
             'Review the results and click Save']
    btnName = 'To CSV'
    def __init__(self, master):
        super().__init__(master)
        self.plate = None
        self.tubes = []

    def validateResult(self,code):
        pageNbr = self.currentPage
        if pageNbr == 0:
            self.plate = code
            return True, f"Plate ID: {code}", False
        elif pageNbr == 1:
            valid = [self.master.validate(i,codeType='sample') for _,i in code]
            self.tubes = code
            return valid,'Manual check before proceed',True


    def displayResult(self):
        valid = [self.master.validate(i,codeType='sample') for _,i in self.tubes]
        msg = [
            f'Plate ID : {self.plate}',
            f"Total valid samples: {sum(valid)} / {len(self.tubes)}",
            "Make sure valid sample # is correct before save."
        ]
        return '\n'.join(msg)
    def saveResult(self):
        yield 'Saving result to ./export folder...'
        if not os.path.exists('./export'):
            os.mkdir('./export')
        with open(f"./export/{self.plate} {datetime.now().strftime('%Y%m%d_%H%M')}.csv",'wt') as f:
            f.write('Well,ID\n')
            f.write('\n'.join(f"{w},{i}" for w,i in self.tubes ))
        yield 'Results saved.'
        yield from self.goHomeDelay(5)
        
        
