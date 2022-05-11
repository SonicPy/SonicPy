.. _settingup:

Setting up sonicPy
==================

The latest stable executable versins of the package **sonicPy** can be downloaded from github.com/hrubiak/sonicpy/releases


Image Analysis
--------------

Shortcuts are the two icons at the upper left of the desktop separate from everything


1.
Click "Open" button upper left
Navigate to location of image files
- PEC drive -> data -> 2021-2 -> CDAC -> Aihaiti

Open respective images
Workings:
Frame is automatically cropped, might need to crop up properly
Scroll = zoom in and out on photo; the little "a" button in the lower left resets zoom
2.
Can resize the crop by the "handles" on the sides
Science: We want to fit the absorbance instead of the raw image
Workings: the program tries to find edges of absorbance automatically, draws rectangles where the edges of the sample are
- You might need to readjust the crop to get the edges of the sample correct
- In my case, this is the gold foil
3.
- Also need to do this for the sample edges in the bottom window (make sure they are selected correctly by the boxes)

4.
Assuming we keep default sample type and polynomial order
5.
Once image cropped properly, click "compute" in upper left corner
Workings: Extracts positions on the upper and lower edges and fits a polynomial line (regression fit)
6.
Then, at the top of the window, the thickness of the sample in pixels is displayed. Then use the um/pixel ratio for your camera to calculate thickness
- This is in our folder already = manta resolution -> manta resolution

7.
Now go though each image and find fitted distance

.. admonition:: Remember!

   For left and right sample images, take the average of left and right thicknesses and figure out correct way to include standard deviation!



.. figure:: /images/time-of-flight.png
   :alt: Time-of-Flight program
   :scale: 40 %
   :align: center

   *Time-of-Flight program*


