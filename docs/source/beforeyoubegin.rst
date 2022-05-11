.. _settingup:

Introduction
==================

sonicPy components
------------------

Sound velocity in a material can be estimated by an experimental measurements of the wave travel distance (d) and the wave travel time (t) 

v = d/t	

The data analysis package sonicPy consists of two GUI programs, :ref:`Image-Analysis <imageanalysis>` and :ref:`Time-of-Flight <tof_analysis>` that allow to estimate the values of d and t, respectively.  

The goal of the Image-Analysis program is to perform measurements of the sample-thickness in the experimentally recorded radiography images. The sample-thickness corresponds to the travel distance (d) of the ultrasound wave. 

The Time-of-Flight program is used to determine the time shift between a series of experimentally recorded ultrasound echoes by performing cross-correlation. In addition, the inverse frequency (f) module inside of the Time-of-Flight program may be used to improve the travel time estimation by preforming the multiple-frequency analysis. 


Installing sonicPy
------------------
The latest release of the executable version of **sonicPy** can be downloaded from `here <https://github.com/hrubiak/sonicpy/releases>`_.

GUI basics
----------

The basis for data exploration in are the image and waveform widgets available in :ref:`Image-Analysis <imageanalysis>` and :ref:`Time-of-Flight <tof_analysis>` 
 
All widgets support to following mouse commands:

- *Left Click:*
    Action depends on the module you are in.
    In the calibration view it will search for peaks.
    In the Mask view it is the primary tool for creating the geometric objects used to build up the mask and in the
    integration view it draws a line at the current two theta value.

- *Left Drag:*
    Zooms into the selected area.
    It will try to scale images accordingly, but will not perfectly zoom in to the selected area, because pixels are
    kept as square objects on the screen.

- *Right Click (Command+Right Click on Mac):*
    Zoom out.

- *Right Double Click (Command + Right Double Click on Mac):*
    Completely zoom out.

- *Mouse Wheel:*
    Zoom in and zoom out based on the current cursor position.

.. figure:: /images/time-of-flight.png
   :alt: Time-of-Flight program
   :scale: 40 %
   :align: center

   *Time-of-Flight program*


