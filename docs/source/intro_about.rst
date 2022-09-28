

About  
-----

Sound velocity (\ :math:`v`) in a material can be estimated using measurements of the 
wave travel distance (\ :math:`d`) and the wave travel time (\ :math:`{\tau}`) 

\ :math:`v = d/{\tau}`	 

.. figure:: /images/intro/cell_schematic.png
   :alt: cell_schematic  
   :width: 450px
   :align: center

The data analysis package sonicPy consists of two GUI programs, :ref:`Image-Analysis <imageanalysis>` 
and :ref:`Time-of-Flight <tof>` that allow to estimate the values of (\ :math:`d`) 
and (\ :math:`{\tau}`), respectively.  

The goal of the :ref:`Image-Analysis <imageanalysis>` program is to perform measurements of the sample-thickness 
in the experimentally recorded radiography images. The sample-thickness corresponds to 
the travel distance (\ :math:`d`) of the ultrasound wave. 

.. figure:: /images/intro/radiography_schematic.png
   :alt: radiography_schematic 
   :width: 500px
   :align: center

The :ref:`Time-of-Flight <tof>` program is used to determine the time shift (\ :math:`{\tau}`) between a 
series of experimentally recorded ultrasound echoes by performing cross-correlation. 

.. _r1-r2: 

.. figure:: /images/intro/echoes_schematic.png
   :alt: echoes_schematic 
   :width: 500px
   :align: center

The inverse frequency (\ :math:`f`\ :sup:`-1`) module of the Time-of-Flight program 
can improve the travel time estimation by performing the multiple-frequency analysis. 

.. figure:: /images/intro/f_schematic.png
   :alt: inverse_f_schematic 
   :width: 400px
   :align: center
 