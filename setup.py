from codecs import open
from os import path
from piprepo import __description__, __version__
from setuptools import find_packages, setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="piprepo",
    version=__version__,
    url="https://github.com/colinhoglund/piprepo",
    author='Colin Hoglund',
    author_email='colinhoglund@gmail.com',
    description=__description__,
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': ['piprepo=piprepo.command:main'],
    },
    install_requires=['pip>=8', 'boto3'],
    extras_require={
        'dev': ['flake8', 'pytest', 'pytest-cov', 'moto']
    },
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
