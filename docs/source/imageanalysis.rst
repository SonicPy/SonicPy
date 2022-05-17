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
   
   Image analysis window after start-up.

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

Open
****

Compute
*******

Thickness
*********

Auto crop
*********

Sample type
************

Polynomial order
****************

Fit threshold
*************

Plot panels
^^^^^^^^^^^

Source image 
************

   This panel displays the normalized image counts from the image, (I/I\ :sub:`0`).

   .. figure:: /images/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center
      
   
   .. note:: The cropping-rechangle (red) can be adjusted by dragging the 
             diamond handles using a mouse. The region-of-interest selected by the cropping-rengangle 
             will be used for subsequent computations and edge finding.

Absorbance
**********

   This panel displays the computed absorbance, (A) = -log\ :sub:`10` (I/I\ :sub:`0`), taken 
   from the region of interest selected in the Source image.

   .. figure:: /images/edge_selection.png
      :alt: edge_selection
      :width: 500px
      :align: center

   .. note:: The program will try to automatically find the edges after opening the image 
      file and select each edge with a region-of-interest rectangle (green).
      If the automatic edge finding fails, please select the edges manually 
      using the green rengangles. The rectangles can be adjusted by dragging the diamond handles using a mouse.

Edge 1 (bottom edge) and Edge 2 (top edge)
******************************************

   


.. _open:

.. _compute:

.. _opened_file:

.. _thickness:

.. _autocrop:

.. _sample_type:

.. _poly_order:

.. _fit_theshold:


Workflow
--------


1. Click "Open" button upper left
   | Navigate to location of image files


   | Open respective images

   .. note:: Workings:
             Frame is automatically cropped, might need to crop up properly
             Scroll = zoom in and out on photo; the little "a" button in the lower left resets zoom

   | Anne
   | Open Image Analysis
   | Click Open -> select image
   | ->	Box select image (on top left).

2. Can resize the crop by the "handles" on the sides

   .. note:: Science: We want to fit the absorbance instead of the raw image

   .. note:: Workings: the program tries to find edges of absorbance automatically, draws rectangles where the edges of the sample are
   
   - You might need to readjust the crop to get the edges of the sample correct
   - In my case, this is the gold foil

   | Anne
   | ->	Bottom left plot: boxes to adjust (edges)
   | -> inverse of top image (absorbance)

3. Also need to do this for the sample edges in the bottom window (make sure they are selected correctly by the boxes)

4. Assuming we keep default sample type and polynomial order
5. Once image cropped properly, click "compute" in upper left corner

   .. note:: Extracts positions on the upper and lower edges and fits a polynomial line (regression fit)

   | Anne
   | Click compute (top left) -> polynomial fit to the pixel intensities for edges.
   | Pg calculates the average distance + std deviation
   | (Values listed @ the top)

   | Fit threshold: choose the highest pixel threshold for the fit.
   | The smaller it is, the brightest the pixels considered.

   | If bottom Au foil is  ͝  (not straight)
   | ->	try to take the average     .
   | and the bottom & then compare. \-> or fit the flat edge if there is one.
   | Icon to choose for fit 
   | Std dev will be high w/   ͝    foil.

6. Then, at the top of the window, the thickness of the sample in pixels is displayed. Then use the um/pixel ratio for your camera to calculate thickness

   - This is in our folder already = manta resolution -> manta resolution

7. Now go though each image and find fitted distance

   .. note:: Remember!

   For left and right sample images, take the average of left and right thicknesses and figure out correct way to include standard deviation!





