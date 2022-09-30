import imp
import sys, os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt 
from um.widgets.CustomWidgets import HorizontalLine, HorizontalSpacerItem, VerticalLine, VerticalSpacerItem
from ia.widgets.collapsible_widget import CollapsibleBox, EliderLabel

import natsort

class YourSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self):
        super(QtWidgets.QFileSystemModel, self).__init__()
 
        self.horizontalHeaders = [''] * 6
        self.fnames = {}
        self.fldr_path = ''

    def get_fnames(self):
        model = QtWidgets.QFileSystemModel
        idx = model.index(self, model.rootPath(self))
        rows = len(self.fnames)
        names = []
        for r in range(rows):
            child = idx.child(r, 0)
            fname =  model.fileName(self, child)
            names.append(fname)
        return names

    def get_table_data(self):
        
       
        lines=[]
        first_line = ['File', 
                    'Distance (pixels)', 
                    'st.dev (pixesl)']
        lines.append(first_line)
       
        for fname in self.fnames:
            
            mean = ''
            stddev = ''
            
            if 'mean' in self.fnames [fname] ['result']:
                mean = self.fnames [fname] ['result']['mean']
            if 'std.dev' in self.fnames [fname] ['result']:
                stddev = self.fnames [fname] ['result']['std.dev']
            line = [fname, mean, stddev]
            lines.append(line)
        return lines

    def process_events(self):
        QtWidgets.QApplication.processEvents()

    def set_fname_result(self, fname, result):
       
        fpath = os.path.normpath(fname)
        '''if not fpath in self.fnames:
            self.fnames[fpath] = {'result':{}}'''
        self.fnames[fpath]['result'] = result

    def get_file_results(self):
        return self.fnames 

    def get_file_paths (self):
        f_out = {}
        for f in sorted(list(self.fnames.keys())):
            file = os.path.normpath(os.path.join(self.fldr_path, f))
            f_out[f] = file
        return f_out

    def columnCount(self, parent = QtCore.QModelIndex()):
        return super(YourSystemModel, self).columnCount()+2

    def data(self, index, role):
        if index.column() == self.columnCount() - 2:
            if role == QtCore.Qt.DisplayRole:
                model = QtWidgets.QFileSystemModel
                
                absp = model.fileInfo(self, index).absoluteFilePath()
                fpath = os.path.normpath(absp)
                f = ''
                if fpath in self.fnames:
                    if 'mean' in self.fnames [fpath] ['result']:
                        f = self.fnames [fpath] ['result']['mean']
                return f
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter
        if index.column() == self.columnCount() - 1:
            if role == QtCore.Qt.DisplayRole:
                model = QtWidgets.QFileSystemModel
               
                absp = model.fileInfo(self, index).absoluteFilePath()
                fpath = os.path.normpath(absp)
                f = ''
                if fpath in self.fnames:
                    if 'std.dev' in self.fnames [fpath] ['result']:
                        f = self.fnames [fpath] ['result']['std.dev']
                return f
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter

        return super(YourSystemModel, self).data(index, role)

    def setRootPath(self, path):
        self.fldr_path = path
        
        ans = QtWidgets.QFileSystemModel.setRootPath(self, path)
        
        self.directoryLoaded.connect(self.loaded_callback)
        self.process_events()

        return ans
        

    def loaded_callback(self, *args, **kwargs):
        model = QtWidgets.QFileSystemModel
        root = model.rootPath(self)
        
        idx = model.index(self, model.rootPath(self))
        files = []
        rows = model.rowCount(self, idx)
        for i in range(0, rows):
            child = idx.child(i, idx.column())
            fname =  model.fileName(self, child)
            if '.tif' in fname or ".bmp" in fname:
                files.append(os.path.normpath(os.path.join(root, fname)))

        files = natsort.natsorted(files)
       
        for f in files:
            if not f in self.fnames:
                self.fnames[f] = {'result':{}}

        self.directoryLoaded.disconnect(self.loaded_callback)
    
    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)
 
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        
            return super().headerData(section, orientation, role)

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignHCenter


        

class FileViewWidget(QtWidgets.QWidget):

    file_selected_signal = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.hlay = QtWidgets.QVBoxLayout(self)
        '''self.treeview = QtWidgets.QTreeView()'''

        btn_layout = QtWidgets.QHBoxLayout()
        self.open_btn = QtWidgets.QPushButton('Open folder')
        btn_layout.addWidget(self.open_btn)
        self.export_btn = QtWidgets.QPushButton('Save results')
        btn_layout.addWidget(self.export_btn)
        btn_layout.addSpacerItem(HorizontalSpacerItem())
        self.hlay.addLayout(btn_layout)

        self.folder_lbl = EliderLabel(mode=QtCore.Qt.ElideLeft)
        self.folder_lbl.setMaximumHeight(20)

        
        self.hlay.addWidget(self.folder_lbl)

        self.listview = QtWidgets.QTreeView()
        self.listview.setColumnHidden(1, True)
        self.listview.setColumnHidden(2, True)
        self.listview.setColumnHidden(3, True)
        

        self.hlay.addWidget(self.listview)

        path = QtCore.QDir.homePath()

        self.fileModel = YourSystemModel()
        
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |  QtCore.QDir.Files)

        self.filters = ["*.tif", '*.tiff', "*.bmp"]
        self.initialized = False
 
    def init_listview(self, folder):
        self.fileModel.setNameFilters(self.filters)
        self.listview.setModel(self.fileModel)
    
        self.listview.setColumnHidden(1, True)
        self.listview.setColumnHidden(2, True)
        self.listview.setColumnHidden(3, True)
        self.listview.setColumnWidth(0,200)
        self.listview.setColumnWidth(4,60)
        self.listview.setColumnWidth(5,40)

        self.fileModel.setHeaderData(0, Qt.Horizontal, "File")
        self.fileModel.setHeaderData(4, Qt.Horizontal, "Distance")
        self.fileModel.setHeaderData(5, Qt.Horizontal, f'\N{GREEK SMALL LETTER SIGMA}')

        self.listview.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.listview.setRootIndex(self. fileModel.setRootPath(folder))
        self.initialized = True
 

    def select_fname(self, fname):
        model =  QtWidgets.QFileSystemModel
        idx = model.index(self.fileModel, model.rootPath(self.fileModel))
        files = self.fileModel.get_fnames()
        row = files.index(fname)
        child = idx.child(row, 0)
        
        self.listview.setCurrentIndex( child)

    
   

    def on_selection_changed(self, index: QtCore.QItemSelection):
        index = index.indexes()[0]
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        if '.'in path:
            ext = path.split('.')[-1]
        else:
            ext = ""
        if '*.'+ext in self.filters:
            self.file_selected_signal.emit(path)

