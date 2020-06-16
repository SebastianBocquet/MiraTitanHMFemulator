MiraTitanHMFemulator
============================

This package provides the emulator for the halo mass function (HMF) from the
*Mira-Titan Universe* suite of cosmological *N*-body simulations.

Installation
------------

This python package only requires the standard packages numpy and scipy. Simply
install using ``pip``::

  pip install MiraTitanHMFemulator

and then ``pytest`` to validate your installation::

  cd /path/to/MiraTitanHMFemulator
  pytest

With every test passed you are good to go!

Documentation
-------------

Documentation is hosted at `ReadTheDocs
<http://MiraTitanHMFemulator.readthedocs.io/>`_. Find examples for how to use
the emulator there!

Citation
--------

Please cite our paper when you use the *Mira-Titan* HMF emulator::

  @ARTICLE{Bocquet2020arXiv200312116B,
           author = {{Bocquet}, Sebastian and {Heitmann}, Katrin and {Habib}, Salman and
                     {Lawrence}, Earl and {Uram}, Thomas and {Frontiere}, Nicholas and
                     {Pope}, Adrian and {Finkel}, Hal},
           title = "{The Mira-Titan Universe. III. Emulation of the Halo Mass Function}",
           journal = {arXiv e-prints},
           keywords = {Astrophysics - Cosmology and Nongalactic Astrophysics},
           year = 2020,
           month = mar,
           eid = {arXiv:2003.12116},
           pages = {arXiv:2003.12116},
           archivePrefix = {arXiv},
           eprint = {2003.12116},
           primaryClass = {astro-ph.CO},
           adsurl = {https://ui.adsabs.harvard.edu/abs/2020arXiv200312116B},
           adsnote = {Provided by the SAO/NASA Astrophysics Data System}}


Feedback, problems, questions
-----------------------------

Please `report issues on GitHub
<https://github.com/SebastianBocquet/MiraTitanHMFemulator/issues>`_ where the
package is hosted.

.. image:: https://zenodo.org/badge/225578117.svg
   :target: https://zenodo.org/badge/latestdoi/225578117
