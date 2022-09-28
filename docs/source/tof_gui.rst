

.. _gui_tof:

GUI basics 
----------

   .. figure:: /images/tof/f15_frequency-view_frequency-plot_zoomed-in_cursor-clicked.png
      :alt: Time of flight analysis window
      :width: 720px
      :align: center 

      Time of flight analysis window
 
- :ref:`Menu <tof_menu>`
- :ref:`Overview <tof_sec_overview>`
- :ref:`Echo correlation <tof_sec_correlation>`
- :ref:`Multiple frequency batch processing <tof_sec_batch>`
- :ref:`Inverse frequency plot <tof_sec_inverse>`
- :ref:`Results output <tof_sec_output>`

.. _tof_menu:

Menu
^^^^ 

- :ref:`New project <prj_new>`
- :ref:`Open project  <prj_open>`
- :ref:`Save project  <prj_save>`
- :ref:`Save project as... <prj_save_as>`
- :ref:`Close project <prj_close>`

- :ref:`Import ultrasound data <data_import>`
- :ref:`Sort data points <data_sort>`
- :ref:`Export <data_export>`


.. _prj_new:

New project
***********

Select a location for the project file. Project files can have an extension ``.bz`` for comppressed (recommended), or ``.json`` for uncompressed. 

.. _prj_open:

Open project
************

Open a previously saved the project file. The project files have an extension ``.bz`` or ``.json``. The program will ask for the new location if it doesn't find the ultrasound data that was originally imported.

.. _prj_save:

Save project
************

Saves all of the settings and calculated results for later retrieval. The original waveform data remains in the original location and must be kept if you wish to open the project later. You can move the original data to another location after saving the project. The program will ask for the new location if it doesn't find the data.

.. _prj_save_as:

Save project as...
******************

Choose a new filename for a project. This may be useful if you want to compare different settings on the same dataset.

.. _prj_close:

Close project
*************

Closes the project and clears all of the output plots.

.. _data_import:

Import ultrasound data
**********************

Either Discrete \ :math:`f` or broadband datasets can be imported. Select the folder containing the ustrasound data. 

* Discrete \ :math:`f`: waveform files should be organized into subfolders. Each subfolder should containe a set of waveform files from a frequency scan at a single P-T condition. 

* Broadband: all waveforms, one per P-T point, should be contained within one folder.


.. _data_sort:

Sort data points
****************

Opens a window that allows changing the order of the P-T steps. The order can be adjusted by selecting a P-T step list item and clicking the buttons :guilabel:`Move up` and :guilabel:`Move down`, or by dragging up or down with a mouse any of the P-T steps.

.. _data_export:

Export
******

Allows to write out data into csv spreadsheets.

* t results: calculated P and S travel times and corresponding standard deviations.
* Overview: waveforms stacked in the Overview plots.
* Correlation: selected waveform, selected echoes, filtered echoes, and correlation data.

.. _tof_sec_overview:

Overview
^^^^^^^^
- :ref:`Top row controls <tof_overview_controls>`
- :ref:`Plot tabs <tof_overview_plot_tabs>`
- :ref:`Scroll bar <tof_overview_scroll_bar>`


.. _tof_overview_controls:

Top row controls
****************

* Scale: Adjust the scaling of the stacked waveforms. Alternatively, hold Control key (Command key on Mac) while scrolling over the stacked plot to adjust the scaling. 

* Clip: Check or uncheck to the display clipped or full-range stacked signals. 

* \ :math:`f` start and \ :math:`f` step: enter values based on your experimental settings. The program uses the \ :math:`f` start and \ :math:`f` step values to calculate the frequency of the waveform.

.. _tof_overview_plot_tabs:

Plot tabs
*********

Frequency tab shows stacked waveforms at fixed frequency and varying P-T conditions. Conversely, P-T step tab shows fixed P-T condition but varying frequencies. 

Clicking any of the stacked wafeforms selects it. The selected waveform is displayed in a different color.

Saved echoes are highlighted in a different color.

.. _tof_overview_scroll_bar:

Scroll bar
**********

The scroll bar and the :guilabel:`-` :guilabel:`+` buttons underneath the Overview section can be used to change the displayed frequency or the P-T step, depending on the selected tab. 

.. _tof_sec_correlation:

Echo correlation
^^^^^^^^^^^^^^^^

.. _tof_correlation_controls:

Top row controls
****************

* \ :math:`f`: displays the frequency that should be used for filtering the selected wafeform. In Discrete \ :math:`f` mode the \ :math:`f` is updated based on the \ :math:`f` start and \ :math:`f` step in the Overview section. In Broadband mode, the \ :math:`f` may be adjusted freely.

* Echo 1 and 2: click the waveform plot at the lower \ :math:`t` bound of the echo to move the curser to that position then and click :guilabel:`Echo 1` or :guilabel:`Echo 2` to set the poistions of the R1 and R2 echoes, respectively. 

* P and S: select :guilabel:`P` for longitudinal or :guilabel:`S` for shear before setting the positions of the R1 and R2 echoes. 

* Save: click :guilabel:`Save` to accept the calculated correlation.

.. _tof_correlation_selected:

Selected wafeform plot
**********************

.. _tof_correlation_correlation:

Echo correlation plot tabs
**************************

.. _tof_sec_batch:

Multiple frequency batch processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _tof_sec_inverse:

Inverse frequency plot
^^^^^^^^^^^^^^^^^^^^^^

.. _tof_sec_output:

Results output
^^^^^^^^^^^^^^

