# /usr/bin/env python
import os

from setuptools import find_packages
from setuptools import setup

def read_requirements(filename):
    """Open a requirements file and return list of its lines."""
    contents = read_file(filename).strip('\n')
    return contents.split('\n') if contents else []


def read_file(filename):
    """Open and a file, read it and return its contents."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as f:
        return f.read()


setup(
    name='thevrapist',
    version='0.0.1',
    description='The virtual therapist',
    author='Grzegorz Parka',
    author_email='grzegorz.parka@gmail.com',
    include_package_data=True,
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    packages=find_packages(include=('thevrapist*',)),
)
