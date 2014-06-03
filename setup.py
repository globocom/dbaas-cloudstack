#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import dbaas_cloudstack

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = dbaas_cloudstack.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dbaas_cloudstack',
    version=version,
    description="""A cloudstack adapter to DBaaS""",
    long_description=readme + '\n\n' + history,
    author='Felippe da Motta Raposo',
    author_email='raposo.felippe@gmail.com',
    url='https://github.com/globocom/dbaas-cloudstack',
    packages=[
        'dbaas_cloudstack',
    ],
    include_package_data=True,
    install_requires=[
        'dbaas_credentials',
        'dbaas_flipper'
    ],
    license="BSD",
    zip_safe=False,
    keywords='dbaas-cloudstack',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)