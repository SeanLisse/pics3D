#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and perform some math upon them, then display the results.

from MRMLSweep import load_fiducials_from_mrml, fiducial_points
from Fiducials import fiducial,vector_from_fiducials, COORDS
from VectorMath import perpendicular_component, magnitude
from Graphing import add_fiducials_to_graph, add_columns_to_graph, add_line_to_graph
from Graphing import add_legend_to_graph, set_graph_boundaries, show_graph
from numpy import Infinity, abs
from Utilities import setdebuglevel, debug_levels, debugprint

PUBIC_SYMPHYSIS_NAME="PS"
SC_JOINT_NAME="SCJ"
LEFT_ISCHIAL_SPINE_NAME="L_IS"
RIGHT_ISCHIAL_SPINE_NAME="R_IS"

REFERENCE_POINT_NAMES=[PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME]

# Draw columns under each point (decorations).  Set to False to not draw.
DRAW_COLUMNS=False

# Add 8 artificial cube corners to the graph to force the same scaling on all graphs.  Set to False to not draw.
PAD_GRAPH=False

incremental_color = 0
def incremental_color_fn(fiducial):
    ''' Basic fiducial point coloration function that colors each point slightly brighter than the last one drawn until we reach white,
    then resets. ''' 
    INCREMENTAL_STEP = 0.01
    global incremental_color
    incremental_color = incremental_color + INCREMENTAL_STEP
    while (incremental_color > 1):
        incremental_color=incremental_color -1
    return [incremental_color, incremental_color, incremental_color]


# Define impossible mins & maxes for use with xyz_color_fn
x_min = y_min = z_min = Infinity
x_max = y_max = z_max = -1 * Infinity

def xyz_color_calibration(fiducial_list):
    ''' Given a list of fiducials, gather their maximum and minimum 3D extents in the x, y, and z coordinates.
    We will later use those extents to determine the RGB components of the color for the fiducials when drawn. '''
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
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

def xyz_color_fn(fiducial):
    ''' Takes a fiducial point and returns a color with R based on relative X, G based on Y and B based on Z.
    NOTE: ASSUMES x_min,x_max,y_min,y_max,and z_min,z_max globals have been properly set!'''
    
    global x_min, y_min, z_min, x_max, y_max,z_max
    
    red = (fiducial.coords[COORDS.X] - x_min) / (x_max - x_min)
    green = (fiducial.coords[COORDS.Y] - y_min) / (y_max - y_min)
    blue = (fiducial.coords[COORDS.Z] - z_min) / (z_max - z_min)
    
    return [red,green,blue]

def z_color_calibration(fiducial_list):
    global z_min, z_max
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
        if (fid.coords[COORDS.Z] < z_min): z_min = fid.coords[COORDS.Z]
        if (fid.coords[COORDS.Z] > z_max): z_max = fid.coords[COORDS.Z]    
        
    return [z_min, z_max]

def z_color_fn(fiducial):
    ''' Takes a fiducial point and returns a color based on its height Z. '''
    green = (fiducial.coords[COORDS.Z] - z_min) / (z_max - z_min)
    red = 1 - green
    
    return [red,green,0]
    

# Globals for use in PIS colorization
PIS_distance_min=Infinity
PIS_distance_max=-1*Infinity

# Set up our pelvic geometry defaults.  These should really *NEVER* be used.
Pubic_Symphysis = fiducial(PUBIC_SYMPHYSIS_NAME,0,0,0) #default to origin 
Left_PIS_Vector = [1,0,0] #default to simple X vector
Right_PIS_Vector = [0,1,0] #default to simple Y vector

def PIS_color_calibration(fiducial_points, PS, L_IS, R_IS):
    ''' Function that sets up our pubis to ischial spine distance colorization.
    Takes as input a set of all fiducial points to be colorized,
    a fiducial point PS for the pubic symphysis,
    L_IS for left ischial spine, and R_IS for right ischial spine.'''
    global Pubic_Symphysis, PIS_distance_min, PIS_distance_max, Left_PIS_Vector, Right_PIS_Vector 
    
    Pubic_Symphysis = PS
    Left_PIS_Vector = vector_from_fiducials(PS, L_IS)
    Right_PIS_Vector = vector_from_fiducials(PS, R_IS)
    
    for key in fiducial_points.iterkeys():
        fid = fiducial_points[key]
        
        if (REFERENCE_POINT_NAMES.count(key) > 0):
            continue
        
        fid_vector = vector_from_fiducials(PS, fid)
        
        L_PIS_distance = abs(magnitude(perpendicular_component(Left_PIS_Vector, fid_vector)))
        R_PIS_distance = abs(magnitude(perpendicular_component(Right_PIS_Vector, fid_vector)))
        
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
    

def PIS_color_fn(fiducial):
    global Pubic_Symphysis, PIS_distance_min, PIS_distance_max, Left_PIS_Vector, Right_PIS_Vector 
    fid_vector = vector_from_fiducials(Pubic_Symphysis, fiducial)
        
    L_PIS_distance = abs(magnitude(perpendicular_component(Left_PIS_Vector, fid_vector)))
    R_PIS_distance = abs(magnitude(perpendicular_component(Right_PIS_Vector, fid_vector)))
    
    if (L_PIS_distance <= R_PIS_distance):
        chosen_PIS_distance = L_PIS_distance
    else:
        chosen_PIS_distance = R_PIS_distance
        
    debugprint("Fiducial named " + fiducial.name + " has min PIS distance " + str(chosen_PIS_distance))
    
    return PIS_distance_color(chosen_PIS_distance)
    
def PIS_distance_color(distance):
    # determine where on the spectrum our chosen PIS distance lies    
    max_distance_fraction = (distance - PIS_distance_min)/(PIS_distance_max - PIS_distance_min)
    
    if (max_distance_fraction < 0):
        max_distance_fraction = 0 # Might be one of the reference points that we ignored during calibration
        
    if (max_distance_fraction > 1):
        max_distance_fraction = 1 # Might be one of the reference points that we ignored during calibration
    
    return(max_distance_fraction, 1 - max_distance_fraction, 0)

def draw_pelvic_points_graph(fid_points, graphname):

    ### OPTION 1: XYZ COLOR CODING
    # minmax_distances = xyz_color_calibration(fiducial_points)
    # color_fn=xyz_color_fn
    
    ### OPTION 2: Z COLOR CODING
#    minmax_distances = z_color_calibration(fiducial_points)
#    color_fn = z_color_fn
    
    ### OPTION 3: PIS DISTANCE COLOR CODING
    minmax_distances = PIS_color_calibration(fiducial_points, 
                                            fiducial_points[PUBIC_SYMPHYSIS_NAME],
                                            fiducial_points[LEFT_ISCHIAL_SPINE_NAME],
                                            fiducial_points[RIGHT_ISCHIAL_SPINE_NAME])
    color_fn = PIS_color_fn
    
    add_fiducials_to_graph(fiducial_points, color_fn)
    
    if DRAW_COLUMNS: 
        add_columns_to_graph(fiducial_points, color_fn)
    
    # Display the P_IS lines on the graph as well
    PS = fiducial_points[PUBIC_SYMPHYSIS_NAME]
    L_IS = fiducial_points[LEFT_ISCHIAL_SPINE_NAME]
    R_IS = fiducial_points[RIGHT_ISCHIAL_SPINE_NAME]
    add_line_to_graph(PS.coords, L_IS.coords, "black")
    add_line_to_graph(PS.coords, R_IS.coords, "black")
    
#    IIS_coords = (L_IS.coords + R_IS.coords)/2
#    add_scatterpoint_to_graph("IIS", IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z],"brown")
#    add_line_to_graph(PS.coords, IIS_coords, "brown")
    
    if(fiducial_points.has_key(SC_JOINT_NAME)):
        add_line_to_graph(PS.coords, fiducial_points[SC_JOINT_NAME].coords, "brown")
    
    if PAD_GRAPH:
        # Pad the graph to keep all graphs at equal scale for comparison
        GRAPH_PADDING=100
        set_graph_boundaries(PS.coords[COORDS.X] + GRAPH_PADDING, 
                             PS.coords[COORDS.X] - GRAPH_PADDING,
                             PS.coords[COORDS.Y] + GRAPH_PADDING, 
                             PS.coords[COORDS.Y] - GRAPH_PADDING,
                             PS.coords[COORDS.Z] + GRAPH_PADDING,
                             PS.coords[COORDS.Z] - GRAPH_PADDING)
        
    # Add a legend 
    add_legend_to_graph("Minimum Distance: " + str(round(minmax_distances[0],1)) + "mm", 
                        "Maximum Distance: " + str(round(minmax_distances[1],1)) + "mm",
                        PIS_distance_color(minmax_distances[0]), 
                        PIS_distance_color(minmax_distances[1]))
    
    # Display the graph
    show_graph(graphname)

#####################
### DEFAULT MAIN PROC
##################### 

if __name__ == '__main__':
    
    from sys import argv
     
    setdebuglevel(debug_levels.ERRORS) 
    
    if len(argv) < 2: 
        print "Need to supply mrml file name argument."
    else:
        filename = argv[1]
    
        debugprint('Now starting pelvic points program',debug_levels.BASIC_DEBUG)
                    
        load_fiducials_from_mrml(filename, fiducial_points)

        ### Here we encode and graph by minimum distance from one of the P->IS lines.        
        if (fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME) 
            and fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
            and fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)):
            
            draw_pelvic_points_graph(fiducial_points, filename)
        else:
            debugprint("Error!  Cannot find one of the points named: " 
                       + PUBIC_SYMPHYSIS_NAME 
                       + "," + LEFT_ISCHIAL_SPINE_NAME 
                       + ", or " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)   
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
