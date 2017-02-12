#!/usr/bin/env python

from distutils.core import setup

setup(
      name='academic_nausea',
      version='0.1.0',
      author='Oleg Yunin',
      author_email='oayunin@gmail.com',
      url='https://github.com/walkingpendulum/academic_nausea',
      packages=['academic_nausea'],
      install_requires=[x for x in open('requirements.txt').read().split('\n') if x],
      scripts=['bin/nausea']
)
