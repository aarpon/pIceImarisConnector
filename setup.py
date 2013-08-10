from distutils.core import setup
import sys

sys.path.append('pIceImarisConnector')
import pIceImarisConnector


setup(name='pIceImarisConnector',
      version='0.3.0',
      author='Aaron Ponti',
      author_email='aarpon@gmail.com',
      url='http://www.scs2.net/next/index.php?id=110',
      download_url='http://www.scs2.net/next/index.php?id=110',
      description='IceImarisConnector for python (pIceImarisConnector) is a simple commodity class that eases communication between Bitplane Imaris and python using the Imaris XT interface.',
      long_description='',
      package_dir={'': 'pIceImarisConnector'},
      py_modules=['pIceImarisConnector'],
      provides=['pIceImarisConnector'],
      keywords='Imaris ImarisXT python Ice',
      license='GPL2.0',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 2',
                   'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                   'Topic :: Scientific/Engineering'
                  ],
     )
