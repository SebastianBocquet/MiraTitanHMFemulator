============
Installation
============

Required packages
-----------------

The ``MiraTitanHMFemulator`` only requires a very minimal ``python``
installation:

 * python
 * numpy
 * scipy
 * pytest (optional but recommended -- only needed to test the installation)

The emulator is confirmed to run properly on python 3.6 (numpy 1.17.4, scipy
1.3.2) and python 2.7 (numpy 1.15.4, scipy 0.19.1).

Installing and testing
----------------------

I recommend you use ``pip``. Just do::

  pip install git+https://github.com/SebastianBocquet/MiraTitanHMFemulator

To make sure nothing bad has happened you should then test the installation::

  cd /path/to/MiraTitanHMFemulator
  pytest

This should take about 20 seconds and should confirm that you are all set. I
suggest you now checkout out the `tutorial notebook
<https://github.com/SebastianBocquet/MiraTitanHMFemulator/blob/master/tutorial.ipynb>`_
to familiarize yourself with the emulator.
