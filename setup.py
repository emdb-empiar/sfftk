# -*- coding: utf-8 -*-
# setup.py
import sys

from setuptools import setup, find_packages

from sfftk import SFFTK_VERSION

with open(u'README.rst') as f:
    long_description = f.read()

SFFTK_NAME = u"sfftk"
SFFTK_AUTHOR = u"Paul K. Korir, PhD"
SFFTK_AUTHOR_EMAIL = u"pkorir@ebi.ac.uk, paul.korir@gmail.com"
SFFTK_DESCRIPTION = u"Toolkit for working with EMDB-SFF and other segmentation file formats"
SFFTK_DESCRIPTION_CONTENT_TYPE = u'text/x-rst; charset=UTF-8'
SFFTK_URL = u"http://sfftk.readthedocs.io/en/latest/index.html"
SFFTK_LICENSE = u"Apache License"
SFFTK_KEYWORDS = u"EMDB-SFF, SFF, segmentation"
SFFTK_CLASSIFIERS = [
    # maturity
    u"Development Status :: 2 - Pre-Alpha",
    # environment
    u"Environment :: Console",
    u"Intended Audience :: Developers",
    u"Intended Audience :: Science/Research",
    # license
    u"License :: OSI Approved :: Apache Software License",
    # os
    u"Operating System :: OS Independent",
    # python versions
    u"Programming Language :: Python :: 2",
    u"Programming Language :: Python :: 2.7",
    u"Programming Language :: Python :: 3",
    u"Programming Language :: Python :: 3.5",
    u"Programming Language :: Python :: 3.6",
    u"Programming Language :: Python :: 3.7",
    u"Programming Language :: Python :: 3.8",
    u"Topic :: Software Development :: Libraries :: Python Modules",
    u"Topic :: Terminals",
    u"Topic :: Text Processing",
    u"Topic :: Text Processing :: Markup",
    u"Topic :: Utilities",
]
if sys.version_info[0] > 2:
    SFFTK_PYTHON3_INSTALL_REQUIRES = ["sfftk-rw", "ahds", "styled", "mrcfile", "bitarray", "requests",
            "mock",
            "numpy-stl"]
    if sys.version_info[1] == 5:
        SFFTK_PYTHON3_INSTALL_REQUIRES += ["pyOpenSSL"]
    setup(
        name=SFFTK_NAME,
        version=SFFTK_VERSION,
        packages=find_packages(),
        author=SFFTK_AUTHOR,
        author_email=SFFTK_AUTHOR_EMAIL,
        description=SFFTK_DESCRIPTION,
        long_description=long_description,
        long_description_content_type=SFFTK_DESCRIPTION_CONTENT_TYPE,
        url=SFFTK_URL,
        license=SFFTK_LICENSE,
        keywords=SFFTK_KEYWORDS,
        setup_requires=["numpy"],
        install_requires=SFFTK_PYTHON3_INSTALL_REQUIRES,
        classifiers=SFFTK_CLASSIFIERS,
        entry_points={
            'console_scripts': [
                'sff = sfftk.sff:main',
            ]
        },
        package_data={
            'sfftk': ['sff.conf'],
        }
    )
else:
    setup(
        name=SFFTK_NAME,
        version=SFFTK_VERSION,
        packages=find_packages(),
        author=SFFTK_AUTHOR,
        author_email=SFFTK_AUTHOR_EMAIL,
        description=SFFTK_DESCRIPTION,
        long_description=long_description,
        long_description_content_type=SFFTK_DESCRIPTION_CONTENT_TYPE,
        url=SFFTK_URL,
        license=SFFTK_LICENSE,
        keywords=SFFTK_KEYWORDS,
        setup_requires=["numpy<1.17"],
        install_requires=["sfftk-rw", "ahds", "lxml", "h5py>2.7.0", "requests", "bitarray",
                          "numpy-stl", "backports.shutil_get_terminal_size", "mock", "mrcfile", "Pillow<7.0.0",
                          "matplotlib<3.0", "scipy<1.2", "RandomWords", "styled", "networkx<2.3", "PyWavelets<1.1.0"],
        classifiers=SFFTK_CLASSIFIERS,
        entry_points={
            'console_scripts': [
                'sff = sfftk.sff:main',
            ]
        },
        package_data={
            'sfftk': ['sff.conf'],
        }
    )
