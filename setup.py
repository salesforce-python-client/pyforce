from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup

setup(
    name='pyforce',
    version='1.9.1',
    install_requires=['defusedxml>=0.5.0', 'requests>=2.0.0', 'six>=1.10.0', ],
    packages=['pyforce'],
    author="Simon Fell et al.  reluctantly Forked by idbentley",
    author_email='ian.bentley@gmail.com, alanjcastonguay@gmail.com',
    description="A Python client wrapping the Salesforce.com SOAP API",
    long_description=open('README.md').read() + "\n" + open('CHANGES.txt').read(),
    long_description_content_type="text/markdown",
    license="GNU GENERAL PUBLIC LICENSE Version 2",
    keywords="python salesforce salesforce.com",
    url="https://github.com/alanjcastonguay/pyforce",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
