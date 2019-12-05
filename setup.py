from setuptools import setup
from os import path
from _version import __version__

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
  name = 'logdna',
  packages = ['logdna'],
  version = __version__,
  description = 'A Python Package for Sending Logs to LogDNA',
  author = 'LogDNA Inc.',
  author_email = 'help@logdna.com',
  license = 'MIT',
  url = 'https://github.com/logdna/python',
  download_url = ('https://github.com/logdna/python/tarball/%s' %(__version__)),
  keywords = ['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
  install_requires=[
    'requests',
  ],
  classifiers = [],
  long_description=long_description,
  long_description_content_type='text/markdown',
)
