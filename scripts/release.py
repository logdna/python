from subprocess import check_call

def run(*args):
    check_call([
        'semantic-release',
        *args
    ])
