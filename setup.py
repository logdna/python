import setuptools
setuptools.setup(
  name = 'logdna',
  packages = ['logdna'],
  version = '1.4.0',
  description = 'A Python Package for Sending Logs to LogDNA',
  author = 'LogDNA Inc.',
  author_email = 'help@logdna.com',
  license = 'MIT',
  url = 'https://github.com/logdna/python',
  download_url = 'https://github.com/logdna/python/tarball/1.4.0',
  keywords = ['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
  install_requires=[
    'requests',
  ],
  classifiers = [],
)
