.. _ia_workflow:

Example walkthrough
-------------------

.. _step1:

1. Click :guilabel:`Open` button in the upper left corner. 
   Navigate to location of image file and open the file. The :ref:`source image <source_image>` will be displayed
   in the top left image panel. 

   .. figure:: /images/ia/i_0.png
      :alt: i/i_0
      :width: 500px
      :align: center
  
   .. note:: 
      The relevant part of the image is automatically selected, but manual :ref:`selection adjustment <crop>` may be needed.
             
   .. hint::
      Use the mouse scroll-wheel to zoom in and out of any of the images; the little :guilabel:`A` button in the lower left resets the zoom.

   

2. The program displays the :ref:`selected edges <absorbance>`
   automatically. Adjustable green boxes are overlaid over the selected edges.

   .. note:: 
      Make  sure make sure the edges are selected correctly by the green boxes.
      The green boxes can be :ref:`manually resized and/or re-positioned <edge_selection>`.

   .. figure:: /images/ia/edge_selection.png
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
     
   .. figure:: /images/ia/edges_fitted.png
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




