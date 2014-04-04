'''
Name       pIceImarisApplication Test Unit
Purpose    Test pIceImarisApplication

Author     Aaron Ponti

Created    21-03-2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

import os
import numpy as np

from pIceImarisConnector import pIceImarisConnector

if __name__ == '__main__':

    # ImarisConnector version
    # =========================================================================
    conn = pIceImarisConnector()
    print('Testing IceImarisConnector version ' + conn.version)
    del(conn)

    # Instantiate pIceImarisConnector object without parameters
    # =========================================================================
    print('Instantiate pIceImarisConnector conn1 object without parameters...')
    conn1 = pIceImarisConnector()
    conn1.display()
    conn1.info()

    # Instantiate pIceImarisConnector object with existing instance as parameter
    # =========================================================================
    print('Instantiate pIceImarisConnector object conn2 with existing instance conn1 as parameter...')
    conn2 = pIceImarisConnector(conn1)

    # Check that conn1 and conn2 are the same object
    # =========================================================================
    print("Check that conn1 and conn2 are the same object...")
    assert(conn1 is conn2)

    # Delete the objects
    # =========================================================================
    del(conn1)
    del(conn2)

    # Create an ImarisConnector object
    # =========================================================================
    print('Create a pIceImarisConnector object...')
    conn = pIceImarisConnector()

    # Start Imaris
    # =========================================================================
    print('Start Imaris...')
    assert(conn.startImaris() == True)

    # Test that the connection is valid
    # =========================================================================
    print('Get version...')
    assert(conn.getImarisVersionAsInteger() > 0)
    print('Test if connection is alive...')
    assert(conn.isAlive() == True)

    # Open a file
    # =======================================================s==================
    print('Load file...')
    currFilePath = os.path.realpath(__file__)
    currPath = os.path.dirname(currFilePath)
    filename = os.path.join(currPath, 'PyramidalCell.ims')
    conn.mImarisApplication.FileOpen(filename, '')

    # Check that there is something loaded
    # =========================================================================
    print('Test that the file was loaded...')
    assert(conn.mImarisApplication.GetDataSet().GetSizeX > 0)

    # Check the extends
    # =========================================================================
    print('Check the dataset extends...')
    EXTENDS = (-0.1140, 57.8398, -0.1140, 57.8398, -0.1510, 20.6310)
    extends = conn.getExtends()
    assert(all([abs(x - y) < 1e-4 for x, y in zip(EXTENDS, extends)]))

    minX, maxX, minY, maxY, minZ, maxZ = conn.getExtends()
    assert(all([abs(x - y) < 1e-4 for x, y in \
                zip(EXTENDS, (minX, maxX, minY, maxY, minZ, maxZ))]))

    # Check the voxel size
    # =========================================================================
    print('Check the voxel size...')
    VOXELSIZES = (0.2273, 0.2282, 0.3012)
    voxelSizes = conn.getVoxelSizes()
    assert(all([abs(x - y) < 1e-4 for x, y in zip(VOXELSIZES, voxelSizes)]))

    vX, vY, vZ = conn.getVoxelSizes()
    assert(all([abs(x - y) < 1e-4 for x, y in zip(VOXELSIZES, (vX, vY, vZ))]))

    # Check the dataset size
    #
    #   X = 255
    #   Y = 254
    #   Z =  69
    #   C =   1
    #   T =   1
    #
    # =========================================================================
    print('Check the dataset size...')
    DATASETSIZE = (255, 254, 69, 1, 1)
    sizes = conn.getSizes()
    assert(DATASETSIZE == sizes)

    sizeX, sizeY, sizeZ, sizeC, sizeT = conn.getSizes()
    assert(sizeX == DATASETSIZE[0])
    assert(sizeY == DATASETSIZE[1])
    assert(sizeZ == DATASETSIZE[2])
    assert(sizeC == DATASETSIZE[3])
    assert(sizeT == DATASETSIZE[4])

    # Get a spot object, its coordinates and check the unit conversions
    # =========================================================================
    print('Count all children at root level...')
    children = conn.getAllSurpassChildren(False)  # No recursion
    assert(len(children) == 4)

    # If the casting in getAllSurpassChildren() works, spot is an actual
    # spot object, and not an IDataItem. If the casting worked, the object will
    # have a method 'GetPositionsXYZ'.
    print('Test autocasting...')
    child = conn.getAllSurpassChildren(False, 'Spots')
    assert(len(child) == 1)
    spot = child[0]
    assert(callable(getattr(spot, 'GetPositionsXYZ')) == True)

    # Get the coordinates
    pos = spot.GetPositionsXYZ()

    # These are the expected spot coordinates
    print('Check spot coordinates and conversions units<->pixels...')
    POS = [
        [18.5396,    1.4178,    8.7341],
        [39.6139,   14.8819,    9.0352],
        [35.1155,    9.4574,    9.0352],
        [12.3907,   21.6221,   11.7459]]

    assert(np.all(abs(np.array(pos) - np.array(POS)) < 1e-4))

    # Convert
    posV = conn.mapPositionsUnitsToVoxels(pos)
    posU = conn.mapPositionsVoxelsToUnits(posV)

    # Check the conversion
    assert(np.all(abs(np.array(posU) - np.array(POS)) < 1e-4))

    # Test filtering the selection
    # =========================================================================
    print('Test filtering the surpass selection by type...')

    # "Select" the spots object
    conn.mImarisApplication.SetSurpassSelection(children[3])

    # Now get it back, first with the right filter, then with the wrong one
    assert(isinstance(conn.getSurpassSelection('Spots'), type(children[3])))
    assert(conn.getSurpassSelection('Surfaces') is None)

    # Test creating and adding new spots
    # =========================================================================
    print('Test creation of new spots...')
    vSpotsData = spot.Get()
    coords = (np.array(vSpotsData.mPositionsXYZ) + 1.00).tolist()
    timeIndices = vSpotsData.mIndicesT
    radii = vSpotsData.mRadii
    conn.createAndSetSpots(coords, timeIndices, radii, 'Test',  np.random.uniform(0, 1, 4))
    spots = conn.getAllSurpassChildren(False, 'Spots')
    assert(len(spots) == 2)

    # Check the filtering and recursion of object finding
    # =========================================================================
    print('Get all 7 children with recursion (no filtering)...')
    children = conn.getAllSurpassChildren(True)
    assert(len(children) == 7)

    print('Check that there is exactly 1 Light Source...')
    children = conn.getAllSurpassChildren(True, 'LightSource')
    assert(len(children) == 1)

    print('Check that there is exactly 1 Frame...')
    children = conn.getAllSurpassChildren(True, 'Frame')
    assert(len(children) == 1)

    print('Check that there is exactly 1 Volume...')
    children = conn.getAllSurpassChildren(True, 'Volume')
    assert(len(children) == 1)

    print('Check that there are exactly 2 Spots...')
    children = conn.getAllSurpassChildren(True, 'Spots')
    assert(len(children) == 2)

    print('Check that there is exactly 1 Surface...')
    children = conn.getAllSurpassChildren(True, 'Surfaces')
    assert(len(children) == 1)

    print('Check that there is exactly 1 Measurement Point...')
    children = conn.getAllSurpassChildren(True, 'MeasurementPoints')
    assert(len(children) == 1)

    # Get the type
    # =========================================================================
    print('Get and check the datatype...')
    datatype = conn.getNumpyDatatype()
    assert(datatype == np.uint8)

    # Get the data volume
    # =========================================================================
    print('Get the data volume...')
    stack = conn.getDataVolume(0, 0)

    print('Check the data volume type...')
    assert(stack.dtype == conn.getNumpyDatatype())

    # Check the sizes
    print('Check the data volume size...')
    x = stack.shape[2]
    y = stack.shape[1]
    z = stack.shape[0]
    assert(x == DATASETSIZE[0])
    assert(y == DATASETSIZE[1])
    assert(z == DATASETSIZE[2])

    # Get the data volume by explicitly passing an iDataSet object
    # =========================================================================
    print('Get the data volume by explicitly passing an iDataSet object...')
    stack = conn.getDataVolume(0, 0, conn.mImarisApplication.GetDataSet())

    print('Check the data volume type...')
    assert(stack.dtype == conn.getNumpyDatatype())

    # Check the sizes
    print('Check the data volume size...')
    x = stack.shape[2]
    y = stack.shape[1]
    z = stack.shape[0]
    assert(x == DATASETSIZE[0])
    assert(y == DATASETSIZE[1])
    assert(z == DATASETSIZE[2])

    # Check the getDataSubVolume() vs. the getDataVolume methods
    # =========================================================================
    print('Check that subvolumes are extracted correctly...')

    # Remember that with Numpy, to get the values between x0 and x, you must
    # use this notation: x0 : x + 1
    subVolume = conn.getDataSubVolume(112, 77, 38, 0, 0, 10, 10, 2)
    subStack = stack[38: 40, 77: 87, 112: 122]
    assert(np.array_equal(subStack, subVolume))

    # Check the boundaries
    # =========================================================================
    print('Check subvolume boundaries...')
    subVolume = conn.getDataSubVolume(0, 0, 0, 0, 0, x, y, z)
    sX = subVolume.shape[2]
    sY = subVolume.shape[1]
    sZ = subVolume.shape[0]
    assert(sX == DATASETSIZE[0])
    assert(sY == DATASETSIZE[1])
    assert(sZ == DATASETSIZE[2])

    # Get the rotation matrix from the camera angle
    # =========================================================================
    print('Get the rotation matrix from the camera angle...')
    R_D = np.array(\
                   [\
                    [0.8471,  0.2345, -0.4769,  0.0000], \
                    [-0.1484,  0.9661,  0.2115,  0.0000], \
                    [0.5103, -0.1084,  0.8532,  0.0000], \
                    [0.0000,  0.0000,  0.0000,  1.0000]], dtype=np.float32)

    R, isI = conn.getSurpassCameraRotationMatrix()
    assert(np.all((abs(R - R_D) < 1e-4)))

    # Check getting/setting colors and transparency
    # =========================================================================
    print('Check getting/setting colors and transparency...')
    children = conn.getAllSurpassChildren(True, 'Spots')
    spots = children[0]

    # We prepare some color/transparency combinations to circle through
    clr = [ \
        [1, 0, 0, 0.00],    # Red, transparency = 0
        [0, 1, 0, 0.00],    # Green, transparency = 0
        [0, 0, 1, 0.00],    # Blue,  transparency = 0
        [1, 1, 0, 0.00],    # Yellow, transparency = 0
        [1, 0, 1, 0.00],    # Purple, transparency = 0
        [1, 0, 1, 0.25],    # Purple, transparency = 0.25
        [1, 0, 1, 0.50],    # Purple, transparency = 0.50
        [1, 0, 1, 0.75],    # Purple, transparency = 0.75
        [1, 0, 1, 1.00]]   # Purple, transparency = 1.00

    for c in clr:

        # Set the RGBA color
        spots.SetColorRGBA(conn.mapRgbaVectorToScalar(c))

        # Get the RGBA color
        current = conn.mapRgbaScalarToVector(spots.GetColorRGBA())

        # Compare (rounding errors allowed)
        assert(all([abs(x - y) < 1e-2 for x, y in zip(c, current)]))

    # Close Imaris
    # =========================================================================
    print('Close Imaris...')
    assert(conn.closeImaris(1) == 1)

    # Create an ImarisConnector object with starting index 0
    # =========================================================================
    print('Create an IceImarisConnector object...')
    conn = pIceImarisConnector()

    # Start Imaris
    # =========================================================================
    print('Start Imaris...')
    assert(conn.startImaris() == 1)

    # Send a data volume that will force creation of a compatible dataset
    # =========================================================================
    print('Send volume (force dataset creation)...')
    stack = np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], \
            [10, 11, 12]], [[13, 14, 15], [16, 17, 18]]], np.uint16)
    conn.setDataVolume(stack, 0, 0)

    # Create a dataset
    # =========================================================================
    print('Create a dataset (replace existing one)...')
    conn.createDataset('uint8', 100, 200, 50, 3, 10, 0.20, 0.25, 0.5, 0.1)

    # Check sizes
    # =========================================================================
    print('Check sizes...')
    sizes = conn.getSizes()
    assert(sizes[0] == 100)
    assert(sizes[1] == 200)
    assert(sizes[2] == 50)
    assert(sizes[3] == 3)
    assert(sizes[4] == 10)

    # Check voxel sizes
    # =========================================================================
    print('Check voxel sizes...')
    voxelSizes = conn.getVoxelSizes()
    assert(voxelSizes[0] == 0.2)
    assert(voxelSizes[1] == 0.25)
    assert(voxelSizes[2] == 0.5)

    # Check the time delta
    # =========================================================================
    print('Check time interval...')
    assert(conn.mImarisApplication.GetDataSet().GetTimePointsDelta() == 0.1)

    # Check transferring volume data
    # =========================================================================
    print('Check two-way data volume transfer...')
    data = np.zeros((2, 255, 255), dtype=np.uint8)
    x = np.linspace(1, 255, 255)
    y = np.linspace(1, 255, 255)
    xv, yv = np.meshgrid(x, y)
    data[0, :, :] = x
    data[1, :, :] = y
    data = data[:, :, 1:255]  # Make it not square in xy
    conn.createDataset('uint8', 254, 255, 2, 1, 1)
    conn.setDataVolume(data, 0, 0)
    dataOut = conn.getDataVolume(0, 0)
    assert(np.array_equal(data, dataOut))

    # Close Imaris
    # =========================================================================
    print('Close Imaris...')
    assert(conn.closeImaris(True) == 1)

    # Make sure Imaris is closed
    # =========================================================================
    print('Make sure Imaris is closed...')
    assert(conn.isAlive() == False)

    # Start Imaris
    # =========================================================================
    print('Start Imaris...')
    assert(conn.startImaris() == 1)

    # Open a file
    # =========================================================================
    print('Load file...')
    currFilePath = os.path.realpath(__file__)
    currPath = os.path.dirname(currFilePath)
    filename = os.path.join(currPath, 'SwimmingAlgae.ims')
    conn.mImarisApplication.FileOpen(filename, '')

    # Get the Spots object
    iSpots = conn.getAllSurpassChildren(False, 'Spots')
    assert (len(iSpots) == 1)

    # Get the tracks
    [tracks, startTimes] = conn.getTracks(iSpots[0])

    # Compare
    TRACKS_0 = np.array([
        [257.0569, 158.0890, 0.5000],
        [258.2019, 160.3281, 0.5000],
        [258.6424, 161.7611, 0.5000],
        [257.0615, 162.8971, 0.5000],
        [254.7822, 163.0764, 0.5000],
        [252.9628, 162.2183, 0.5000],
        [251.9430, 160.6685, 0.5000],
        [252.0315, 159.2506, 0.5000],
        [252.5433, 157.9091, 0.5000],
        [254.0479, 156.8815, 0.5000],
        [255.7876, 156.3626, 0.5000],
        [257.4710, 156.3670, 0.5000]])

    TRACKS_1 = np.array([
        [245.0000, 125.4513, 0.5000],
        [248.0088, 127.2925, 0.5000],
        [251.1482, 128.9230, 0.5000],
        [254.2048, 130.3164, 0.5000],
        [257.1553, 132.4333, 0.5000],
        [259.4069, 134.9209, 0.5000],
        [261.9462, 137.7944, 0.5000],
        [264.0524, 140.6828, 0.5000]])

    TRACKS_2 = np.array([
        [284.0000, 128.0667, 0.5000],
        [281.3237, 130.0378, 0.5000],
        [278.5699, 131.9248, 0.5000],
        [275.9659, 133.9807, 0.5000]])

    # Check spot coordinates
    assert (np.all(abs(tracks[0] - TRACKS_0) < 1e-4))
    assert (np.all(abs(tracks[1] - TRACKS_1) < 1e-4))
    assert (np.all(abs(tracks[2] - TRACKS_2) < 1e-4))

    # Check start time points
    assert (np.all(startTimes == np.array([0, 4, 8])))

    # All done
    # =========================================================================
    print('')
    print('All test successfully run.')
