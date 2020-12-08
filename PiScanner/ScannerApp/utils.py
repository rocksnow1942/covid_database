def validateBarcode(code,sampleType):
    """
    to validate a barcode if its right format
    1. have check sum for one digit
    2. one digit indicate what type of plate it is.
    3. specimen barcode validate against all submitted samples list
    4. for plate to plate, if a code already exist in date base,
       then it should be the from plate.
    5. special code for control samples on the speciment plate.    

    sampleType:
    'plate'
    'specimen'
    """
    


    return len(code) == 10 and code.isnumeric()


def indexToGridName(index,grid=(12,8),direction='top'):
    "convert 0-95 index to A1-H12,"
    rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:grid[1]]
    rowIndex = rowIndex if direction == 'top' else rowIndex[::-1]
    row = index//grid[0] + 1
    col = index - (row-1) * grid[0] + 1
    rowM = rowIndex[row-1]
    return f"{rowM}{col}"


class PageMixin():
    def displaymsg(self, msg, color='black'):
        self.msgVar.set(msg)
        if color:
            self.msg.config(fg=color)
    
    def initKeyboard(self):
        self.bind("<Key>",self.scanlistener)
        self.keySequence = []

    def scanlistener(self,e):       
        char = e.char
        if char.isalnum():
            self.keySequence.append(char)
        else:
            if self.keySequence:
                self.keyboardCb(''.join(self.keySequence))
            self.keySequence=[]
        #return 'break' to stop keyboard event propagation.
        return 'break'