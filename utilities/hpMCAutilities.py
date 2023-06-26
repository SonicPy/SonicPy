from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from functools import partial
import json
import copy
from um.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from pathlib import Path
import numpy as np
import os

def compare_lists(a,b):
   if len(a) !=len(b):
      return False
   else:
      if len(a):
         a_0 = a[0]
      else: 
         return True  # means both lists are empty thus equal
      b_0 = b[0]
      a_0_type = type(a_0)
      b_0_type = type(b_0)
      if a_0_type != b_0_type:
         return False
      else:
         for i, a_i in enumerate(a):
               b_i = b[i]
               return compare(a_i,b_i)

def compare(a,b):
   a_type = type(a)
   b_type = type(b)
   if a_type != b_type:
      return False
   else:
      if isinstance(a, np.ndarray):
         a_s = a.shape
         b_s = b.shape
         if a_s!=b_s:
               return False
         same = (a==b).all()
      elif isinstance(a, list):
         a_l=len(a)
         b_l=len(b)
         if a_l!=b_l:
               return False
         same =compare_lists(a,b)
      else:
         same = a==b
      return same

class Preferences():
   def __init__(self, params, name = ''):
      self.auto_process = False
      self.done = False
      self.params = dict.fromkeys(params)
      self.out_params = {}
      self.config_modified = False
      self.name = name

   def set_config(self, config_dict):
      self.done = False
      self.config_modified = {}
      params = list(self.params.keys())
      #start_time = time.time()
      for p in params:
         if p in config_dict:
               old = self.params[p]
               new = config_dict[p]
               same = compare(old,new)
               if not same:
                  self.params[p]=config_dict[p]
                  self.config_modified[p] = True
         else:
               if self.params[p] is not None:
                  self.params[p] = None
                  self.config_modified[p] = True
      #print("--- %s seconds ---" % (time.time() - start_time))
      if self.auto_process:
         mod = False
         for conf in self.config_modified:
            if self.config_modified[conf]:
               mod = True
         if mod:
               #print(self.name+' calc - config triggered')
               self.update()
               self.config_modified = {}
         self.done = True

   def set_auto_process(self, state):
      self.auto_process = state
      if self.auto_process:
         if self.config_modified:
               #print(self.name+' calc - set autoprocess triggered')
               self.update()
               self.config_modified = False
         self.done = True

   def update(self):
      pass

def readconfig(config_file):
        with open(config_file,'r') as f:
            config_dict = json.loads(f.read())
        return config_dict 

def json_compatible_dict(params):
    options_out = dict()
    obj = params
    for key in obj:
        if key != 'modified':  # this key is reserved for internal use only
            item = obj[key]
            if isinstance(item, np.ndarray):  # ndarrays cant be 'pickled' by the json package
                item = list(item)
                if len(item):
                    if isinstance(item[0], np.ndarray):
                        ii = []
                        for i in item:
                            if isinstance(i, np.ndarray):
                                i = list(i)
                            ii.append(i)
                    item = ii
            options_out[key] = item
    return options_out

############################################################
class mcaFilePreferences(QtWidgets.QDialog):
   def __init__(self, parent, options=None):
      super(mcaFilePreferences, self).__init__(parent)
      self.original_options = options
      self.ok = [False, options]
      if options is None:
         self.options = mcaDisplay_options()
      else:
         self.options = copy.deepcopy(options)
      self._layout = QtWidgets.QVBoxLayout()  
      self.setWindowTitle('File Preferences')
      self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint )
      self.opts = {"warn_overwrite" :["Warning when overwriting file:", self.options.warn_overwrite, None] ,
                   "warn_erase"     :["Warning when erasing unsaved data:", self.options.warn_erase, None],
                   #"inform_save"    :["Informational popup after saving file:", self.options.inform_save, None],
                   "autosave"       :["Autosave when acquisition stops:", self.options.autosave, None],
                   "autorestart"    :["Auto-restart when acquisition stops:", self.options.autorestart, None]
                  }
      for key in self.opts:
         t = self.add_row(self, key, self.opts[key][0], self.opts[key][1])
         self.opts[key][2]=t[1]        # remember a reference to "yes" button in option row widget
         self._layout.addWidget(t[0])  # option row widget
      self.button_widget = QtWidgets.QWidget(self)
      self.button_widget.setObjectName('file_settings_control_button_widget')
      self._button_layout = QtWidgets.QHBoxLayout()
      self._button_layout.setContentsMargins(0, 0, 0, 0)
      self._button_layout.setSpacing(6)
      self.ok_btn = FlatButton('OK')
      self.ok_btn.clicked.connect(partial(self.button_press, "OK"))
      self.cancel_btn = FlatButton('Cancel')
      self.cancel_btn.clicked.connect(partial(self.button_press, "Cancel"))
      self._button_layout.addWidget(self.ok_btn)
      self._button_layout.addWidget(self.cancel_btn)
      self.button_widget.setLayout(self._button_layout)
      self._layout.addWidget(self.button_widget)
      self.setLayout(self._layout)
      self.setFixedSize(self.sizeHint())
     
   @classmethod
   def showDialog(cls, parent, options_in):
      dialog = cls(parent, options_in)
      dialog.exec_()
      ok = copy.deepcopy(dialog.ok)
      dialog.deleteLater()
      return ok

   ############################################################
   def add_row(self, parent, option, text, value):
      button_widget = QtWidgets.QWidget(parent)
      button_widget.setObjectName(option)
      _button_layout = QtWidgets.QHBoxLayout()
      _button_layout.setContentsMargins(5, 5, 5, 5)
      _button_layout.setSpacing(12)
      option_lbl = QtWidgets.QLabel(text)
      _button_layout.addSpacerItem(HorizontalSpacerItem())
      no_btn = QtWidgets.QRadioButton('No')
      yes_btn = QtWidgets.QRadioButton('Yes')
      if value == 0 or value == False:
         no_btn.setChecked(True)
      elif value == 1 or value == True:
         yes_btn.setChecked(True)
      _button_layout.addWidget(option_lbl)
      _button_layout.addWidget(no_btn)
      _button_layout.addWidget(yes_btn)
      button_widget.setLayout(_button_layout)
      return [button_widget, yes_btn]

   ############################################################
   def button_press(self, button):
      if (button == 'OK'):
         self.options.warn_overwrite = \
                                 self.opts["warn_overwrite"][2].isChecked()
         self.options.warn_erase = \
                                 self.opts["warn_erase"][2].isChecked()
         #self.options.inform_save = \
         #                        self.opts["inform_save"][2].isChecked()
         self.options.autosave = \
                                 self.opts["autosave"][2].isChecked()
         self.options.autorestart = \
                                 self.opts["autorestart"][2].isChecked()
         self.ok = [True, self.options]
      else : self.ok = [False, self.original_options]
      self.close()

############################################################      
def restore(file, obj):

   attributes  = [key for key, value in obj.__dict__.items() if not key.startswith("__")]
   if os.path.isfile(file):
      try:
         with open(file) as f:
            openned_file = json.load(f)
         ok = True
         
      except:
         ok = False
         displayErrorMessage( 'opt_read') 

      
      if ok:
         for Opt in attributes:
            if Opt in openned_file: 
               setattr(obj, Opt, openned_file[Opt])
         
   return obj

############################################################
def restore_file_settings(file):
   obj = mcaDisplay_options() 
   return restore(file, obj)

############################################################
def restore_folder_settings(file):
   obj = mcaDisplay_file()
   return restore(file, obj)

############################################################
def save(options, file):
   options_out = dict()
   obj = options.__dict__
   for key in obj:
      options_out[key] = obj[key]
   try:
      with open(file, 'w') as outfile:
         json.dump(options_out, outfile,sort_keys=True, indent=4)
         outfile.close()
   except:
      displayErrorMessage( 'opt_save') 

############################################################
def save_folder_settings(options, file='hpMCA_folder_settings.json'):
   save(options, file)

############################################################
def save_file_settings(options, file='hpMCA_file_settings.json'):
   save(options, file)



############################################################

def create_error_messages():
   errors = dict()
   errors['fr'] = ["File read error", 
            "There was a problem reading the file, please check the file format"]
   errors['fs'] = ["File save error", 
            "There was a problem saving the file, file not saved"]
   errors['calroi'] = ["mcaCalibration Error", 
               "Too few defined regions of interest (ROIs) to perform calibration"]
   errors['plot'] = ["Plot error", 
               "Trere was a problem updating the view"]
   errors['init'] = ["Initialization error", 
               "Initialization error"]
   errors['opt_save'] = ["Settings file error", 
               "Error saving settings in file"]
   errors['opt_read'] = ["Settings file error", 
               "Error reading settings in file"]
   errors['general'] = ["Undefined error", 
               "General error message"]           
   errors['phase'] = ["Phase read error", 
               'Could not load phase file. Please check if the format of the input file is correct.']      
   return errors
    
def displayErrorMessage(errorKey='general'):
   errors = create_error_messages()
   QtWidgets.QMessageBox.about(None, errors[errorKey][0],errors[errorKey][1])


############################################################

class mcaDisplay_colors:
   def __init__(self):
      self.background           = 'black'
      self.markers              = 'red'
      self.highlight_markers    = 'green'
      self.klm                  = 'green'
      self.highlight_klm        = 'light blue'
      self.jcpds                = 'green'
      self.highlight_jcpds      = 'light blue'
      self.foreground_spectrum  = 'yellow'
      self.background_spectrum  = 'green'
      self.roi                  = 'blue'
      self.labels               = 'blue'
      self.entry_foreground     = 'black'
      self.entry_background     = 'lightblue'
      self.label_foreground     = 'blue'
      self.label_background     = 'white'

############################################################
class mcaDisplay_options:
   def __init__(self):
      self.autosave       = False # Automatically save file when acq. completes
      self.autorestart    = False # Automatically restart acq. when acq. completes
      self.warn_overwrite = True  # Warn user of attempt to overwrite existing file
      self.save_done      = False # Flag to keep track of save done before erase
      #self.inform_save    = False # Inform user via popup of successful file save
      self.download_rois  = False # Download ROIs to record when reading file
      self.warn_erase     = False # Warn user of attempt to erase without prior save
      self.download_cal   = False # Download calibration to record when reading file
      self.download_data  = False # Download MCA data to record when reading file
      self.debug          = False # Debug flag - not presently used

############################################################
class mcaDisplay_file:
   def __init__(self):
      home = str(Path.home())
      self.phase         = home
      self.savedata      = home          # name of saved or read
      self.export_ext    = '.xy'
      

############################################################
class mcaDisplay_display:
   def __init__(self):
      self.update_time = .5
      self.current_time = 0.
      self.current_counts = 0
      self.current_bgd = 0
      self.current_acqg = 0
      self.prev_time   = 0.
      self.prev_counts = 0
      self.prev_bgd    = 0
      self.prev_acqg   = 0
      self.new_stats   = 0
      self.horiz_mode  = 0
      self.hmin        = 0
      self.hmax        = 2048
      self.vlog        = 1
      self.lmarker     = 100
      self.rmarker     = 200
      self.cursor      = 300
      self.klm         = 26 # Start with Fe
      self.current_roi = 0
      self.pressure    = 0.
      self.temperature = 0.
      self.psym        = 0
      self.k_lines = ['Ka1', 'Ka2', 'Kb1', 'Kb2']
      self.l_lines = ['La1', 'Lb1', 'Lb2', 'Lg1', 'Lg2', 'Lg3', 'Lg4', 'Ll']

############################################################
class mcaDisplay_mca:
   def __init__(self):
      self.mca          = None
      self.name         = ''
      self.valid        = 0
      self.is_detector  = 0
      self.nchans       = 0
      self.data         = []
      self.elapsed      = None
      self.roi          = []


############################################################
############################################################

class mcaDisplay_presets():
   def __init__(self):

      self.channel_advance=0
      self.dwell=0.0
      self.end_channel=0
      self.live_time=0.0
      self.prescale=1
      self.real_time=0.0
      self.start_channel=0
      self.total_counts=0


############################################################

class mcaControlPresets(QtWidgets.QDialog):
   def __init__(self, parent,presets=mcaDisplay_presets(), options=None):
      """
      Creates a new GUI window 
      The preset live time, real time, start channel, end channel and total
      counts can be controlled.

      Inputs:
         
      """

      super(mcaControlPresets, self).__init__(parent)
      
      self.original_presets = presets
      self.ok = [False, presets]
      if presets is None:
         self.presets = mcaDisplay_presets()
      else:
         self.presets = copy.deepcopy(presets)
      self._layout = QtWidgets.QVBoxLayout()  
      self.setWindowTitle('Presets')
      self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint )
      self.opts = {"real_time"   :["Real time:", self.presets.real_time, None],
                   "live_time"   :["Live time:", self.presets.live_time, None],
                   "total_counts":["Total counts:", self.presets.total_counts, None],
                   "start_chan"  :["Start channel:", self.presets.start_channel, None],
                   "end_chan"    :["End channel:", self.presets.end_channel, None]
                  }
      
      
      for key in self.opts:
         t = self.add_row_number_field(self, key, self.opts[key][0], self.opts[key][1])
         self.opts[key][2]=t[1]        # remember a reference to "yes" button in option row widget
         self._layout.addWidget(t[0])  # option row widget
      self.button_widget = QtWidgets.QWidget(self)
      self.button_widget.setObjectName('file_settings_control_button_widget')
      self._button_layout = QtWidgets.QHBoxLayout()
      self._button_layout.setContentsMargins(0, 0, 0, 0)
      self._button_layout.setSpacing(6)
      self.ok_btn = FlatButton('OK')
      self.ok_btn.clicked.connect(partial(self.button_press, "OK"))
      self.cancel_btn = FlatButton('Cancel')
      self.cancel_btn.clicked.connect(partial(self.button_press, "Cancel"))
      self._button_layout.addWidget(self.ok_btn)
      self._button_layout.addWidget(self.cancel_btn)
      self.button_widget.setLayout(self._button_layout)
      self._layout.addWidget(self.button_widget)
      self.setLayout(self._layout)
      self.setFixedSize(self.sizeHint())

   @classmethod
   def showDialog(cls, parent, presets_in):
      dialog = cls(parent, presets_in)
      dialog.exec_()
      return dialog.ok

   ############################################################
   def add_row_number_field(self, parent, option, text, value):
      button_widget = QtWidgets.QWidget(parent)
      button_widget.setObjectName(option)
      _button_layout = QtWidgets.QHBoxLayout()
      _button_layout.setContentsMargins(5, 5, 5, 5)
      #_button_layout.setSpacing(5)
      option_lbl = QtWidgets.QLabel(text)
      _button_layout.addSpacerItem(HorizontalSpacerItem())
      value_control = DoubleSpinBoxAlignRight()
      value_control.setMinimumWidth(120)
      value_control.setMaximum(10000)
      value_control.setDecimals(0)
      value_control.setValue(value)
      _button_layout.addWidget(option_lbl)
      _button_layout.addWidget(value_control)
      button_widget.setLayout(_button_layout)
      return [button_widget, value_control]

   ############################################################
   def button_press(self, button):
      if (button == 'OK'):
         self.presets.real_time = \
                                 int(self.opts["real_time"][2].value())
         self.presets.live_time = \
                                 int(self.opts["live_time"][2].value())
         self.presets.total_counts = \
                                 int(self.opts["total_counts"][2].value())
         self.presets.start_channel = \
                                 int(self.opts["start_chan"][2].value())
         self.presets.end_channel = \
                                 int(self.opts["end_chan"][2].value())
         self.ok = [True, self.presets]
      else : self.ok = [False, self.original_presets]
      self.close()

