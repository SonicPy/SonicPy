.. _tof_analysis:

Time of flight analysis
=======================

This section describes Time of flight analysis


Workflow Jonathan
-----------------

1. First, enter information about Ultrasonic measurements so the program knows which frequency you started and ended at (enter in upper top middle left boxes)
2. Then click "open folder" in the upper left. Find and select folder with ultrasound data
3. Two tabs = frequency and P-T condition

.. note:: Science: in frequency tab, looking at spectra with same frequency, but different pressures (0-8100psi)
    In the P-T tab, looking at same pressure but different frequencies (16-50mhz)

.. note:: Workings:
    The scale on the left side orders first files on the bottom, last files on top
    Can click individual signals and they display in the upper right window
    When when you switch tabs, it keeps the correct signal selected between left & upper right windows

4. Need to select two echoes: sample echo and buffer rod echo. Once you select, goes to different view to help select echoes

.. note:: Science: The ones that shift aren't noise, those are actual signal from experiment

| Stationary echoes are reflections from the other parts of the Ultrasonic apparatus
| Higher pressure: sound speed increases as well

5. Processing

Select one wave, and correlate the echoes right next to each other

- Helpful to zoom in on that region when selecting

.. note:: Workings: The plots are linked so clicking in the bigger one moves the cursor in the upper right smaller one
    
Select the first peak (center between the largest peaks) then click "echo 1"

- Pressure waves travel faster so they're the first pair before the shear waves

Select second echo with ROI and click "echo two" (still p-wave)

.. note:: Science: cyan and magenta waves are filtered to get just frequency

.. note:: Science: based on fourier transform - the signal is a combo of many frequencies - we are singling out the frequency of interest

.. note:: Science: So we are shift the signals in time and see when they produce the most constructive interference (or when they overlap the most)

.. note:: Science: The phase shift that produces the largest constructive interference is the value that contains our travel time (check on this)

The green plot is a plot of the phase shift between the cyan & magenta signals and the interference it produces at each phase shift

- We will get a plot of maxima and minima as the signals go in and out of phase where the x-axis lists the current phase shift and the y-axis is the amplitude of interference
- This data is exported to create an inverse frequency graph which is the last step before we determine the travel time

Once cross-correlation complete, click "save correlation" in the upper right corner

Uses same filename as original ultrasonic signal and saves as JSON file

- Contains info about time, x-axis for minima and maxima, bounds of echoes

- This is reference data, not for analysis

Complete the process again on the same signal, but find the shear waves within the signal
First zoom out (little "a" button) on upper plot to see cursor, then zoom in to view shear waves

.. important:: IMPORTANT: Select S-Waves in the upper middle of the window to denote you are finding shear waves!

- This saves the cross correlations in a new folder labeled "S" instead of a folder labeled "P" for the P-Wave data we found previously
- So make sure you keep track of which wave you are specifying so that the information saves to the right folder
- Example: don't want to find P-Wave travel time, but have S-Wave selected, so the data is incorrectly saved to the S-Wave folder

Now select the "echo 1" button, drag the bounds to contain it, then select "echo 2" and drag the bounds to contain it (all S-Wave data)
Get the green plot again for cross-correlation and save it

.. hint:: *****Tip: this process is required for each frequency and each P-T condition (both tabs)*****

.. hint:: Tip: the regions of interest stay in position so, if for example you're finding P-Wave echoes, you can click each signal and the echoes will most likely remain within the ROI

- You might find that at higher/lower frequencies you need to shift ROIs to keep echoes you want inside the bounds

Then click "save correlation"


2. Travel Time Determination

Once all of your correlation data is recorded, click "inverse f" at the upper right corner

.. note:: Science: This is the arrow plot I've seen before!

Next, click "open" (upper right)

Select all of the .json files to load them

Now the minima and maxima have been loaded

.. note:: Science: vertical axis is the time axis which is the same horizontal axis on the green plot

.. note:: Science: horizontal axis is inverse frequency

Now for analysis, all you need to do is click the "auto" button 

.. note:: Science: the program performs linear regression and extrapolates to zero frequency

- The intersection of the regressions is the two-way travel time of the ultrasonic wave in the sample

Semi-Important Note: There is checkmark at the upper left marked with the "plus or minus" symbol

- When checked you are looking at maxima, when not checked you are looking at minima
- This is important because both settings might give slightly different delays, but ideally should give same delay.
- Good Practice: record both results to see what the differences might be

First, calculate with the "plus" setting, then calculate with the "minus" setting

The result you should use for calculations is the one where the blue set has the flattest slope

- This is because, for example, "plus" might not be as flat as "minus"
- The choice actually depends on the material and the impedances between it and the buffer rod
- If buffer rod impedance lower or higher then sample impedence) then it will get reflected with a phase shift (either inverts ot doesn't invert)

The time delay is listed at the bottom of the window, with standard deviation next to it

Now copy these values to the spreadsheet to keep track of them

.. hint:: Extra Tip(s): 

    - The data contained in the spreadsheet is for analysis
    - It is your choice to keep data on ANL computer or personal computer
    - It is reccomended to keep a copy at Argonne in case your personal data is lost
    - Our specific experiment folder can be resynced for Globus if original data is needed

Workflow Anne
-------------

* Time – of – flight analysis software:

difference between R1 reflection & R2 reflection = double travel time
	
    * R2-R1 = 2 τ

Multiple freq method

-> Pantea et al. Rev. Sci. Instr. 2005

Cross- correlation : measures the interference between 2 wave-forms.

->	calculate the time delay between 2 pulses.

In software:

Open folder

Left plot: data @ fixed frequency
	
    * stacked @ # Pressures.

| Scale bar @ bottom: to change frequency.
| R0 : reflection @ ~ 4 µsec
| Distance shifts as P↑ cos sample gets thinner
| Clip or not clip (box @ top): might help w/visualization (or not).
| Select 1 waveform -> sown on top right plot.
| Start freq & freq step : enter it from our notebook.
| (P-T stop tab – data stacked as function of freq for fixed P-T.)
| Vp	Select a peak, place vertical line at center

| Click Echo 1 -> define region
| Select second peak
| Click Echo 2

* does the cross correlation (bottom right plots).

| There’s some flexibility on peak selection.
| Vs	Click on S-wave (top right)
| Make sure to click on “save correlation” each time*
| Back to P-wave & P-T step -> save correlation individually

* = for each T & each frequency.

| Compressional signal : maximized @ high freq
| Shear signal: visible @ low freq

* Create inverse freq. plot: using the files collected above. Done in the same software.

| Top right: “inverse f” button -> click on it
| ->	window appears -> open 

*	select file

| Plot is time delay as a function of frequency.
| Click Auto -> fits the lines
| Calculates the delay @ ∞ freq
| (@ the bottom of plot).
| Typo = time delay axis -> unit is not sec.
| The calculated time delay is the double travel time -> ÷2.

| ->	We now have sample thickness & travel time
| -->Vp & Vs can be calculated

| Sample 3: R1 starts @4.6 µs.
| At lower time: R0 & electrical noise
| R2: likely @ 4.8 µs (not 4.9)->R3
| Inverse freq. plot: to remove data @ specific freq: either do not select the files or select these data + calculate again.
