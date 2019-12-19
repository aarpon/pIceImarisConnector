import os
import numpy as np

from pIceImarisConnector import pIceImarisConnector

def TestPIceTwo(aImarisId):

    # Instantiate the pIceImarisConnector object
    conn = pIceImarisConnector(aImarisId)

    # Open the SwimmingAlgae file
    # =======================================================s==================
    print('Load file...')
    conn.loadSwimmingAlgaeTestDataset()

    # Check that there is something loaded
    # =========================================================================
    print('Test that the file was loaded...')
    assert(conn.mImarisApplication.GetDataSet().GetSizeX() > 0)

    # Get the Spots object
    print('Test retrieving spot object...')
    iSpots = conn.getAllSurpassChildren(False, 'Spots')
    assert (len(iSpots) == 1)

    # Get the tracks
    print('Test retrieving tracks from spot object...')
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
    print('Test tracks coordinates...')
    assert (np.all(abs(tracks[0] - TRACKS_0) < 1e-4))
    assert (np.all(abs(tracks[1] - TRACKS_1) < 1e-4))
    assert (np.all(abs(tracks[2] - TRACKS_2) < 1e-4))

    # Check start time points
    print('Test timepoints...')
    assert (np.all(startTimes == np.array([0, 4, 8])))
