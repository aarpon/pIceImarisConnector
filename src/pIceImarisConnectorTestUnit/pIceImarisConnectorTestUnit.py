'''
Name       pIceImarisApplication Test Unit
Purpose    Test pIceImarisApplication

Author     Aaron Ponti

Created    21-03-2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

import os
import numpy as np;

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
    
    # Check the starting index
    # =========================================================================
    print('Check default starting index...')
    assert(conn.indexingStart == 0)
    
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
    children = conn.getAllSurpassChildren(False) # No recursion
    assert(len(children) == 4)
     
    # If the casting in getAllSurpassChildren() works, spot is an actual
    # spot object, and not an IDataItem. If the casting worked, the object will
    # have a method 'GetPositionsXYZ'.
    print('Test autocasting...')
    child = conn.getAllSurpassChildren(False, 'Spots')
    assert(len(child) == 1)
    spot = child[ 0 ]
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
    print datatype
    assert(datatype == np.uint8)

    # # Get the data volume
    # # =========================================================================
    # print('Get the data volume...')
    # stack = conn.getDataVolume(0, 0)
    # 
    # print('Check the data volume type...')
    # assert(isa(stack, type) == 1)
    # 
    # # Check the sizes
    # print('Check the data volume size...')
    # assert(size(stack, 1) == DATASETSIZE(1) == 1)
    # assert(size(stack, 2) == DATASETSIZE(2) == 1)
    # assert(size(stack, 3) == DATASETSIZE(3) == 1)
    # 
    # # Get the data volume by explicitly passing an iDataSet object
    # # =========================================================================
    # print('Get the data volume by explicitly passing an iDataSet object...')
    # stack = conn.getDataVolume(0, 0, conn.mImarisApplication.GetDataSet)
    # 
    # print('Check the data volume type...')
    # assert(isa(stack, type) == 1)
    # 
    # # Check the sizes
    # print('Check the data volume size...')
    # assert(size(stack, 1) == DATASETSIZE(1) == 1)
    # assert(size(stack, 2) == DATASETSIZE(2) == 1)
    # assert(size(stack, 3) == DATASETSIZE(3) == 1)
    # 
    # # Check the getDataVolumeRM() method
    # # =========================================================================
    # print('Check getting the volume in row-major order...')
    # stackRM = conn.getDataVolumeRM(0, 0)
    # assert(all(all(stack(:, :, 27) == (stackRM(:, :, 27))')))
    # 
    # # Get the rotation matrix from the camera angle
    # # =========================================================================
    # print('Get the rotation matrix from the camera angle...')
    # R_D = [
    #     0.8471    0.2345   -0.4769         0
    #    -0.1484    0.9661    0.2115         0
    #     0.5103   -0.1084    0.8532         0
    #          0         0         0    1.0000
    #         ]
    # R = conn.getSurpassCameraRotationMatrix()
    # assert(all(all(abs(R - R_D) < 1e-4)) == 1)
    # 
    # # Check getting/setting colors and transparency
    # # =========================================================================
    # print('Check getting/setting colors and transparency...')
    # children = conn.getAllSurpassChildren(1, 'Spots')
    # spots = children{1}
    # 
    # # We prepare some color/transparency commbinations to circle through (to
    # # check the int32/uint32 type casting we are forced to apply)
    # clr = [...
    #     1 0 0 0.00    # Red, transparency = 0
    #     0 1 0 0.00    # Green, transparency = 0
    #     0 0 1 0.00    # Blue,  transparency = 0
    #     1 1 0 0.00    # Yellow, transparency = 0
    #     1 0 1 0.00    # Purple, transparency = 0
    #     1 0 1 0.25    # Purple, transparency = 0.25
    #     1 0 1 0.50    # Purple, transparency = 0.50
    #     1 0 1 0.75    # Purple, transparency = 0.75
    #     1 0 1 1.00]  # Purple, transparency = 1.00
    # 
    # for i = 1 : size(clr, 1)
    #     
    #     # Set the RGBA color
    #     spots.SetColorRGBA(conn.mapRgbaVectorToScalar(clr(i, :)))
    #     
    #     # Get the RGBA color
    #     current = conn.mapRgbaScalarToVector(spots.GetColorRGBA())
    #     
    #     # Compare (rounding erros allowed)
    #     assert(abs(all(clr(i, :) - current)) < 1e-2)
    # 
    # end
    #     
    # # Close Imaris
    # # =========================================================================
    # print('Close Imaris...')
    # assert(conn.closeImaris(1) == 1)
    # 
    # # Create an ImarisConnector object with starting index 1
    # # =========================================================================
    # clear 'conn'
    # print('Create an IceImarisConnector object with starting index 1...')
    # conn = IceImarisConnector([], 1)
    # 
    # # Start Imaris
    # # =========================================================================
    # print('Start Imaris...')
    # assert(conn.startImaris == 1)
    # 
    # # Check the starting index
    # # =========================================================================
    # print('Check starting index...')
    # assert(conn.indexingStart() == 1)
    # 
    # # Open a file
    # # =========================================================================
    # print('Load file...')
    # filename = fullfile(fileparts(which(mfilename)), 'PyramidalCell.ims')
    # conn.mImarisApplication.FileOpen(filename, '')
    # 
    # # Get and compare the data volume
    # # =========================================================================
    # print('Get and compare the data volume...')
    # stackIndx1 = conn.getDataVolume(1, 1)
    # 
    # cmp = stack == stackIndx1
    # assert(all(cmp(:)))
    # 
    # # Close Imaris
    # # =========================================================================
    # print('Close Imaris...')
    # assert(conn.closeImaris == 1)
    # 
    # # Create an ImarisConnector object with starting index 0
    # # =========================================================================
    # clear 'conn'
    # print('Create an IceImarisConnector object with starting index 0...')
    # conn = IceImarisConnector([], 0)
    # 
    # # Start Imaris
    # # =========================================================================
    # print('Start Imaris...')
    # assert(conn.startImaris == 1)
    # 
    # # Create a dataset
    # # =========================================================================
    # print('Create a dataset')
    # conn.createDataset('uint8', 100, 200, 50, 3, 10, 0.20, 0.25, 0.5, 0.1)
    # 
    # # Check sizes
    # # =========================================================================
    # print('Check sizes...')
    # sizes = conn.getSizes()
    # assert(sizes(1) == 100)
    # assert(sizes(2) == 200)
    # assert(sizes(3) == 50)
    # assert(sizes(4) == 3)
    # assert(sizes(5) == 10)
    # 
    # # Check voxel sizes
    # # =========================================================================
    # print('Check voxel sizes...')
    # voxelSizes = conn.getVoxelSizes()
    # assert(voxelSizes(1) == 0.2)
    # assert(voxelSizes(2) == 0.25)
    # assert(voxelSizes(3) == 0.5)
    # 
    # # Check the time delta
    # # =========================================================================
    # print('Check time interval...')
    # assert(conn.mImarisApplication.GetDataSet().GetTimePointsDelta() == 0.1)
    # 
    # # Check transfering volume data
    # # =========================================================================
    # print('Check two-way data volume transfer...')
    # data(:, :, 1) = [ 1 2 3 4 5 6 ]
    # data(:, :, 2) = [ 7 8 9 10 11 12]
    # data = uint8(data)
    # conn.createDataset('uint8', 3, 2, 2, 1, 1)
    # conn.setDataVolumeRM(data, 0, 0)
    # dataOut = conn.getDataVolumeRM(0, 0)
    # r = data == dataOut
    # assert(all(r(:)))
 
    # Close Imaris
    # =========================================================================
    print('Close Imaris...')
    assert(conn.closeImaris(True) == 1)
 
    # Make sure Imaris is closed
    # =========================================================================
    print('Make sure Imaris is closed...')
    assert(conn.isAlive() == False)
 
    # All done
    # =========================================================================
    print('')
    print('All test succesfully run.')
