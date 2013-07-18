"""
Name      IceImarisConnector for python (pIceImarisConnector)
Purpose   pIceImarisConnector is a simple Python class eases communication
          between Bitplane Imaris and Python using the Imaris XT interface.

Author    Aaron Ponti

License

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
import subprocess
import time
import numpy as np

class pIceImarisConnector(object):
    """pIceImarisConnector is a simple Python class that eases communication
    between Bitplane Imaris and Python using the Imaris XT interface.

    """

    # pIceImarisConnector version
    _mVersion = "0.3.1-alpha"

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

    # Use control
    _mUserControl = 0


    @property
    def version(self):
        return self._mVersion


    @property
    def mImarisApplication(self):
        return self._mImarisApplication


    @property
    def indexingStart(self):
        return self._mIndexingStart


    def __new__(cls, *args, **kwargs):
        """Create or re-use a pIceImarisConnector object."""
        if args and args[0] is not None and \
                type(args[0]).__name__ == "pIceImarisConnector":
            # Reusing passed object
            return args[0]
        else:
            # Creating new object
            return object.__new__(cls, *args, **kwargs)


    def __init__(self, imarisApplication=None, indexingStart=0):
        """"Initializes the created pIceImarisConnector object.

SYNOPSIS:

@TODO

ARGUMENTS:

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

                    In the MATLAB version of IceImarisConnector,
                    indexingStart can optionally be set to 1 to
                    map the 1-based indexing of MATLAB to the 0-
                    based indexing used by ImarisLib and ICE,
                    though by default it is set to 0 to maintain
                    consistency across MATLAB and ICE.

                    Since pIceImarisConnector strives to offer
                    the same API as its MATLAB counterpart,
                    indexingStart can be set here as well, though
                    in practice it might not make much sense to
                    change the default value of 0.

                    By default, then, to get the data volume
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
        # object without changes. The __new__() method took care of
        # returnig a reference to the passed object instead of creating
        # a new one.
        if imarisApplication is not None and \
                type(imarisApplication).__name__ == "pIceImarisConnector":
            return

        # Check arguments
        if indexingStart != 0 and indexingStart != 1:
            raise ValueError("indexingStart must be either 0 or 1!")

        # Store the required paths
        self._findImaris()

        # Change to the Imaris path folder. This is needed to make sure
        # that the required dynamic libraries are imported correctly.
        os.chdir(self._mImarisPath)

        # Add the python lib folder to the python path
        sys.path.append(self._mImarisLibPath)

        # Import the ImarisLib module
        ImarisLib = self._importImarisLib()

        # Instantiate and store the ImarisLib object
        self._mImarisLib = ImarisLib.ImarisLib()

        # Assign a random id
        self._mImarisObjectID = random.randint(0, 100000)

        # Set the indexing start
        self._mIndexingStart = indexingStart

        # Now we check the (optional) input parameter imarisApplication.
        # We have three remaining cases (the first one we took care of
        # already; it was the case where imarisApplication was a
        # reference to an existing pIceImarisConnector object):
        # - if imarisApplication is omitted, we just create a
        #   pIceImarisConnector object that does nothing. Alternatively,
        #   imarisApplication could be:
        # - an Imaris Application ID as provided by Imaris: we query
        #   the Imaris Server for the application and assign it to the
        #   mImarisApplication property
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
        if self._mUserControl == 1:
            if self._mImarisApplication is not None:
                self.closeImaris()


    def __str__(self):
        """Converts the pIceImarisConnector object to a string."""
        if self._mImarisApplication is None:
            return "pIceImarisConnector: not connected to an Imaris " \
                  "instance yet."
        else:
            return "pIceImarisConnector: connected to Imaris."


    def autocast(self, dataItem):
        """Casts IDataItems to their derived types.

SYNOPSIS:

@TODO

ARGUMENTS:

dataItem: an Imaris::IDataItem object

returns one of the Imaris::IDataItem subclasses:
                    - Imaris::IClippingPlane
                    - Imaris::IDataContainer
                    - Imaris::IFilaments
                    - Imaris::IFrame
                    - Imaris::IDataSet
                    - Imaris::IICells
                    - Imaris::ILightSource
                    - Imaris::IMeasurementPoints
                    - Imaris::ISpots
                    - Imaris::ISurfaces
                    - Imaris::IVolume
                    - Imaris::ISurpassCamera
                    - Imaris::IImageProcessing
                    - Imaris::IFactory
        """

        # Get the factory
        factory = self.mImarisApplication.GetFactory()

        # Cast
        if factory.IsLightSource(dataItem):
            return factory.ToLightSource(dataItem)
        elif factory.IsFrame(dataItem):
            return factory.ToFrame(dataItem)
        elif factory.IsVolume(dataItem):
            return factory.ToVolume(dataItem)
        elif factory.IsSpots(dataItem):
            return factory.ToSpots(dataItem)
        elif factory.IsSurfaces(dataItem):
            return factory.ToSurfaces(dataItem)
        elif factory.IsDataSet(dataItem):
            return factory.ToDataSet(dataItem)
        elif factory.IsSurpassCamera(dataItem):
            return factory.ToSurpassCamera(dataItem)
        elif factory.IsFilaments(dataItem):
            return factory.ToFilaments(dataItem)
        elif factory.IsClippingPlane(dataItem):
            return factory.ToClippingPlane(dataItem)
        elif factory.IsApplication(dataItem):
            return factory.ToApplication(dataItem)
        elif factory.IsMeasurementPoints(dataItem):
            return factory.ToMeasurementPoints(dataItem)
        elif factory.IsDataContainer(dataItem):
            return factory.ToDataContainer(dataItem)
        elif factory.IsCells(dataItem):
            return factory.ToCells(dataItem)
        elif factory.IsFactory(dataItem):
            return factory.ToFactory(dataItem)
        elif factory.IsImageProcessing(dataItem):
            return factory.ToImageProcessing(dataItem)
        else:
            raise ValueError('Invalid IDataItem object!')


    def closeImaris(self, quiet=False):
        """Closes the Imaris instance associated to the pIceImarisConnector
object and resets the mImarisApplication property.

SYNOPSIS:

@TODO

ARGUMENTS:

quiet : (optional, default False) If True, Imaris won't pop-up a save
        dialog and close silently.

        """

        # Check if the connection is still alive
        if not self.isAlive():
            return True

        # Close Imaris
        try:

            if quiet:
                self._mImarisApplication.SetVisible(False)

            self._mImarisApplication.Quit()
            self._mImarisApplication = None
            return True

        except:

            print("Error: " + str(sys.exc_info()[1]))
            return False


    # @TODO
    def createAndSetSpots(self, coords, timeIndices, radii, name,
                          color, container=None):
        """Creates Spots and adds them to the Surpass Scene.

SYNOPSIS:

(1) newSpots = createAndSetSpots(coords, timeIndices, radii, ...
                      name, color)
(2) newSpots = createAndSetSpots(coords, timeIndices, radii, ...
                      name, color, container)

ARGUMENTS:

coords      : (nx3) [x y z]n coordinate matrix (list)
              in dataset units
timeIndices : (nx1) vector (list) of spots time indices
radii       : (nx1) vector (list) of spots radii
name        : name of the Spots object
color       : (1x4), (0..1) vector (list, tuple or Numpy Array) of [R G B A] values
container   : (optional) if not set, the Spots object is added at the
              root of the Surpass Scene.
              Please note that it is the user's responsibility to
              attach the container to the surpass scene!

OUTPUTS

newSpots    : the generated Spots object.

        """
        if not self.isAlive():
            return None

        # Check input argument coords
        if not isinstance(coords, list):
            raise TypeError("coords must be a list.")

        nDims = len(coords[0]) if len(coords) != 0 else 0
        if nDims == 0:
            return None

        if nDims != 3:
            raise ValueError("coords must be an nx3 matrix of coordinates.")

        # Check input argument timeIndices
        if not isinstance(timeIndices, list):
            raise TypeError("timeIndices must be a list.")

        # Check input argument radii
        if not isinstance(radii, list):
            raise TypeError("radii must be a list.")

        # Check argument size consistency
        nSpots = len(coords)
        if len(timeIndices) != nSpots:
            raise ValueError("timeIndices must contain " +
                             str(nSpots) + "elements.")

        if len(radii) != nSpots:
            raise ValueError("radii must contain " +
                             str(nSpots) + "elements.")

        # If the container was not specified, add to the Surpass Scene
        if container is None:
            container = self._mImarisApplication.GetSurpassScene()
        else:
            # Make sure the container is valid
            if not self._mImarisApplication.GetFactory().IsDataContainer():
                raise ValueError("Invalid data container!")

        # Create a new Spots object
        newSpots = self._mImarisApplication.GetFactory().CreateSpots()

        # Set coordinates, time indices and radii
        newSpots.Set(coords, timeIndices, radii)

        # Set the name
        newSpots.SetName(name)

        # Set the color
        newSpots.SetColorRGBA(self.mapRgbaVectorToScalar(color))

        # Add the new Spots object to the container
        container.AddChild(newSpots, -1)

        # Return it
        return newSpots


    def createDataset(self):
        """Creates an Imaris dataset and replaces current one."""
        pass


    def display(self):
        """Displays the string representation of the pIceImarisConnector object."""

        print(self.__str__())


    def getAllSurpassChildren(self, recursive, typeFilter=None):
        """Returns all children of the surpass scene recursively.
Folders (i.e. IDataContainer objects) may be scanned (recursively)
but are not returned. Optionally, the returned objects may be filtered
by type.

SYNOPSIS:

@TODO

ARGUMENTS:

recursive:  {True | False} If True, folders will be scanned recursively;
            if False, only objects at root level will be inspected.

typeFilter: (optional) Filters the children by type. Only the surpass
            children of the specified type are returned; typeFilter is
            one of:

                'Cells'
                'ClippingPlane'
                'Dataset'
                'Filaments'
                'Frame'
                'LightSource'
                'MeasurementPoints'
                'Spots'
                'Surfaces'
                'SurpassCamera'
                'Volume'

        """

        # Check that recursive is boolen
        if recursive is not True and recursive is not False:
            raise ValueError("Invalid value for ''recursive''.")

        # Possible filter values
        if typeFilter is not None:
            possibleTypeFilters = ["Cells", "ClippingPlane", "Dataset", \
                                   "Frame", "LightSource", \
                                   "MeasurementPoints", "Spots", \
                                   "Surfaces", "SurpassCamera", "Volume"]

            if not typeFilter in possibleTypeFilters:
                raise ValueError("Invalid value for ''typeFilter''.")

        # Check that there is a Surpass Scene and there are children
        surpassScene = self.mImarisApplication.GetSurpassScene()
        if surpassScene is None:
            return []

        # Do we have children at all?
        if surpassScene.GetNumberOfChildren() == 0:
            return []

        # Scan the children recursively. For performance reasons, we use a
        # separate function for the case where filtering is requested.
        children = []
        if typeFilter is None:
            children = self._getChildrenAtLevel(surpassScene,
                                                recursive,
                                                children)
        else:
            children = self._getFilteredChildrenAtLevel(surpassScene,
                                                        recursive,
                                                        typeFilter,
                                                        children)

        return children


    # @TODO
    def getDataSubVolume(self, x0, y0, z0, channel,
        timepoint, dX, dY, dZ, iDataSet=None):
        """Returns a data subvolume from Imaris.

SYNOPSIS:

(1) stack = conn.getDataSubVolume(x0, y0, z0, channel, timepoint, dX, dY, dZ)
(2) stack = conn.getDataSubVolume(x0, y0, z0, channel, timepoint, dX, dY, dZ,
                                    iDataSet)

ARGUMENTS:

x0, y0, z0  : coordinates (0/1-based depending on indexing start) of
              the top-left vertex of the subvolume to be returned.
channel     : channel number (0/1-based depending on indexing start)
timepoint   : timepoint number (0/1-based depending on indexing start)
dX, dY, dZ  : extension of the subvolume to be returned
iDataset    : (optional) get the data volume from the passed IDataset
              object instead of current one; if omitted, current dataset
              (i.e. self._mImarisApplication.GetDataSet()) will be used.
              This is useful for instance when masking channels.

Coordinates and extension are in voxels and not in units!

The following holds:

if conn.indexingStart == 0:

    subA = conn.getDataSubVolume(x0, y0, z0, 0, 0, dX, dY, dZ)
    A = conn.getDataVolume(0, 0)
    A(x0 + 1 : x0 + dX, y0 + 1 : y0 + dY, z0 + 1 : z0 + dZ) === subA

if conn.indexingStart == 1:

    subA = conn.getDataSubVolume(x0, y0, z0, 1, 1, dX, dY, dZ)
    A = conn.getDataVolume(1, 1)
    A(x0 : x0 + dX - 1, y0 : y0 + dY - 1, z0 : z0 + dZ - 1) === subA

OUTPUTS:

stack : data subvolume (3D matrix)

REMARKS:

This function gets the volume as a 1D array and reshapes it in place.
        """
        pass


    def getDataVolume(self, channel, timepoint, iDataSet=None):
        """Returns the data volume from Imaris.

SYNOPSIS:

@TODO

ARGUMENTS:

channel:    channel number (0/1-based depending on indexing start)
timepoint:  timepoint number (0/1-based depending on indexing start)
iDataset:   (optional) get the data volume from the passed IDataset
            object instead of current one; if omitted, current dataset
            (i.e. self._mImarisApplication.GetDataSet()) will be used.
            This is useful for instance when masking channels.

OUTPUTS:

stack    :  data volume (3D Numpy array)

REMARKS:

    This function gets the volume as a 1D array and reshapes it in place.

        """

        if not self.isAlive():
            return None

        if iDataSet is None:
            iDataSet = self.mImarisApplication.GetDataSet()
        else:
            # Is the passed argument a valid iDataSet?
            if not self.mImarisApplication.GetFactory().IsDataSet(iDataSet):
                raise Exception("Invalid IDataSet object.")

        if iDataSet.GetSizeX() == 0:
            return None

        #  Convert channel and timepoint to 0-based indexing
        channel = channel - self._mIndexingStart
        timepoint = timepoint - self._mIndexingStart

        # Check that the requested channel and timepoint exist
        if channel > iDataSet.GetSizeC() - 1:
            raise Exception("The requested channel index is out of bounds!")
        if timepoint > iDataSet.GetSizeT() - 1:
            raise Exception("The requested time index is out of bounds!")

        # Get the dataset class
        imarisDataType = str(iDataSet.GetType())
        if imarisDataType == "eTypeUInt8":
            # Ice returns uint8 as a string: we must cast. This behavior might
            # be changed in the future.
            arr = np.array(iDataSet.GetDataVolumeAs1DArrayBytes(channel, timepoint))
            arr = np.frombuffer(arr.data, dtype=np.uint8)
        elif imarisDataType == "eTypeUInt16":
            arr = np.array(iDataSet.GetDataVolumeAs1DArrayShorts(channel, timepoint),
                              dtype=np.uint16)
        elif imarisDataType == "eTypeFloat":
            arr = np.array(iDataSet.GetDataVolumeAs1DArrayFloats(channel, timepoint),
                              dtype=np.float32)
        else:
            raise Exception("Bad value for iDataSet::getType().")

        # Reshape
        sz = self.getSizes()
        arr = np.reshape(arr, sz[0:3])

        # Return
        return arr


    def getExtends(self):
        """Returns the dataset extends."""

        # Wrap the extends into a tuple
        return (self._mImarisApplication.GetDataSet().GetExtendMinX(),
                self._mImarisApplication.GetDataSet().GetExtendMaxY(),
                self._mImarisApplication.GetDataSet().GetExtendMinY(),
                self._mImarisApplication.GetDataSet().GetExtendMaxY(),
                self._mImarisApplication.GetDataSet().GetExtendMinZ(),
                self._mImarisApplication.GetDataSet().GetExtendMaxZ())


    def getImarisVersionAsInteger(self):
        """Returns the Imaris version as an integer."""

        # Is Imaris running?
        if not self.isAlive():
            return 0

        # Get the version string and extract the major, minor and patch versions
        # The version must be in the form M.N.P
        version = self.mImarisApplication.GetVersion()

        # Parse version
        match = re.search(r'(\d)+\.(\d)+\.+(\d)?', version)
        if not match:
            raise Exception("Could not retrieve version information from Imaris.")

        # Get the major, minor and patch versions
        groups = match.groups()

        major = int(groups[0])
        if major is None:
            # Must be defined
            raise Exception("Invalid version information!")

        minor = int(groups[1])
        if minor is None:
            # Must be defined
            raise Exception("Invalid version information!")

        patch = int(groups[2])
        if patch is None:
            # In case the patch version is not set we assume 0 is meant
            patch = 0

        # Compute version as integer
        version = 1e6 * major + 1e4 * minor + 1e2 * patch

        # Cast into an integer and return
        return int(version)


    def getNumpyDatatype(self):
        """Returns the datatype of the dataset as a python Numpy type
(e.g. one of np.uint8, np.uint16, np.float32, or None if the
datatype is unknown to Imaris).

        """

        if not self.isAlive():
            return None

        # Alias
        iDataSet = self.mImarisApplication.GetDataSet()

        # Get the dataset class
        imarisDataType = str(iDataSet.GetType())
        if imarisDataType == "eTypeUInt8":
            return np.uint8
        elif imarisDataType == "seTypeUInt16":
            return np.uint16
        elif imarisDataType == "eTypeFloat":
            return np.float32
        elif imarisDataType == "eTypeUnknown":
            return None
        else:
            raise Exception("Bad value for iDataSet::getType().")


    def getSizes(self):
        """Returns the dataset sizes."""

        # Wrap the sizes into a tuple
        return (self._mImarisApplication.GetDataSet().GetSizeX(),
                self._mImarisApplication.GetDataSet().GetSizeY(),
                self._mImarisApplication.GetDataSet().GetSizeZ(),
                self._mImarisApplication.GetDataSet().GetSizeC(),
                self._mImarisApplication.GetDataSet().GetSizeT())

    # @TODO
    def getSurpassCameraRotationMatrix(self):
        """Calculates the rotation matrix that corresponds to current view in
        the Surpass Scene (from the Camera Quaternion) for the axes with
        "Origin Bottom Left".
        @TODO Verify the correctness for the other axes orientations.

SYNOPSIS:

[R, isI] = conn.getSurpassCameraRotationMatrix()

ARGUMENTS:

None

OUTPUTS:

R:      (4 x 4) rotation matrix
isI:    true if the rotation matrix is the Identity matrix, i.e. the
        camera is perpendicular to the dataset

        """
        pass


    def getSurpassSelection(self, typeFilter=None):
        """Returns the auto-casted current surpass selection. If
the 'typeFilter' parameter is specified, the object class is checked
against it and None is returned instead of the object if the type
does not match.

SYNOPSIS:

@TODO

ARGUMENTS:

typeFilter: {True | False} (optional, default False) Specifies
            the expected object class. If the selected object
            is not of the specified type, the function will
            return None instead. Type is one of:

                'Cells'
                'ClippingPlane'
                'Dataset'
                'Filaments'
                'Frame'
                'LightSource'
                'MeasurementPoints'
                'Spots'
                'Surfaces'
                'SurpassCamera'
                'Volume'

        """

        # Is Imaris running?
        if not self.isAlive():
            return None

        # Get current selection
        selection = self.autocast(self.mImarisApplication.GetSurpassSelection())
        if selection is None:
            return None

        # Check type?
        if typeFilter is None:
            return selection

        # If the object is not of the specified type, return None
        if not self._isOfType(selection, typeFilter):
            return None

        # Return the object
        return selection


    def getVoxelSizes(self):
        """Returns the X, Y, and Z voxel sizes of the dataset."""

        # Voxel size X
        vX = (self._mImarisApplication.GetDataSet().GetExtendMaxX() - \
              self._mImarisApplication.GetDataSet().GetExtendMinX()) / \
              self._mImarisApplication.GetDataSet().GetSizeX()

        # Voxel size Y
        vY = (self._mImarisApplication.GetDataSet().GetExtendMaxY() - \
              self._mImarisApplication.GetDataSet().GetExtendMinY()) / \
              self._mImarisApplication.GetDataSet().GetSizeY()

        # Voxel size Z
        vZ = (self._mImarisApplication.GetDataSet().GetExtendMaxZ() - \
              self._mImarisApplication.GetDataSet().GetExtendMinZ()) / \
              self._mImarisApplication.GetDataSet().GetSizeZ()

        # Wrap the voxel sizes into a tuple
        return (vX, vY, vZ)


    def info(self):
        """Prints pIceImarisConnector information."""

        # Display info to console
        print("pIceImarisConnector version " + self.version + " using:")
        print("- Imaris path: " + self._mImarisPath)
        print("- Imaris executable: " + self._mImarisExePath)
        print("- ImarisServer executable: " + self._mImarisServerExePath)
        print("- ImarisLib.jar archive: " + self._mImarisLibPath)


    def isAlive(self):
        """Checks whether the (stored) connection to Imaris is still alive."""

        # Do we have an ImarisApplication object?
        if self._mImarisApplication is None:
            return False

        # If we do, we try accessing it
        try:
            self.mImarisApplication.GetVersion()
            return True
        except:
            self._mImarisApplication = None
            return False


    def mapPositionsUnitsToVoxels(self, *args):
        """Maps voxel coordinates in dataset units to voxel indices.

SYNOPSIS

pos = conn.mapPositionsUnitsToVoxels(uPos)

INPUT

   uPos  : (N x 3) matrix containing the X, Y, Z coordinates in dataset
           units

OUTPUT

   pos   : (N x 3) matrix containing the X, Y, Z voxel indices

        """

        # Do we have a connection?
        if not self.isAlive():
            return None

        # Error message
        errMsg = "Expected an (n x 3) array or Numpy array."

        # Check the number, type and dimensions of arguments
        nArg = len(args)
        if nArg != 1:
            raise ValueError(errMsg)

        # Get the input
        uPos = args[0]

        # Check the input parameter uPos
        if not isinstance(uPos, list) and \
            not isinstance(uPos, np.ndarray):
            raise TypeError(errMsg)

        # If list, convert to Numpy array
        if isinstance(uPos, list):
            uPos = np.array(uPos)

        # Check dimensions
        if uPos.ndim != 2 or uPos.shape[1] != 3:
            raise ValueError(errMsg)

        # Get the voxel sizes into a Numpy array
        voxelSizes = np.array(self.getVoxelSizes())

        # Get the extends into a Numpy array
        extends = np.array([
            self.mImarisApplication.GetDataSet().GetExtendMinX(),
            self.mImarisApplication.GetDataSet().GetExtendMinY(),
            self.mImarisApplication.GetDataSet().GetExtendMinZ()])

        # Map units to voxels
        p = (uPos - extends) / voxelSizes + 0.5

        # Return the mapped coordinates in an array
        return p.tolist()


    def mapPositionsVoxelsToUnits(self, *args):
        """Maps voxel indices in dataset units to unit coordinates.

SYNOPSIS

pos = conn.mapPositionsVoxelsToUnits(vPos)

INPUT

   vPos  : (N x 3) matrix containing the X, Y, Z unit coordinates
            mapped onto a voxel grid

OUTPUT

   pos   : (N x 3) matrix containing the X, Y, Z coordinates in
           dataset units

        """

        # Is Imaris running?
        if not self.isAlive():
            return

        # Error message
        errMsg = "Expected an (n x 3) array or Numpy array."

        # Check the number, type and dimensions of arguments
        nArg = len(args)
        if nArg != 1:
            raise ValueError(errMsg)

        # Get the input
        vPos = args[0]

        # Check the input parameter vPos
        if not isinstance(vPos, list) and \
            not isinstance(vPos, np.ndarray) :
            raise TypeError(errMsg)

        # If list, convert to Numpy array
        if isinstance(vPos, list):
            vPos = np.array(vPos)

        # Check dimensions
        if vPos.ndim != 2 or vPos.shape[1] != 3:
            raise ValueError(errMsg)

        # Get the voxel sizes
        voxelSizes = np.array(self.getVoxelSizes())

        # Get the extends into a Numpy array
        extends = np.array([
            self.mImarisApplication.GetDataSet().GetExtendMinX(),
            self.mImarisApplication.GetDataSet().GetExtendMinY(),
            self.mImarisApplication.GetDataSet().GetExtendMinZ()])

        # Map units to voxels
        p = (vPos - 0.5) * voxelSizes + extends

        # Return the mapped coordinates in an array
        return p.tolist()


    # @TODO Finish
    def mapRgbaScalarToVector(self, rgbaScalar):
        """Maps an int32 RGBA scalar to an 1-by-4, (0..1) vector.

        Imaris returns an uint32 scalar as int32. We need to typecast
        before we can operate on it.
        
        """
        # rgbaScalar is a signed integer 32 bit, but we support
        # also the value already wrapped as an uint32 into a numpy
        # "scalar"
        if isinstance(rgbaScalar, int):
            rgbaScalar = np.array(rgbaScalar, dtype=np.uint32)
        elif isinstance(rgbaScalar, np.ndarray) and \
            rgbaScalar.dtype == np.uint32:
            pass
        else:
            raise TypeError('Expected integer of Numpy scalar (uint32).')

        # Extract the uint32 scalar into a vector of 4 uint8s
        rgbaUint8Vector = np.frombuffer(rgbaScalar.data, dtype=np.uint8)
        
        # And now tranform it into a vector of floats in the 0 .. 1 range
        return np.asarray(rgbaUint8Vector, dtype=np.float32) / 255 

    # @TODO Finish
    def mapRgbaVectorToScalar(self, rgbaVector):
        """Maps an 1-by-4, (0..1) RGBA vector to an int32 scalar.

        """

        # Make sure that rgbaScalar is a list or Numpy array with
        # four values in the 0 .. 1 range
        if isinstance(rgbaVector, list):
            rgbaVector = np.array(rgbaVector, dtype=np.float32)
        elif isinstance(rgbaVector, np.ndarray):
            pass
        else:
            raise TypeError('Expected list or Numpy array.')

        # Check rgbaVector
        if rgbaVector.ndim != 1 or rgbaVector.shape[0] != 4 or \
        np.any(np.logical_or(rgbaVector < 0, rgbaVector > 1)):
            raise ValueError("rgbaVector must be a vector with 4 elements in " +
                             "the 0 .. 1 range.")

        # Bring it into the 0..255 range
        rgbaVector = np.asarray(255 * rgbaVector, dtype=np.uint8)
        
        # Wrap it into an int32
        rgba = np.frombuffer(rgbaVector.data, dtype=np.int32)
        return int(rgba)

    # @TODO
    def setDataVolume(self, stack, channel, timepoint):
        """Sets the data volume to Imaris.

        """
        pass


    def startImaris(self, userControl=False):
        """Starts an Imaris instance and stores the ImarisApplication ICE object.

SYNOPSIS:

@TODO

ARGUMENTS:

userControl :   (optional, default False) The optional parameter
                userControl sets the fate of Imaris when the client
                is closed: if userControl is True, Imaris terminates
                when the pIceImarisConnector object (conn) is deleted.
                If is it set to False, Imaris stays open after the
                client is closed.

        """

        # Check the platform
        if not self._isSupportedPlatform():
            raise Exception('pIceImarisConnector can only work on Windows and Mac OS X.')

        # Store the userControl
        self._mUserControl = userControl

        # If an Imaris instance is open, we close it -- no questions asked
        if self.isAlive() == True:
            self.closeImaris(True)

        # Now we open a new one
        try:

            # Start ImarisServer
            if not self._startImarisServer():
                raise Exception("Could not start ImarisServer!")

            # Launch Imaris
            args = "id" + str(self._mImarisObjectID)
            try:
                subprocess.Popen([self._mImarisExePath, args], bufsize=-1)
            except OSError as o:
                print(o)
                return False
            except ValueError as v:
                print(v)
                return False
            except:
                print "Unexpected error:", sys.exc_info()[0]
                return False

            # Try getting the application over a certain time period in case it
            # takes to long for Imaris to be registered.
            nAttempts = 0
            while nAttempts < 200:
                try:
                    # A too quick call to mImarisLib.GetApplication() could
                    # potentially throw an exception and leave the _mImarisLib
                    # object in an unusable state. As a workaround, we
                    # reinstantiate ImarisLib() at every iteration. This
                    # will make sure that sooner or later we will get the
                    # application.
                    ImarisLib = self._importImarisLib()
                    self._mImarisLib = ImarisLib.ImarisLib()
                    vImaris = self._mImarisLib.GetApplication(self._mImarisObjectID)
                except:
                    print("Exception when trying to get the Application from ImariServer")

                if vImaris is not None:
                    break

                # Try again in 0.1 s
                time.sleep(0.1)

                # Increment nAttemps
                nAttempts += 1

            # At this point we should have the application
            if vImaris is None:
                print('Could not link to the Imaris application.')
                return False

            # We can store the application
            self._mImarisApplication = vImaris

            # Return success
            return True

        except:
            print("Error: " + str(sys.exc_info()[0]))


    # --------------------------------------------------------------------------
    #
    # PRIVATE METHODS
    #
    # --------------------------------------------------------------------------

    def _findImaris(self):
        """Gets or discovers the path to the Imaris executable."""

        # Try getting the environment variable IMARISPATH
        imarisPath = os.getenv('IMARISPATH')

        # If imarisPath is None, we search for Imaris
        if imarisPath is None:

            # Search for Imaris in reasonable places
            if self._ispc():
                tmp = "C:\\Program Files\\Bitplane"
            elif self._ismac():
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
        if self._ispc():
            exePath = os.path.join(imarisPath, 'Imaris.exe')
            serverExePath = os.path.join(imarisPath,
                                         'ImarisServerIce.exe')
            libPath = os.path.join(imarisPath, 'XT', 'python')
        elif self._ismac():
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


    def _findNewestVersionDir(self, directory):
        """Scans for candidate Imaris directories and returns the one
        with highest version number. For internal use only!

SYNOPSIS:

@TODO

ARGUMENTS:

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
            version = int(1e6 * major + 1e4 * minor + 1e2 * patch)

            # Is it the newest yet?
            if version > newestVersion:
                newestVersionDir = d
                newestVersion = version

        return newestVersionDir


    def _getChildrenAtLevel(self, container, recursive, children):
        """Scans the children of a given container recursively."""

        for i in range(container.GetNumberOfChildren()):

            # Get current child
            child = container.GetChild(i)

            # Is this a folder? If it is, call this function recursively
            if self.mImarisApplication.GetFactory().IsDataContainer(child):
                if recursive == True:
                    children = self._getChildrenAtLevel(self.autocast(child),
                                                        recursive,
                                                        children)
            else:
                children.append(self.autocast(child))

        return children


    def _getFilteredChildrenAtLevel(self, container, recursive, \
                                    typeFilter, children):
        """Scans the children of a certain type in a given container recursively."""

        for i in range(container.GetNumberOfChildren()):

            child = container.GetChild(i)

            # Is this a folder? If it is, call this function recursively
            if self.mImarisApplication.GetFactory().IsDataContainer(child):
                if recursive == True:
                    children = self._getFilteredChildrenAtLevel(
                        self.autocast(child), recursive, typeFilter, children)
            else:
                currentChild = self.autocast(child)
                if self._isOfType(currentChild, typeFilter):
                    children.append(currentChild)

        return children


    def _importImarisLib(self):
        """Imports the ImarisLib module."""

        # Dynamically find and import the ImarisLib module
        fileobj, pathname, description = imp.find_module('ImarisLib')
        ImarisLib = imp.load_module('ImarisLib', fileobj, pathname, description)
        fileobj.close()
        return ImarisLib


    def _isImarisServerIceRunning(self):
        """ Checks whether an instance of ImarisServerIce is already running and
can be reused.

        """

        # The check will be different on Windows and on Mac OS X
        if self._ispc():
            cmd = "tasklist /NH /FI \"IMAGENAME eq ImarisServerIce.exe\""
            result = subprocess.check_output(cmd)
            if "ImarisServerIce.exe" in result:
                return True

        elif self._ismac():
            result = subprocess.check_output(["ps", "aux"])
            if self._mImarisServerExePath in result:
                return True
        else:
            raise OSError('Unsupported platform.')

        return False


    def _ismac(self):
        """Returns true if pIceImarisConnector is being run on Mac OS X."""

        return platform.system() == "Darwin"


    def _isOfType(self, obj, typeValue):
        """Checks that a passed object is of a given type.

SYNOPSIS:

@TODO

ARGUMENTS:

obj: object for which the type is to be checked

typeValue:  one of:
            'Cells'
            'ClippingPlane'
            'Dataset'
            'Filaments'
            'Frame'
            'LightSource'
            'MeasurementPoints'
            'Spots'
            'Surfaces'
            'SurpassCamera'
            'Volume'

        """
        # Possible type values
        possibleTypeValues = ["Cells", "ClippingPlane", "Dataset", "Frame", \
                              "LightSource", "MeasurementPoints", "Spots", \
                              "Surfaces", "SurpassCamera", "Volume"]

        if not typeValue in possibleTypeValues:
            raise ValueError("Invalid value for typeValue.")

        # Get the factory
        factory = self.mImarisApplication.GetFactory()

        # Test the object
        if typeValue == 'Cells':
            return factory.IsCells(obj)
        elif typeValue == 'ClippingPlane':
            return factory.IsClippingPlane(obj)
        elif typeValue == 'Dataset':
            return factory.IsDataset(obj)
        elif typeValue == 'Filaments':
            return factory.IsFilaments(obj)
        elif typeValue == 'Frame':
            return factory.IsFrame(obj)
        elif typeValue == 'LightSource':
            return factory.IsLightSource(obj)
        elif typeValue == 'MeasurementPoints':
            return factory.IsMeasurementPoints(obj)
        elif typeValue == 'Spots':
            return factory.IsSpots(obj)
        elif typeValue == 'Surfaces':
            return factory.IsSurfaces(obj)
        elif typeValue == 'SurpassCamera':
            return factory.IsSurpassCamera(obj)
        elif typeValue == 'Volume':
            return factory.IsVolume(obj)
        else:
            raise ValueError('Bad value for ''typeValue''.')


    def _ispc(self):
        """Returns true if pIceImarisConnector is being run on Windows."""

        return platform.system() == "Windows"


    def _isSupportedPlatform(self):
        """Returns True if running on a supported platform."""
        return (self._ispc() or self._ismac())


    def _startImarisServer(self):
        """Starts an instance of ImarisServerIce and waits until it is ready
to accept connections."""

        # Imaris only runs on Windows and Mac OS X
        if not self._isSupportedPlatform():
            raise Exception('IceImarisConnector can only work on Windows and Mac OS X')

        # Check whether an instance of ImarisServerIce is already running.
        # If this is the case, we can return success
        if self._isImarisServerIceRunning():
            return True

        # We start an instance of ImarisServerIce and wait until it is running
        # before returning success. We set a 10s time out limit
        try:
            process = subprocess.Popen(self._mImarisServerExePath, bufsize=-1)
        except OSError as o:
            print(o)
            return False
        except ValueError as v:
            print(v)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return False

        if not process:
            return False

        # Now wait until ImarisIceServer is running (or we time out)
        t = time.time()
        timeout = t + 10
        while t < timeout:
            if self._isImarisServerIceRunning() == True:
                return True
            # Update the elapsed time
            t = time.time()

        return False
