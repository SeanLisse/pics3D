#! /usr/bin/env python
# Author: Sean Lisse
# This code contains all user-editable options for the PICS3D code.

from Utilities import enum
from pylab import rcParams

# *****************************************************************
# ******** DO NOT CHANGE ANYTHING IN THIS SECTION!         ********
# *****************************************************************

# Coordinate enumeration - basically equates [X] to [0], [Y] to [1] and [Z] to [2].
COORDS=enum('X','Y','Z')

# This is the pattern used to match Fiducial names and parse out the row number (from apex, A) and column number (from left, L).
# We want to find the part of the string that starts with an A followed by some numerals, then an L followed by some numerals.
INDEX_PATTERN='[Aa](\d+)[Ll](\d+)'

##### Constants to look for when loading fiducials from an MRML file.
# SLICER 4.0-4.2 version
SLICER4_2_FIDUCIAL_XML_NODE_NAME = "AnnotationFiducials"
SLICER4_2_FIDUCIAL_COORD_ATTR_NAME = "ctrlPtsCoord"
SLICER4_2_FIDUCIAL_NAME_ATTR_NAME = "name"

##### Constants to look for when loading fiducials from an MRML file.
# SLICER 4.3+ version
SLICER4_3_FIDUCIAL_XML_NODE_NAME = "MarkupsFiducialStorage"
SLICER4_3_FIDUCIAL_CSV_FILENAME_ATTR_NAME = "fileName"

# And v4.3 constants to describe the order in which our X,Y,Z, and NAME values are coming from the fiducial CSV files:
SLICER4_3_CSV_NAME_INDEX=11
SLICER4_3_CSV_X_INDEX=1
SLICER4_3_CSV_Y_INDEX=2
SLICER4_3_CSV_Z_INDEX=3

# *****************************************************************
# ********** OK TO CHANGE CAREFULLY BELOW HERE. ************
# *****************************************************************



# *****************************************************************
# Pelvic anatomy and naming options 
# *****************************************************************

# Special fiducial point keywords
PUBIC_SYMPHYSIS_NAME="PS"
SC_JOINT_NAME="SCJ"
LEFT_ISCHIAL_SPINE_NAME="L_IS"
RIGHT_ISCHIAL_SPINE_NAME="R_IS"
INTER_ISCHIAL_SPINE_NAME="IIS"
REFERENCE_POINT_NAMES={PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME} # Removed INTER_ISCHIAL_SPINE_NAME for now to clean up graph

# Should we compute and display the inter-ischial-spine point?
CREATE_IIS = False

# String constants for constructing standard names
LEFT_EDGE_PREFIX="L_"
RIGHT_EDGE_PREFIX="R_"
CENTER_PREFIX="Mid_"

# *****************************************************************
# PICS3D and scaling options
# *****************************************************************

# (34 degrees above horizontal is 0.5934 in radians)
DESIRED_SCIPP_ANGLE = -0.593411946

# Scale points around the origin? WARNING WARNING - IF THESE ARE TRUE, THEN ALL MEASUREMENTS BECOME RELATIVE AND ARE NO LONGER ABSOLUTE VALUES!!!
SCALE_BY_SCIPP_LINE=False
SCALE_BY_IIS_LINE=False

# If scaling is desired, to what length should we normalize the SCIPP line? 
SCIPP_SCALE_LENGTH=100
IIS_SCALE_LENGTH=100

# Which axes go where.
# In "lisse" encoding, "X" increases to the patient's left, 
# "Y" increases to the patient's posterior, and 
# "Z" increases to the patient's superior.
#
# In "pics3d" encoding, "X" increases to the patient's posterior, 
# "Y" increases to the patient's superior, 
# and "Z" increases to the patient's left.
# 
# In "pseudo-JCS" encoding, that "X" increases to the patient's anterior, 
# "Y" increases to the patient's superior, and 
# "Z" increases to the patient's right.
# 
# In ALL of the above, we adjust the anterior-posterior axis to attempt to correct pelvic inclination to true "standing" position.
AXIS_CODING_OPTIONS = enum('lisse','pics3d')
AXIS_CODING = AXIS_CODING_OPTIONS.lisse

# *****************************************************************
# Statistics computation and graphing options
# *****************************************************************

# Should we compute statistics for points on the edges of the structure?
COMPUTE_LEFT_EDGES = True
COMPUTE_RIGHT_EDGES = False
# What about statistics for the mid-sagittal section?
COMPUTE_CENTER = False
# Should we compute statistics for all points by name?
COMPUTE_ALL_INDIVIDUAL_POINTS = False

# How long should they be?  length = std_dev * graph_multiplier.
STD_DEV_GRAPH_MULTIPLIER = 2

# *****************************************************************
# Basic Graphing options
# *****************************************************************

# Set the size of the graph in inches
GRAPH_HEIGHT = 10
GRAPH_WIDTH = 5
rcParams['figure.figsize'] = GRAPH_HEIGHT, GRAPH_WIDTH

COLORIZATION_OPTIONS = enum('XYZ', 'Z', 'PIS_DISTANCE', 'WIDTH', 'SEQUENTIAL')
DEFAULT_COLORIZATION_STRATEGY = COLORIZATION_OPTIONS.SEQUENTIAL

# Default color for pelvic points
DEFAULT_COLOR=[0.5,0.5,0.75]

REFERENCE_POINT_COLOR = [0,0,0]

# Used for sequential_color_fn
SEQ_COLOR_FN_STEP_SIZE = 0.1

# CONSTANTS
COLOR_STRAT = COLORIZATION_OPTIONS.Z

# *****************************************************************
# Detailed Graphing options
# *****************************************************************

GRAPH_TITLE = "PICS3D Graphing"
GRAPH_BACKGROUND_COLOR="#DDDDDD"

POINT_COLOR = "#000000"
COORD_TO_GRAPH=COORDS.Z

# Maximum and minimum Y axis values on our coordinates graph
COORDINATE_GRAPH_MAX_MM = 100
COORDINATE_GRAPH_MIN_MM = -50

# Maximum and minimum Y axis values on our paravaginal gap graph
PARAVAG_GRAPH_MAX_MM = 100
PARAVAG_GRAPH_MIN_MM = -50

# Maximum and minimum Y axis values on our width graph
WIDTH_GRAPH_MIN_MM = 0
WIDTH_GRAPH_MAX_MM = 70

# Which graphs should we generate?
SHOW_COORDINATE_GRAPH = True
SHOW_PARAVAG_GRAPH = False
SHOW_WIDTH_GRAPH = False

# Which data should we show on the graphs?
SHOW_INDIVIDUAL_VALUES = True
SHOW_RANGE_VALUES = True

# Should we draw P_IS lines?
SHOW_P_IS = False

# Which points should we include in our graphed display?
SHOW_REFERENCE_POINTS = False

# *****************************************************************
#  Additional Range Comparison Graphing Options
# *****************************************************************

RANGE_ONE_COLOR = 'darkred'
RANGE_TWO_COLOR = 'darkblue'