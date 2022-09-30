# import necessary modules
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
 
 
class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, data):
        super(QFileSystemModel, self).__init__()
 
        self.horizontalHeaders = [''] * 4
        self.setHeaderData(0, Qt.Horizontal, "Column 0")
        self._data = data
 
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
 
 
class DisplayDirectoryView(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.initializeUI()
 
    def initializeUI(self):
 
        self.setMinimumSize(500, 400)
        self.setWindowTitle('12.1 – View Directory Example')
 
        self.createMenu()
        self.setupTree()
 
        self.show()
 
    def createMenu(self):
        """
        Set up the menu bar.
        """
        open_dir_act = QAction('Open Directory...', self)
        open_dir_act.triggered.connect(self.selectDirectory)
 
        root_act = QAction("Return to Root", self)
        root_act.triggered.connect(self.returnToBaseDirectory)
 
        # Create menubar
        menu_bar = self.menuBar()
        # menu_bar.setNativeMenuBar(False) # uncomment for macOS
 
        # Create file menu and add actions
        dir_menu = menu_bar.addMenu('Directories')
        dir_menu.addAction(open_dir_act)
        dir_menu.addAction(root_act)
 
    def setupTree(self):
        """
        Set up the QTreeView so that it displays the contents 
        of the Project. 
        """
        #self.model = QFileSystemModel()
        self.model = CustomFileSystemModel('Project Contents')
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setIndentation(10)
        self.tree.setModel(self.model)
        self.tree.header().hideSection(1)
        self.tree.header().hideSection(2)
        self.tree.header().hideSection(3)
        self.model.setHeaderData(0, Qt.Horizontal, 'Project Contents')
 
        # Set up container and layout
        frame = QFrame()  # The QFrame class is used as a container to group and surround widgets, or to act as placeholders in GUI
        # applications. You can also apply a frame style to a QFrame container to visually separate it from near by widgets.
        frame_v_box = QVBoxLayout()
        frame_v_box.addWidget(self.tree)
        frame.setLayout(frame_v_box)
        self.setCentralWidget(frame)
 
    def selectDirectory(self):
        """
        Select a directory to display.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        directory = file_dialog.getExistingDirectory(self, "Open Directory",
                                                     "", QFileDialog.ShowDirsOnly)
 
        self.tree.setRootIndex(self.model.index(directory))
 
    def returnToBaseDirectory(self):
        """
        Re-display the contents of the root directory. 
        """
        self.tree.setRootIndex(self.model.index(''))
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DisplayDirectoryView()
    sys.exit(app.exec_())