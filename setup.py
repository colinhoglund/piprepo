from os import path
import piprepo
from setuptools import find_packages, setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="piprepo",
    version=piprepo.__version__,
    url="https://github.com/colinhoglund/piprepo",
    author='Colin Hoglund',
    author_email='colinhoglund@gmail.com',
    description=piprepo.__description__,
    long_description=long_description,
    packages=find_packages(),
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
        'Intended Audience :: System Administrators'
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
