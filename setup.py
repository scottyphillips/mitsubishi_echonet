from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='mitsubishi_echonet',
    version='0.1.7',
    author='Scott Phillips',
    author_email='jrh@example.com',
    packages=['mitsubishi_echonet'],
    url='http://pypi.python.org/pypi/mitsubishi_echonet/',
    license='LICENSE.txt',
    description='A library for interfacing with Mitsubishi HVAC via the Echonet lite protocol.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # install_requires=[
    #    "Django >= 1.1.1",
    #    "caldav == 0.1.4",
    #],
)
