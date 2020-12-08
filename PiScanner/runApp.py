from ScannerApp import ScannerApp

app = ScannerApp()
app.protocol('WM_DELETE_WINDOW',app.on_closing)
app.mainloop()
