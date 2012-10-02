# This file contains some basic 3D vector math for use when doing physical reasoning.
# It assumes that each 3D point is a numpy array with 3 components, ordered as 'X', 'Y', 'Z'.

import numpy
# import scipy


def distance_vector(startfiducial, endfiducial):
    ''' Takes two points, startfiducial and endfiducial, and returns the vector from start to end. '''
    
    startarray = startfiducial.coords
    endarray = endfiducial.coords
    result = endarray - startarray
    return result

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

def length(vectorList):
    ''' Given a list of vectors, sum their magnitudes and return that as a scalar. '''
    
    total_length=0
    
    for i in range(len(vectorList)): 
        vector = vectorList[i]
        total_length=total_length + magnitude(vector)
    
    return total_length

def parallel_component(reference_vector, comparison_vector):
    ''' Given a reference vector and a comparison vector, projects the comparison onto the reference and returns
    only the component of the comparison vector that is parallel to the reference vector.'''
    
    ref_vector_normal = normalize(reference_vector)
    parallel_magnitude= numpy.dot(ref_vector_normal, comparison_vector)
    result = magnify(ref_vector_normal, parallel_magnitude)
    
    return result

def perpindicular_component(reference_vector, comparison_vector):
    ''' Given a reference vector and a comparison vector, projects the comparison onto the reference and returns
    only the component of the comparison vector that is perpindicular to the reference vector.'''
    
    ref_vector_normal = normalize(reference_vector)
    result = comparison_vector - parallel_component(reference_vector, comparison_vector)
    
    return result