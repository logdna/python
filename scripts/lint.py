from os import path
from subprocess import check_call

ROOT = path.realpath(path.abspath(path.join(path.dirname(__file__), '..')))


def run():
    check_call(['flake8', '--doctests'])


def fix():
    check_call(cwd=ROOT,
               args=[
                   'yapf', '-r', '-i',
                   path.join(ROOT, 'logdna'),
                   path.join(ROOT, 'scripts'),
                   path.join(ROOT, 'tests')
               ])

    run()
