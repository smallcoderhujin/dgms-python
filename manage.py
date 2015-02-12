#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
    
    
from setuptools import setup
from setuptools import find_packages

setup(
    name="qga-proxy",
    version="0.1",
    url='http://www.chinac.com',
    author='hujin',
    author_email='hujin@chinac.com',
    description='Qemu-guest-agent proxy',
    license='GPL',
    packages=find_packages(),
)
