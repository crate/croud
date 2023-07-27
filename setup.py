#!/usr/bin/env python
#
# Licensed to CRATE Technology GmbH ("Crate") under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  Crate licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
# However, if you have executed another commercial license agreement
# with Crate these terms will supersede the license and you may use the
# software solely pursuant to the terms of the relevant commercial agreement.

from pkg_resources.extern.packaging.version import Version
from setuptools import find_packages, setup

__version__ = Version("1.5.0")

try:
    with open("README.rst", "r", encoding="utf-8") as f:
        readme = f.read()
except IOError:
    readme = ""


setup(
    name="croud",
    author="Crate.io",
    author_email="office@crate.io",
    url="https://github.com/crate/croud",
    description="A command line interface for CrateDB Cloud",
    long_description=readme,
    version=str(__version__),
    entry_points={"console_scripts": ["croud = croud.__main__:main"]},
    packages=find_packages(),
    install_requires=[
        "appdirs==1.4.4",
        "bitmath==1.3.3.1",
        "certifi",
        "colorama==0.4.6",
        "marshmallow==3.19.0",
        "pyyaml==6.0",
        "requests==2.31.0",
        "tabulate>=0.8,<1.0",
        "yarl==1.9.2",
        "halo==0.0.31",
        "shtab==1.6.2",
        "tqdm==4.65.0",
    ],
    extras_require={
        "testing": [
            "tox==3.14.2",
            "pytest-freezegun==0.4.2",
        ],
        "development": [
            "black==23.3.0",
            "flake8==3.8.4",
            "isort==5.12.0",
            "mypy==0.812",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
