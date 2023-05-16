import sys
import os

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    from distutils.core import setup
    from distutils.core import Command as TestCommand

class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open('LICENSE.txt') as f:
    license = f.read()

exec(open(os.path.join('arya', 'version.py')).read())

PKGNAME = 'arya'
URL = 'https://github.com/datacenter/' + PKGNAME
DOWNLOADURL = URL + '/releases/tag/' + str(__version__)

setup(
    name=PKGNAME,
    version=__version__,
    description='APIC Rest to pYthon Adapter',
    long_description=open('README.md').read(),
    packages=[PKGNAME],
    url='https://github.com/datacenter/arya',
    download_url=DOWNLOADURL,
    license=license,
    author='Paul Lesiak',
    author_email='palesiak@cisco.com',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        "console_scripts": [
            "arya=arya.arya:main",
            "getconfigfromapic=arya.getconfigfromapic:main",
            "apicxmljson=arya.apicxmljson:main",
        ],
    },
    tests_require = ['pytest'],
    cmdclass = {'test': PyTest},
)
