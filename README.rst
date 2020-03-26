MiraTitanHMFemulator
============================

This package provides the emulator for the halo mass function (HMF) from the
*Mira-Titan Universe* suite of cosmological *N*-body simulations.

Installation
------------

This python package only requires the standard packages numpy and scipy. Simply
install using ``pip``::

  pip install git+https://github.com/SebastianBocquet/MiraTitanHMFemulator

and then ``pytest`` to validate your installation::

  cd /path/to/MiraTitanHMFemulator
  pytest

With every test passed you are good to go!

Documentation
-------------

Documentation is hosted at `ReadTheDocs
<http://MiraTitanHMFemulator.readthedocs.io/>`_. Alternatively, take a
look at the `tutorial notebook on GitHub
<https://github.com/SebastianBocquet/MiraTitanHMFemulator/blob/master/tutorial.ipynb>`_
for a working example.

Citation
--------

Please cite our paper when you use the *Mira-Titan* HMF emulator::

  @article{Bocquet2020,
           author = {{Bocquet}, Sebastian and {Heitmann}, Katrin and
                     {Habib}, Salman and {Lawrence}, Earl and
                     {Uram}, Thomas and {Frontiere}, Nicholas and
                     {Pope}, Adrian and {Finkel}, Hal},
           title = "{The Mira-Titan Universe. III. Emulation of the Halo Mass Function}",
           year = "2020",
           journal = {arXiv e-prints},}

Feedback, problems, questions
-----------------------------

Please `report issues on GitHub
<https://github.com/SebastianBocquet/MiraTitanHMFemulator/issues>`_ where the
package is hosted.
