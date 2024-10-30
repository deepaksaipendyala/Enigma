import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

setup(
    name='Enigma',
    version='3.0',
    description='A Discord music bot that recommends songs based on user input, created as a part of CSC510 Software Engineering course at NC State University.',
    author='Group 36 (Nico Field, Riley Joncas, Biruk Tadesse)',
    author_email='rbjoncas@ncsu.edu',
    zip_safe=False,
    classifiers=['Development Status :: Development',
                 'Intended Audience :: Engineers',
                 'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE',
                 'Programming Language :: Python :: 3.12'],
    tests_require=['pytest'],
    exclude_package_data={
        '': ['.gitignore'],
        'images': ['*.xcf', '*.blend']
    },
)
