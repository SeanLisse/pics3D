#! /usr/bin/env python

# This file contains some basic 3D vector math for use when doing physical reasoning.
# It assumes that each 3D point is a numpy array with 3 components, ordered as 'X', 'Y', 'Z'.

import numpy
# import scipy

def magnitude(vector):
    ''' Given a 3D vector, computes and returns the scalar magnitude of the vector'''
    
    a=vector[0]
    b=vector[1]
    c=vector[2]
    
    magnitude=numpy.sqrt(a**2 + b**2 + c**2)
    return magnitude

def magnify(vector, magnification):
    ''' Given a 3D vector, returns the original multiplied by the provided scalar magnification. '''
    newvector=numpy.zeros((3))
    newvector[0] = vector[0]*magnification
    newvector[1] = vector[1]*magnification
    newvector[2] = vector[2]*magnification
    return newvector
    
def normalize(vector):
    ''' Given a vector, return a copy that is normalized to have length 1.'''
    newvector=numpy.zeros((3))
    mag=magnitude(vector)
    
    if (mag==0): return newvector
    
    newvector=vector/mag
    
    return newvector

def vector_magnitude_sum(vectorList):
    ''' Given a list of vectors, sum their magnitudes and return that as a scalar. '''
    
    total_length=0
    
    for i in range(len(vectorList)): 
        vector = vectorList[i]
        total_length= total_length + magnitude(vector)
    
        # print("summing " + str(magnitude(vector)))

    # print("total:" + str(total_length))
    
    return total_length


def parallel_component(reference_vector, comparison_vector):
    ''' Given a reference vector and a comparison vector, projects the comparison onto the reference and returns
    only the component of the comparison vector that is parallel to the reference vector.'''
    
    ref_vector_normal = normalize(reference_vector)
    parallel_magnitude= numpy.dot(ref_vector_normal, comparison_vector)
    result = magnify(ref_vector_normal, parallel_magnitude)
    
    return result

def perpendicular_component(reference_vector, comparison_vector):
    ''' Given a reference vector and a comparison vector, projects the comparison onto the reference and returns
    only the component of the comparison vector that is perpindicular to the reference vector.'''
    
    result = comparison_vector - parallel_component(reference_vector, comparison_vector)
    
    return result

def orthogonalize(reference_vector, comparison_vector):
    ''' Given a reference vector and a comparison vector, return a vector ORTHOGONAL to both of them.'''
    
    result = numpy.cross(reference_vector, comparison_vector)
    return result

####################################
### DEFAULT MAIN PROC (UNIT TESTING)
####################################


if __name__ == '__main__':
    print("Unit Testing all functions in " + __file__ + ".")
    
    origin = numpy.array([0,0,0])
    x_vec = numpy.array([1,0,0])
    y_vec = numpy.array([0,1,0])
    z_vec = numpy.array([0,0,1])
    
    #Test magnitude
    if not (magnitude(x_vec) == 1): raise Exception("TEST FAILED.  X Vector should have magnitude 1.")
    double_y = magnify(y_vec, 2)
    if not (magnitude(double_y) == 2): raise Exception("TEST FAILED. Double Y Vector should have magnitude 2.")
   
    #Test normalize
    if not (magnitude(normalize(double_y)) == 1): raise Exception("TEST FAILED.  Normalization did not yield vector of length 1.")
    
    #Test vector_magnitude_sum
    if not (vector_magnitude_sum((x_vec, y_vec, z_vec)) == 3): raise Exception("TEST FAILED. 3x 'X' path is not 3!")

    #Test parallel_component
    if not (magnitude(parallel_component(x_vec, y_vec)) == 0): 
        raise Exception("TEST FAILED. Parallel component test 1.")
    if not (magnitude(parallel_component(x_vec, x_vec)) == 1): 
        raise Exception("TEST FAILED. Parallel component test 2.")
    if not (magnitude(parallel_component(x_vec, magnify(x_vec,3))) == 3): 
        raise Exception("TEST FAILED. Parallel component test 3.")
    if not (magnitude(parallel_component(magnify(x_vec,3), x_vec)) == 1): 
        raise Exception("TEST FAILED. Parallel component test 4.")
    
    #Test perpendicular component
    if not (magnitude(perpendicular_component(x_vec, x_vec)) == 0): 
        raise Exception("TEST FAILED. Perpindicular component test 1.")
    if not (magnitude(perpendicular_component(x_vec, y_vec)) == 1): 
        raise Exception("TEST FAILED. Perpindicular component test 2.")
    if not (magnitude(perpendicular_component(x_vec, magnify(y_vec,3))) == 3): 
        raise Exception("TEST FAILED. Perpindicular component test 3.")
    if not (magnitude(perpendicular_component(magnify(x_vec,3), y_vec)) == 1): 
        raise Exception("TEST FAILED. Perpindicular component test 4.")
    
    #Check parallel against perpendicular
    if not (numpy.dot(parallel_component(x_vec, [1,1,1]), perpendicular_component(x_vec, [1,1,1])) == 0):
        raise Exception("TEST FAILED. Parallel component is NOT perpendicular to perpendicular component!")
    
    #TODO: Add a test for orthogonalize
    if not (magnitude(orthogonalize(x_vec, y_vec)) == 1):
        raise Exception("TEST FAILED.  Orthogonalize of two unit vectors yields a non-unit vector!")
    if not (numpy.dot(parallel_component(x_vec, [1,1,1]), orthogonalize(x_vec, [1,1,1])) == 0):
        raise Exception("TEST FAILED.  Orthogonalized vector is not perpendicular to 'parallel' vector!")
    
    print("All tests succeeded.")
    
    