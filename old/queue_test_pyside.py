#idle_queue.py

import queue as Queue

#Global queue, import this from anywhere, you will get the same object.
idle_loop = Queue.Queue()

def idle_add(func, *args, **kwargs):
    #use this function to add your callbacks/methods
    def idle():
        func(*args, **kwargs)
        return False
    idle_loop.put(idle)


from PyQt5.QtCore import QThread, QEvent

from PyQt5.QtWidgets import QMainWindow, QApplication


class ThreadDispatcher(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        while True:
            callback = idle_loop.get()
            if callback is None:
                break
            QApplication.postEvent(self.parent, _Event(callback))

    def stop(self):
        idle_loop.put(None)
        self.wait()


class _Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        #thread-safe
        super().__init__(_Event.EVENT_TYPE)
        self.callback = callback



class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        
        #....
        
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        
        self.show()

    def customEvent(self, event):
        #process idle_queue_dispatcher events
        event.callback()


def main():
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    widget = Gui()
 
    app.exec_()
    del app

if __name__ == '__main__':
    main()