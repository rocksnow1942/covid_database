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

def n7PlateToRP4Plate(wells):
    "convert well types on a N7 plate to RP4 plate"
    for well in wells.values():
        ot = well['type']
        well['type'] = {'N':'R','O':'S','M':'Q','P':'T'}.get(ot,'?')
    return wells

class BarcodeValidator():
    def __init__(self,master):
        self.master = master
        self.config = master.codeValidationRules
        self.URL = master.URL
    
    def validateBarcode(self, code,digits = 10,):
        return len(code) == digits and code.isnumeric()    
    
    def checkSum(self,code,):
        "10 digits and check sum of second digit"
        return self.validateBarcode(code,10) and sum(int(i) for i in code[3:]) == int(code[1:3])

    def __call__(self,code,codeType=None):
        """
        simple local validate
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
        
    def validateInDatabase(self,code,codeType,validationType):
        """
        first validate locally, 
        codeType: same as self.__call__.
        then check in database according to validationType
        validationType:
        exist, not-exist
        if server response error, will return None
        """
        if not self(code,codeType): # if not valid according to local rules:
            return False
        if codeType in ('lyse','lampN7','lampRP4') and validationType=='exist':
            return self.plateExist(code)

        elif codeType in ('lyse','lampN7','lampRP4') and validationType == 'not-exist':
            return self.nonExistConverter(self.plateExist(code))
        
        elif codeType == 'samplePlate' and validationType == 'not-exist':
            return self.nonExistConverter(self.samplePlateExist(code))
    
    def plateExist(self,id):
        'check if a plate exist in plate database'
        try:
            res = requests.get(self.URL+f'/plates/id/{id}')
            if res.status_code == 200:
                return True
            elif res.status_code == 400:
                return False
            else:
                return None
        except Exception as e:
            self.master.error(f'BarcodeValidator.plateExist error <{id}>: {e}')
            return None

    def samplePlateExist(self,id):
        try:
            res = requests.get(self.URL+'/store',json={'plateId':id})
            if res.status_code != 200:
                return None
            if res.json():
                return res.json()[0]['location']
            else:
                return False
        except Exception as e:
            self.master.error(f"BarcodeValidator.samplePlateExist error <{id}>: {e}")
            return None

    def nonExistConverter(self,res):
        "convert an exist answer to nont-exist answer"
        if res is None: return res
        else: return not res


    





class Plate:
    _layout = ""
    def __init__(self,routine) -> None:
        "master is the app."
        self.routine = routine
        self.master = routine.master

    def wellType(self,label,grid=(12,8)):
        "convert label such as A1 to position index,default considering a 96 plate format."
        row = 'ABCDEFGHIJKLMNOPQRST'.index(label[0].upper())
        col = int(label[1:])
        return grid[0]*row + col - 1
        
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
    
    def validateSpecimen(self,toValidate,*args,**kwargs):
        # use a filter to filter out the control positions.
        controlFilter = lambda i:self.wellType(i)!='N'
        toValidateIds = [i[1] for i in toValidate]
        validlist = [True] * len(toValidate)
        duplicates = []
        invalids = []
        # first validate these sample IDs locally.

        for index,id in enumerate(toValidateIds):
            # if a sample is control, don't validate it.
            if controlFilter(toValidate[index][0]): # this gets the label of this position. like A1
                continue
            # if an id is presented more than once, then cause duplication error.
            elif id and toValidateIds.count(id)>1:
                validlist[index] = False
                duplicates.append(toValidate[index])
            # also check if the ID meet requirement for 'sample' type. check <BarcodeValidator> for detailed requirement.
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

            # return the validlist:[True,False...] this is used to render red box indicate valdiation error.
            # msg is a string, will be displayed in the info textbox.
            # False is to say it will not allow bypass, so that the 'Next' button will not be clickable.
            return validlist, '\n'.join(msg),False

        # if local validation passed, need to validate results in server.
        url = self.master.URL+ '/samples'
        try:
            # check if all sample IDs is already presented in database.
            res = requests.get(url,json={'sampleId':{'$in':toValidateIds}})
        except Exception as e:
            res = None
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Validation request failed: {e}')

        if (not res) or res.status_code != 200: #request problem
            # validation failed due to server error
            self.routine.error(f'{self.__class__.__name__}.validateSpecimen: Server respond with <{ res and res.status_code}>.')
            return [False]*len(toValidate),f'Validation Server Error! Response: <{res and res.status_code}>',False
        
        # create a dictionary of {sampleId: storagePlate ID}
        validIds =  { i.get('sampleId'):i.get('sPlate') for i in res.json()}
        
        for index,id in enumerate(toValidateIds):
            if controlFilter(toValidate[index][0]):
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
    def __init__(self, routine) -> None:
        super().__init__(routine)
        self.validlist = [False]*96
    def withinCount(self,label,count):
        "check if a label is within a count from to to bottom, left to right"
        col = int(label[1:])
        row = label[0]
        c = (col-1) * 8 + 'ABCDEFGH'.index(row)
        return c<count

    def validateSpecimen(self,toValidate,totalCount=None,**kwargs):
        controlFilter = lambda i:self.wellType(i)!='N'
        toValidateIds = [i[1] for i in toValidate]
        validlist = [True] * len(toValidate)
        duplicates = [] # this is not actually checking duplicates, 
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
            if not self.withinCount(toValidate[index][0],totalCount):
                # if the sample is out of the total count range,
                continue
            if controlFilter(toValidate[index][0]):
                continue            
            if id in validIds:
                if validIds[id]: # the sample is already in another sample plate
                    duplicates.append(toValidate[index])
            else:
                # use validlist again for store Ids that were not found in database.
                validlist[index] = False
                if toValidate[index][1]: # if the ID is not empty string, append it to invalids.
                    invalids.append(toValidate[index])
        msg = []
        if invalids:
            msg.append("These samples doesn't exist in database:")
            msg.append('\n'.join(str(i) for i in invalids))
            
        if duplicates:
            msg.append('These samples already in another plate:')
            msg.append('\n'.join(str(i) for i in duplicates))
        
        if not msg:
            msg.append(f'{len(toValidateIds)} samples are all valid.')
        
        return validlist,'\n'.join(msg),True

    def compileWells(self,wells):
        """
        input is a list of welllabel and well Id, like [(A1,'123455')]
        return the wells that contain either sample or control.
        i.e. the wells that is True in validlist.
        """
        return { wellname:{'sampleId':id,"type":self.wellType(i,),"raw":0}
                for i,(wellname,id) in enumerate(wells) if self.validlist[i]}
    
    def compileSampleIDs(self,wells):
        "return only the IDs of salvia samples"
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
