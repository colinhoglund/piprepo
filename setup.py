import piprepo
from setuptools import find_packages, setup

setup(
    name="piprepo",
    version=piprepo.__version__,
    url="https://github.com/colinhoglund/piprepo",
    description=piprepo.__description__,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['piprepo=piprepo.command:main'],
    },
    install_requires=["pip>=8"],
    license="BSD",
)
