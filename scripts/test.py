import os
from os import path
from subprocess import check_call

ROOT = path.realpath(path.abspath(path.join(path.dirname(__file__), '..')))
COVERAGE_DIR = path.join(ROOT, 'coverage')
JUNIT_PATH = path.join(COVERAGE_DIR, 'test.xml')
print(JUNIT_PATH)


def run():
    try:
        os.mkdir(COVERAGE_DIR)
    except FileExistsError:
        pass

    check_call([
        'pytest',
        '--junitxml={0}'.format(JUNIT_PATH),
        '--cov=logdna',
        '--cov-report=html',
        '--cov-report=xml',
        '--cov-config=setup.cfg',
        '--cov-branch'
    ])
