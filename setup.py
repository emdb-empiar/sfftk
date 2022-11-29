# -*- coding: utf-8 -*-
# setup.py
import sys

from setuptools import setup, find_packages

from sfftk import SFFTK_VERSION

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

SFFTK_NAME = "sfftk"
SFFTK_AUTHOR = "Paul K. Korir, PhD"
SFFTK_AUTHOR_EMAIL = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
SFFTK_DESCRIPTION = "Toolkit for working with EMDB-SFF and other segmentation file formats"
SFFTK_DESCRIPTION_CONTENT_TYPE = 'text/x-rst; charset=UTF-8'
SFFTK_URL = "https://emdb-empiar.github.io/EMDB-SFF/"
SFFTK_PROJECT_URLS = {
    "Report Issues": "https://github.com/emdb-empiar/sfftk/issues",
    "Documentation": "http://sfftk.readthedocs.io/en/latest/index.html",
    "Souce Code": "https://github.com/emdb-empiar/sfftk"
}
SFFTK_LICENSE = "Apache License"
SFFTK_KEYWORDS = "EMDB-SFF, SFF, segmentation"
SFFTK_CLASSIFIERS = [
    # maturity
    "Development Status :: 2 - Pre-Alpha",
    # environment
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    # license
    "License :: OSI Approved :: Apache Software License",
    # os
    "Operating System :: OS Independent",
    # python versions
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Terminals",
    "Topic :: Text Processing",
    "Topic :: Text Processing :: Markup",
    "Topic :: Utilities",
]
SFFTK_PYTHON3_INSTALL_REQUIRES = [
    "sfftk-rw", "numpy", "ahds", "styled", "mrcfile", "bitarray", "requests",
    "mock", "numpy-stl"
]

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
    project_urls=SFFTK_PROJECT_URLS,
    license=SFFTK_LICENSE,
    keywords=SFFTK_KEYWORDS,
    setup_requires=["numpy"],
    install_requires=SFFTK_PYTHON3_INSTALL_REQUIRES,
    classifiers=SFFTK_CLASSIFIERS,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'sff = sfftk.sff:main',
        ]
    },
    package_data={
        'sfftk': ['sff.conf'],
    }
)
