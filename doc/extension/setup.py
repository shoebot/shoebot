# -*- coding: utf-8 -*-

# Base off the gnuplot extension
from setuptools import setup, find_packages

long_desc = '''
This package enables Sphinx documents to render graphics using shoebot.

Example::
  
  .. shoebot::
     
     fill(0, 128, 128)
     rect(0, 0, 40, 40)
      
'''

requires = ['shoebot>=0.4a4']

setup(
    name='sphinxcontrib-shoebot',
    version='0.1',
    url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-shoebot',
    license='BSD',
    author='Stuart Axon',
    author_email='stuaxo2@yahoo.com',
    description='Sphinx extension shoebot',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
