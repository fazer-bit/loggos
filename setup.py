#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", encoding="utf8") as fh:
    long_description = fh.read()
__version__ = "0.1.1"

setup(
    name="loggos",
    version=__version__,
    description="Python library for wrapping logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="fazer-bit",
    author_email="git-dotcom@mail.ru",
    url="https://github.com/fazer-bit/loggos.git",
    keywords="Python library for wrapping logging",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial"
    ],
    python_requires='>=3'
    )

