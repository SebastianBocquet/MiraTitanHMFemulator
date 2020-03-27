import inspect
import os

version_filename = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[0][1])), 'VERSION')
with open(version_filename, 'r') as version_file:
    __version__ = version_file.read().strip()

__author__ = "Sebastian Bocquet"
__email__ = "sebastian.bocquet@gmail.com"

from .MiraTitanHMFemulator import Emulator
