

""" File unrelated to the package, except for convenience in deploying """
import re
import sh
import os

commit_count = sh.git('rev-list', ['--all']).count('\n')

with open('setup.py') as f:
    setup = f.read()

setup = re.sub("MICRO_VERSION = '[0-9]+'", "MICRO_VERSION = '{}'".format(commit_count), setup)

major = re.search("MAJOR_VERSION = '([0-9]+)'", setup).groups()[0]
minor = re.search("MINOR_VERSION = '([0-9]+)'", setup).groups()[0]
micro = re.search("MICRO_VERSION = '([0-9]+)'", setup).groups()[0]
version = '{}.{}.{}'.format(major, minor, micro)
with open('setup.py', 'w') as f:
    f.write(setup)

py_version = "py" if sh.which("py") is not None else "python"
os.system('{} setup.py sdist bdist_wheel upload'.format(py_version))