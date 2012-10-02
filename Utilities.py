# Collection of utility scripts

NO_DEBUG=0
BASIC_DEBUG=1
DETAILED_DEBUG=2

debug_level=NO_DEBUG
# debug_level=BASIC_DEBUG
# debug_level=DETAILED_DEBUG

def debugprint(info, level=1):
    ''' Prints info if level is less than or equal to the current debug_level '''
    if(level <= debug_level): 
        print(info)
        
def setdebuglevel(level):
    ''' Set the current debug_level '''
    debug_level = level
    
