#!/usr/bin/env python

from setuptools import setup
import subprocess
import os
import sys

# check that python version is 3.5 or above
python_version = sys.version_info
print('Running Python version %s.%s.%s' % python_version[:3])
if python_version < (3, 5, 4):
    sys.exit('Python < 3.5.4 is not supported, aborting setup')
else:
    print('Confirmed Python version 3.5.4 or above')

def write_version_file(version):
    """ Writes a file with version information to be used at run time

    Parameters
    ----------
    version: str
        A string containing the current version information

    Returns
    -------
    version_file: str
        A path to the version file

    """
    try:
        git_log = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%h %ai']).decode('utf-8')
        git_diff = (subprocess.check_output(['git', 'diff', '.']) +
                    subprocess.check_output(
                        ['git', 'diff', '--cached', '.'])).decode('utf-8')
        if git_diff == '':
            git_status = '(CLEAN) ' + git_log
        else:
            git_status = '(UNCLEAN) ' + git_log
    except Exception as e:
        print("Unable to obtain git version information, exception: {}"
              .format(e))
        git_status = ''

    version_file = '.version'
    if os.path.isfile(version_file) is False:
        with open('pystq/' + version_file, 'w+') as f:
            f.write('{}: {}'.format(version, git_status))

    return version_file


def get_long_description():
    """ Finds the README and reads in the description """
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md')) as f:
            long_description = f.read()
    return long_description


def readfile(filename):
    with open(filename) as fp:
        filecontents = fp.read()
    return filecontents


VERSION = '1.0.0'
version_file = write_version_file(VERSION)
long_description = get_long_description()

setup(name='pystq',
      description='''
    A gravitational wave interferometer parameter optimisation game, 
                  written in Python and run in a Jupyter Notebook.
      ''',
      long_description=long_description,
      url='https://github.com/gwoptics/SpacePyQuest',
      author='Philip Jones, Isobel Romero-Shaw, Roshni Vincent, Andreas Freise',
      author_email='isobel.romeroshaw@gmail.com',
      license="GPL 3",
      version=VERSION,
      packages=['pystq'],
      package_dir={'': 'pystq'},
      install_requires=[
          'bokeh>=0.12.9',
          'jupyter'
      ],
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "License :: GNU General Public License 3",
          "Operating System :: OS Independent"])
