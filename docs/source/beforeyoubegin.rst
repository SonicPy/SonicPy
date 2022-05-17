.. _settingup:

Introduction
==================

About  
-----

Sound velocity (\ :math:`v`) in a material can be estimated by an experimental measurements of the 
wave travel distance (\ :math:`d`) and the wave travel time (\ :math:`{\tau}`) 

\ :math:`v = d/{\tau}`	 

The data analysis package sonicPy consists of two GUI programs, :ref:`Image-Analysis <imageanalysis>` 
and :ref:`Time-of-Flight <tof_analysis>` that allow to estimate the values of (\ :math:`d`) 
and (\ :math:`{\tau}`), respectively.  

The goal of the Image-Analysis program is to perform measurements of the sample-thickness 
in the experimentally recorded radiography images. The sample-thickness corresponds to 
the travel distance (\ :math:`d`) of the ultrasound wave. 

The Time-of-Flight program is used to determine the time shift (\ :math:`{\tau}`) between a 
series of experimentally recorded ultrasound echoes by performing cross-correlation. 
The inverse frequency (\ :math:`f`\ :sup:`-1`) module of the Time-of-Flight program 
can improve the travel time estimation by performing the multiple-frequency analysis. 


Installation
------------
The latest release of the executable version of **sonicPy** can be downloaded from `here <https://github.com/hrubiak/sonicpy/releases>`_.

GUI basics
----------

This section describes the mouse interaction basics for the image and waveform plots in :ref:`Image-Analysis <imageanalysis>` and :ref:`Time-of-Flight <tof_analysis>` 
 
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


