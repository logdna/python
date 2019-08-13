<p align="center">
  <a href="https://app.logdna.com">
    <img height="95" width="202" src="https://raw.githubusercontent.com/logdna/artwork/master/logo%2Bpython.png">
  </a>
  <p align="center">Python package for logging to <a href="https://app.logdna.com">LogDNA</a></p>
</p>

---

* **[Installation](#installation)**
* **[Setup](#setup)**
* **[Usage](#usage)**
* **[API](#api)**
* **[License](#license)**


## Installation

```bash
$ pip install logdna
```

## Setup
```python
import logging
from logdna import LogDNAHandler

key = 'YOUR INGESTION KEY HERE'

log = logging.getLogger('logdna')
log.setLevel(logging.INFO)

options = {
  'hostname': 'pytest',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE'
}

# Defaults to False; when True meta objects are searchable
options['index_meta'] = True

test = LogDNAHandler(key, options)

log.addHandler(test)

log.warning("Warning message", {'app': 'bloop'})
log.info("Info message")

```
_**Required**_
* [LogDNA Ingestion Key](https://app.logdna.com/manage/profile)

_**Optional**_
* Hostname - *(String)* - max length 32 chars
* MAC Address - *(String)*
* IP Address - *(String)*
* Max Length - *(Boolean)* - formatted as options['max_length']
* Index Meta - *(Boolean)* - formatted as options['index_meta']

## Usage

After initial setup, logging is as easy as:
```python
# Simplest use case
log.info('My Sample Log Line')

# Add a custom level
log.info('My Sample Log Line', { 'level': 'MyCustomLevel' })

# Include an App name with this specific log
log.info('My Sample Log Line', { 'level': 'Warn', 'app': 'myAppName'})

# Pass associated objects along as metadata
meta = {
    'foo': 'bar',
    'nested': {
        'nest1': 'nested text'
    }
}

opts = {
    'level': 'warn',
    'meta': meta
}

log.info('My Sample Log Line', opts)
```

### Usage with File Config

To use `LogDNAHandler` with [`fileConfig`](https://docs.python.org/2/library/logging.config.html#logging.config.fileConfig) (e.g., in a Django `settings.py` file):

```python
import os
import logging
from logdna import LogDNAHandler #  required to register `logging.handlers.LogDNAHandler`

LOGGING = {
    # Other logging settings...
    'handlers': {
        'logdna': {
            'level': logging.DEBUG,
            'class': 'logging.handlers.LogDNAHandler',
            'key': os.environ.get('LOGDNA_INGEST_KEY'),
            'options': {
                'app': '<app name>',
                'env': os.environ.get('ENVIRONMENT'),
                'index_meta': <True|False>,
            },
        },
    },
    'loggers': {
        '': {
            'handlers': ['logdna'],
            'level': logging.DEBUG
        },
    },
}
```

(This example assumes you have set environment variables for `ENVIRONMENT` and `LOGDNA_INGEST_KEY`)

## API

### LogDNAHandler(key, [options])
---
#### key

* _**Required**_
* Type: `String`
* Values: `YourAPIKey`

The [LogDNA API Key](https://app.logdna.com/manage/profile) associated with your account.

#### options

##### app

* _Optional_
* Type: `String`
* Default: `''`
* Values: `YourCustomApp`
* Max Length: `32`

The default app passed along with every log sent through this instance.

##### env

* _Optional_
* Type: `String`
* Default: `''`
* Values: `YourCustomEnv`
* Max Length: `32`

The default env passed along with every log sent through this instance.

##### hostname

* _Optional_
* Type: `String`
* Default: `''`
* Values: `YourCustomHostname`
* Max Length: `32`

The default hostname passed along with every log sent through this instance.

##### include_standard_meta

* _Optional_
* Type: `Boolean`
* Default: `False`

Python [`LogRecord` objects](https://docs.python.org/2/library/logging.html#logrecord-objects) includes language-specific information that may be useful metadata in logs.  Setting `include_standard_meta` to `True` automatically populates meta objects with `name`, `pathname`, and `lineno` from the `LogRecord`.  See [`LogRecord` docs](https://docs.python.org/2/library/logging.html#logrecord-objects) for more details about these values.


##### index_meta

* _Optional_
* Type: `Boolean`
* Default: `False`

We allow meta objects to be passed with each line. By default these meta objects are stringified and not searchable, and are only displayed for informational purposes.

If this option is set to True then meta objects are parsed and searchable up to three levels deep. Any fields deeper than three levels are stringified and cannot be searched.

*WARNING* If this option is True, your metadata objects MUST have consistent types across all log messages or the metadata object may not be parsed properly.


##### level

* _Optional_
* Type: `String`
* Default: `Info`
* Values: `Debug`, `Trace`, `Info`, `Warn`, `Error`, `Fatal`, `YourCustomLevel`
* Max Length: `32`

The default level passed along with every log sent through this instance.

##### verbose

* _Optional_
* Type: `String` or `Boolean`
* Default: `True`
* Values: False or any level

Sets the verbosity of log statements for failures.

##### request_timeout

* _Optional_
* Type: `int`
* Default: `30000`

The amount of time (in ms) the request should wait for LogDNA to respond before timing out.

##### tags

* _Optional_
* Type: `String[]`
* Default: `[]`

List of tags used to dynamically group hosts.  More information on tags is available at [How Do I Use Host Tags?](https://docs.logdna.com/docs/logdna-agent#section-how-do-i-use-host-tags-)

##### url

* _Optional_
* Type: `String`
* Default: `'https://logs.logdna.com/logs/ingest'`

A custom ingestion endpoint to stream log lines into.

### log(line, [options])
---
#### line

* _Required_
* Type: `String`
* Default: `''`
* Max Length: `32000`

The log line to be sent to LogDNA.

#### options

##### level

* _Optional_
* Type: `String`
* Default: `Info`
* Values: `Debug`, `Trace`, `Info`, `Warn`, `Error`, `Fatal`, `YourCustomLevel`
* Max Length: `32`

The level passed along with this log line.

##### app

* _Optional_
* Type: `String`
* Default: `''`
* Values: `YourCustomApp`
* Max Length: `32`

The app passed along with this log line.

##### env

* _Optional_
* Type: `String`
* Default: `''`
* Values: `YourCustomEnv`
* Max Length: `32`

The environment passed with this log line.

##### meta

* _Optional_
* Type: `JSON`
* Default: `None`

A meta object for additional metadata about the log line that is passed. Please ensure values are JSON serializable,
values that are not JSON serializable will be removed and the respective keys will be added to the `__errors` string.

##### index_meta

* _Optional_
* Type: `Boolean`
* Default: `False`

We allow meta objects to be passed with each line. By default these meta objects will be stringified and will not be
searchable, but will be displayed for informational purposes.

If this option is turned to true then meta objects will be parsed and will be searchable up to three levels deep. Any fields deeper than three levels will be stringified and cannot be searched.

*WARNING* When this option is true, your metadata objects across all types of log messages MUST have consistent types or the metadata object may not be parsed properly!

##### timestamp

* _Optional_
* Default: `time.time()`

The time in seconds since the epoch to use for the log timestamp. It must be within one day or current time - if it is not, it is ignored and time.time() is used in its place.


## License

MIT © [LogDNA](https://logdna.com/)

*Happy Logging!*
