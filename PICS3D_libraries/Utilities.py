#! /usr/bin/env python
# Author: Sean Lisse
# Collection of utility scripts

from numpy import pi

# Enum definition borrowed from the internet.  Thank you internet.
def enum(*sequential, **named):
    ''' Custom enumerator creator - 
    example:  
    Numbers = enum('ZERO', 'ONE', 'TWO')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1
    '''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

debug_levels = enum('NO_DEBUG','ERRORS','BASIC_DEBUG','DETAILED_DEBUG')
debug_level = debug_levels.BASIC_DEBUG

def debugprint(info, level = debug_levels.BASIC_DEBUG):
    ''' Prints info if level is less than or equal to the current debug_level '''
    global debug_level
    if(level <= debug_level): 
        print(info)
        
def setdebuglevel(level):
    ''' Set the current debug_level '''
    global debug_level
    
    #print("Debug level is: " + str(debug_level))
    debug_level = level
    #print("Debug level is now: " + str(debug_level))


def rad_to_degrees(radians):
    
    return(radians*180 /pi)
