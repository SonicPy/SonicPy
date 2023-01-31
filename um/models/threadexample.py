
from PyQt5 import QtWidgets

from PyQt5.QtCore import QThread, pyqtSignal, QObject
import queue 
import time

app = QtWidgets.QApplication([])

class mythread(QThread):

    finished = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.my_queue = queue.Queue()


        

    def set_task(self,  task):
        
        self.my_queue.put(task)

    def run(self):
        self.go= True
       
        # do stuff
        while self.go:
            
            task = self.my_queue.get()
            print('task in queue: ' + str(task))
            
            if 'task_name' in task:

                if task['task_name'] == 'print':
                    #print(task['data'])
                    out = {}
                    out['output'] = task['data']
                    self.finished.emit(out)
                elif task['task_name'] == 'stop':
                    self.go = False
            
            time.sleep(0.05)

        self.finished.emit({'output':'exiting'})

def output_signal_callback(message):
    data = message['output']
    print('output received: '+ data)


my_thread = mythread()

my_thread.finished.connect(output_signal_callback)

my_thread.start()

my_thread.set_task({'task_name': 'print', 'data':'hello'})

my_thread.set_task({'task_name': 'print', 'data':'world'})

my_thread.set_task({'task_name': 'stop'})





app.exec_()