import imp
import sys

from PyQt5 import QtWidgets, QtCore



class FileViewWidget(QtWidgets.QWidget):

    file_selected_signal = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.hlay = QtWidgets.QVBoxLayout(self)
        '''self.treeview = QtWidgets.QTreeView()'''

        self.open_btn = QtWidgets.QPushButton('Open folder')
        self.hlay.addWidget(self.open_btn)
        self.listview = QtWidgets.QListView()
        '''hlay.addWidget(self.treeview)'''
        self.hlay.addWidget(self.listview)

        path = QtCore.QDir.homePath()

        '''self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setRootPath(QtCore.QDir.rootPath())
        self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)'''
        

        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |  QtCore.QDir.Files)

        self.filters = ["*.tif", '*.tiff', "*.bmp", "*.png", "*.jpg"]
        self.fileModel.setNameFilters(self.filters)
        

        '''self.treeview.setModel(self.dirModel)
        for i in  range( self.dirModel.columnCount()-1):
            self.treeview.hideColumn(i +1)'''
        self.listview.setModel(self.fileModel)

        '''self.treeview.setRootIndex(self.dirModel.index(path))'''
        self.listview.setRootIndex(self.fileModel.index(path))

        self.open_btn.clicked.connect(self.on_clicked)
        self.listview.clicked.connect(self.on_selection_changed)

    def on_clicked(self, index):

        path = QtWidgets.QFileDialog.getExistingDirectory(self, caption='Select US folder',
                                                     directory='')
        if len(path):
            self.listview.setRootIndex(self.fileModel.setRootPath(path))

    def on_selection_changed(self, index):

        path = self.fileModel.fileInfo(index).absoluteFilePath()
        if '.'in path:
            ext = path.split('.')[-1]
        else:
            ext = ""
        if '*.'+ext in self.filters:
            self.file_selected_signal.emit(path)