import requests


    
    

def wellTypeDecode(l):
    # layoutmap encoding:
    # N-> ukn-N7, R-> ukn-RP4, 
    # O-> N7 NTC, S-> RP4 NTC, 
    # M-> N7 PTC, Q-> RP4 PTC, 
    # P-> N7 IAB, T-> RP4 IAB
    return {
        'N':'ukn-N7','O':'ntc-N7',
        'P': 'ptc-N7', 'Q':'iab-N7',
        'R':'ukn-RP4','S':'ntc-RP4',
        'T':'ptc-RP4','U':'iab-RP4'
    }[l]


class BarcodeValidator():
    def __init__(self,master):
        self.master = master
        self.config = master.config['codeValidation']
    
    def validateBarcode(self, code,digits = 10,):
        return len(code) == digits and code.isnumeric()    
    
    def checkSum(self,code,):
        "10 digits and check sum of second digit"
        return self.validateBarcode(code,10) and sum(int(i) for i in code[2:]) % 9 == int(code[1])

    def __call__(self,code,codeType=None):
        """
        codeType:
        sample: data matrix code for salvia collection tube
        samplePlate: plate for store saliva sample
        lyse: plate for lyse saliva sample.
        lampN7: plate for lamp reaction N7 primer
        lampRP4: plate for lamp reaction RP4 primer
        """
        if codeType=='sample':
            return self.validateBarcode(code,self.config['sampleCodeDigits'])
        elif codeType == 'samplePlate':
            return self.checkSum(code) and code[0] in self.config['samplePlateFirstDigit']
        elif codeType == 'lyse':
            return self.checkSum(code) and code [0] in self.config['lysePlateFirstDigit']
        elif codeType == 'lampN7':
            return self.checkSum(code) and code [0] in self.config['lampN7PlateFirstDigit']
        elif codeType == 'lampRP4':
            return self.checkSum(code) and code [0] in self.config['lampRP4PlateFirstDigit']
        return False


class Plate:
    _layout = ""
    def __init__(self,routine) -> None:
        "master is the app."
        self.routine = routine
        self.master = routine.master

    def wellType(self,idx):
        return self._layout[idx]

class Sample88_2NTC_3PTC_3IAB(Plate):
    _layout="""\
NNNNNNNNNNNO\
NNNNNNNNNNNO\
NNNNNNNNNNNP\
NNNNNNNNNNNP\
NNNNNNNNNNNP\
NNNNNNNNNNNQ\
NNNNNNNNNNNQ\
NNNNNNNNNNNQ\
"""
    
    def validateSpecimen(self,toValidate):
        controlFilter = lambda i:self.wellType(i)!='N'
        toValidateIds = [i[1] for i in toValidate]
        validlist = [True] * len(toValidate)
        duplicates = []
        invalids = []
        for index,id in enumerate(toValidateIds):
            if controlFilter(index):
                continue
            elif id and toValidateIds.count(id)>1:
                validlist[index] = False
                duplicates.append(toValidate[index])
            elif not self.master.validate(id,'sample'):
                validlist[index] = False
                invalids.append(toValidate[index])
        
        if not all(validlist):
            # not all valid by local criteria
            msg = []
            if duplicates:
                msg.append('Found duplicate IDs:')
                msg.append('\n'.join(str(i) for i in duplicates))
            if invalids:
                msg.append('Found invalid IDs:')
                msg.append('\n'.join(str(i) for i in invalids))
            return validlist, '\n'.join(msg),False

        url = self.master.URL+ '/samples'
        try:
            res = requests.get(url,json={'sampleId':{'$in':toValidateIds}})
        except Exception as e:
            res = None
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Validation request failed: {e}')

        if (not res) or res.status_code != 200: #request problem
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Server respond with <{ res and res.status_code}>.')
            return [False]*len(toValidate),'Validation Server Error!',False
        validIds =  { i.get('sampleId'):i.get('sPlate') for i in res.json()}
        
        for index,id in enumerate(toValidateIds):
            if controlFilter(index):
                continue
            if id in validIds:
                if validIds[id]: # the sample is already in another sample well
                    duplicates.append(toValidate[index])
            else:
                # use validlist again for store Ids that were not found in database.
                validlist[index] = False
                invalids.append(toValidate[index])
        msg = []
        if duplicates:
            msg.append('These samples already in another plate:')
            msg.append('\n'.join(str(i) for i in duplicates))
        if invalids:
            msg.append("These samples doesn't exist in database:")
            msg.append('\n'.join(str(i) for i in invalids))
        if not msg:
            msg.append(f'{len(toValidateIds)} samples are all valid.')
        return validlist,'\n'.join(msg),False

    def compileWells(self,wells):
        return { wellname:{'sampleId':id,"type":self.wellType(i,),"raw":0}
                for i,(wellname,id) in enumerate(wells)}
    def compileSampleIDs(self,wells):
        return [(well,id) for i,(well,id) in enumerate(wells) if self.wellType(i)=='N']
    
    @property
    def totalSample(self,):
        "return the patient sample count on the plate"
        return 88

class VariableSample_2NTC_3PTC_3IAB(Plate):
    _layout="""\
NNNNNNNNNNNO\
NNNNNNNNNNNO\
NNNNNNNNNNNP\
NNNNNNNNNNNP\
NNNNNNNNNNNP\
NNNNNNNNNNNQ\
NNNNNNNNNNNQ\
NNNNNNNNNNNQ\
"""
    def validateSpecimen(self,toValidate):
        controlFilter = lambda i:self.wellType(i)!='N'
        toValidateIds = [i[1] for i in toValidate]
        validlist = [True] * len(toValidate)
        duplicates = []
        invalids = []
        # remember the validlist so that only compile valid wells.
        self.validlist = validlist

        url = self.master.URL+ '/samples'
        try:
            res = requests.get(url,json={'sampleId':{'$in':toValidateIds}})
        except Exception as e:
            res = None
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Validation request failed: {e}')

        if (not res) or res.status_code != 200: #request problem
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Server respond with <{ res and res.status_code}>.')
            return [False]*len(toValidate),'Validation Server Error!',True
        validIds =  { i.get('sampleId'):i.get('sPlate') for i in res.json()}
        
        for index,id in enumerate(toValidateIds):
            if controlFilter(index):
                continue
            if id in validIds:
                if validIds[id]: # the sample is already in another sample well
                    duplicates.append(toValidate[index])
            else:
                # use validlist again for store Ids that were not found in database.
                validlist[index] = False
                invalids.append(toValidate[index])
        msg = []
        if duplicates:
            msg.append('These samples already in another plate:')
            msg.append('\n'.join(str(i) for i in duplicates))
        if invalids:
            msg.append("These samples doesn't exist in database:")
            msg.append('\n'.join(str(i) for i in invalids))
        if not msg:
            msg.append(f'{len(toValidateIds)} samples are all valid.')
        
        return validlist,'\n'.join(msg),True

    def compileWells(self,wells):
        "input is a list of welllabel and well Id, like [(A1,'123455')]"
        return { wellname:{'sampleId':id,"type":self.wellType(i,),"raw":0}
                for i,(wellname,id) in enumerate(wells) if self.validlist[i]}
    
    def compileSampleIDs(self,wells):
        return [(well,id) for i,(well,id) in enumerate(wells) if (self.wellType(i)=='N' and self.validlist[i])]
        
    @property
    def totalSample(self,):
        "return the patient sample count on the plate"
        return sum(self.validlist) - 8



def selectPlateLayout(plateId):
    "select plate layout according to first digits of plateId"
    return plateId and {
        "0": Sample88_2NTC_3PTC_3IAB,
        "1": VariableSample_2NTC_3PTC_3IAB
    }.get(plateId[0],None)
