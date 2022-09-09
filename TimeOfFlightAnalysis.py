
# TODO hdf5 (data measurement and analysis)
# TODO add color for already selected echoes
# TODO project file
# TODO save echoes per frequency in file dict
# TODO cycle through all frequencies automatically
# TODO broad pulse 
# TODO fix arrow plot updating
# TODO Vp and Vs output
# TODO plots/data output for publication

from ua import TOF

TOF()

'''
Traceback (most recent call last):
  File "/Users/hrubiak/GitHub/sonicPy/ua/controllers/ArrowPlotController.py", line 119, in auto_data
    arrow_plot.auto_sort_optima(opt)
  File "/Users/hrubiak/GitHub/sonicPy/ua/models/ArrowPlotModel.py", line 320, in auto_sort_optima
    diff = abs(np.asarray(next_t)-t)
TypeError: unsupported operand type(s) for -: 'float' and 'NoneType'
'''