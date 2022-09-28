.. _tof:


Time of flight analysis
=======================

The program relies on the multiple frequency method to obtain the couplant-corrected wave travel times (`Pantea et al. Rev. Sci. Instr. 2005 <https://aip.scitation.org/doi/full/10.1063/1.2130715>`_, `Sturtevant et al. Rev. Sci. Instr. 2020 <https://aip.scitation.org/doi/full/10.1063/5.0010475>`_). 

A cross-correlation procedure measures the optimal interference between the original waveform and its copy with a phase shift by varying the ammount of shift. This process is used to calculate the time delay between any 2 pulses.

The difference between R1 & R2 reflection = double travel time
	
        \ :math:`R2 - R1 = 2 τ`


.. toctree::
   :glob:
   :maxdepth: 1
 
   tof_gui
   tof_walkthrough 