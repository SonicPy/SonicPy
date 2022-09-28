# -*- coding: utf8 -*-

import sys
import os
from pathlib import Path
import platform
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import pyqtgraph

from ._version import get_versions
import traceback
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import traceback

from um.widgets.UtilityWidgets import ErrorMessageBox
import time

__version__ = get_versions()['version']
del get_versions
print(__version__)

if __version__ == "0+unknown":
    __version__ = "0.6.1"
sonicpy_version = __version__[:5]




def excepthook(exc_type, exc_value, traceback_obj):
    """
    Global function to catch unhandled exceptions. This function will result in an error dialog which displays the
    error information.

    :param exc_type: exception type
    :param exc_value: exception value
    :param traceback_obj: traceback object
    :return:
    """
    separator = '-' * 80
    log_file = "error.log"
    notice = \
        """An unhandled exception occurred. Please report the bug under:\n """ \
        """\t%s\n""" \
        """or via email to:\n\t <%s>.\n\n""" \
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("https://github.com/hrubiak/hp-edxd/issues",
         "hrubiak@anl.gov",
         os.path.join(os.path.dirname(__file__), log_file))
    version_info = '\n'.join((separator, "SonicPy Version: %s" % sonicpy_version))
    time_string = time.strftime("%Y-%m-%d, %H:%M:%S")
    tb_info_file = StringIO()
    traceback.print_tb(traceback_obj, None, tb_info_file)
    tb_info_file.seek(0)
    tb_info = tb_info_file.read()
    errmsg = '%s: \n%s' % (str(exc_type), str(exc_value))
    sections = [separator, time_string, separator, errmsg, separator, tb_info]
    msg = '\n'.join(sections)
    try:
        f = open(log_file, "w")
        f.write(msg)
        f.write(version_info)
        f.close()
    except IOError:
        pass
    errorbox = ErrorMessageBox()
    errorbox.setText(str(notice) + str(msg) + str(version_info))
    errorbox.exec_()



theme = 1
autoload = False

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')
title = "SonicPy: Time-of-flight analysis. ver." + __version__ + "  © R. Hrubiak, 2022."
home_path = str(Path.home())




def TOF():
    from ua.controllers.TimeOfFlightController import TimeOfFlightController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    _platform = platform.system()
    app = QtWidgets.QApplication([])
    sys.excepthook = excepthook
    controller = TimeOfFlightController(app = app)
    controller.show_window()

    if autoload:
        fname = ''
        mac_file = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam3/US/myproject.bz'
        win_file = "C:\\Users\\hrubiak\\Desktop\\Ultrasound_XRD_datasets_for_dissemination\\Ultrasound_data_for_dissemination_June_2018_Exp4\\Gaussian\\myproject.bz"
        mac_file_2 = '/Users/hrubiak/Downloads/Ultrasound_XRD_datasets_for_dissemination/Ultrasound_data_for_dissemination_June_2018_Exp4/Gaussian/myproject.bz'
        possible_files = [mac_file,
                            win_file,
                            mac_file_2]
        for f in possible_files:
            if os.path.isfile(f):
                fname = f
                break
        if len(fname):
            if os.path.isfile(fname):
                controller._open_project(filename=fname)
    
    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.widget
        pact = QtWidgets.QAction('Preferences', app)
        pact.triggered.connect(controller.preferences_module)
        pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
        pmenu = QtWidgets.QMenu('Preferences')
        pmenu.addAction(pact)
    return app.exec_()

