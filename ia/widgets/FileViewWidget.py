import imp
import sys, os

from PyQt5 import QtWidgets, QtCore, QtGui

class YourSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self, *args, **kwargs):
        QtWidgets.QFileSystemModel.__init__(self, *args, **kwargs)

        self.fnames = {}
        self.fldr_path = ''

    def set_fname_status(self, fname, status):
        
        self.fnames[fname]['status'] = str(status)

    def set_fname_result(self, fname, result):
        
        self.fnames[fname]['result'] = result

    def get_file_results(self):
        return self.fnames 

    def get_file_paths (self):
        f_out = {}
        for f in sorted(list(self.fnames.keys())):
            file = os.path.join(self.fldr_path, f)
            f_out[f] = file
        return f_out

    def columnCount(self, parent = QtCore.QModelIndex()):
        return super(YourSystemModel, self).columnCount()+1

    def data(self, index, role):
        if index.column() == self.columnCount() - 1:
            if role == QtCore.Qt.DisplayRole:
                
                
                model = QtWidgets.QFileSystemModel
                idx = model.index(self, model.rootPath(self))
                
                child = idx.child(index.row(), idx.column())
                fname =  model.fileName(self, child)
                if fname in self.fnames:
                    
                    f = self.fnames [fname] ['status']
                else :
                    f = ''
                
                return f
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter

        return super(YourSystemModel, self).data(index, role)

    def setRootPath(self, path):
        self.fldr_path = path
        self.fnames = {}
        ans = QtWidgets.QFileSystemModel.setRootPath(self, path)
        QtWidgets.QApplication.processEvents()
        model = QtWidgets.QFileSystemModel
        idx = model.index(self, model.rootPath(self))
        for i in range(0, model.rowCount(self, idx)):
            child = idx.child(i, idx.column())
            fname =  model.fileName(self, child)
            self.fnames [fname] = {'status':'', 'result':{}}

        return ans
        

class FileViewWidget(QtWidgets.QWidget):

    file_selected_signal = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.hlay = QtWidgets.QVBoxLayout(self)
        '''self.treeview = QtWidgets.QTreeView()'''

        self.open_btn = QtWidgets.QPushButton('Open folder')
        self.hlay.addWidget(self.open_btn)
        self.listview = QtWidgets.QTreeView()
        self.listview.setColumnHidden(1, True)
        self.listview.setColumnHidden(2, True)
        self.listview.setColumnHidden(3, True)
        '''hlay.addWidget(self.treeview)'''
        self.hlay.addWidget(self.listview)

        path = QtCore.QDir.homePath()

        '''self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setRootPath(QtCore.QDir.rootPath())
        self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)'''
        

        self.fileModel = YourSystemModel()
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |  QtCore.QDir.Files)

        self.filters = ["*.tif", '*.tiff', "*.bmp", "*.png", "*.jpg"]
        self.fileModel.setNameFilters(self.filters)
        

        '''self.treeview.setModel(self.dirModel)
        for i in  range( self.dirModel.columnCount()-1):
            self.treeview.hideColumn(i +1)'''
        self.listview.setModel(self.fileModel)
        self.listview.setColumnHidden(1, True)
        self.listview.setColumnHidden(2, True)
        self.listview.setColumnHidden(3, True)
        self.listview.setColumnWidth(0,200)

        '''self.treeview.setRootIndex(self.dirModel.index(path))'''
        self.listview.setRootIndex(self.fileModel.index(path))

        self.open_btn.clicked.connect(self.on_clicked)
        self.listview.clicked.connect(self.on_selection_changed)

    def on_clicked(self, index):

        path = QtWidgets.QFileDialog.getExistingDirectory(self, caption='Select US folder',
                                                     directory='')
        if len(self.path):
            self.listview.setRootIndex(self.fileModel.setRootPath(self))

            files = self.fileModel.get_file_paths()
            

    def on_selection_changed(self, index):

        path = self.fileModel.fileInfo(index).absoluteFilePath()
        if '.'in path:
            ext = path.split('.')[-1]
        else:
            ext = ""
        if '*.'+ext in self.filters:
            self.file_selected_signal.emit(path)