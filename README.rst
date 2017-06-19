.. image:: https://travis-ci.org/colinhoglund/piprepo.svg?branch=master
    :target: https://travis-ci.org/colinhoglund/piprepo
.. image:: https://coveralls.io/repos/github/colinhoglund/piprepo/badge.svg?branch=master
    :target: https://coveralls.io/github/colinhoglund/piprepo?branch=master


piprepo
=======

piprepo is a tool for building and synchronizing PEP-503 compliant package repositories.

It currently supports synchronization to a local directory as well as AWS S3.

Installation
------------

`pip install piprepo`

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

The `piprepo build` command simply builds a package index in the
specified directory.

Download some source tarballs or wheels::

    pip download -d /tmp/localrepo pyyaml
    pip wheel -w /tmp/localrepo pip

Build a simple package repository from downloaded packages::

    piprepo build /tmp/localrepo

Build and sychronize to a destination repo
..........................................

The `piprepo sync` command builds in the local source directory and
syncs packages and index files to the specified destination.

Download some source tarballs or wheels::

    pip download -d /tmp/syncrepo pyyaml
    pip wheel -w /tmp/syncrepo pip

Synchronize to local directory::

    piprepo sync /tmp/syncrepo /tmp/newrepo

Synchronize to an S3 bucket::

    piprepo sync /tmp/syncrepo s3://my-bucket/piprepo

Development
-----------

Installing development requirements::

    pip install -e .[dev]
