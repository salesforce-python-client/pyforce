
from setuptools import setup

setup(name='pyforce',
    version='1.8.0',
    install_requires=['defusedxml>=0.5.0'],
    package_dir={'': 'src'},
    packages=['pyforce'],
    author = "Simon Fell et al.  reluctantly Forked by idbentley",
    author_email = 'ian.bentley@gmail.com, alanjcastonguay@gmail.com',
    description = "A Python client wrapping the Salesforce.com SOAP API",
    long_description = open('README.md').read() + "\n" + open('CHANGES.txt').read(),
    license = "GNU GENERAL PUBLIC LICENSE Version 2",
    keywords = "python salesforce salesforce.com",
    url = "https://github.com/alanjcastonguay/pyforce",
    )
