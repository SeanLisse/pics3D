#! /usr/bin/env python
# Author: Sean Lisse

# File encapsulating all of my graph coloring logic for pelvic floor graphing.

# Built-in imports
from numpy import Infinity, abs, floor

# Nonspecific imports
from Utilities import debug_levels, debugprint, enum

# My custom function imports
from Fiducials import vector_from_fiducials, get_fiducial_row_and_column
from VectorMath import perpendicular_component, magnitude

# Constants
from Fiducials import COORDS, REFERENCE_POINT_NAMES

COLORIZATION_OPTIONS = enum('XYZ', 'Z', 'PIS_DISTANCE', 'WIDTH', 'SEQUENTIAL')
DEFAULT_COLORIZATION_STRATEGY = COLORIZATION_OPTIONS.XYZ

REFERENCE_POINT_COLOR = [0,0,0]

# PIS Colorization globals (careful, multideclaration!)
PIS_distance_min = x_min = y_min = z_min = Infinity
PIS_distance_max = x_max = y_max = z_max = -1 * Infinity

# Globals used for sequential_color_fn
seq_color_fn_counter = 0
SEQ_COLOR_FN_STEP_SIZE = 0.1

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

def xyz_color_fn(fiducial, vagdisplay):
    ''' Takes a fiducial point and returns a color with R based on relative X, G based on Y and B based on Z.
    NOTE: ASSUMES x_min,x_max,y_min,y_max,and z_min,z_max globals have been properly set!'''
    
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    if (fiducial.name in REFERENCE_POINT_NAMES): 
        return REFERENCE_POINT_COLOR
    
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

def z_color_fn(fiducial, vagdisplay):
    ''' Takes a fiducial point and returns a color based on its height Z. '''
    
    if (fiducial.name in REFERENCE_POINT_NAMES): 
        return REFERENCE_POINT_COLOR
    
    green = (fiducial.coords[COORDS.Z] - z_min) / (z_max - z_min)
    red = 1 - green
    
    return [red,green,0]


def PIS_color_calibration(vagdisplay):
    ''' Function that sets up our pubis to ischial spine distance colorization.
    Takes as input a set of all fiducial points to be colorized,
    a fiducial point PS for the pubic symphysis,
    L_IS for left ischial spine, and R_IS for right ischial spine.''' 
    
    global PIS_distance_min, PIS_distance_max
    
    PIS_distance_min=Infinity
    PIS_distance_max=-1*Infinity
    
    fiducial_points = vagdisplay._fiducial_points
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
        if (key in REFERENCE_POINT_NAMES):
            continue
        
        fid_vector = vector_from_fiducials(vagdisplay._Pubic_Symphysis, fid)
        
        L_PIS_distance = abs(magnitude(perpendicular_component(vagdisplay._Left_PIS_Vector, fid_vector)))
        R_PIS_distance = abs(magnitude(perpendicular_component(vagdisplay._Right_PIS_Vector, fid_vector)))
        
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
    

def PIS_color_fn(fiducial, vagdisplay):
    ''' determine where on the red-green spectrum our chosen point distance lies (based on minimum distance from the nearest PIS line) '''
    
    # read-only vars so don't need to be declared global - this is a reminder.
    # global PIS_distance_min, PIS_distance_max 
    
    if (fiducial.name in REFERENCE_POINT_NAMES): 
        return REFERENCE_POINT_COLOR
    
    fid_vector = vector_from_fiducials(vagdisplay._Pubic_Symphysis, fiducial)
        
    L_PIS_distance = abs(magnitude(perpendicular_component(vagdisplay._Left_PIS_Vector, fid_vector)))
    R_PIS_distance = abs(magnitude(perpendicular_component(vagdisplay._Right_PIS_Vector, fid_vector)))
    
    if (L_PIS_distance <= R_PIS_distance):
        chosen_PIS_distance = L_PIS_distance
    else:
        chosen_PIS_distance = R_PIS_distance
        
    debugprint("Fiducial named " + fiducial.name + " has min PIS distance " + str(chosen_PIS_distance))
    
    return fraction_color(chosen_PIS_distance, PIS_distance_min, PIS_distance_max)
    
def fraction_color(distance, minimum, maximum):
    ''' Given a distance, a minimum, and a maximum, encodes how far along the distance is and return it as a color (start red, end green). '''     
    max_distance_fraction = (distance - minimum)/(maximum - minimum)
    
    if (max_distance_fraction < 0):
        max_distance_fraction = 0 # Might be one of the reference points that we ignored during calibration
        
    if (max_distance_fraction > 1):
        max_distance_fraction = 1 # Might be one of the reference points that we ignored during calibration
    
    return(max_distance_fraction, 1 - max_distance_fraction, 0)

def width_distance_color_calibration(vagdisplay):
    ''' Determine the vaginal width at each level, then color-code based on the longest and shortest. 
        Assumes that each point to be included in a width has a name of the format *A_L_*, 
        where the number after A is the rank from the apex (starting at 1)
        and the number after L is the rank from the left side (starting at 1).
        
        E.G. the top-left most vaginal point will be at least "A1L1", but could be something like "A1L1 (Os)" or "(Os) A1L1".
        
        Assumes that there are no gaps within a row (the sequence can go A1L4, A1L5, A1L6, but cannot go A1L1, A1L4, A1L5)
        '''
    
    debugprint("Calibrating vaginal widths", debug_levels.DETAILED_DEBUG)
    
    for rowindex in range(0,len(vagdisplay._vagwidths)):
        
        red = (vagdisplay._vagwidths[rowindex] - vagdisplay._globalvagwidthmin) / (vagdisplay._globalvagwidthmax - vagdisplay._globalvagwidthmin)
        green = 1 - red
        blue = 0
        vagdisplay._vagrowcolors.append([red,green,blue])
    
    return([vagdisplay._globalvagwidthmin, vagdisplay._globalvagwidthmax])
        

def width_distance_color_fn(fiducial,vagdisplay):
    ''' Determine the vaginal width at each level, then color-code based on the longest and shortest. 
        Return the color determined by our previous calibration. '''

    if (fiducial.name in REFERENCE_POINT_NAMES): 
        return REFERENCE_POINT_COLOR
    
    rownum, colnum = get_fiducial_row_and_column(fiducial)
    
    if (rownum == None):
        return "Grey"
     
    rowindex = rownum - 1
    
    return vagdisplay._vagrowcolors[rowindex]


 
def sequential_color_fn_calibration(vagdisplay):
    ''' Each vagina gets a different color.'''
    
    global seq_color_fn_counter
    
    seq_color_fn_counter += SEQ_COLOR_FN_STEP_SIZE
    
    # Define RGB colors.  Arbitrary colorization functions that I made up.
    red_color_fraction = seq_color_fn_counter 
    green_color_fraction = (seq_color_fn_counter % 0.5) * 2
    blue_color_fraction =  (seq_color_fn_counter % 0.5) * 3
    
    # Limit the range of each portion of RGB to 0..1
    red_color_fraction = red_color_fraction % 1
    green_color_fraction = green_color_fraction % 1
    blue_color_fraction = blue_color_fraction % 1 
    
    def custom_color_fn(fiducial, vagdisplay): 
        return [red_color_fraction, green_color_fraction, blue_color_fraction] 
    
    return custom_color_fn

def calibrate_colorization_strategy_fn(vagdisplay):
    ''' Calibrates a colorization strategy given its enum and the vaginal properties.
        Returns a tuple of [fn, minmax] where "function" is a colorizing function to be used later
        and "minmax" is a tuple [min,max] of minimum and maximum values to add to the graph legend.'''

    color_strat_enum = vagdisplay._color_strategy
    
    color_fn = None
    minmax_distances=[Infinity, -1 * Infinity]

    ### OPTION 1: XYZ COLOR CODING
    if (color_strat_enum == COLORIZATION_OPTIONS.XYZ):
        minmax_distances = xyz_color_calibration(vagdisplay._fiducial_points)
        color_fn = xyz_color_fn
    
    ### OPTION 2: Z COLOR CODING
    if (color_strat_enum == COLORIZATION_OPTIONS.Z):
        minmax_distances = z_color_calibration(vagdisplay._fiducial_points)
        color_fn = z_color_fn
    
    ### OPTION 3: PIS DISTANCE COLOR CODING
    if (color_strat_enum == COLORIZATION_OPTIONS.PIS_DISTANCE):
        minmax_distances = PIS_color_calibration(vagdisplay)
        color_fn = PIS_color_fn
        
    ### OPTION 4: VAGINAL WIDTH BY ROW
    if (color_strat_enum == COLORIZATION_OPTIONS.WIDTH):
        minmax_distances = width_distance_color_calibration(vagdisplay)    
        color_fn = width_distance_color_fn
        
    ### OPTION 5: SEQUENTIAL COLORING
    if (color_strat_enum == COLORIZATION_OPTIONS.SEQUENTIAL):
        color_fn = sequential_color_fn_calibration(vagdisplay)
        minmax_distances = [-1 * Infinity,Infinity]
        
    return color_fn, minmax_distances