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

The emulator is confirmed to run properly on python 3.8.2 (numpy 1.18.1, scipy
1.4.1), python 3.6.9 (numpy 1.17.4, scipy 1.3.2), and python 2.7 (numpy 1.15.4,
scipy 0.19.1).

Installing and testing
----------------------

I recommend you use ``pip``. Just do::

  pip install MiraTitanHMFemulator

You may want to test the installation::

  cd /path/to/MiraTitanHMFemulator
  pytest

The tests take about 20 seconds on my laptop and should confirm that you are all
set.
