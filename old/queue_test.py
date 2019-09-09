import sys

from PyQt5 import QtCore, QtWidgets
from functools import partial

class TaskManager(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int, QtCore.QByteArray)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._process = QtCore.QProcess(self)
        self._process.finished.connect(self.handleFinished)
        self._progress = 0
        self._currentTask = None

    def start_tasks(self, tasks):
        self._tasks = iter(tasks)
        self.fetchNext()
        self.started.emit()
        self._progress = 0

    def fetchNext(self, additional_args=None):
            try:
                self._currentTask = next(self._tasks)
            except StopIteration:
                return False
            else:
                program = self._currentTask.get("program")
                args = self._currentTask.get("args")
                if additional_args is not None:
                    args += additional_args
                self._process.start(program, args)
            return True

    def processCurrentTask(self):
        output = self._process.readAllStandardOutput()
        self._progress += 1
        fun = self._currentTask.get("function")
        res = None
        if fun:
            res = fun(output)
        self.progressChanged.emit(self._progress, output)
        return res

    def handleFinished(self):
        args = self.processCurrentTask()
        if not self.fetchNext(args):
            self.finished.emit()


def fun1to2(args):
    return "-additional_arg_for_process2_from_result1" 

def fun2to3(args):
    return "-additional_arg_for_process3_from_result2" 

class gui(QtWidgets.QMainWindow):
    def __init__(self):
        super(gui, self).__init__()
        self.initUI()


    def dataReady(self, progress, result):
        self.output.append(str(result, "utf-8"))
        self.progressBar.setValue(progress)


    def callProgram(self):
        tasks = [{"program": "python", "args": ["scripts/script1.py", "default_argument1"], "function": fun1to2},
                 {"program": "python", "args": ["scripts/script2.py", "default_argument2"], "function": fun2to3},
                 {"program": "python", "args": ["scripts/script3.py", "default_argument3"]}]

        self.progressBar.setMaximum(len(tasks))
        self.manager.start_tasks(tasks)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.runButton = QtWidgets.QPushButton('Run')

        self.runButton.clicked.connect(self.callProgram)

        self.output = QtWidgets.QTextEdit()

        self.progressBar = QtWidgets.QProgressBar()

        layout.addWidget(self.output)
        layout.addWidget(self.runButton)
        layout.addWidget(self.progressBar)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.manager = TaskManager(self)
        self.manager.progressChanged.connect(self.dataReady)
        self.manager.started.connect(partial(self.runButton.setEnabled, False))
        self.manager.finished.connect(partial(self.runButton.setEnabled, True))


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui=gui()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()