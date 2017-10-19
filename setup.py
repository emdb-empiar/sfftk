# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup, find_packages

setup(
    name = "sfftk",
    version = "0.1.1.dev0",
    packages = find_packages(),
    author = "Paul K. Korir, PhD",
    author_email = "pkorir@ebi.ac.uk, paul.korir@gmail.com",
    description = "Toolkit for working with EMDB-SFF and other segmentation file formats",
    url = "https://ccpforge.cse.rl.ac.uk/gf/project/ccpem/scmsvn/?action=browse&path=%2Fsrc%2Fccpem_progs%2Femdb_sfftk%2F",
    license = "Apache License",
    keywords = "EMDB-SFF, SFF, segmentation",
    install_requires= ["ahds", "lxml", "h5py", "requests", "scikit-image", "bitarray", "numpy-stl"],
    classifiers = [
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
