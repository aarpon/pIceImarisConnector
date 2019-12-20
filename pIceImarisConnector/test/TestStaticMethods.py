# This file tests static functionality of pIceImarisConnector and does not require to
# be connected to Imaris to run.

from pIceImarisConnector import pIceImarisConnector as pIce
import numpy as np
import math

# testCalcRotationBetweenVectors3D
def testCalcRotationBetweenVectors3D(start, dest, expected_q, epsilon=1e-4):
    q = pIce.calcRotationBetweenVectors3D(start, dest)
    return np.all(np.abs(q - expected_q) <= epsilon)

# testMapAxisAngleToQuaternion
def testMapAxisAngleToQuaternion(axis, angle, expected_q, epsilon=1e-4):
    q = pIce.mapAxisAngleToQuaternion(axis, angle)
    return np.all(np.abs(q - expected_q) <= epsilon)

# testMapAxisAngleToRotationMatrix
def testMapAxisAngleToRotationMatrix(axis, angle, expected_R, expected_x, expected_y, expected_z, epsilon=1e-4):
    R, x, y, z = pIce.mapAxisAngleToRotationMatrix(axis, angle)
    return np.all(np.abs(R - expected_R) <= epsilon) and np.all(np.abs(x - expected_x) <= epsilon) and \
           np.all(np.abs(y - expected_y) <= epsilon) and np.all(np.abs(z - expected_z) <= epsilon)

# testMapQuaternionToRotationMatrix
def testMapQuaternionToRotationMatrix(q, expected_R, expected_x, expected_y, expected_z, epsilon=1e-4):
    R, x, y, z = pIce.mapQuaternionToRotationMatrix(q)
    return np.all(np.abs(R - expected_R) <= epsilon) and np.all(np.abs(x - expected_x) <= epsilon) and \
           np.all(np.abs(y - expected_y) <= epsilon) and np.all(np.abs(z - expected_z) <= epsilon)

# testMultiplyQuaternions
def testMultiplyQuaternions(q1, q2, expected_q, epsilon=1e-4):
    q = pIce.multiplyQuaternions(q1, q2)
    return np.all(np.abs(q - expected_q) <= epsilon)

# testMapAxisAngleToQuaternion
def testNormalize(v, expected_n, epsilon=1e-4):
    n = pIce.normalize(v)
    return np.all(np.abs(n - expected_n) <= epsilon)

# testQuaternionConjugate
def testQuaternionConjugate(q, expected_qc, epsilon=1e-4):
    qc = pIce.quaternionConjugate(q)
    return np.all(np.abs(qc - expected_qc) <= epsilon)

# ======================================================================================================================

#
# calcRotationBetweenVectors3D
#
assert (testCalcRotationBetweenVectors3D([1, 0, 1], [0, 1, 0], [-0.5000, 0.0000, 0.5000, 0.7071]))
assert (testCalcRotationBetweenVectors3D([0, 0, 0], [0, 0, 0], [0.0000, 0.0000, 0.0000, 0.7071]))
assert (testCalcRotationBetweenVectors3D([1.8339, -2.2588, 0.8622], [0.3188, -1.3077, -0.4336],
                                         [0.2634, 0.1338, -0.2098, 0.9321]))

#
# mapAxisAngleToQuaternion
#
assert (testMapAxisAngleToQuaternion([0.0, 1.0, 0.0], 0.0, [0.0, 0.0, 0.0, 1.0]))
assert (testMapAxisAngleToQuaternion([0.0, 0.0, 0.0], 0.0, [0.0, 0.0, 0.0, 1.0]))
assert (testMapAxisAngleToQuaternion([0.0, 1.0, 0.0], math.pi/4.0, [0.0, 0.3827, 0.0, 0.9239]))
assert (testMapAxisAngleToQuaternion([0.0, -1.0, 0.0], math.pi/4.0, [0.0, -0.3827, 0.0, 0.9239]))
assert (testMapAxisAngleToQuaternion([1.0, 1.0, 1.0], math.pi/4.0, [0.2209, 0.2209, 0.2209, 0.9239]))
assert (testMapAxisAngleToQuaternion([0.0, 1.0, 0.0], math.pi, [0.0, 1.0, 0.0, 0.0]))
assert (testMapAxisAngleToQuaternion([-1.0689, -0.8095, -2.9443], 1.4384, [-0.2177, -0.1648, -0.5995, 0.7523]))

#
# mapAxisAngleToRotationMatrix
#
expected_R = [[1.0, 0.0, 0.0, 0.0],
              [0.0, 1.0, 0.0, 0.0],
              [0.0, 0.0, 1.0, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [1.0, 0.0, 0.0]
expected_y = [0.0, 1.0, 0.0]
expected_z = [0.0, 0.0, 1.0]
assert (testMapAxisAngleToRotationMatrix([0.0, 1.0, 0.0], 0.0, expected_R,
                                         expected_x, expected_y, expected_z))

expected_R = [[0.7071, 0.0, 0.7071, 0.0],
              [0.0, 1.0, 0.0, 0.0],
              [-0.7071, 0.0, 0.7071, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [0.7071, 0.0, -0.7071]
expected_y = [0.0, 1.0, 0.0]
expected_z = [0.7071, 0.0, 0.7071]
assert (testMapAxisAngleToRotationMatrix([0.0, 1.0, 0.0], math.pi / 4.0, expected_R,
                                         expected_x, expected_y, expected_z))

expected_R = [[0.6552, -0.7467, -0.1147, 0],
              [0.5398, 0.5690, -0.6204, 0.0],
              [0.5285, 0.3445, 0.7759, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [0.6552, 0.5398, 0.5285]
expected_y = [-0.7467, 0.5690, 0.3445]
expected_z = [-0.1147, -0.6204, 0.7759]
assert (testMapAxisAngleToRotationMatrix([0.3, -0.2, 0.4], math.pi / 3.0, expected_R,
                                         expected_x, expected_y, expected_z))

#
# mapQuaternionToRotationMatrix
#
expected_R = [[1.0, 0.0, 0.0, 0.0],
              [0.0, -1.0, 0.0, 0.0],
              [0.0, 0.0, -1.0, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [1.0, 0.0, 0.0]
expected_y = [0.0, -1.0, 0.0]
expected_z = [0.0, 0.0, -1.0]
assert (testMapQuaternionToRotationMatrix([1.0, 0.0, 0.0, 0.0], expected_R, expected_x, expected_y, expected_z))

expected_R = [[1.0, 0.0, 0.0, 0.0],
              [0.0, 1.0, 0.0, 0.0],
              [0.0, 0.0, 1.0, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [1.0, 0.0, 0.0]
expected_y = [0.0, 1.0, 0.0]
expected_z = [0.0, 0.0, 1.0]
assert (testMapQuaternionToRotationMatrix([0.0, 0.0, 0.0, 0.0], expected_R, expected_x, expected_y, expected_z))

expected_R = [[0.1667, 0.9513, -0.2592, 0.0],
              [0.4018, 0.1746, 0.8989, 0.0],
              [0.9004, -0.2540, -0.3532, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
expected_x = [0.1667, 0.4018, 0.9004]
expected_y = [0.9513, 0.1746, -0.2540]
expected_z = [-0.2592, 0.8989, -0.3532]
assert (testMapQuaternionToRotationMatrix([1.4090, 1.4172, 0.6715, -1.2075],
                                          expected_R, expected_x, expected_y, expected_z))

#
# quaternionConjugate
#
assert(testQuaternionConjugate([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]))
assert(testQuaternionConjugate([1.0, 1.0, 1.0, 1.0], [0.5000, -0.5000, -0.5000, -0.5000]))
assert(testQuaternionConjugate([-1.0, -1.0, -1.0, -1.0], [-0.5000, 0.5000, 0.5000, 0.5000]))
assert(testQuaternionConjugate([10.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]))
assert(testQuaternionConjugate([-0.0631, 0.7147, -0.2050, -0.1241], [-0.0834, -0.9448, 0.2710, 0.1641]))

#
# multiplyQuaternions
#
assert (testMultiplyQuaternions([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]))
assert (testMultiplyQuaternions([1.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]))
assert (testMultiplyQuaternions([1.0, 1.0, 1.0, 1.0], [-1.0, -1.0, -1.0, -1.0], [-0.5000, -0.5000, -0.5000, 0.5000]))
assert (testMultiplyQuaternions([1.6302, 0.4889, 1.0347, 0.7269], [-0.3034, 0.2939, -0.7873, 0.8884],
                                [0.2017, 0.6054, 0.3647, 0.6780]))

#
# normalize
#
assert (testNormalize([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
assert (testNormalize(np.array([0.0, 0.0, 0.0]), [0.0, 0.0, 0.0]))
assert (testNormalize([1.0, 0.0, 0.0], [1.0, 0.0, 0.0]))
assert (testNormalize([[1.0], [0.0], [0.0]], [[1.0], [0.0], [0.0]]))   # Column vector

# Test calling a static method from the object
conn = pIce()
n = conn.normalize([0.0, 3.0, 4.0])
expected_n = [0.0, 0.6, 0.8]
assert(np.all(np.abs(n - expected_n) <= 1e-4))
