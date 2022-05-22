.. _imageanalysis:

Image analysis
==================

Image analysis software is used to determine the sample thickness which corresponds to the ulstrasound 
wave travel distance (\ :math:`d`).
This chapter describes the :ref:`GUI basics <gui>` of the Image analysis software and provides an :ref:`example Workflow <workflow>` for determining the sample thickness.


.. _gui:

GUI basics
----------

.. figure:: /images/ia_start.png
   :alt: image_analysis_start_screen 
   :width: 720px
   :align: center
    
   Image analysis window

Control panel
^^^^^^^^^^^^^

- :ref:`Open <open>`
- :ref:`Compute  <compute>`
- :ref:`File  <opened_file>`
- :ref:`Thickness <thickness>`
- :ref:`Auto crop <autocrop>`
- :ref:`Sample type <sample_type>`
- :ref:`Polynomial order <poly_order>`
- :ref:`Fit threshold <fit_theshold>`


.. _open:

Open
****

Click :guilabel:`Open` button to navigate to and select an radiography image file. Typically the 
radiography files are saved in the ``Images`` folder
and have an extension ``*.tif``.

.. _opened_file:

Opened file
***********

Displays the file name of the opened image.

.. hint:: The file name can be copied by ``ctrl+C`` and pasted into a spreadsheet program, e.g. Excel.

.. _compute:

Compute
*******

The program extracts positions of the lower (Edge 1) and upper (Edge 2) edges by fitting a polynomial to edge pixel positions weighted by the the pixel intensities. 

.. _thickness:

Thickness
*********

The thickness of the sample and standard deviation are displayed in units of nubmer of pixels. 
   
   .. note:: Use an appropriate 
      \ :math:`{\mu}m / pixel` resolution for your camera to calculate the thickness 
      The relolution can be found in your calibration folder, typically in a file :file:`manta_resolution.docx`.

.. _autocrop:

Auto crop
*********

The relevant part of the image is automatically selected by a red box each time when a new image is opened. 

For cases where a manual selection is needed or if you want to keep the same red box position when opening new images, 
you can disable the autotomatic selection by un-selecting the :guilabel:`Auto crop` button. 

If you have manually adjusted the red box position and would like to go back to the automatic selection, 
select the :guilabel:`Auto crop` button. 
   

.. _sample_type:

Sample type
***********

Click the appropriate icon that looks closest to your sample edge configuration. 
For exaple, the image below has two thin gold foils as edges, in this case we select the first choice from the left:

   .. figure:: /images/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center

   .. figure:: /images/edge_types.png
      :alt: edge_types
      :width: 250px
      :align: center

.. _poly_order:

Polynomial order
****************

If an edge is very deformed try to use the option of polynomial order 3.

.. note:: 
   The average sample thickness obtained from tilted or deformed edges 
   may still be usable for sound velocity calculation since the 
   standard deviation will reflect the thickness uncertainty and 
   can be propagated to the sound velocity uncertainty.

.. _fit_theshold:

Fit threshold
*************

Choose the highest pixel threshold for the fit. The smaller it is, the brightest the pixels considered.


Plot panels
^^^^^^^^^^^

.. _source_image:

Source image 
************

   The top left panel displays the normalized image counts from the image, (I/I\ :sub:`0`).

   The red box delimits the relevant part of the image that will be used for finding the edges.

.. _crop:   

   .. note:: The red box can be adjusted by dragging the 
             diamond handles using a mouse. The region-of-interest selected by the red box
             will be used for subsequent computations and edge finding.

   .. figure:: /images/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center
      
.. _absorbance:

Absorbance
**********

   The bottom left panel displays the computed absorbance, (A) = -log\ :sub:`10` (I/I\ :sub:`0`), taken 
   from the part of the image selected by the red box in the :ref:`Source image <source_image>`. 

   The program will try to automatically find the edges after opening the image 
   file and select each edge with a region-of-interest box (green).

.. _edge_selection:  

   .. note:: 
      If the automatic edge finding fails, please select the edges manually. 
      The boxes can be adjusted by dragging the diamond handles using a mouse.
      In the case below the edges are the gold (Au) foils. 

   .. figure:: /images/edge_selection.png
      :alt: edge_selection
      :width: 500px
      :align: center

.. _edge_result:

Edge 1 (bottom edge) and Edge 2 (top edge)
******************************************

The top right and the bottom right panels will display the edge fit results (red dashed lines), overlaid over
the observed edges. Check that the fit is good by checking that the red dashed lines match well the positions of the edges. 
If the fit is not good, it may help to adjust the following:

   *  :ref:`Edge selection <edge_selection>`
   *  :ref:`Fit threshold <fit_theshold>`
   *  :ref:`Polynomial order <poly_order>`

   .. figure:: /images/edges_fitted.png
      :alt: edges_fitted
      :width: 600px
      :align: center

.. _workflow:

Workflow
--------

.. _step1:

1. Click :guilabel:`Open` button in the upper left corner. 
   Navigate to location of image file and open the file. The :ref:`source image <source_image>` will be displayed
   in the top left image panel. 

   .. note:: 
      The relevant part of the image is automatically selected, but manual :ref:`selection adjustment <crop>` may be needed.
             
   .. hint::
      Use the mouse scroll-wheel to zoom in and out of any of the images; the little :guilabel:`A` button in the lower left resets the zoom.

   .. figure:: /images/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center

2. The program displays the computed :ref:`absorbance image <absorbance>` in the bottom left panel and tries to find 
   the edges automatically. Green boxes are overlaid over the found edges.

   .. note:: 
      Make  sure make sure the edges are selected correctly by the green boxes.
      The green boxes can be :ref:`manually resized and/or re-positioned <edge_selection>`.

   .. figure:: /images/edge_selection.png
      :alt: edge_selection
      :width: 500px
      :align: center

3. Select the :ref:`sample edge type <sample_type>` based on your particular sample configuration. 

4. Once image cropped properly, click :guilabel:`Compute` in upper left corner. The fitted edge polynomials
   will be displayed in the :ref:`Edge panels <edge_result>`. 

   .. note:: 
      You may need to adjust the :ref:`fit threshold <fit_theshold>` for edges with non-uniform contrast. 

   .. note:: Ideally the edges should be fit with a polynomial of order 1 or 2. 
      However if the edge is not straight you can try to use a :ref:`higher order polynomial <poly_order>`.
     
   .. figure:: /images/edges_fitted.png
      :alt: edges_fitted
      :width: 600px
      :align: center

5. The thickness of the sample and standard deviation are displayed at the top of the 
   window in the units of number of pixels.  

   .. hint:: The file name and thickness output can be copied by ``ctrl+C`` and pasted into a 
      spreadsheet program, e.g. Excel.

6. Repeat steps 1-5 for each image that you recorded and record the 
   fitted distances and standard deviations 
   in a spreadsheet
   


   .. note:: If you recorded multiple images per data-point (e.g. left + center + right), 
      use may need to compute the average thickness for the sound velocity estimation.




