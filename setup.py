# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="sfftk",
    version="0.2.1.dev3",
    packages=find_packages(),
    author="Paul K. Korir, PhD",
    author_email="pkorir@ebi.ac.uk, paul.korir@gmail.com",
    description="Toolkit for working with EMDB-SFF and other segmentation file formats",
    long_description=long_description,
    url="http://sfftk.readthedocs.io/en/latest/index.html",
    license="Apache License",
    keywords="EMDB-SFF, SFF, segmentation",
    install_requires=["ahds", "lxml", "h5py==2.6.0", "requests", "scikit-image", "bitarray", "numpy-stl",
                      "configparser", "backports.shutil_get_terminal_size"],
    classifiers=[
        # maturity
        'Development Status :: 2 - Pre-Alpha',
        # environment
        'Environment :: Console',
        # audience
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # license
        'License :: OSI Approved :: Apache Software License',
        # python version
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'sff = sfftk.sff:main',
        ]
    },
)
