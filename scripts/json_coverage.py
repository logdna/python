import json
from os import path
from coverage import Coverage

ROOT = path.realpath(path.abspath(path.join(path.dirname(__file__), '..')))
COVERAGE_DIR = path.join(ROOT, 'coverage')
JUNIT_PATH = path.join(COVERAGE_DIR, 'test.xml')


def json_coverage():
    COVERAGE_FILE = path.join(COVERAGE_DIR, 'coverage-final.json')
    COVERAGE_SUMMARY = path.join(COVERAGE_DIR, 'coverage-summary.json')

    coverage = Coverage(config_file=path.join(ROOT, 'pyproject.toml'))
    coverage.load()
    coverage.json_report(outfile=COVERAGE_FILE)

    report = json.load(open(COVERAGE_FILE))
    totals = report.get('totals')
    summary = {
        'lines': {
            'total':
            totals['covered_lines'] + totals['missing_lines'],
            'covered':
            totals['covered_lines'],
            'pct':
            totals['covered_lines'] /
            (totals['covered_lines'] + totals['missing_lines']) * 100
        },
        'statements': {
            'total': None,
            'covered': None,
            'pct': None,
        },
        'functions': {
            'total': None,
            'covered': None,
            'pct': None,
        },
        'branches': {
            'total': totals['num_branches'],
            'covered': totals['covered_branches'],
            'pct': totals['covered_branches'] / totals['num_branches'] * 100
        }
    }

    json.dump({'total': summary}, open(COVERAGE_SUMMARY, 'w'))


if __name__ == "__main__":
    json_coverage()
