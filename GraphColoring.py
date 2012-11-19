#! /usr/bin/env python
# Author: Sean Lisse

# File encapsulating all of my graph coloring logic for pelvic floor graphing.

# Built-in imports
from numpy import Infinity, abs

# Nonspecific imports
from Utilities import debug_levels, debugprint, enum

# My custom function imports
from Fiducials import vector_from_fiducials, get_fiducial_row_and_column
from VectorMath import perpendicular_component, magnitude, vector_magnitude_sum

# Constants
from Fiducials import COORDS, REFERENCE_POINT_NAMES, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, PUBIC_SYMPHYSIS_NAME

COLORIZATION_OPTIONS = enum('XYZ', 'Z', 'PIS_DISTANCE', 'WIDTH')
COLORIZATION_STRATEGY = COLORIZATION_OPTIONS.PIS_DISTANCE

PIS_distance_min = Infinity
PIS_distance_max = -1 * Infinity

def xyz_color_calibration(fiducial_list):
    ''' Given a list of fiducials, gather their maximum and minimum 3D extents in the x, y, and z coordinates.
    We will later use those extents to determine the RGB components of the color for the fiducials when drawn. '''
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    for key in fiducial_list.iterkeys():
        fid = fiducial_list[key]
        
        x = fid.coords[COORDS.X]
        y = fid.coords[COORDS.Y]
        z = fid.coords[COORDS.Z]
        
        if (x < x_min): x_min = x
        if (y < y_min): y_min = y
        if (z < z_min): z_min = z
        if (x > x_max): x_max = x
        if (y > y_max): y_max = y
        if (z > z_max): z_max = z
        
    # Not quite appropriate return here, but it'll at least give some info for the legend.
    return [x_min, x_max]

def xyz_color_fn(fiducial, vagprops):
    ''' Takes a fiducial point and returns a color with R based on relative X, G based on Y and B based on Z.
    NOTE: ASSUMES x_min,x_max,y_min,y_max,and z_min,z_max globals have been properly set!'''
    
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    red = (fiducial.coords[COORDS.X] - x_min) / (x_max - x_min)
    green = (fiducial.coords[COORDS.Y] - y_min) / (y_max - y_min)
    blue = (fiducial.coords[COORDS.Z] - z_min) / (z_max - z_min)
    
    return [red,green,blue]

def z_color_calibration(fiducial_list):
    global z_min, z_max
    
    for key in fiducial_list.iterkeys():
        if (key in REFERENCE_POINT_NAMES):
            continue
        
        fid = fiducial_list[key]
        
        if (fid.coords[COORDS.Z] < z_min): z_min = fid.coords[COORDS.Z]
        if (fid.coords[COORDS.Z] > z_max): z_max = fid.coords[COORDS.Z]    
        
    return [z_min, z_max]

def z_color_fn(fiducial, vagprops):
    ''' Takes a fiducial point and returns a color based on its height Z. '''
    green = (fiducial.coords[COORDS.Z] - z_min) / (z_max - z_min)
    red = 1 - green
    
    return [red,green,0]


def PIS_color_calibration(vagprops):
    ''' Function that sets up our pubis to ischial spine distance colorization.
    Takes as input a set of all fiducial points to be colorized,
    a fiducial point PS for the pubic symphysis,
    L_IS for left ischial spine, and R_IS for right ischial spine.''' 
    
    global PIS_distance_min, PIS_distance_max
    
    PIS_distance_min=Infinity
    PIS_distance_max=-1*Infinity
    
    fiducial_points = vagprops._fiducial_points
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
        if (key in REFERENCE_POINT_NAMES):
            continue
        
        fid_vector = vector_from_fiducials(vagprops._Pubic_Symphysis, fid)
        
        L_PIS_distance = abs(magnitude(perpendicular_component(vagprops._Left_PIS_Vector, fid_vector)))
        R_PIS_distance = abs(magnitude(perpendicular_component(vagprops._Right_PIS_Vector, fid_vector)))
        
        if (L_PIS_distance <= R_PIS_distance):
            chosen_PIS_distance = L_PIS_distance
        else:
            chosen_PIS_distance = R_PIS_distance
        
        # Ignore any points that happen to be *on* the line in our calibration.    
        if (chosen_PIS_distance > 0.05):
            if (chosen_PIS_distance > PIS_distance_max): PIS_distance_max = chosen_PIS_distance
            if (chosen_PIS_distance < PIS_distance_min): PIS_distance_min = chosen_PIS_distance
        else: 
            debugprint("Ignoring fiducial " + key + "as being on our reference line.", debug_levels.BASIC_DEBUG)
            
        debugprint("Fiducial " + key, debug_levels.DETAILED_DEBUG)
        debugprint("L_PIS distance: " + str(L_PIS_distance), debug_levels.DETAILED_DEBUG)
        debugprint("R_PIS distance: " + str(R_PIS_distance), debug_levels.DETAILED_DEBUG)
        debugprint("Chosen PIS distance: " + str(chosen_PIS_distance), debug_levels.DETAILED_DEBUG)    
        
    debugprint("Max PIS distance: " + str(PIS_distance_max), debug_levels.DETAILED_DEBUG)
    debugprint("Min PIS distance: " + str(PIS_distance_min), debug_levels.DETAILED_DEBUG)
    
    return([PIS_distance_min, PIS_distance_max])
    

def PIS_color_fn(fiducial, vagprops):
    ''' determine where on the red-green spectrum our chosen point distance lies (based on minimum distance from the nearest PIS line) '''
    
    # read-only vars so don't need to be declared global - this is a reminder.
    # global PIS_distance_min, PIS_distance_max 
    
    fid_vector = vector_from_fiducials(vagprops._Pubic_Symphysis, fiducial)
        
    L_PIS_distance = abs(magnitude(perpendicular_component(vagprops._Left_PIS_Vector, fid_vector)))
    R_PIS_distance = abs(magnitude(perpendicular_component(vagprops._Right_PIS_Vector, fid_vector)))
    
    if (L_PIS_distance <= R_PIS_distance):
        chosen_PIS_distance = L_PIS_distance
    else:
        chosen_PIS_distance = R_PIS_distance
        
    debugprint("Fiducial named " + fiducial.name + " has min PIS distance " + str(chosen_PIS_distance))
    
    return fraction_color(chosen_PIS_distance, PIS_distance_min, PIS_distance_max)
    
def fraction_color(distance, min, max):
    ''' Given a distance, a minimum, and a maximum, encodes how far along the distance is and return it as a color (start red, end green). '''     
    max_distance_fraction = (distance - min)/(max - min)
    
    if (max_distance_fraction < 0):
        max_distance_fraction = 0 # Might be one of the reference points that we ignored during calibration
        
    if (max_distance_fraction > 1):
        max_distance_fraction = 1 # Might be one of the reference points that we ignored during calibration
    
    return(max_distance_fraction, 1 - max_distance_fraction, 0)


# Vaginal width globals
vagrowcolors=[]

def width_distance_color_calibration(fid_points):
    ''' Determine the vaginal width at each level, then color-code based on the longest and shortest. 
        Assumes that each point to be included in a width has a name of the format *A_L_*, 
        where the number after A is the rank from the apex (starting at 1)
        and the number after L is the rank from the left side (starting at 1).
        
        E.G. the top-left most vaginal point will be at least "A1L1", but could be something like "A1L1 (Os)" or "(Os) A1L1".
        
        Assumes that there are no gaps within a row (the sequence can go A1L4, A1L5, A1L6, but cannot go A1L1, A1L4, A1L5)
        '''
    
    # "rows" is a list of lists.
    # Outer list index is row number (minus one), so A1 == rows[0]
    # Inner list index is column number (minus one), so A1L3 == rows[0][2]
    # Note that we may have some empty entries (fid point A1L1 may not exist, for example), which we will skip when tabulating later.
    rows=[]
    
    # Iterate through the fiducial points and gather those that have a row and column number into "rows"
    for key in fid_points.iterkeys():
        
        rownum,colnum = get_fiducial_row_and_column(fid_points[key])

        if ((rownum == None) or (colnum == None)):
            continue

        rowindex = int(rownum) - 1
        colindex = int(colnum) - 1

        # Expand rows[] to encompass our new row as needed
        while(len(rows) < (rowindex + 1)):
            rows.append([])
 
        # Expand rows[][] to encompass our new column as needed
        while(len(rows[rowindex]) < (colindex + 1)):
            rows[int(rowindex)].append([])
 
        fid = fid_points[key]
        rows[rowindex][colindex] = fid
    
  
    # List of vaginal widths for each row 
    vagwidths=[]  
    
    # Minimum and maximum row width overall for colorization and display purposes
    vagwidthmin = Infinity
    vagwidthmax = -1 * Infinity
    
    # Iterate over all the fiducial points and collect them into a sequence of point-to-point vectors for each row 
    for rowindex in range(0,len(rows)):

        columns = rows[rowindex]
        
        # Our list of vectors from each point to the next in the list, starting leftmost and continuing right.
        vecs = []
        
        for colindex in range(1, len(columns)):
            # Start at 1 to intentionally skip the first point so we don't underrun when looking at rows[colindex - 1]. 
            
            if (columns[colindex-1]) and (columns[colindex]):
                # We know we have two non-empty entries, so add a vector from this point to the point before
                vecs.append(vector_from_fiducials(columns[colindex - 1], columns[colindex]))

        vagwidths.insert(rowindex,vector_magnitude_sum(vecs))
        
        if (vagwidths[rowindex] < vagwidthmin): 
            vagwidthmin = vagwidths[rowindex]
            
        if (vagwidths[rowindex] > vagwidthmax):
            vagwidthmax = vagwidths[rowindex]

    global vagrowcolors
    
    for rowindex in range(0,len(vagwidths)):
        
        red = (vagwidths[rowindex] - vagwidthmin) / vagwidthmax
        green = 1 - red
        blue = 0
        vagrowcolors.append([red,green,blue])
    
    return([vagwidthmin, vagwidthmax])
        

def width_distance_color_fn(fid_point,vagprops):
    ''' Determine the vaginal width at each level, then color-code based on the longest and shortest. 
        Return the color determined by our previous calibration. '''
    # The below line is an unnecessary line because we're not modifying vagrowcolors,
    #   but it's a good reminder that we're pulling in a global.
    ## global vagrowcolors
    
    rownum, colnum = get_fiducial_row_and_column(fid_point)
    
    if (rownum == None):
        return [0,0,0]
     
    rowindex = rownum - 1
        
    print("coloring point " + fid_point.name)
    print("****" + str(rowindex) + "******")
    
    return vagrowcolors[rowindex]

def calibrate_colorization_strategy_fn(color_strat_enum, vagprops):
    ''' Calibrates a colorization strategy given its enum and the fiducial points to be drawn.
        Returns a tuple of [fn, minmax] where "function" is a colorizing function 
        and "minmax" is a tuple [min,max] of minimum and maximum values to add to the graph legend.'''

    fid_points = vagprops._fiducial_points

    ### OPTION 1: XYZ COLOR CODING
    if (COLORIZATION_STRATEGY == COLORIZATION_OPTIONS.XYZ):
        minmax_distances = xyz_color_calibration(fid_points)
        color_fn=xyz_color_fn
    
    ### OPTION 2: Z COLOR CODING
    if (COLORIZATION_STRATEGY == COLORIZATION_OPTIONS.Z):
        minmax_distances = z_color_calibration(fid_points)
        color_fn = z_color_fn
    
    ### OPTION 3: PIS DISTANCE COLOR CODING
    if (COLORIZATION_STRATEGY == COLORIZATION_OPTIONS.PIS_DISTANCE):
        minmax_distances = PIS_color_calibration(vagprops)
        color_fn = PIS_color_fn
        
    ### OPTION 4: VAGINAL WIDTH BY ROW
    if (COLORIZATION_STRATEGY == COLORIZATION_OPTIONS.WIDTH):
        minmax_distances = width_distance_color_calibration(fid_points)    
        color_fn = width_distance_color_fn
        
    return color_fn, minmax_distances