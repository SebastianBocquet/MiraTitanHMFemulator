============
Installation
============

Required packages
-----------------

The ``MiraTitanUniverseHMFemulator`` only requires a very minimal ``python``
installation:

 * python
 * numpy
 * scipy
 * pytest (optional but recommended -- only needed to test the installation)


Installing and testing
----------------------

I recommend you use ``pip``. Just do::

  pip install git+https://github.com/SebastianBocquet/MiraTitanUniverseHMFemulator

To make sure nothing bad has happened you should then test the installation::

  cd /path/to/MiraTitanUniverseHMFemulator
  pytest

This should take 10-15 seconds and should confirm that you are all set. I
suggest you now checkout out the `tutorial notebook
<https://github.com/SebastianBocquet/MiraTitanUniverseHMFemulator/blob/master/tutorial.ipynb>`_
to familiarize yourself with the emulator.
