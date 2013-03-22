'''
Name       pIceImarisConnector
Purpose    pIceImarisConnector is a simple Python class eases communication
           between Bitplane Imaris and Python using the Imaris XT interface.

Author     Aaron Ponti

Created    21.03.2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

import os

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
        self.__imarisApplication__ = imarisApplication
        self.__indexingStart__ = indexingStart
        self.__imarisPath__ = ""
        
        # Find Imaris
        self.findImaris()

    @property
    def version(self):
        return self.__version__
    
    @property
    def mImarisApplication(self):
        return self.__imarisApplication__
    
    @property
    def indexingStart(self):
        return self.__indexingStart__

    def findImaris(self):
        ''' 
        findImaris() gets the Imaris path to the Imaris executable.
        '''
        IMARISPATH = os.getenv('IMARISPATH')
        if IMARISPATH is None:
            self.__imarisPath__ = "NOT FOUND."
        else:
            self.__imarisPath__ = IMARISPATH

    def display(self):
        '''
        Print pIceImarisConnector version
        '''
        print("pIceImarisConnector v" + self.__version__)
    
    def info(self):
        '''
        Print pIceImarisConnector information
        '''
        print("Imaris found at '" + self.__imarisPath__ +"'")
        
        