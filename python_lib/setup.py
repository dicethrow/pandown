# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/

from setuptools import setup, find_packages

setup(
    name='pandown',
    version='0.1.0',
    packages=find_packages(include=['pandown'])
)
