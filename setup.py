# Copyright (c) 2007-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb.
# Redistributable under the revised BSD license
# https://opensource.org/licenses/BSD-3-Clause

from setuptools import setup, find_packages
from sys import version_info
import re
import io

version = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('ipdb3/__main__.py', encoding='utf_8_sig').read()
    ).group(1)

long_description = (open('README.rst').read() +
    '\n\n' + open('HISTORY.txt').read())


if version_info[0] == 2:
    console_script = 'ipdb3'
else:
    console_script = 'ipdb3%d' % version_info.major


setup(name='ipdb3',
      version=version,
      description="IPython-enabled pdb with extra functionality and customisation",
      long_description=long_description,
      classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Software Development :: Debuggers',
        'License :: OSI Approved :: BSD License',
      ],
      keywords='pdb ipython ipdb ipdb3',
      author='Gilad Barnea',
      author_email='giladbrn@gmail.com',
      url='https://github.com/giladbarnea/ipdb3',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      test_suite='tests',
      python_requires=">=3.4",
      install_requires=[
          'IPython >= 7.0'
      ],
      
      tests_require=[
          'mock'
      ],
      entry_points={
          'console_scripts': ['%s = ipdb3.__main__:main' % console_script]
      }
)
