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

    isImarisOnForTestThree = False
    
    # No parameters
    conn1 = pIceImarisConnector()
    print("conn1:")
    conn1.display()
    conn1.info()
    
    # Pass the existing pIceImarisConnector object - will return the reference
    conn2 = pIceImarisConnector(conn1)
    print("conn2:")
    print("Check: conn1 and conn2 are the same object: " + str(conn1 is conn2))
    
    if isImarisOnForTestThree == True:
    
        # Try connecting to an open Imaris instance (Imaris must be running!)
        print("conn3:")
        try:
            conn3 = pIceImarisConnector(0)
            conn3.display()
            print("Check: conn1 and conn3 are different objects: " + str(conn1 is not conn3))
        
            # Use the ImarisApplication object in conn3 to initialize conn4
            print("conn4:")
            conn4 = pIceImarisConnector(conn3.mImarisApplication)
            conn4.display()

        except Exception:
            print("Imaris must be running for this test!")

    # Try starting an instance of Imaris via pIceImarisConnector
    print("conn5:")
    conn5 = pIceImarisConnector()
    if not conn5.startImaris():
        print("Could not start Imaris!")
        exit()

    conn5.display()
    print(conn5.getImarisVersionAsInteger())
    conn5.closeImaris(True)
