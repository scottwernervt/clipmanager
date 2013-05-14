from setuptools import setup, find_packages

# Application specific data
from clipmanager import __version__ as version
from clipmanager.defs import APP_ORG as organization
from clipmanager.defs import APP_NAME as name
from clipmanager.defs import APP_DOMAIN as domain
from clipmanager.defs import APP_DESCRIPTION as description
from clipmanager.defs import APP_AUTHOR as author
from clipmanager.defs import APP_EMAIL as email

setup(
    name = name.lower(),
    version = version,
    packages = find_packages(exclude=('tests',)),
    scripts = ['bin/clipmanager'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['PySide>=1.1.2'],

    # include_package_data = True,
    package_data = {
        'clipmanager': ['*.txt'],
        'clipmanager': ['icons/*.png', 'icons/*.ico'],
    },

    # metadata for upload to PyPI
    author = author,
    author_email = email,
    description = description,
    license = 'BSD',
    keywords = "hello world example examples",
    url = domain
)