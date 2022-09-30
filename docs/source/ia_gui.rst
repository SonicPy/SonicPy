

.. _ia_gui_im:

GUI basics
----------

- :ref:`Control panel <ia_control_panel>`
- :ref:`File list <ia_file_list>`
- :ref:`Plot panels  <ia_plot_panels>`


.. figure:: /images/ia/ia_start.png
   :alt: image_analysis_start_screen 
   :width: 720px
   :align: center
    
   Image analysis window

.. _ia_control_panel:

Control panel 
^^^^^^^^^^^^^

- :ref:`Open folder <ia_open_folder>`
- :ref:`Save results  <ia_save_results>`
- :ref:`Open <ia_open>`
- :ref:`Compute  <ia_compute>`
- :ref:`File  <ia_opened_file>`
- :ref:`Thickness <ia_thickness>`
- :ref:`Auto crop <ia_autocrop>`
- :ref:`Sample type <ia_sample_type>`
- :ref:`Polynomial order <ia_poly_order>`
- :ref:`Fit threshold <ia_fit_theshold>`

.. _ia_open_folder:

Open folder
***********

Click :guilabel:`Open folder` button to navigate to and select the ``Images`` folder. The folder should contain radiography images with an extension ``*.tif``.

.. _ia_save_results:

Save results
************

Click :guilabel:`Save results` button to write out the results to a csv spreadsheet.

.. _ia_open:

Open
****

Click :guilabel:`Open` button to navigate to and select an radiography image file. Typically the 
radiography files are saved in the ``Images`` folder
and have an extension ``*.tif``.

.. _ia_opened_file:

Opened file
***********

Displays the file name of the opened image.

.. hint:: The file name can be copied by ``ctrl+C`` and pasted into a spreadsheet program, e.g. Excel.

.. _ia_compute:

Compute
*******

The :guilabel:`Compute` button is a checkable button. When clicked the button will be in a checked state and highlighted orange. Clicking again unchecks the button. While in checked state the distances will be calculated automatically after selecting a file. The program extracts positions of the lower (Edge 1) and upper (Edge 2) edges by fitting a polynomial to edge pixel positions weighted by the the pixel intensities. 

.. _ia_thickness:

Thickness
*********

The thickness of the sample and standard deviation are displayed in units of nubmer of pixels. 
   
   .. note:: Use an appropriate 
      \ :math:`{\mu}m / pixel` resolution for your camera to calculate the thickness 
      The relolution can be found in your calibration folder, typically in a file :file:`manta_resolution.docx`.

.. _ia_autocrop:

Auto crop
*********

The relevant part of the image is automatically selected by a red box each time when a new image is opened. 

For cases where a manual selection is needed or if you want to keep the same red box position when opening new images, 
you can disable the autotomatic selection by un-selecting the :guilabel:`Auto crop` button. 

If you have manually adjusted the red box position and would like to go back to the automatic selection, 
select the :guilabel:`Auto crop` button. 
   

.. _ia_sample_type:

Sample type
***********

Click the appropriate icon that looks closest to your sample edge configuration. 
For exaple, the image below has two thin gold foils as edges, in this case we select the first choice from the left:

   .. figure:: /images/ia/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center

   .. figure:: /images/ia/edge_types.png
      :alt: edge_types
      :width: 250px
      :align: center

.. _ia_poly_order:

Polynomial order
****************

If an edge is very deformed try to use the option of polynomial order 3.

.. note:: 
   The average sample thickness obtained from tilted or deformed edges 
   may still be usable for sound velocity calculation since the 
   standard deviation will reflect the thickness uncertainty and 
   can be propagated to the sound velocity uncertainty.

.. _ia_fit_theshold:

Fit threshold
*************

Choose the highest pixel threshold for the fit. The smaller it is, the brightest the pixels considered.


.. _ia_file_list:

File list
^^^^^^^^^
The file list panel displays the files in the currently opened folder. Clicking on a file selects it for processing. Calculated distance and uncertainty will be displayed next to a selected file.



.. _ia_plot_panels:

Plot panels
^^^^^^^^^^^

.. _ia_source_image:

Source image 
************

   The top left panel displays the normalized image counts from the image, (I/I\ :sub:`0`).

   The red box delimits the relevant part of the image that will be used for finding the edges.

.. _ia_crop:   

   .. note:: The red box can be adjusted by dragging the 
             diamond handles using a mouse. The region-of-interest selected by the red box
             will be used for subsequent computations and edge finding.

   .. figure:: /images/ia/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center
      
.. _ia_absorbance:

Edge selection
**************

   The bottom left panel displays the computed absorbance, (A) = -log\ :sub:`10` (I/I\ :sub:`0`), taken 
   from the part of the image selected by the red box in the :ref:`Source image <ia_source_image>`. 

   The program will automatically locate the top and the bottom edges and overlay each edge with a green box.

.. _ia_edge_selection:  

   .. note:: 
      If the automatic edge finding fails, please select the edges manually. 
      The boxes can be adjusted by dragging the diamond handles using a mouse.
      In the case below the edges are the gold (Au) foils. 

   .. figure:: /images/ia/edge_selection.png
      :alt: edge_selection
      :width: 500px
      :align: center

.. _ia_edge_result:

Edge 1 (bottom edge) and Edge 2 (top edge)
******************************************

The top right and the bottom right panels will display the edge fit results (red dashed lines), overlaid over
the observed edges. Check that the fit is good by checking that the red dashed lines match well the positions of the edges. 
If the fit is not good, it may help to adjust the following:

   *  :ref:`Edge selection <ia_edge_selection>`
   *  :ref:`Fit threshold <ia_fit_theshold>`
   *  :ref:`Polynomial order <ia_poly_order>`
 
   .. figure:: /images/ia/edges_fitted.png
      :alt: edges_fitted
      :width: 600px
      :align: center

 

