from setuptools import setup
from os import path, sep

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')

kwargs = {"dir": this_directory, "sep": sep}
with open("{dir}{sep}logdna{sep}VERSION".format(**kwargs)) as f:
    version = f.read().strip('\n')

setup(
    name='logdna',
    packages=['logdna'],
    package_data={'': ['VERSION']},
    version=version,
    description='A Python Package for Sending Logs to LogDNA',
    author='LogDNA Inc.',
    author_email='help@logdna.com',
    license='MIT',
    url='https://github.com/logdna/python',
    download_url=('https://github.com/logdna/python/tarball/%s' % (version)),
    keywords=['logdna', 'logging', 'logs', 'python', 'logdna.com', 'logger'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Topic :: System :: Logging',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
