import keyboard
import tkinter as tk
from threading import Thread
# https://pypi.org/project/keyboard/

def get_next_scan():
    "return 10 digits barcode or "
    # scan = []
    # laste = None
    # while True:
    #     e = keyboard.read_key()
    #     if e == laste:
    #         laste = None
    #         if e in '0123456789':
    #             scan.append(e)
    #         elif e=='enter':
    #             return ''.join(scan)
    #         else:
    #             scan = []
    #     else:
    #         laste = e
        
        
    events = keyboard.record(until='enter')
    barcode = list(keyboard.get_typed_strings(events))[0]
    return barcode
    # if len(barcode)==10 and barcode.isnumeric():
    #     return barcode
    # else:
    #     return None
    
    

class Scaner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scanner App')        
        self.geometry('800x480+0+0')    
        self.create_widgets()    
        Thread(target=self.scanlistener,daemon=True).start()
        
        
    def create_widgets(self):
        tk.Label(text='First Scan:',font=('Arial',40)).place(anchor='ne',x=390,y=20)
        #grid(column=0,row=0,sticky='e',padx=(40,10),pady=(55,50))
        
        self.scanVar1 = tk.StringVar()
        # self.scanVar1.set('1234567890')
        
        self.scan1 = tk.Label(textvariable=self.scanVar1,font=('Arial',40))
        self.scan1.place(x=410,y=20)#grid(column=1,row=0,)
        
        tk.Label(text='Second Scan:',font=('Arial',40)).place(anchor='ne',x=390,y=110)
        #.grid(column=0,row=1,sticky='e',padx=(40,10),pady=(55,50))
        self.scanVar2 = tk.StringVar()
        # self.scanVar2.set('1234567890')
        self.scan2 = tk.Label(textvariable=self.scanVar2,font=('Arial',40))
        self.scan2.place(x=410,y=110)#.grid(column=1,row=1,)
        
        tk.Button(text='Confirm',font=('Arial',60),command=self.confirm).place(x=20,y=210,height=150,width=360)#grid(column=0,row=2,sticky='n',pady=(55,50))
        tk.Button(text='Cancel',font=('Arial',60),command=self.cancel).place(x=420,y=210,height=150,width=360)#grid(column=1,row=2,sticky='n',padx=(50,20),pady=(55,50))
         
        self.msgVar = tk.StringVar()
        self.msg = tk.Label(textvariable=self.msgVar,font=('Arial',30))
        # self.msgVar.set('Confirm/Cancel before new scan')
        self.msg.place(x=50,y=380)#grid(column=0,row=3,columnspan=2)
         
    def displaymsg(self,msg,color='black'):
        self.msgVar.set(msg)
        if color:
            self.msg.config(fg=color)
    def scanlistener(self):
        while True:            
            res = get_next_scan()
            if len(res)==10 and res.isnumeric():
                self.displayScan(res)
            else:
                
                self.displaymsg(f"Unrecoginzed: {res}",'red')

    def displayScan(self,code):
        if code == self.scanVar1.get():
            self.displaymsg('Same code!','red')
            self.scan1.config(bg='red')
        elif not self.scanVar1.get():
            self.scanVar1.set(code)
            self.scan1.config(bg='green',fg='white')
        elif not self.scanVar2.get():
            self.scanVar2.set(code)
            self.scan2.config(bg='green',fg='white')
        else:
            self.displaymsg('Confirm/Cancel before new scan.','red')

    def confirm(self):
        code1 = self.scanVar1.get()
        code2 = self.scanVar2.get()
        if code1 and code2:
            self.displaymsg(f'Link {code1} to {code2}','green')
            self.scanVar1.set('')
            self.scanVar2.set('')
    
    def cancel(self):
        self.scanVar1.set('')
        self.scanVar2.set('')
        self.scan1.config(bg='white')
        self.scan2.config(bg='white')
        self.displaymsg('','white')

    def on_closing(self):
        print('exit...')
        self.destroy()

if __name__ == '__main__':
    app = Scaner()
    app.protocol('WM_DELETE_WINDOW',app.on_closing)
    app.mainloop()