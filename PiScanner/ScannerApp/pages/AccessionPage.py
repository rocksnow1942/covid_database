import tkinter as tk
from threading import Thread
from ..utils import parseISOTime
import time
from ..firebaseClient import Firebase
from . import BaseViewPage


class AccessionPage(BaseViewPage):
    resultType = dict
    # result key consist of:
    # name: patient name, 
    # extId: for booking, is /booking/asdfasdg
    # sampleId: sample Id linked to the patient.
    def __init__(self, parent, master):
        super().__init__(parent, master)
        self.create_widgets()
        self.fb = Firebase(**self.master.FirebaseConfig)
        self.initKeyboard()
        self.bind("<Button-1>", lambda x:self.focus_set())
        self.lastInputTime = time.time()
        self.patientPageIndex = 0 # the index of currently showing patient search result
        self.patientPage = [] # patient results to show

    def create_widgets(self):
        self._msgVar = tk.StringVar()
        self._msgVar.set('t asdf agsfsd asdf asdf sagas asdg aswe')
        self.nameVar = tk.StringVar()
        self.nameVar.set('testname asodfi')
        self.timeVar = tk.StringVar() 
        self.timeVar.set('2021-01-32 9:12AM')
        self.dobVar = tk.StringVar() # store DOB of user
        self.dobVar.set('1988-12-23')
        self.checkVar = tk.StringVar() # store whether user is checked in
        self.checkVar.set('Already Checked In')
        self.codeVar = tk.StringVar() #store tube barcode        
        self.codeVar.set('1234567899123')
        self.variables = [self.nameVar,self.timeVar,self.dobVar,self.checkVar,self.codeVar]

        font = ('Arial',30)
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial',20))
        self.name = tk.Entry(self, textvariable=self.nameVar, font=font)
        self.time = tk.Label(self, textvariable=self.timeVar, font=font)
        self.dob = tk.Label(self, textvariable=self.dobVar, font=font)
        self.check = tk.Label(self, textvariable=self.checkVar, font=font)
        self.code = tk.Label(self, textvariable=self.codeVar, font=('Arial',30))
        self.home = tk.Button(self,text='Home',font=('Arial',32),command=self.prevPageCb)
        self.save = tk.Button(self,text='Save',font=('Arial',32),command=self.saveCb)        
        self.search = tk.Button(self,text='Search',font=('Arial',32),command=self.searchCb)
        self.prev = tk.Button(self,text='<',font=('Arial',32),command=self.searchPagerCb(-1))
        self.next = tk.Button(self,text='>',font=('Arial',32),command=self.searchPagerCb(1))

        # plate widgets
        Y_DIS = 63
        Y_START = 20
        X = 20        
        tk.Label(self,text='Name:',font=('Arial',30)).place(x=X,y=Y_START)        
        tk.Label(self,text='DoB:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*1)
        tk.Label(self,text='Time:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*2)
        tk.Label(self,text='Check In:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*3)
        tk.Label(self,text='Sample ID:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*4)        
        X+=230
        self.name.place(x=X,y=Y_START,width=500)
        self.dob.place(x=X,y=Y_START+Y_DIS*1)
        self.time.place(x=X,y=Y_START+Y_DIS*2)        
        self.check.place(x=X,y=Y_START+Y_DIS*3)
        self.code.place(x=X,y=Y_START+Y_DIS*4)

        self._msg.place(x=20, y=420, width=760,)
        BY=350
        self.home.place(x=40 , y=BY,  height=60 ,width=130,)
        self.save.place(x=630 , y=BY, height=60, width=130)
        self.search.place(x=335,y=BY, height=60,width=130)
        self.prev.place(x=240,y=BY,height=60,width=60)
        self.next.place(x=500,y=BY,height=60,width=60)

    def searchPagerCb(self,step):
        'generate change result page call back.'
        def cb():
            N = len(self.patientPage)
            nextPage = self.patientPageIndex + step
            if nextPage<0 or nextPage>=N:
                return
            self.patientPageIndex +=step
            self.showPatient(self.patientPage[self.patientPageIndex])
            self.displaymsg(f"Result {self.patientPageIndex+1} / {N}")
        return cb
 
    def scanlistener(self,e):    
        "need to handle the special case in QR code."
        char = e.char
        if time.time() - self.lastInputTime >1:
            # if the last input is more than 1 seconds ago, reset keySequence.
            self.keySequence=[]
        if char=='\r':
            if self.keySequence:
                self.keyboardCb(''.join(self.keySequence))
            self.keySequence=[]            
        else:
            self.keySequence.append(char)
        self.lastInputTime = time.time()
        #return 'break' to stop keyboard event propagation.
        return 'break'

    def showPatient(self,data):
        "show the patient information from data dictionary to display."
        name = data.get('name','No Name!!!')
        dob = data.get('dob','No DoB')
        self.nameVar.set(name)
        self.dobVar.set(dob)
        if data.get('date',None) and data.get('time',None):
            self.timeVar.set( f"{parseISOTime(data['date']).strftime('%Y-%m-%d')} , {data['time']}" )
        else:
            self.timeVar.set('No appointment time found.')
        if data['checkin']:
            self.checkVar.set('Already Check In.')
        else:
            self.checkVar.set("Not Yet.")
        self.result.update(name=name,extId=data.get('docID'))

    def keyboardCb(self,code):
        "call back when a QR code is scanned."                
        def getInfo():            
            # if the code is a booking reservation:
            if code.startswith('/booking'):
                # first reset state.
                self.resetState()
                try:
                    self.displaymsg('Validating with server...','green')
                    res = self.fb.get(f'/booking/info{code}',)
                    if res.status_code == 200:
                        data = res.json()
                        self.showPatient(data)
                        self.displaymsg('Please confirm patient info.','green')                        
                    else:
                        self.error(f"keyboardCb: server response [{res.status_code}], {res.json()}")
                        self.nameVar.set("")
                        self.dobVar.set('')
                        self.timeVar.set('')
                        self.checkVar.set('')                    
                        self.displaymsg(f'Server response code: [{res.status_code}]')
                except Exception as e:
                    self.error(f'keyboarCb: {e}')
                    self.displaymsg('Read QR code error.[100]','red')
            else: # otherwise the code should be tube barcode.
                self.codeVar.set(code)
                self.displaymsg('Sample Id read. Verify before save.')
                self.result['sampleIds'] = [code]
                self.result['company'] = 'online-booking'
        Thread(target=getInfo).start()

    def showPage(self,*_,**__ ):        
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.displaymsg('Scan QR code to start.')
        self.fb.start() # start fetching token.
        

    def closePage(self):
        self.fb.stop()
        self.home['state']='normal'
        self.search['state']='normal'
        self.save['state'] ='normal'
        

    def resetState(self):
        for v in self.variables:
            v.set('')        
        self.result = self.resultType()
        self.patientPage = []
        self.patientPageIndex = 0

        
        
    def searchCb(self):
        self.focus_set()        
        name = self.nameVar.get()
        
        if not name.strip():
            self.displaymsg('Enter name to search.' , 'red')
            return

        def search():
            self.resetState()
            self.displaymsg('Searching name...','green')
            self.disableBtn()
            res = self.fb.post('/booking/query',json={"firstName":name,'lastName':""})
            if res.status_code == 200:
                self.patientPage = res.json()
                self.showPatient(self.patientPage[0])
                N = len(self.patientPage)
                self.displaymsg(f'Found {N} matching results. 1/{N}')
            else:
                self.displaymsg(res.json()['error'],'red')
            self.enableBtn()
        
        Thread(target=search).start()

    def enableBtn(self,):
        self.home['state']='normal'
        self.search['state']='normal'
        self.save['state'] ='normal'
    def disableBtn(self):
        self.home['state'] = 'disabled'
        self.save['state'] ='disabled'
        self.search['state'] ='disabled'

    def saveCb(self):
        self.focus_set()
        def save():
            # save self.result
            if self.result.get('extId',None) == None:
                self.displaymsg('Nothing to save. Scan QR code to start.','red')
            elif self.result.get('sampleIds',None) == None:
                self.displaymsg('Scan sample tube ID before save.','red')            
            elif self.checkVar.get() == 'Already Check In.':
                self.displaymsg('This patient already submitted sample.','red')
            else:
                try:
                    for msg in self.master.currentRoutine.saveResult():
                        self.displaymsg(msg)
                    # check this patient in on firestore so that we know he already submitted sample.
                    time.sleep(0.5)
                    self.displaymsg('Writing back to cloud...')
                    res = self.fb.post('/booking/checkin',json={'docID':self.result['extId']})
                    if res.status_code==200:
                        self.displaymsg('Saved successfully.','green')
                    else:
                        self.displaymsg('Save result to cloud error.')
                        
                    self.resetState()
                except Exception as e:
                    self.error(f"AccessionPage.saveCb error: {e}")
                    self.displaymsg(f'Error in saving: {str(e)[0:40]}','red')
            self.enableBtn()            
        Thread(target=save).start()
        self.displaymsg('Saving results...','green')
        
        self.disableBtn()

