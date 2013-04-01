# pIceImarisConnector setup script
from distutils.core import setup
setup(name='pIceImarisConnector',
      license='GPL v2',
      version='0.2.0',
      description='pIceImarisConnector is a simple commodity class that eases communication between Bitplane Imaris and python using the Imaris XT interface.',
      author='Aaron Christian Ponti',
      author_email="aarpon@gmail.com",
      maintainer='Aaron Christian Ponti',
      maintainer_email='aarpon@gmail.com',
      url='http://www.scs2.net/next/index.php?id=110',
      packages=['pIceImarisConnector'],
      package_dir={'pIceImarisConnector': '.'},
      package_data={'pIceImarisConnector': ['./gpl-2.0.txt']})
