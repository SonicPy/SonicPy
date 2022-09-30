

About  
-----

A LiNbO\ :sub:`3` transducer, which generates and receives both compressional and shear waves simultaneously, is attached to the back side of the top WC anvil. An Al\ :sub:`2`\O\ :sub:`3` buffer rod is placed between the WC anvil and the sample. Elastic waves pass through the WC anvil, propagate through the Al\ :sub:`2`\O\ :sub:`3` buffer rod and enter the sample. A series of reflected elastic wave signals come from the interfaces of anvil/buffer rod (R0), buffer rod/sample (R1), sample/Al\ :sub:`2`\O\ :sub:`3` plate (R2), and Al\ :sub:`2`\O\ :sub:`3` plate/BN pressure medium (R3). Then, elastic wave velocity (\ :math:`v = d/{\tau}`) is calculated using the elastic wave travel time and sample length determined by X-ray radiography measurement. (`Kono et al. PEPI 228 (2014) 269–280 <https://www.sciencedirect.com/science/article/pii/S0031920113001295>`_)

   

.. figure:: /images/intro/cell_schematic.png
   :alt: Ultrasound cell schematic     
   :width: 450px
   :align: center

   Ultrasound cell schematic

.. figure:: /images/intro/echoes_schematic.png
   :alt: Elastic wave singnals
   :width: 500px
   :align: center

   Elastic wave singnals

.. figure:: /images/intro/radiography_schematic.png
   :alt: Radiography image 
   :width: 500px
   :align: center

   Radiography image

The data analysis package sonicPy consists of two GUI programs, :ref:`Image-Analysis <imageanalysis>` 
and :ref:`Time-of-Flight <tof>` that allow to estimate the values of (\ :math:`d`) 
and (\ :math:`{\tau}`), respectively.  

The goal of the :ref:`Image-Analysis <imageanalysis>` program is to perform measurements of the sample-thickness 
in the experimentally recorded radiography images. The sample-thickness corresponds to 
the travel distance (\ :math:`d`) of the ultrasound wave. 

The :ref:`Time-of-Flight <tof>` program is used to determine the time shift (\ :math:`{\tau}`) between a 
series of experimentally recorded ultrasound echoes by performing cross-correlation. 

The difference between R1 & R2 reflection = double travel time
	
        \ :math:`R2 - R1 = 2 τ`

.. _r1-r2: 

The Time-of-flight program relies on the multiple frequency method to obtain the couplant-corrected wave travel times (`Pantea et al. Rev. Sci. Instr. 2005 <https://aip.scitation.org/doi/full/10.1063/1.2130715>`_, `Sturtevant et al. Rev. Sci. Instr. 2020 <https://aip.scitation.org/doi/full/10.1063/5.0010475>`_). 

.. figure:: /images/intro/f_schematic.png
   :alt: inverse_f_schematic 
   :width: 400px
   :align: center
 