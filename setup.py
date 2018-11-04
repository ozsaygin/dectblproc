#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='dectblproc',
    version='1.0',
    description='A command-line tool designed to process boolean decision tables',
    author='Oguz Ozsaygin',
    author_email='oguzozsaygin@sabanciuniv.edu',
    python_requires='>=3.6.0',
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['dectblproc=dectblproc.dectblproc:main'],
    },
    install_requires=[
        'tabulate',
        'satispy==1.1b1'
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
