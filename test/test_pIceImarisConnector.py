'''
Name       pIceImarisApplication Test Unit
Purpose    Test pIceImarisApplication

Author     Aaron Ponti

Created    21-03-2013
Copyright  (c) Aaron Ponti 2013
Licence    GPL v2
'''

import unittest
import os
import numpy as np;

from pIceImarisConnector import pIceImarisConnector

class test_pIceImarisConnector(unittest.TestCase):
    
    _conn = None

    # Start with some fundamental tests
    # =========================================================================

    # Instantiating IceImarisConnector object with no parameters
    def test_init_no_params(self):
        self._conn = pIceImarisConnector()
        self._conn.display()
        self._conn.info()

    # Pass the existing pIceImarisConnector object - will return the reference
    def test_init_with_conn(self):
        conn2 = pIceImarisConnector(self._conn)
        self.assertTrue(self._conn is conn2,
                        "The references do not point to the same object.")
        del(conn2)

    # ImarisConnector version
    # =========================================================================
    def test_get_version(self):
        self.assertTrue(self._conn.version is not "",
                        "Could not get version info.")
        
    # Start Imaris
    # =========================================================================
    def test_start_Imaris(self):
        self.assertTrue(self._conn.startImaris() == True, 
                        "Failed starting Imaris.")
    
    # Test that the connection is valid
    # =========================================================================
    def test_get_version_int(self):
        self.assertTrue(self._conn.getImarisVersionAsInteger() > 0,
                        "Could not get version as integer.")
    
    def test_is_alive(self):
        self.assertTrue(self._conn.isAlive() == True,
                        "No connection with Imaris.")
    
    # Check the starting index
    # =========================================================================
    def test_starting_index(self):
        self.assertTrue(self._conn.indexingStart == 0,
                        "Default indexing start is not zero.")
    
    # Open a file
    # =======================================================s==================
    def test_load_file(self):
        currFilePath = os.path.realpath(__file__)
        currPath = os.path.dirname(currFilePath)
        filename = os.path.join(currPath, 'PyramidalCell.ims')
        self._conn.mImarisApplication.FileOpen(filename, '')
    
    # Check that there is something loaded
    # =========================================================================
    def test_is_dataset_loaded(self):
        self.assertTrue(self._conn.mImarisApplication.GetDataSet().GetSizeX > 0,
                        "No dataset loaded.")
    
    # Check the extends
    # =========================================================================
    def test_extends_tuple(self):
        EXTENDS = (-0.1140, 57.8398, -0.1140, 57.8398, -0.1510, 20.6310)
        extends = self._conn.getExtends()
        self.assertTrue(all([abs(x - y) < 1e-4 for x, y in zip(EXTENDS, extends)]),
                        "Extends do not match.")

    def test_extends_individual(self):     
        minX, maxX, minY, maxY, minZ, maxZ = self._conn.getExtends()
        self.assertTrue(all([abs(x - y) < 1e-4 for x, y in \
                zip(EXTENDS, (minX, maxX, minY, maxY, minZ, maxZ))]),
                        "Extends do not match.")
    
    # Check the voxel size
    # =========================================================================
    def test_voxel_size_tuple(self):
        VOXELSIZES = (0.2273, 0.2282, 0.3012)
        voxelSizes = self._conn.getVoxelSizes()
        self.assertTrue(all([abs(x - y) < 1e-4 for x, y in zip(VOXELSIZES, voxelSizes)]),
                        "Voxel sizes do not match.")
 
    def test_voxel_size_individual(self):
        vX, vY, vZ = conn.getVoxelSizes()
        self.assertTrue(all([abs(x - y) < 1e-4 for x, y in zip(VOXELSIZES, (vX, vY, vZ))]),
                        "Voxel sizes do not match.")

    # Check the dataset size
    #
    #   X = 255
    #   Y = 254
    #   Z =  69
    #   C =   1
    #   T =   1
    #
    # =========================================================================
    def tast_dataset_size_tuple(self):
        DATASETSIZE = (255, 254, 69, 1, 1)
        sizes = self._conn.getSizes()
        self.assertTrue(DATASETSIZE == sizes,
                        "Dataset size does not match.")    
    
    def tast_dataset_size_individual(self):
        sizeX, sizeY, sizeZ, sizeC, sizeT = self._conn.getSizes()
        self.assertTrue(sizeX == DATASETSIZE[0] and
                        sizeY == DATASETSIZE[1] and
                        sizeZ == DATASETSIZE[2] and
                        sizeC == DATASETSIZE[3] and
                        sizeT == DATASETSIZE[4],
                        "Dataset size does not match.")
 
    # Check getting children
    # =========================================================================
    def test_count_children_at_root(self):
        children = self._conn.getAllSurpassChildren(False) # No recursion
        self.assertTrue(len(children) == 4,
                        "There should be 4 children at the root level.")
     
    # If the casting in getAllSurpassChildren() works, spot is an actual
    # spot object, and not an IDataItem. If the casting worked, the object will
    # have a method 'GetPositionsXYZ'.
    def test_autocast(self):
        child = self._conn.getAllSurpassChildren(False, 'Spots')
        spot = child[ 0 ]
        self.assertTrue(callable(getattr(spot, 'GetPositionsXYZ')) == True,
                        "Autocasting of spot object failed.")
    

    # Get and compare spot coordinates
    def test_get_spot_coords(self):
        # Get the coordinates
        child = self._conn.getAllSurpassChildren(False, 'Spots')
        spot = child[ 0 ]
        pos = spot.GetPositionsXYZ()
    
        # These are the expected spot coordinates
        POS = [
               [18.5396,    1.4178,    8.7341],
               [39.6139,   14.8819,    9.0352],
               [35.1155,    9.4574,    9.0352],
               [12.3907,   21.6221,   11.7459]]

        self.assertTrue(np.all(abs(np.array(pos) - np.array(POS)) < 1e-4),
                        "Spot coordinates do not match.")
        
    # Convert back and forth
    def test_spot_coords_conversions(self):
        # Get the coordinates
        child = self._conn.getAllSurpassChildren(False, 'Spots')
        spot = child[ 0 ]
        pos = spot.GetPositionsXYZ()
        
        # Convert
        posV = conn.mapPositionsUnitsToVoxels(pos)
        posU = conn.mapPositionsVoxelsToUnits(posV)
 
        # Check the conversion
        self.assertTrue(np.all(abs(np.array(posU) - np.array(POS)) < 1e-4),
                        "Coordinate conversions failed.")
    
    # Test filtering the selection
    # =========================================================================

    def test_filter_spot(self):
        # "Select" the spots object
        self._conn.mImarisApplication.SetSurpassSelection(children[3])
        self.assertTrue(isinstance(conn.getSurpassSelection('Spots'),
                                   type(children[3])),
                        "Failed retrieving Spots object.")

    # Test creating and adding new spots
    # =========================================================================
    def test_create_spots(self):
        child = self._conn.getAllSurpassChildren(False, 'Spots')
        spot = child[ 0 ]
        vSpotsData = spot.Get()
        coords = (np.array(vSpotsData.mPositionsXYZ) + 1.00).tolist()
        timeIndices = vSpotsData.mIndicesT
        radii = vSpotsData.mRadii
        self._conn.createAndSetSpots(coords, timeIndices, radii, 'Test',  
                                     np.random.uniform(0, 1, 4))
        spots = self._conn.getAllSurpassChildren(False, 'Spots')
        self.assertTrue(len(spots) == 2,
                        "Failed creating spot object.")

    # Check the filtering and recursion of object finding
    # =========================================================================
    
    # Get all 7 children with recursion (no filtering)
    def test_more_filtering(self):
        children = self._conn.getAllSurpassChildren(True)
        self.assertTrue(len(children) == 7,
                        "Expected 7 objects.")
 
    # Check that there is exactly 1 LightSource
    def test_find_one_light_source(self):
        children = self._conn.getAllSurpassChildren(True, 'LightSource')
        self.assertTrue(len(children) == 1,
                        "Expected on light source.")
 
    # Check that there is exactly 1 Frame
    def test_find_one_frame(self):
        children = self._conn.getAllSurpassChildren(True, 'Frame')
        self.assertTrue(len(children) == 1,
                        "Expected one frame.")
 
    # Check that there is exactly 1 Volume
    def test_find_one_volume(self):
        children = self._conn.getAllSurpassChildren(True, 'Volume')
        self.assertTrue(len(children) == 1,
                        "Expected one Volume.")
 
    # Check that there are exactly 2 Spots
    def test_find_two_spots(self):
        children = self._conn.getAllSurpassChildren(True, 'Spots')
        self.assertTrue(len(children) == 2,
                        "Expected two Spots.")
 
    # Check that there is exactly 1 Surface
    def test_find_one_surface(self):
        children = self._conn.getAllSurpassChildren(True, 'Surfaces')
        self.assertTrue(len(children) == 1,
                        "Expected one surface.")
 
    # Check that there is exactly 1 Measurement Point
    def test_find_one_meaurement_point(self):
        children = self._conn.getAllSurpassChildren(True, 'MeasurementPoints')
        self.assertTrue(len(children) == 1,
                        "Expected one measurement point.")
 
 
    # Get the type
    # =========================================================================
    # Get and check the datatype
    def test_datatype(self):
        datatype = self._conn.getNumpyDatatype()
        self.assertTrue(datatype == np.uint8,
                        "Wrong datatype.")

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
    def test_close_Imaris(self):
        self.assertTrue(self._conn.closeImaris(True) == 1,
                        "Could not close Imaris.")
 
    # Make sure Imaris is closed
    # =========================================================================
    def test_Imaris_is_closed(self):
        self.assertTrue(self._conn.isAlive() == False,
                        "Imaris is not closed.")
 


    
if __name__ == '__main__':
    unittest.main()
    
