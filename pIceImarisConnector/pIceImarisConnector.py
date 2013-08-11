import os
import sys
import platform
import glob
import re
import random
import imp
import subprocess
import time
import math
import numpy as np

class pIceImarisConnector(object):
    """pIceImarisConnector is a simple Python class that eases communication
between Bitplane Imaris and Python using the Imaris XT interface.

*Copyright Aaron Ponti, 2013.*

:param imarisApplication: (optional) if omitted, a pIceImarisConnector object is created that is not connected to any Imaris instance.

imarisApplication can be:

* None (i.e. omitted)
* an Imaris Application ID as provided by Imaris
* a pIceImarisConnector reference
* an Imaris Application ICE object.

If no input argument is provided, Imaris can then be started (and connected) using the ``startImaris()`` method:

>>> conn.startImaris()

    """

    # pIceImarisConnector version
    _mVersion = "0.3.0"

    # Imaris-related paths
    _mImarisPath = ""
    _mImarisExePath = ""
    _mImarisServerIceExePath = ""
    _mImarisLibPath = ""

    # ImarisLib object
    _mImarisLib = None

    # ICE ImarisApplication object
    _mImarisApplication = None

    # Imaris ID
    _mImarisObjectID = 0

    # Use control
    _mUserControl = False


    @property
    def version(self):
        return self._mVersion


    @property
    def mImarisApplication(self):
        return self._mImarisApplication


    def __new__(cls, *args, **kwargs):
        """Create or re-use a pIceImarisConnector object.

If an argument of type pIceImarisConnector is passed to __new__(),
this is returned; otherwise, a new pIceImarisConnector object is
instantiated and returned.

        """

        if args and args[0] is not None and \
                type(args[0]).__name__ == "pIceImarisConnector":
            # Reusing passed object
            return args[0]
        else:
            # Creating new object
            return object.__new__(cls, *args, **kwargs)


    def __init__(self, imarisApplication=None):
        """"Initializes the created pIceImarisConnector object.

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

        """

        # If imarisApplication is a pIceImarisConnector reference,
        # we return immediately, because we want to re-use the
        # object without changes. The __new__() method took care of
        # returnig a reference to the passed object instead of creating
        # a new one.
        if imarisApplication is not None and \
                type(imarisApplication).__name__ == "pIceImarisConnector":
            return

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
        """pIceImarisConnector destructor.

If UserControl is True, Imaris terminates when the IceImarisConnector
object is deleted. If is it set to False, Imaris stays open after the
IceImarisConnector object is deleted.

        """

        if self._mUserControl == True:
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

:param dataItem: object to be cast
:type  dataItem: Imaris::IDataItem

:return: object cast to the appropriate *Imaris::IDataItem* subclass.
:rtype: One of:

* Imaris::IClippingPlane
* Imaris::IDataContainer
* Imaris::IFilaments
* Imaris::IFrame
* Imaris::IDataSet
* Imaris::IICells
* Imaris::ILightSource
* Imaris::IMeasurementPoints
* Imaris::ISpots
* Imaris::ISurfaces
* Imaris::IVolume
* Imaris::ISurpassCamera
* Imaris::IImageProcessing
* Imaris::IFactory

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

:param quiet: (optional, default False) If True, Imaris won't pop-up a save dialog and close silently.
:type  quiet: Boolean

:return: True it Imaris could be closed successfully, False otherwise.
:rtype: Boolean

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


    def createAndSetSpots(self, coords, timeIndices, radii, name,
                          color, container=None):
        """Creates Spots and adds them to the Surpass Scene.

:param coords: (nx3) [x y z]n coordinate matrix in dataset units
:type coords: list
:param timeIndices: (nx1) vector (list) of spots time indices
:type timeIndices: list
:param radii: (nx1) vector (list) of spots radii
:type radii: list
:param name: name of the Spots object
:type name: string
:param color: (1x4), (0..1) vector of [R, G, B, A] values
:type color: list, tuple or float32 Numpy Array
:param container: (optional) if not set, the Spots object is added at the root of the Surpass Scene. Please note that it is the user's responsibility to attach the container to the surpass scene!
:type container: an Imaris::IDataContainer object


:return: the generated Spots object.
:rtype: Imaris::ISpots

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


    def createDataset(self, datatype, sizeX, sizeY, sizeZ, sizeC, sizeT, \
                      voxelSizeX=1, voxelSizeY=1, voxelSizeZ=1, deltaTime=1):
        """Creates an Imaris dataset and replaces current one.

:param datatype: datype for the dataset to be created
:type datatype: one of 'uint8', 'uint16', 'single', Imaris.tType.eTypeUInt8,
            Imaris.tType.eTypeUInt16, Imaris.tType.eTypeFloat

:param sizeX: dataset width
:type sizeX: int
:param sizeY: dataset height
:type sizeY: int
:param sizeZ: number of planes
:type sizeZ: int
:param sizeC: number of channels
:type sizeC: int
:param sizeT: number of timepoints
:type sizeT: int
:param voxelSizeX: (optional, default = 1) voxel size in X direction
:type voxelSizeX: float
:param voxelSizeY: (optional, default = 1) voxel size in Y direction
:type voxelSizeY: float
:param voxelSizeZ: (optional, default = 1) voxel size in Z direction
:type voxelSizeZ: float
:param deltaTime: (optional, default = 1) time difference between consecutive time points
:type deltaTime: float

:return: created DataSet
:rtype: Imaris::IDataSet

**EXAMPLE**

>>> conn.createDataset('uint8', 100, 200, 50, 3, 10, 0.20, 0.25, 0.5, 0.1)

**REMARKS**

The function takes care of adding the created dataset to Imaris.
        """

        # Is Imaris running?
        if not self.isAlive():
            return

        # Get the Factory
        factory = self._mImarisApplication.GetFactory()

        # Get the ImarisType object
        if self._mImarisApplication.GetDataSet() is not None:
            ImarisTType = self._mImarisApplication.GetDataSet().GetType()
        else:
            ImarisTType = factory.CreateDataSet().GetType()

        # Data type
        if datatype == np.uint8 or \
        str(datatype) == 'uint8' or \
        str(datatype) == 'eTypeUInt8':

            imarisDataType = ImarisTType.eTypeUInt8

        elif datatype == np.uint16 or \
        str(datatype) == 'uint16' or \
        str(datatype) == 'eTypeUInt16':

            imarisDataType = ImarisTType.eTypeUInt16

        elif datatype == np.float32 or \
        str(datatype) == 'float' or \
        str(datatype) == 'eTypeFloat':

            imarisDataType = ImarisTType.eTypeFloat

        else:

            raise ValueError("Unknown datatype " + datatype )

        # Create the dataset
        iDataSet = factory.CreateDataSet()
        iDataSet.Create(imarisDataType, sizeX, sizeY, sizeZ, sizeC, sizeT)

        # Apply the spatial calibration
        iDataSet.SetExtendMinX(0)
        iDataSet.SetExtendMinY(0)
        iDataSet.SetExtendMinZ(0)
        iDataSet.SetExtendMaxX(sizeX * voxelSizeX)
        iDataSet.SetExtendMaxY(sizeY * voxelSizeY)
        iDataSet.SetExtendMaxZ(sizeZ * voxelSizeZ)

        # Apply the temporal calibration
        iDataSet.SetTimePointsDelta(deltaTime)

        # Set the dataset in Imaris
        self._mImarisApplication.SetDataSet(iDataSet)

        # Return the created dataset
        return iDataSet


    def display(self):
        """Displays the string representation of the pIceImarisConnector object."""

        print(self.__str__())


    def getAllSurpassChildren(self, recursive, typeFilter=None):
        """Returns all children of the surpass scene recursively. Folders (i.e. IDataContainer objects) may be scanned (recursively) but are not returned. Optionally, the returned objects may be filtered by type.

:param recursive:  If True, folders will be scanned recursively; if False, only objects at root level will be inspected.
:type recursive: Boolean
:param typeFilter: (optional) Filters the children by type. Only the surpass children of the specified type are returned. One of:
:type typeFilter: string

* 'Cells'
* 'ClippingPlane'
* 'Dataset'
* 'Filaments'
* 'Frame'
* 'LightSource'
* 'MeasurementPoints'
* 'Spots'
* 'Surfaces'
* 'SurpassCamera'
* 'Volume'

:return: child objects
:rtype: list

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


    def getDataSubVolume(self, x0, y0, z0, channel,
        timepoint, dX, dY, dZ, iDataSet=None):
        """Returns a data subvolume from Imaris.

:param x0: x coordinate of the top-left vertex of the subvolume to be returned.
:type x0: int
:param y0: y coordinate of the top-left vertex of the subvolume to be returned.
:type y0: int
:param z0: z coordinate of the top-left vertex of the subvolume to be returned.
:type z0: int
:param channel: channel index
:type channel: int
:param timepoint: timepoint index
:type timepoint: int
:param dX: extension in x direction of the subvolume to be returned.
:param dY: extension in y direction of the subvolume to be returned.
:param dZ: extension in z direction of the subvolume to be returned.
:param iDataSet: (optional) get the data volume from the passed IDataSet object instead of current one; if omitted, current dataset (i.e. ``conn.mImarisApplication.GetDataSet()``) will be used. This is useful for instance when masking channels.
:type iDataSet: Imaris::IDataSet

:return: data subvolume
:rtype: Numpy array with dtype being on of ``numpy.uint8``, ``numpy.uint16``, ``numpy.float32``.

**EXAMPLE**

The following holds:

>>> stack = conn.getDataVolume(0, 0)
>>> subVolume = conn.getDataSubVolume(x0, y0, z0, 0, 0, dX, dY, dZ)
>>> subStack = stack[z0 : z0 + dZ, y0 : y0 + dY, x0 : x0 + dX]
>>> subVolume === subStack

**REMARKS**

* Implementation detail: this function gets the subvolume as a 1D array and reshapes it in place.
* Coordinates and extensions are in voxels and not in units!

        """

        if not self.isAlive():
            return None

        if iDataSet is None:
            iDataSet = self.mImarisApplication.GetDataSet()
        else:
            # Is the passed argument a valid iDataSet?
            if not self.mImarisApplication.GetFactory().IsDataSet(iDataSet):
                raise Exception("Invalid IDataSet object.")

        if iDataSet is None or iDataSet.GetSizeX() == 0:
            return None

        # Check the boundaries
        if x0 < 0 or x0 > iDataSet.GetSizeX() - 1:
            raise ValueError('The requested starting position x0 is out of bounds.')

        if y0 < 0 or y0 > iDataSet.GetSizeY() - 1:
            raise ValueError('The requested starting position y0 is out of bounds.')

        if z0 < 0 or z0 > iDataSet.GetSizeZ() - 1:
            raise ValueError('The requested starting position z0 is out of bounds.')

        if channel < 0 or channel > iDataSet.GetSizeC() - 1:
            raise ValueError('The requested channel index is out of bounds.')

        if timepoint < 0 or timepoint > iDataSet.GetSizeT() - 1:
            raise ValueError('The requested timepoint index is out of bounds.')

        # Check that we are within bounds
        if x0 + dX > iDataSet.GetSizeX():
            raise ValueError('The requested x range dimension is out of bounds.')

        if y0 + dY > iDataSet.GetSizeY():
            raise ValueError('The requested x range dimension is out of bounds.')

        if z0 + dZ > iDataSet.GetSizeZ():
            raise ValueError('The requested x range dimension is out of bounds.')

        # Check that the requested channel and timepoint exist
        if channel < 0 or channel > iDataSet.GetSizeC() - 1:
            raise Exception("The requested channel index is out of bounds!")
        if timepoint < 0 or timepoint > iDataSet.GetSizeT() - 1:
            raise Exception("The requested time index is out of bounds!")

        # Get the dataset class
        imarisDataType = str(iDataSet.GetType())
        if imarisDataType == "eTypeUInt8":
            # Ice returns uint8 as a string: we must cast. This behavior might
            # be changed in the future.
            arr = np.array(iDataSet.GetDataSubVolumeAs1DArrayBytes( \
                x0, y0, z0, channel, timepoint, dX, dY, dZ))
            arr = np.frombuffer(arr.data, dtype=np.uint8)
        elif imarisDataType == "eTypeUInt16":
            arr = np.array(iDataSet.GetDataSubVolumeAs1DArrayShorts( \
                x0, y0, z0, channel, timepoint, dX, dY, dZ), \
                dtype=np.uint16)
        elif imarisDataType == "eTypeFloat":
            arr = np.array(iDataSet.GetDataSubVolumeAs1DArrayFloats( \
                x0, y0, z0, channel, timepoint, dX, dY, dZ), \
                dtype=np.float32)
        else:
            raise Exception("Bad value for iDataSet::getType().")

        # Reshape
        arr = np.reshape(arr, (dZ, dY, dX))

        # Return
        return arr


    def getDataVolume(self, channel, timepoint, iDataSet=None):
        """Returns the data volume from Imaris.

:param channel: channel index
:type channel: int
:param timepoint: timepoint index
:type timepoint: int
:param iDataSet: (optional) get the data volume from the passed IDataSet object instead of current one; if omitted, current dataset (i.e. ``conn.mImarisApplication.GetDataSet()``) will be used. This is useful for instance when masking channels.

:return:  data volume (3D Numpy array).
:rtype: Numpy array with dtype being on of ``np.uint8``, ``np.uint16``, ``np.float32``.

**REMARKS**

Implementation detail: this function gets the volume as a 1D array and reshapes it in place.

        """

        if not self.isAlive():
            return None

        if iDataSet is None:
            iDataSet = self.mImarisApplication.GetDataSet()
        else:
            # Is the passed argument a valid iDataSet?
            if not self.mImarisApplication.GetFactory().IsDataSet(iDataSet):
                raise Exception("Invalid IDataSet object.")

        if iDataSet is None or iDataSet.GetSizeX() == 0:
            return None

        # Check that the requested channel and timepoint exist
        if channel < 0 or channel > iDataSet.GetSizeC() - 1:
            raise Exception("The requested channel index is out of bounds!")
        if timepoint < 0 or timepoint > iDataSet.GetSizeT() - 1:
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
        arr = np.reshape(arr, (sz[2], sz[1], sz[0]))

        # Return
        return arr


    def getExtends(self):
        """Returns the dataset extends.

:return: DataSet extends
:rtype: tuple

The extends tuple is: ``(minX, minY, minZ, maxX, maxY, maxZ)``, where:

* minX : min extend along X dimension,
* minY : min extend along Y dimension,
* minZ : min extend along Z dimension,
* maxX : max extend along X dimension,
* maxY : max extend along Y dimension,
* maxZ : max extend along Z dimension.

        """

        # Wrap the extends into a tuple
        return (self._mImarisApplication.GetDataSet().GetExtendMinX(),
                self._mImarisApplication.GetDataSet().GetExtendMaxY(),
                self._mImarisApplication.GetDataSet().GetExtendMinY(),
                self._mImarisApplication.GetDataSet().GetExtendMaxY(),
                self._mImarisApplication.GetDataSet().GetExtendMinZ(),
                self._mImarisApplication.GetDataSet().GetExtendMaxZ())


    def getImarisVersionAsInteger(self):
        """Returns the Imaris version as an integer.

The conversion is performed as follows: ``v = 100000 * Major + 10000 * Minor + 100 * Patch``

:return: Imaris version as integer.
:rtype: int

        """

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
        """Returns the datatype of the dataset as a python Numpy type (or None).

:return: datatype of the dataset as a Numpy type
:rtype: one of ``np.uint8``, ``np.uint16``, ``np.float32``, or ``None`` if the type is unknown in Imaris.

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
            raise Exception("Bad value for iDataSet::GetType().")


    def getSizes(self):
        """Returns the dataset sizes.

:return: DataSet sizes
:rtype: tuple

The sizes tuple is: ``(sizeX, sizeY, sizeZ, sizeC, sizeT)``, where:

* sizeX : dataset size X,
* sizeY : dataset size Y,
* sizeZ : number of planes,
* sizeC : number of channels,
* sizeT : number of time points.

        """

        # Wrap the sizes into a tuple
        return (self._mImarisApplication.GetDataSet().GetSizeX(),
                self._mImarisApplication.GetDataSet().GetSizeY(),
                self._mImarisApplication.GetDataSet().GetSizeZ(),
                self._mImarisApplication.GetDataSet().GetSizeC(),
                self._mImarisApplication.GetDataSet().GetSizeT())


    def getSurpassCameraRotationMatrix(self):
        """Calculates the rotation matrix that corresponds to current view in the Surpass Scene (from the Camera Quaternion) for the axes with "Origin Bottom Left".

:return: tuple with (4 x 4) rotation matrix (R) and a Boolean (isI) that indicates whether or not the rotation matrix is the Identity matrix (i.e. the camera is perpendicular to the dataset).
:rtype: tuple (R, isI)

**REMARKS**

**TODO**: Verify the correctness for the other axes orientations.

        """

        # Get the camera
        vCamera = self.mImarisApplication.GetSurpassCamera();
        if vCamera is None:
            return None

        # Get the camera position quaternion
        q = vCamera.GetOrientationQuaternion();

        # Aliases
        X = q[0];
        Y = q[1];
        Z = q[2];
        W = q[3];

        # Make sure the quaternion is a unit quaternion
        n2 = X**2 + Y**2 + Z**2 + W**2
        if abs(n2 - 1) > 1e-4:
            n = math.sqrt(n2)
            X = X / n
            Y = Y / n
            Z = Z / n
            W = W / n

        # Calculate the rotation matrix R from the quaternion
        R = np.zeros((4, 4), dtype=np.float32)
        x2 = X + X
        y2 = Y + Y
        z2 = Z + Z;
        xx = X * x2
        xy = X * y2
        xz = X * z2
        yy = Y * y2
        yz = Y * z2
        zz = Z * z2
        wx = W * x2
        wy = W * y2
        wz = W * z2;

        R[0, 0] = 1.0 - (yy + zz)
        R[0, 1] = xy - wz
        R[0, 2] = xz + wy

        R[1, 0] = xy + wz
        R[1, 1] = 1.0 - (xx + zz)
        R[1, 2] = yz - wx

        R[2, 0] = xz - wy
        R[2, 1] = yz + wx
        R[2, 2] = 1.0 - (xx + yy)

        R[3, 3] = 1.0

        # Is R the Identity matrix?
        T = R == np.identity(4)
        isI = np.all(abs(R - T) < 1e-4)

        # Return R and isI
        return (R, isI)


    def getSurpassSelection(self, typeFilter=None):
        """Returns the auto-cast current surpass selection. If the 'typeFilter' parameter is specified, the object class is checked against it and None is returned instead of the object if the type does not match.

:param typeFilter: (optional, default False) Specifies the expected object class. If the selected object is not of the specified type, the function will return None instead. Type is one of:
:type typeFilter: Boolean

* 'Cells'
* 'ClippingPlane'
* 'Dataset'
* 'Filaments'
* 'Frame'
* 'LightSource'
* 'MeasurementPoints'
* 'Spots'
* 'Surfaces'
* 'SurpassCamera'
* 'Volume'

:return: autocast, currently selected surpass object; if nothing is selected, or if the object class does not match the passed type, selection will be None instead.
:rtype: One of:

* Imaris::IClippingPlane
* Imaris::IDataContainer
* Imaris::IFilaments
* Imaris::IFrame
* Imaris::IDataSet
* Imaris::IICells
* Imaris::ILightSource
* Imaris::IMeasurementPoints
* Imaris::ISpots
* Imaris::ISurfaces
* Imaris::IVolume
* Imaris::ISurpassCamera
* Imaris::IImageProcessing
* Imaris::IFactory

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
        """Returns the X, Y, and Z voxel sizes of the dataset.

:return: dataset voxel sizes
:rtype: tuple

The voxelsize tuple is: ``(voxelSizeX, voxelSizeY, voxelSizeZ)``, where:

* voxelSizeX: voxel Size in X direction,
* voxelSizeY: voxel Size in Y direction,
* voxelSizeZ: voxel Size in Z direction.

        """

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
        """Prints to console the full paths to the Imaris and ImarisServerIce executables  and the ImarisLib module.

        """

        # Display info to console
        print("pIceImarisConnector version " + self.version + " using:")
        print("- Imaris path: " + self._mImarisPath)
        print("- Imaris executable: " + self._mImarisExePath)
        print("- ImarisServerIce executable: " + self._mImarisServerIceExePath)
        print("- ImarisLib module: " + self._mImarisLibPath)


    def isAlive(self):
        """Checks whether the (stored) connection to Imaris is still alive.

:return: True if the connection is still alive, False otherwise.
:rtype: Boolean

        """

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


    def mapPositionsUnitsToVoxels(self, uPos):
        """Maps voxel coordinates in dataset units to voxel indices.

:param uPos: (N x 3) matrix containing the X, Y, Z coordinates in dataset units.
:type uPos: list or float32 Numpy array.

:return: (N x 3) matrix containing the X, Y, Z voxel indices.
:rtype: list

        """

        # Do we have a connection?
        if not self.isAlive():
            return None

        # Error message
        errMsg = "Expected an (n x 3) list or Numpy array (np.float32)."

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

        # Make sure to have a float32 array
        if uPos.dtype != np.float32:
            uPos = uPos.astype(np.float32)

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


    def mapPositionsVoxelsToUnits(self, vPos):
        """Maps voxel indices in dataset units to unit coordinates.

:param vPos: (N x 3) matrix containing the X, Y, Z unit coordinates mapped onto a voxel grid.
:type vPos: list or float32 Numpy array.

:return: (N x 3) matrix containing the X, Y, Z coordinates in dataset units.
:rtype: list

        """

        # Is Imaris running?
        if not self.isAlive():
            return

        # Error message
        errMsg = "Expected an (n x 3) array or Numpy array."

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

        # Make sure to have a float32 array
        if vPos.dtype != np.float32:
            vPos = vPos.astype(np.float32)

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


    def mapRgbaScalarToVector(self, rgbaScalar):
        """Maps an int32 RGBA scalar to an 1-by-4, (0..1) float vector.

:param rgbaScalar: scalar coding for RGBA (as returned from Imaris via the ``GetColorRGBA()`` method of IDataItem objects).
:type rgbaScalar: int32

:return: 1-by-4 array with [R, G, B, A] indicating (R)ed, (G)reen, (B)lue, and (A)lpha (=transparency; 0 is opaque) in the 0..1 range.
:rtype: float Numpy array

**IMPORTANT REMARKS**

Imaris stores the color components of objects internally as an **uint32** scalar. When this scalar is returned by ImarisXT via the ``GetColorRGBA()`` method, it reaches python as **signed int32** instead.

By the way the R, G, B and A components are packed into the scalar, a forced typecast from uint32 to int32 corrupts the value of the transparency component (the actual colors are not affected). In case the transparency is zero, the uint32 and int32 rendition of the number is the same, and there is no problem; but if it is not, the returned value WILL BE NEGATIVE and will need to be casted before it can be processed.

The mapRgbaScalarToVector() method will transparently work around this problem for you.

**EXAMPLE**

In this example, current color of a Spots object is obtained from Imaris and pushed back.

>>> spots = conn.getSurpassSelection('Spots')
>>> current = conn.mapRgbaScalarToVector(spots.GetColorRGBA())
>>> spots.SetColorRGBA(conn.mapRgbaVectorToScalar(current))

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


    def mapRgbaVectorToScalar(self, rgbaVector):
        """Maps an 1-by-4, (0..1) RGBA vector to an int32 scalar.

:param rgbaVector: 1-by-4 array with [R, G, B, A] indicating (R)ed, (G)reen, (B)lue, and (A)lpha (=transparency; 0 is opaque). All values are between 0 and 1.
:type rgbaVector: float32 Numpy array

:return: scalar coding for RGBA (to be used with the ``SetColorRGBA()`` method of IDataItem objects).
:rtype: int32

**IMPORTANT REMARKS**

The way one calculates the RGBA value from an [R, G, B, A] vector (with the values of R, G, B, and A all between 0 and 1) is simply:

``uint32([R G B A] * [1 256 256^2 256^3])``

(where * is the matrix product). This gives a number between 0 and 2^32 - 1.

To pass this number to Imaris through ImarisXT via the ``SetColorRGBA()`` method, we need to type cast it to **signed int32**. If we do not do this, Imaris will misinterpret the value for the transparency.

The mapRgbaVectorToScalar() method will transparently work around this problem for you.

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
        rgbaVector = np.asarray(np.round(255 * rgbaVector), dtype=np.uint8)

        # Wrap it into an int32
        rgba = np.frombuffer(rgbaVector.data, dtype=np.int32)
        return int(rgba)


    def setDataVolume(self, stack, channel, timepoint):
        """Sets the data volume to Imaris.

:param stack: 3D array
:type stack: np.uint8, np.uint16 or np.float32
:param channel: channel index
:type channel: int
:param timepoint: timepoint index
:type timepoint: int

**REMARKS**

If a dataset exists, the X, Y, and Z dimensions must match the ones of the stack being copied in. If no dataset exists, one will be created to fit it with default other values.

        """

        if not self.isAlive():
            return None

        # Check that we have a numpy array
        if not isinstance(stack, np.ndarray):
            raise TypeError("Expected numpy array.")

        # Get the dataset
        iDataSet = self._mImarisApplication.GetDataSet()

        if iDataSet is None:

            # Create and store a new dataset
            sz = stack.shape
            if len(sz) == 2:
                sz = (sz[0], sz[1], 1)
            iDataSet = self.createDataset(stack.dtype, sz[0], sz[1], sz[2], 1, 1)

        # Check that the requested channel and timepoint exist
        if channel > iDataSet.GetSizeC() - 1:
            raise Exception("The requested channel index is out of bounds!")
        if timepoint > iDataSet.GetSizeT() - 1:
            raise Exception("The requested time index is out of bounds!")

        # Get the dataset class (we enforce datatype compatibility)
        imarisDataType = str(iDataSet.GetType())
        if imarisDataType == "eTypeUInt8":
            if stack.dtype != np.uint8:
                raise TypeError("Incompatible datatype (expected numpy.uint8.")
            iDataSet.SetDataVolumeAs1DArrayBytes(stack.ravel(), channel, timepoint)
        elif imarisDataType == "eTypeUInt16":
            if stack.dtype != np.uint16:
                raise TypeError("Incompatible datatype (expected numpy.uint16.")
            iDataSet.SetDataVolumeAs1DArrayShorts(stack.ravel(), channel, timepoint)
        elif imarisDataType == "eTypeFloat":
            if stack.dtype != np.float32:
                raise TypeError("Incompatible datatype (expected numpy.float32.")
            iDataSet.SetDataVolumeAs1DArrayFloats(stack.ravel(), channel, timepoint)
        else:
            raise Exception("Bad value for iDataSet::getType().")


    def startImaris(self, userControl=False):
        """Starts an Imaris instance and stores the ImarisApplication ICE object.

:param userControl: (optional, default False) The optional parameter userControl sets the fate of Imaris when the client is closed: if userControl is True, Imaris terminates when the pIceImarisConnector object is deleted. If is it set to False, Imaris stays open after the pIceImarisConnector object is deleted.
:type userControl: Boolean

:return: True if starting Imaris was successful, False otherwise.
:rtype: Boolean

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

            # Start ImarisServerIce
            if not self._startImarisServerIce():
                raise Exception("Could not start ImarisServerIce!")

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
    # PRIVATE METHODS FOR INTERNAL USE ONLY.
    #
    #    Please do not rely on the API of these methods to be preserved!
    #
    # --------------------------------------------------------------------------

    def _findImaris(self):
        """Gets or discovers the path to the Imaris executable. For internal use only!

        """

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

        # Set the path to the Imaris and ImarisServerIce executable and to
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
            raise OSError("Could not find the ImarisServerIce executable.")

        # Now we can store the information and return success
        self._mImarisExePath = exePath
        self._mImarisServerIceExePath = serverExePath
        self._mImarisLibPath = libPath


    def _findNewestVersionDir(self, directory):
        """Scans for candidate Imaris directories and returns the one with highest version number. For internal use only!

:param directory:  directory to be scanned. Most likely C:\\Program Files\\Bitplane in Windows and /Applications on Mac OS X.
:type directory: string

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
        """Scans the children of a given container recursively. For internal use only!

:param container: data container to be scanned for children
:type container: Imaris::IDataContainer
:param recursive: True if the container must be scanned recursively, False otherwise.
:type recursive: Boolean
:param children : list of children. Since this is a recursive function, the list of children is passed as input so that the children found in current iteration can be appended to the list and returned for the next iteration.
:type children: list

:return: children found (so far).
:rtype: list

        """

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
        """Scans the children of a certain type in a given container recursively. For internal use only!

:param container: data container to be scanned for children
:type container: Imaris::IDataContainer
:param recursive: True if the container must be scanned recursively, False otherwise.
:type recursive: Boolean
:param typeFilter: Filters the children by type. Only the surpass children of the specified type are returned. One of:
:type typeFilter: string

* 'Cells'
* 'ClippingPlane'
* 'Dataset'
* 'Filaments'
* 'Frame'
* 'LightSource'
* 'MeasurementPoints'
* 'Spots'
* 'Surfaces'
* 'SurpassCamera'
* 'Volume'

:param children : list of children. Since this is a recursive function, the list of children is passed as input so that the children found in current iteration can be appended to the list and returned for the next iteration.
:type children: list

:return: children found (so far).
:rtype: list

        """

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
        """Imports the ImarisLib module. For internal use only!

        """

        # Dynamically find and import the ImarisLib module
        fileobj, pathname, description = imp.find_module('ImarisLib')
        ImarisLib = imp.load_module('ImarisLib', fileobj, pathname, description)
        fileobj.close()
        return ImarisLib


    def _isImarisServerIceRunning(self):
        """ Checks whether an instance of ImarisServerIce is already running and can be reused. For internal use only!

:return: True is an instance of ImarisServerIce is running and can be reused, False otherwise.
:rtype: Boolean

        """

        # The check will be different on Windows and on Mac OS X
        if self._ispc():
            cmd = "tasklist /NH /FI \"IMAGENAME eq ImarisServerIce.exe\""
            result = subprocess.check_output(cmd)
            if "ImarisServerIce.exe" in result:
                return True

        elif self._ismac():
            result = subprocess.check_output(["ps", "aux"])
            if self._mImarisServerIceExePath in result:
                return True
        else:
            raise OSError('Unsupported platform.')

        return False


    def _ismac(self):
        """Returns true if pIceImarisConnector is being run on Mac OS X. For internal use only!

:return: True if pIceImarisConnector is being run on Mac OS X, False otherwise.
:rtype: Boolean

        """

        return platform.system() == "Darwin"


    def _isOfType(self, obj, typeValue):
        """Checks that a passed object is of a given type. For internal use only!

:param obj: object for which the type is to be checked.
:type obj: one of the Imaris objects
:param typeValue: Required type for the object. One of:
:type typeValue: string

* 'Cells'
* 'ClippingPlane'
* 'Dataset'
* 'Filaments'
* 'Frame'
* 'LightSource'
* 'MeasurementPoints'
* 'Spots'
* 'Surfaces'
* 'SurpassCamera'
* 'Volume'

:return: True if the checked object is of the passed type, False otherwise.
:rtype: Boolean

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
        """Returns true if pIceImarisConnector is being run on Windows. For internal use only!

:return: True if pIceImarisConnector is being run on Windows, False otherwise.
:rtype: Boolean

        """

        return platform.system() == "Windows"


    def _isSupportedPlatform(self):
        """Returns True if running on a supported platform. For internal use only!

:return: True if pIceImarisConnector is being run on Windows or Mac OS X, False otherwise.
:rtype: Boolean

        """
        return (self._ispc() or self._ismac())


    def _startImarisServerIce(self):
        """Starts an instance of ImarisServerIce and waits until it is ready to accept connections. For internal use only!

:return: True if ImarisServerIce could be started successfully, False otherwise.
:rtype: Boolean

        """

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
            process = subprocess.Popen(self._mImarisServerIceExePath, bufsize=-1)
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
