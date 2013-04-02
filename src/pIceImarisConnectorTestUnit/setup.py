# pIceImarisConnector setup script
from distutils.core import setup
setup(name='pIceImarisConnectortTestUnit',
      license='GPL v2',
      version='0.2.0',
      description='pIceImarisConnectorTestUnit is the pIceImarisConnector test unit.',
      author='Aaron Christian Ponti',
      author_email="aarpon@gmail.com",
      maintainer='Aaron Christian Ponti',
      maintainer_email='aarpon@gmail.com',
      url='http://www.scs2.net/next/index.php?id=110',
      packages=['pIceImarisConnectorTestUnit'],
      package_dir={'pIceImarisConnectorTestUnit': '.'},
      package_data={'pIceImarisConnectorTestUnit': ['./PyramidalCell.ims', './gpl-2.0.txt']})
