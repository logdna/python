from setuptools import setup
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'logdna',
  packages = ['logdna'],
  version = '1.4.1',
  description = 'A Python Package for Sending Logs to LogDNA',
  author = 'LogDNA Inc.',
  author_email = 'help@logdna.com',
  license = 'MIT',
  url = 'https://github.com/logdna/python',
  download_url = 'https://github.com/logdna/python/tarball/1.4.1',
  keywords = ['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
  install_requires=[
    'requests',
  ],
  classifiers = [],
  long_description=long_description,
  long_description_content_type='text/markdown',
)
