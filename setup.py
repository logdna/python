from setuptools import setup
from os import path

with open('VERSION.txt') as version_file:
    pkg_version = version_file.read().strip()

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
  name = 'logdna',
  packages = ['logdna'],
  version = pkg_version,
  description = 'A Python Package for Sending Logs to LogDNA',
  author = 'LogDNA Inc.',
  author_email = 'help@logdna.com',
  license = 'MIT',
  url = 'https://github.com/logdna/python',
  download_url = 'https://github.com/logdna/python/tarball/1.4.2',
  keywords = ['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
  install_requires=[
    'requests',
  ],
  classifiers = [],
  long_description=long_description,
  long_description_content_type='text/markdown',
)
