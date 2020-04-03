.. image:: https://travis-ci.org/colinhoglund/piprepo.svg?branch=master
    :target: https://travis-ci.org/colinhoglund/piprepo
.. image:: https://coveralls.io/repos/github/colinhoglund/piprepo/badge.svg?branch=master
    :target: https://coveralls.io/github/colinhoglund/piprepo?branch=master
.. image:: https://img.shields.io/pypi/v/piprepo.svg
    :target: https://pypi.python.org/pypi/piprepo/
    :alt: Latest Version


piprepo
=======

piprepo is a tool for building and synchronizing `PEP-503 <https://www.python.org/dev/peps/pep-0503/>`_ compliant package repositories.

It currently supports synchronization to a local directory as well as AWS S3.

Installation
------------

``pip install piprepo``

Usage
-----

Build::

    usage: piprepo build [-h] directory

    positional arguments:
      directory   Local directory to build

    optional arguments:
      -h, --help  show this help message and exit

Sync::

    usage: piprepo sync [-h] source destination

    positional arguments:
      source       Repository source
      destination  Repository destination

    optional arguments:
      -h, --help   show this help message and exit

Building a local package repo
.............................

The ``piprepo build`` command builds a simple package index
from packages contained in the specified directory.

Download some source tarballs or wheels::

    pip download -d /tmp/localrepo pyyaml
    pip wheel -w /tmp/localrepo pip

Or create a wheel from your source and copy it out:

    python setup.py sdist bdist_wheel
    cp dist/*.whl /tmp/localrepo/

Build a simple package repository from downloaded packages::

    piprepo build /tmp/localrepo

Build and sychronize to a destination repo
..........................................

The ``piprepo sync`` command builds a simple package index from
packages contained in the local source directory, and syncs
packages and index files to the specified destination.

Download some source tarballs or wheels::

    pip download -d /tmp/syncrepo pyyaml
    pip wheel -w /tmp/syncrepo pip

Synchronize to local directory::

    piprepo sync /tmp/syncrepo /tmp/newrepo

Synchronize to an S3 bucket::

    piprepo sync /tmp/syncrepo s3://my-bucket/piprepo

Install from a local repo
.........................

Once you have built your repo, you can install using::

    pip install my-pkg --extra-index-url file:///tmp/localrepo/simple/

Development
-----------

Installing development requirements::

    pip install -e .[dev]
