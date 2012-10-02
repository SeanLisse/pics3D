#! /usr/bin/env python
# Author: Sean Lisse
# Collection of utility scripts

# Enum definition borrowed from this page: 
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

#TODO: collect the below into a range
debug_levels=enum('NO_DEBUG','BASIC_DEBUG','DETAILED_DEBUG')

debug_level=debug_levels.NO_DEBUG
# debug_level=BASIC_DEBUG
# debug_level=DETAILED_DEBUG

def debugprint(info, level=1):
    ''' Prints info if level is less than or equal to the current debug_level '''
    if(level <= debug_level): 
        print(info)
        
def setdebuglevel(level):
    ''' Set the current debug_level '''
    debug_level = level
    
