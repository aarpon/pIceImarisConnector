from setuptools import setup
from pIceImarisConnector import pIceImarisConnector

setup(name='pIceImarisConnector',
      version=pIceImarisConnector.__version__,
      author='Aaron Ponti',
      author_email='aaron.ponti@bsse.ethz.ch',
      url='https://github.com/aarpon/pIceImarisConnector',
      download_url='https://github.com/aarpon/pIceImarisConnector/releases',
      project_urls={
          "Bug Tracker": "https://github.com/aarpon/pIceImarisConnector/issues",
          "Documentation": "https://piceimarisconnector.readthedocs.io/",
          "Source Code": "https://github.com/aarpon/pIceImarisConnector",
      },
      description='Easier communication between Bitplane Imaris and python over ImarisXT.',
      long_description='IceImarisConnector for python (pIceImarisConnector) is a simple commodity class that eases communication between Bitplane Imaris and python using the Imaris XT interface.',
      include_package_data=True,
      packages=['pIceImarisConnector'],
      package_dir={'pIceImarisConnector': 'pIceImarisConnector'},
      provides=['pIceImarisConnector'],
      keywords='Imaris ImarisXT python Ice',
      license='GPL2.0',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                   'Topic :: Scientific/Engineering'
                  ],
      requires=['numpy']
)
