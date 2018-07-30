import setuptools
setuptools.setup(
  name = 'logdna',
  packages = ['logdna'],
  version = '1.2.8',
  description = 'A python package for sending logs to LogDNA',
  author = 'Answerbook Inc.',
  author_email = 'help@logdna.com',
  url = 'https://github.com/logdna/python',
  download_url = 'https://github.com/logdna/python/tarball/1.2.7',
  keywords = ['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
  install_requires=[
    'requests',
  ],
  classifiers = [],
)
