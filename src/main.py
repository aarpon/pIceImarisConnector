'''
Name       Main
Purpose    Module to try out pIceImarisConnector: it is not a test unit.
See        pIceImarisConnectorTestUnit.py

Author     Aaron Ponti

Created    21.03.2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

from pIceImarisConnector import pIceImarisConnector

if __name__ == '__main__':
    conn = pIceImarisConnector()
    conn2 = pIceImarisConnector(conn)
    conn3 = pIceImarisConnector(1)
    conn.display()
    conn.info()