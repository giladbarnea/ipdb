# Copyright (c) 2007-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb-extended.
# GNU package is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# GNU package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.

from setuptools import setup, find_packages
import re

with open('ipdbx/__main__.py') as mainpy:
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment
                      mainpy.read())
    version = match.group(1)

long_description = (open('README.rst').read()
                    # + '\n\n' + open('HISTORY.txt').read()
                    )

console_script = 'ipdbx'

setup(name='ipdbx',
      version=version,
      description="IPython-enabled pdb with extra functionality and customisation",
      long_description=long_description,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
          'Topic :: Software Development :: Debuggers',
          'License :: OSI Approved :: BSD License',
          ],
      keywords='pdb ipython ipdb ipdbx ipdb-extended',
      author='Gilad Barnea',
      author_email='giladbrn@gmail.com',
      url='https://github.com/giladbarnea/ipdbx',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      test_suite='tests',
      python_requires=">=3.6",
      install_requires=[
          'IPython >= 7.0'
          ],

      tests_require=[
          'mock'
          ],
      extras_require = {'dev':['twine']},
      entry_points={
          'console_scripts': ['%s = ipdbx.__main__:main' % console_script]
          }
      )
