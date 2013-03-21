'''
Name       pIceImarisConnector
Purpose    pIceImarisConnector is a simple Python class eases communication
           between Bitplane Imaris and Python using the Imaris XT interface.

Author     Aaron Ponti

Created    21.03.2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

class pIceImarisConnector:
    
    '''
    pIceImarisConnector is a simple Python class eases communication between
    Bitplane Imaris and Python using the Imaris XT interface.
    '''
    
    def __init__(self, imarisApplication = None, indexingStart = 0):
    
        ''' 
        pIceImarisConnector constructor

        Arguments:

        imarisApplication:  <describe> (default None)
        indexingStart:      <describe> (default 0)
        '''
        
        self.__version__ = "0.2.0"
        self._mImarisApplication = imarisApplication


    def display(self):
        '''
        Print pIceImarisConnector information
        '''
        print("pIceImarisConnector v" + self.__version__)

    def findImaris(self):
        
        ''' 
        This methods gets the Imaris path to the Imaris executable and
        to the ImarisLib.jar library from the environment variable IMARISPATH.
        '''
        pass