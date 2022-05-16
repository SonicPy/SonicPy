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

This section describes the basics for data plots exploration in are the image and waveform widgets available in :ref:`Image-Analysis <imageanalysis>` and :ref:`Time-of-Flight <tof_analysis>` 
 
All of the data plot panels support the following mouse commands:

- *Left Click:*
    Move the vertical line cursor to the current mouse position.   

- *Left Drag:*
    Zoom-in to the selected area.

- *Right Click:*
    Zoom out.

- *Mouse Wheel:*
    Zoom in and zoom out centered around the current mouse position.

.. figure:: /images/time-of-flight.png
   :alt: Time-of-Flight program
   :scale: 40 %
   :align: center

   *Time-of-Flight program*


