import time
import sys
import psutil
import subprocess

#
# start by batch file
# @echo off
# set root=C:\Users\aptitude\Anaconda3
# call %root%\Scripts\activate.bat %root%
# C:\Users\aptitude\Anaconda3\pythonw.exe "C:\Users\aptitude\Aptitude-Cloud\R&D\Users\Hui Kang\Scripts\ppt_monitor\PPT_monitor_watcher.py"
#
# To auto start on log on:
# use task schedular

monitor_script = "resultCSVmonitor.py"

def start_script():
    result = subprocess.Popen(
        [sys.executable, monitor_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result


def main():    
    monitorpid = start_script()
    print('started script')
    while 1:
        try:
            pids = [p.pid for p in psutil.process_iter()]
            if monitorpid.pid not in pids:  # restart if process is gone.                
                try:
                    monitorpid = start_script()                  
                except Exception as e:
                    pass
            # check every 600 seconds if the monitor service is running.
            time.sleep(600)         
        except:           
            time.sleep(600)
            continue

if __name__ == '__main__':
    # DEBUG to get more info
    main()

