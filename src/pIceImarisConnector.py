"""
Name      pIceImarisConnector
Purpose   pIceImarisConnector is a simple Python class eases communication
          between Bitplane Imaris and Python using the Imaris XT interface.

Author    Aaron Ponti

ImarisConnector is a simple commodity class that eases communication between
Imaris and MATLAB using the Imaris XT interface.
Copyright (C) 2013  Aaron Ponti

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""

import os
import sys
import platform
import glob
import re
import random
import imp

class pIceImarisConnector(object):
    """pIceImarisConnector is a simple Python class eases communication 
    between Bitplane Imaris and Python using the Imaris XT interface.
    
    """
    
    # pIceImarisConnector version
    _mVersion = "0.2.0"

    # Imaris-related paths
    _mImarisPath = ""
    _mImarisExePath = ""
    _mImarisServerExePath = ""
    _mImarisLibPath = ""
    
    # ImarisLib object
    _mImarisLib = None

    # ICE ImarisApplication object
    _mImarisApplication = None

    # Indexing start
    _mIndexingStart = 0
    
    # Imaris ID
    _mImarisObjectID = 0

    def __new__(cls, *args, **kwargs):
        """Create or re-use a pIceImarisConnector object."""
        if args and \
                args[0] is not None and \
                type(args[0]).__name__ == "pIceImarisConnector":
            # Reusing passed object
            return args[0]
        else:
            # Creating new object
            return object.__new__(cls, *args, **kwargs)

    def __init__(self, imarisApplication=None, indexingStart=0):
        """"Initialize the created pIceImarisConnector object.

        Arguments:

        imarisApplication : (optional) if omitted (or set to None), a
                            pIceImarisConnector object is created that
                            is not connected to any Imaris instance.

                            Imaris can then be started (and connected) 
                            using the startImaris() method, i.e.

                                conn.startImaris()

                            Alternatively, imarisApplication can be:
                            
                            - an Imaris Application ID as provided by Imaris
                            - a pIceImarisConnector reference    
                            - an Imaris Application ICE object.

        indexingStart     : (optional, default is 0) either 0 or 1, 
                            depending on whether you prefer to index 
                            arrays in pIceImarisConnector starting at
                            0 or 1. 

                            All indexing in ICE starts at 0; in contrast, 
                            MATLAB indexing starts at 1. To keep 
                            consistency, indexing in pIceImarisConnector
                            is also 0-based (i.e. indexingStart defaults 
                            to 0). This means that to get the data volume
                            for the first channel and first time point of
                            the dataset you will use:
                             
                                conn.GetDataVolume(0, 0)
                                
                            It you are come confortable with 1-based 
                            indexing, i.e. you prefer using: 
                                
                                conn.GetDataVolume(1, 1)
                                 
                            you can set indexingStart to 1.

                            Whatever you choose, be consistent!

        """

        # If imarisApplication is a pIceImarisConnector reference,
        # we return immediately, because we want to re-use the 
        # object without changes.
        if imarisApplication is not None and \
                type(imarisApplication).__name__ == "pIceImarisConnector":
            return

        # Check arguments
        if indexingStart != 0 and indexingStart != 1:
            raise ValueError("indexingStart must be either 0 or 1!")
        
        # Store the required paths
        self.findImaris()

        # Change to the Imaris path folder. This is needed to make sure
        # that the required dynamic libraries are imported correctly.
        os.chdir(self._mImarisPath)
        
        # Add the python lib folder to the python path
        sys.path.append(self._mImarisLibPath)
        
        # Import the ImarisLib module
        fileobj, pathname, description = imp.find_module('ImarisLib')
        ImarisLib = imp.load_module('ImarisLib', fileobj, pathname, description)
        fileobj.close()

        # Instantiate and store the ImarisLib object
        self._mImarisLib = ImarisLib.ImarisLib()

        # Assign a random id
        self._mImarisObjectID = random.randint(0, 100000)
        
        # Set the indexing start
        self._mIndexingStart = indexingStart
        
        # Now we check the (optional) input parameter imarisApplication.
        # We have three cases. If imarisApplication is omitted, we just
        # create a pIceImarisConnector object that does nothing.
        # Alternatively, imarisApplication could be:
        # - an Imaris Application ID as provided by Imaris: we query 
        #   the Imaris Server for the application and assign it to the
        #   mImarisApplication property
        # - a pIceImarisConnector reference: we just return it
        # - an Imaris Application ICE object (rare): we simply assign
        #   it to the mImarisApplication property.
        
        # Case 0: no connection yet
        if imarisApplication is None:
            # We already did everything
            return
        
        # Case 1: we got the ID from Imaris
        elif isinstance(imarisApplication, int):
            # Get the application corresponding to the passed ID
            self._mImarisApplication = self._mImarisLib.GetApplication(imarisApplication)
            
            if self._mImarisApplication is None:
                raise Exception('Could not connect to Imaris!')

        # Case 2: we get an ImarisApplication object
        elif type(imarisApplication).__name__ == "IApplicationPrx":
            self._mImarisApplication = imarisApplication
        
        else:
            raise Exception("Invalid imarisApplication argument!")

    def __del__(self):
        """pIceImarisConnector destructor."""
        pass

    def __str__(self):
        """Converts the pIceImarisConnector object to a string."""
        if self._mImarisApplication is None: 
            return "pIceImarisConnector: not connected to an Imaris " \
                  "instance yet."
        else:
            return "pIceImarisConnector: connected to Imaris."

    @property
    def version(self):
        return self._mVersion
    
    @property
    def mImarisApplication(self):
        return self._mImarisApplication
    
    @property
    def indexingStart(self):
        return self._mIndexingStart

    def findImaris(self):
        """Gets or discovers the path to the Imaris executable."""
        
        # Try getting the environment variable IMARISPATH 
        imarisPath = os.getenv('IMARISPATH')
        
        # If imarisPath is None, we search for Imaris
        if imarisPath is None:
            
            # Search for Imaris in reasonable places
            if self.ispc():
                tmp = "C:\\Program Files\\Bitplane"
            elif self.ismac():
                tmp = "/Applications"
            else:
                raise OSError("pIceImarisConnector only works " + \
                                  "on Windows and Mac OS X.")

            # Check that the folder exist
            if os.path.isdir(tmp):
            
                # Pick the directory name with highest version number
                newestVersionDir = self._findNewestVersionDir(tmp)
                if newestVersionDir is None:
                    raise OSError("No Imaris installation found " + \
                                  "in " + tmp + ". Please define " + \
                                  "an environment variable " + \
                                  "'IMARISPATH'.")
                else:
                    imarisPath = newestVersionDir
        
        else: # if imarisPath is None
            
            # Check that IMARISPATH points to a valid directory
            if not os.path.isdir(imarisPath):
                raise OSError("The content of the IMARISPATH " + \
                              "environment variable does not " + \
                              "point to a valid directory.")
        
        # Now store imarisPath and proceed with setting all required 
        # executables and libraries
        self._mImarisPath = imarisPath

        # Set the path to the Imaris and ImarisServer executable and to
        # the ImarisLib library
        if self.ispc():
            exePath = os.path.join(imarisPath, 'Imaris.exe')
            serverExePath = os.path.join(imarisPath,
                                         'ImarisServerIce.exe')
            libPath = os.path.join(imarisPath, 'XT', 'python')
        elif self.ismac():
            exePath = os.path.join(imarisPath, 
                                   'Contents', 'MacOS', 'Imaris')
            serverExePath = os.path.join(imarisPath, 
                                         'Contents', 'MacOS',
                                         'ImarisServerIce')
            libPath = os.path.join(imarisPath, 'Contents', 'SharedSupport',
                                   'XT', 'python')
        else:
            raise OSError("pIceImarisConnector only works " + \
                          "on Windows and Mac OS X.")

        # Check whether the executable Imaris file exists
        if not os.path.isfile(exePath):
            raise OSError("Could not find the Imaris executable.")
        
        if not os.path.isfile(serverExePath):
            raise OSError("Could not find the ImarisServer executable.")
        
        # Now we can store the information and return success
        self._mImarisExePath = exePath
        self._mImarisServerExePath = serverExePath
        self._mImarisLibPath = libPath


    def display(self):
        print(self.__str__())
    
    def info(self):
        """Print pIceImarisConnector information."""
        print("pIceImarisConnector version " + self.version + " using:")
        print("- Imaris path: " + self._mImarisPath)
        print("- Imaris executable: " + self._mImarisExePath)
        print("- ImarisServer executable: " + self._mImarisServerExePath)
        print("- ImarisLib.jar archive: " + self._mImarisLibPath)
        
    def _findNewestVersionDir(self, directory):
        """Scans for candidate Imaris directories and returns the one 
        with highest version number. For internal use only!

        Arguments:
        
        directory:  directory to be scanned. Most likely 
                    C:\\Program Files\\Bitplane in Windows and 
                    /Applications on Mac OS X.
        
        """
        
        # If found, this will be the (relative) ImarisPath
        newestVersionDir = None
        
        # Newest version. Initially set to one since valid versions will
        # be larger, invalid versions might be zero.
        newestVersion = 1
        
        # Get all subfolders
        subDirs = glob.glob(directory + '/Imaris*')
        
        # Go over all subfolder and analyze them
        for d in subDirs:
            
            # First of all, make sure we are treating directories and 
            # not files
            if os.path.isfile(d):
                continue
            
            # Make sure to ignore the Scene Viewer, the File Converter 
            # and the 32bit version on 64 bit machines
            if "ImarisSceneViewer" in d or \
                "FileConverter" in d or \
                "32bit" in d:
                continue
            
            # Get version information
            match = re.search(r'(\d)+\.(\d)+\.+(\d)?', d)
            if not match:
                continue
            
            # Get the major, minor and patch versions
            groups = match.groups()
            
            major = int(groups[0])
            if major is None:
                # Must be defined
                continue

            minor = int(groups[1])
            if minor is None:
                # Must be defined
                continue

            patch = int(groups[2])
            if patch is None:
                # In case the patch version is not set we assume 0 is meant
                patch = 0

            # Compute version as integer
            version = 1e6 * major + 1e4 * minor + 1e2 * patch
            
            # Is it the newest yet?
            if version > newestVersion:
                newestVersionDir = d
                newestVersion = version
                
        return newestVersionDir

    def ispc(self):
        """Return true if pIceImarisConnector is being run on Windows."""
        
        return platform.system() == "Windows"
    
    def ismac(self):
        """Return true if pIceImarisConnector is being run on Mac OS X."""
        
        return platform.system() == "Darwin"