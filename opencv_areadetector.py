from PyQt5 import QtCore, QtWidgets, uic, QtGui
import sys 
import cv2 
import numpy as np 
#import threading 
import time 
#import Queue 

import sys, platform

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QLabel, QSizePolicy, QApplication 
from PyQt5.QtGui import QPixmap, QImage      
from PyQt5.QtCore import Qt

form_class = uic.loadUiType("widgets/simple.ui")[0]

class OwnImageWidget(QtWidgets.QWidget): 
    def __init__(self, parent=None): 
        super().__init__(parent) 
        self.image = None   
        
    def setImage(self, image): 
        self.image = image 
        sz = image.size() 
        self.setMinimumSize(sz) 
        self.update()   
    def paintEvent(self, event): 
        qp = QtGui.QPainter() 
        qp.begin(self) 
        if self.image: 
            qp.drawImage(QtCore.QPoint(0, 0), self.image) 
        qp.end() 



_platform = platform.system()
Theme = 1

class MyWindowClass(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        
        self.initUI()
        

        self.capture_thread = myThread(self)   

        self.show()  
        
        
        self.capture_thread.callbackSignal.connect(self.update_frame)
        self.capture_thread.start()
        
    def initUI(self):                                                                                                                                                                                          
        self.setGeometry(10,10,640, 400)                                                                                                                                                                       

        self.pixmap_label = QLabel()                                                                                                                                                                                
        self.pixmap_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)                                                                                                                                   
        self.pixmap_label.resize(640,400)                                                                                                                                                                           
        self.pixmap_label.setAlignment(Qt.AlignCenter)                                                                                                                                                              

                                                                                                                                                                                

        self.setCentralWidget(self.pixmap_label)                                                                                                                                                                    
        self.show()     


    def start_clicked(self):
        
        self.capture_thread.start()
        self.startButton.setEnabled(False)
        self.startButton.setText('Starting...')


    def update_frame(self, q):
        
        
        img = q['data']

        img_colors, img_width, img_height = img.shape
        
        im_np = img.astype(np.dtype('int8'))
        im_np = np.transpose(im_np, (0,1,2)).copy() 
        #im_np_cpy = np.copy(im_np) 
        shape = im_np.shape
        #cv2.cvtColor(im_np,cv2.c)
        qimage = QImage(im_np, im_np.shape[0], im_np.shape[1], QImage.Format_RGB888)  
        pixmap = QPixmap(qimage)                                                                                                                                                                               
        pixmap = pixmap.scaled(1800,1000, Qt.KeepAspectRatio)      
                                                                                                                                                  
        self.pixmap_label.setPixmap(pixmap)         


    def closeEvent(self, event):
        self.capture_thread.stop()

import epics
import time
class myThread(QThread):
    callbackSignal = pyqtSignal(dict)  
    def __init__(self, parent):
        super().__init__(parent=parent)  
        self.settings = {}
        self.go = False
        
        self.pvname = '16AVT2:image1:ArrayData'
        self.img_pv  = epics.PV(self.pvname)

        
        self.make_connections()

    def make_connections(self):
        pass

    def set_settings(self, settings):
        self.settings = settings
    
    def run(self):
        self.go = True
        d = {}
        while self.go:
            raw_image = self.img_pv.get()
            im = raw_image.reshape((1936,1216, 3))
            
            
            d['data']=im
            self.callbackSignal.emit(d)
            time.sleep(0.04)
    
    def stop(self):
        #print('stopping')
        self.go = 0   

def main():
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    controller = MyWindowClass()
    

    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.display_window
        
    
    app.exec_()
    del app

if __name__ == '__main__':
    
    main()