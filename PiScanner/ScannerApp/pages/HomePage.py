import tkinter as tk
from threading import Thread
import requests,time,json
import time

class HomePage(tk.Frame):
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        self.buttons = []
        self.currentPage = 0
        self.maxPage = len(self.master.enabledRoutine)//4 + bool(len(self.master.enabledRoutine) % 4)
        self.create_widgets()
        Thread(target=self.checkUpdate,daemon=True).start()
    
    def checkUpdate(self):
        'check update every 1 hour'
        githubURL = 'https://raw.githubusercontent.com/rocksnow1942/covid_database/master/package.json'
        while True:
            try:                
                res = requests.get(githubURL)
                ver = json.loads(res.text)['version']
                if ver != self.master.__version__:
                    self.versionVar.set(f'Need update {self.master.__version__} > {ver}')
                else:
                    self.versionVar.set(f'^{self.master.__version__}')
            except:
                self.versionVar.set('Check update error')
            time.sleep(3600)

        
    def create_widgets(self):
        "4 buttons Maximum"
        # rtBtnNames = {r.__name__:r.btnName for r in Routines}
        self.versionVar = tk.StringVar()
        self.versionVar.set(self.master.__version__)
        tk.Label(self,textvariable=self.versionVar,).place(x=780,y=10,anchor='ne')
        tk.Button(self,text='Exit',font=('Arial',35),command=self.master.on_closing).place(
            x=630,y=400,height=50,width=150)

        self.pageVar = tk.StringVar()
        self.pageVar.set(f'1 / {self.maxPage}')
        tk.Label(self,textvariable=self.pageVar,font=('Arial',25)).place(x=350,y=400,width=100,height=50)

        self.prevBtn = tk.Button(self,text='<',font=('Arial',40),command=self.prevPage)
        self.prevBtn.place(x=300,y=400,width=50,height=50)
        self.prevBtn['state'] = 'disabled'

        self.nextBtn = tk.Button(self,text='>',font=('Arial',40),command=self.nextPage)
        self.nextBtn.place(x=450,y=400,width=50,height=50)
        if self.maxPage ==1:
            self.nextBtn['state'] = 'disabled'

        self.serverVar = tk.StringVar()
        
        self.serverStatus = tk.Label(self,textvariable=self.serverVar,font=('Arial',20))
        self.serverStatus.place(x=50,y=400,width=200,height=50)       
        self.showBtnPage(self.currentPage)
        
        Thread(target = self.pollServer,daemon=True).start()
    
    def pollServer(self):
        while True:
            try:
                t0=time.perf_counter()
                res = requests.get(self.master.URL)
                dt = time.perf_counter() - t0
                if res.status_code == 200 and res.json().get('live',None):
                    self.serverVar.set(f'{int(dt*1000)} ms')
                    self.serverStatus.config(fg='green')
                else:
                    self.serverVar.set('Disconnected')
                    self.serverStatus.config(fg='red')
            except:
                self.serverVar.set('Disconnected')
                self.serverStatus.config(fg='red')
            time.sleep(10)

    def showBtnPage(self,n):
        self.pageVar.set(f'{n+1} / {self.maxPage}')
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        for i,rtName in enumerate(self.master.enabledRoutine[n*4:n*4+4]):
            r = i//2
            c = i%2            
            btn = tk.Button(self,text=self.master.routine[rtName].btnName,font=('Arial',55),command=self.master.startRoutineCb(rtName))
            btn.place(x=20 + c*400,y=40+170*r,height=150,width=360)
            self.buttons.append(btn)

    def prevPage(self):
        self.currentPage -= 1
        self.showBtnPage(self.currentPage)
        if self.currentPage==0:
            self.prevBtn['state'] = 'disabled'
        if self.currentPage < self.maxPage -1:
            self.nextBtn['state'] = 'normal'

    def nextPage(self):
        self.currentPage +=1
        self.showBtnPage(self.currentPage)
        if self.currentPage==self.maxPage-1:
            self.nextBtn['state'] = 'disabled'
        if self.currentPage > 0:
            self.prevBtn['state'] = 'normal'
    
    def showPage(self):
        self.tkraise()
        self.focus_set()

