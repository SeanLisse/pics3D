#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree and perform some math upon them, then display the results.

# Built-in imports
from numpy import Infinity, abs

# Nonspecific imports
from Utilities import setdebuglevel, debug_levels, debugprint, enum

# My custom function imports
from MRMLSweep import load_fiducials_from_mrml
from VaginalProperties import VaginalProperties
from Fiducials import fiducial,vector_from_fiducials, COORDS
from VectorMath import perpendicular_component, magnitude, vector_magnitude_sum
from Graphing import add_fiducials_to_graph, add_columns_to_graph, add_line_to_graph, add_scatterpoint_to_graph
from Graphing import add_legend_to_graph, set_graph_boundaries, show_graph, PelvicGraph


PUBIC_SYMPHYSIS_NAME="PS"
SC_JOINT_NAME="SCJ"
LEFT_ISCHIAL_SPINE_NAME="L_IS"
RIGHT_ISCHIAL_SPINE_NAME="R_IS"

REFERENCE_POINT_NAMES={PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME}

COLORIZATION_OPTIONS = enum('XYZ', 'Z', 'PIS_DISTANCE', 'WIDTH')
COLORIZATION_STRATEGY = COLORIZATION_OPTIONS.WIDTH

# This is the pattern used to match fiducial names and parse out the row number (from apex, A) and column number (from left, L).
# We want to find the part of the string that starts with an A followed by some numerals, then an L followed by some numerals.
INDEX_PATTERN='A(\d+)L(\d+)'

# Add 8 artificial cube corners to the graph to force the same scaling on all graphs.  Set to False to not draw.
PAD_GRAPH=False

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
    
    for key in fiducial_list.iterkeys():
        if (key in REFERENCE_POINT_NAMES):
            continue
        
        fid = fiducial_list[key]
        
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
        
        if (key in REFERENCE_POINT_NAMES):
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
    ''' determine where on the red-green spectrum our chosen point distance lies (based on minimum distance from the nearest PIS line) '''
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
    ''' determine where on the red-green spectrum our chosen PIS distance lies '''    
    max_distance_fraction = (distance - PIS_distance_min)/(PIS_distance_max - PIS_distance_min)
    
    if (max_distance_fraction < 0):
        max_distance_fraction = 0 # Might be one of the reference points that we ignored during calibration
        
    if (max_distance_fraction > 1):
        max_distance_fraction = 1 # Might be one of the reference points that we ignored during calibration
    
    return(max_distance_fraction, 1 - max_distance_fraction, 0)


def get_fiducial_row_and_column(fid_point):
    ''' Parse a fiducial point's name to find out what its row and column are.  
    Returns a [row, column] tuple.  E.g. if the point is A1L1, returns [1,1].
    Returns [None, None] if it cannot find them.'''
     
    # Grab the regular expressions library "re" so we can use it to parse fiducial names
    import re
       
    # Ignore reference points
    if (fid_point.name in REFERENCE_POINT_NAMES):
        return [None, None]

    searchresults = re.search(INDEX_PATTERN, fid_point.name)
    
    if (searchresults == None): return [None, None]
    
    rownum = searchresults.groups()[0] # the first group we grab should be the number after the 'A', so the row number.
    colnum = searchresults.groups()[1] # The second group we grab should be the number after the 'L', so the column number.
    
    return [int(rownum), int(colnum)]

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
        

def width_distance_color(fid_point):
    ''' Determine the vaginal width at each level, then color-code based on the longest and shortest. 
        Return the color determined by our previous calibration. '''
    # The below line is an unnecessary line because we're not modifying vagrowcolors,
    #   but it's a good reminder that we're pulling in a global.
    #global vagrowcolors
    
    rownum, colnum = get_fiducial_row_and_column(fid_point)
    
    if (rownum == None):
        return [0,0,0]
     
    rowindex = rownum - 1
        
    print("coloring point " + fid_point.name)
    print("****" + str(rowindex) + "******")
    
    return vagrowcolors[rowindex]

def draw_pelvic_points_graph(fid_points, graphname):

    graph = PelvicGraph(graphname)

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
        minmax_distances = PIS_color_calibration(fid_points, 
                                                fid_points[PUBIC_SYMPHYSIS_NAME],
                                                fid_points[LEFT_ISCHIAL_SPINE_NAME],
                                                fid_points[RIGHT_ISCHIAL_SPINE_NAME])
        color_fn = PIS_color_fn
        
    ### OPTION 4: VAGINAL WIDTH BY ROW
    if (COLORIZATION_STRATEGY == COLORIZATION_OPTIONS.WIDTH):
        minmax_distances = width_distance_color_calibration(fid_points)
        
        color_fn = width_distance_color
    
    add_fiducials_to_graph(graph, fid_points, color_fn)
    
    # Display the P_IS lines on the graph as well
    PS = fid_points[PUBIC_SYMPHYSIS_NAME]
    L_IS = fid_points[LEFT_ISCHIAL_SPINE_NAME]
    R_IS = fid_points[RIGHT_ISCHIAL_SPINE_NAME]
    add_line_to_graph(graph, PS.coords, L_IS.coords, "black")
    add_line_to_graph(graph, PS.coords, R_IS.coords, "black")
    
    IIS_coords = (L_IS.coords + R_IS.coords)/2
    add_scatterpoint_to_graph(graph, "IIS", IIS_coords[COORDS.X], IIS_coords[COORDS.Y], IIS_coords[COORDS.Z],"black")
    
    if(fid_points.has_key(SC_JOINT_NAME)):
        add_line_to_graph(graph, PS.coords, fid_points[SC_JOINT_NAME].coords, "black")
    
    if PAD_GRAPH:
        # Pad the graph to keep all graphs at equal scale for comparison
        GRAPH_PADDING=100
        set_graph_boundaries(graph,
                             PS.coords[COORDS.X] + GRAPH_PADDING, 
                             PS.coords[COORDS.X] - GRAPH_PADDING,
                             PS.coords[COORDS.Y] + GRAPH_PADDING, 
                             PS.coords[COORDS.Y] - GRAPH_PADDING,
                             PS.coords[COORDS.Z] + GRAPH_PADDING,
                             PS.coords[COORDS.Z] - GRAPH_PADDING)
        
    # Add a legend 
    add_legend_to_graph(graph,
                        "Minimum Distance: " + str(round(minmax_distances[0],1)) + "mm", 
                        "Maximum Distance: " + str(round(minmax_distances[1],1)) + "mm",
                        PIS_distance_color(minmax_distances[0]), 
                        PIS_distance_color(minmax_distances[1]))
    
    # Display the graph
    show_graph(graph)



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
        
        vag_props = VaginalProperties()
                    
        load_fiducials_from_mrml(filename, vag_props._fiducial_points)

        ### Here we encode and graph by minimum distance from one of the P->IS lines.        
        if (vag_props._fiducial_points.has_key(PUBIC_SYMPHYSIS_NAME) 
            and vag_props._fiducial_points.has_key(LEFT_ISCHIAL_SPINE_NAME) 
            and vag_props._fiducial_points.has_key(RIGHT_ISCHIAL_SPINE_NAME)):
            
            draw_pelvic_points_graph(vag_props._fiducial_points, filename)
        else:
            debugprint("Error!  Cannot find one of the points named: " 
                       + PUBIC_SYMPHYSIS_NAME 
                       + "," + LEFT_ISCHIAL_SPINE_NAME 
                       + ", or " + RIGHT_ISCHIAL_SPINE_NAME, debug_levels.ERRORS)   
            
        debugprint('Now leaving pelvic points program',debug_levels.BASIC_DEBUG)
