.. _imageanalysis:

Image analysis
==================

Image analysis software is used to determine the sample thickness.
This section describes the Image analysis software and provides an example Workflow for determining the sample thickness.

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


.. _opened_file:

Opened file
***********

.. _compute:

Compute
*******

The program extracts positions of the lower (Edge 1) and upper (Edge 2) edges by fitting a polynomial to edge pixel positions weighted by the the pixel intensities. 

.. _thickness:

Thickness
*********

.. _autocrop:

Auto crop
*********

.. _sample_type:

Sample type
***********

.. figure:: /images/edge_types.png
   :alt: edge_types
   :width: 250px
   :align: center

.. _poly_order:

Polynomial order
****************

If an edge is very deformed try to use the polynomial of order 3.

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

   This panel displays the normalized image counts from the image, (I/I\ :sub:`0`).

.. _crop:   

   .. note:: The cropping-rechangle (red) can be adjusted by dragging the 
             diamond handles using a mouse. The region-of-interest selected by the cropping-rengangle 
             will be used for subsequent computations and edge finding.

   .. figure:: /images/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center
      
.. _absorbance:

Absorbance
**********

   This panel displays the computed absorbance, (A) = -log\ :sub:`10` (I/I\ :sub:`0`), taken 
   from the region of interest selected in the Source image.

.. _edge_selection:  

   .. note:: The program will try to automatically find the edges after opening the image 
      file and select each edge with a region-of-interest box (green).
      If the automatic edge finding fails, please select the edges manually 
      using the green rengangles. The boxes can be adjusted by dragging the diamond handles using a mouse.
      In the case below the edges are the gold (Au) foils. 

   .. figure:: /images/edge_selection.png
      :alt: edge_selection
      :width: 500px
      :align: center

Edge 1 (bottom edge) and Edge 2 (top edge)
******************************************

   

Workflow
--------

.. _step1:

1. Click :guilabel:`Open` button in the upper left corner. 
   Navigate to location of image file and open the file. The :ref:`source image <source_image>` will be displayed
   in the top left image panel. The red box delimits the 
   relevant part of the image that will be used for finding the edges (top left panel).

   .. note:: 
      The relevant part of the image is automatically selected, but manual :ref:`selection adjustment <crop>` may be needed.
             
   .. hint::
      Use the mouse scroll-wheel to zoom in and out of any of the images; the little "a" button in the lower left resets the zoom.

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

3. Select the sample edge type based on your particular sample configuration. Click the appropriate
   icon that looks closest to your sample edge configuration. For exaple, the image in :ref:`step 1 <step1>` above 
   has two thin gold foils as edges, in this case we select the first choice from the left:

   .. figure:: /images/edge_types.png
      :alt: edge_types
      :width: 250px
      :align: center

4. Once image cropped properly, click :guilabel:`Compute` in upper left corner.

   .. note:: 
      You may need to adjust the :ref:`fit threshold <fit_theshold>` for edges with non-uniform contrast. 

   .. note:: Ideally the edges should be fit with a polynomial of order 1 or 2. 
      However if the edge is not straight you can try to use a :ref:`higher order polynomial <poly_order>`.
     
   .. figure:: /images/edges_fitted.png
      :alt: edges_fitted
      :width: 600px
      :align: center

5. The thickness of the sample and standard deviation, in pixels, are displayed at the top of the window. 
   
   .. note:: Use an appropriate 
      \ :math:`{\mu}m / pixel` resolution for your camera to calculate the thickness 
      The relolution can be found in your calibration folder, typically in a file :file:`manta_resolution.docx`.

6. Repeat steps 1-5 for each image that you recorded and record the 
   fitted distances and standard deviations 
   in a spreadsheet
   
   .. hint:: The file name and thickness output can be copied ``ctrl+C`` and pasted into a 
      spreadsheet program, e.g. Excel.

   .. note:: If you recorded multiple images per data-point (e.g. left + center + right), 
      use may need to compute the average thickness for the sound velocity estimation.




