
from setuptools import setup

setup(name='pyforce',
    version='1.4', # be sure to update the version in pyforce.py too
    package_dir={'': 'src'},
    packages=['pyforce'],
    author = "Simon Fell et al.  reluctantly Forked by idbentley",
    author_email = 'ian.bentley@gmail.com',
    description = "A Python client wrapping the Saleforce.com SOAP API",
    long_description = open('README.md').read() + "\n" + open('CHANGES.txt').read(),
    license = "GNU GENERAL PUBLIC LICENSE Version 2",
    keywords = "python salesforce salesforce.com",
    url = "https://github.com/idbentley/pyforce",
    )
