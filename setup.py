import setuptools
import os

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('MiraTitanHMFemulator/VERSION', 'r') as version_file:
    version = version_file.read().strip()


setuptools.setup(
    name="MiraTitanHMFemulator",
    version=version,
    author="Sebastian Bocquet",
    author_email="sebastian.bocquet@gmail.com",
    description="Mira-Titan Universe: Halo mass function emulator",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/SebastianBocquet/MiraTitanHMFemulator",
    packages=['MiraTitanHMFemulator'],
    package_data = {'MiraTitanHMFemulator': ['VERSION', 'data/*.npy', 'tests/*py']},
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = ['numpy', 'scipy'],
)
