#! /usr/bin/env python
# Author: Sean Lisse
# This code contains all user-editable options for the PICS3D code.

from Utilities import enum

# ******** DO NOT CHANGE THIS SECTION. ********

# Coordinate enumeration - basically equates [X] to [0], [Y] to [1] and [Z] to [2].
COORDS=enum('X','Y','Z')

# This is the pattern used to match Fiducial names and parse out the row number (from apex, A) and column number (from left, L).
# We want to find the part of the string that starts with an A followed by some numerals, then an L followed by some numerals.
INDEX_PATTERN='A(\d+)L(\d+)'

# Constants to look for when loading fiducials from an MRML file.
FIDUCIAL_XML_NODE_NAME = "AnnotationFiducials"
FIDUCIAL_COORD_ATTR_NAME = "ctrlPtsCoord"
FIDUCIAL_NAME_ATTR_NAME = "name"

# ********** OK TO CHANGE CAREFULLY BELOW HERE. ************

# *****************************************************************
# Pelvic anatomy and naming options 
# *****************************************************************

# Special fiducial point keywords
PUBIC_SYMPHYSIS_NAME="PS"
SC_JOINT_NAME="SCJ"
LEFT_ISCHIAL_SPINE_NAME="L_IS"
RIGHT_ISCHIAL_SPINE_NAME="R_IS"
INTER_ISCHIAL_SPINE_NAME="IIS"
REFERENCE_POINT_NAMES={PUBIC_SYMPHYSIS_NAME, SC_JOINT_NAME, LEFT_ISCHIAL_SPINE_NAME, RIGHT_ISCHIAL_SPINE_NAME, INTER_ISCHIAL_SPINE_NAME}

# String constants for constructing standard names
LEFT_EDGE_PREFIX="Left_Edge_"
RIGHT_EDGE_PREFIX="Right_Edge_"
CENTER_PREFIX="Center_"

# *****************************************************************
# PICS3D and scaling options
# *****************************************************************

# (34 degrees above horizontal is 0.5934 in radians)
DESIRED_SCIPP_ANGLE = -0.593411946

# Scale points around the origin? WARNING WARNING - IF THESE ARE TRUE, THEN ALL MEASUREMENTS BECOME RELATIVE AND ARE NO LONGER ABSOLUTE VALUES!!!
SCALE_BY_SCIPP_LINE=False
SCALE_BY_IIS_LINE=False

# If scaling is desired, to what length should we normalize the SCIPP line? 
SCIPP_SCALE_LENGTH=1
IIS_SCALE_LENGTH=1

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
# In ALL of the above, we adjust the anterior-posterior axis to attempt to corect pelvic inclination to true "standing" position.
AXIS_CODING_OPTIONS = enum('lisse','pics3d')
AXIS_CODING = AXIS_CODING_OPTIONS.lisse

# *****************************************************************
# Statistics computation and graphing options
# *****************************************************************

# Should we compute statistics for points on the edges of the structure?
COMPUTE_EDGES = True
# What about statistics for the mid-sagittal section?
COMPUTE_CENTER = False
# Should we compute statistics for all points by name?
COMPUTE_ALL_INDIVIDUAL_POINTS = False

# How long should they be?  length = std_dev * graph_multiplier.
STD_DEV_GRAPH_MULTIPLIER = 2

# *****************************************************************
# Basic Graphing options
# *****************************************************************

COLORIZATION_OPTIONS = enum('XYZ', 'Z', 'PIS_DISTANCE', 'WIDTH', 'SEQUENTIAL')
DEFAULT_COLORIZATION_STRATEGY = COLORIZATION_OPTIONS.XYZ

# Default color for pelvic points
DEFAULT_COLOR=[0.5,0.5,0.75]

REFERENCE_POINT_COLOR = [0,0,0]

# Used for sequential_color_fn
SEQ_COLOR_FN_STEP_SIZE = 0.1

# CONSTANTS
COLOR_STRAT = COLORIZATION_OPTIONS.WIDTH

# *****************************************************************
# Detailed Graphing options
# *****************************************************************

REFERENCE_POINT_BAR_COLOR="#AABBAA"
BAR_COLOR = "#EEEEEE"
POINT_COLOR = "#000000"
COORD_TO_GRAPH=COORDS.Z

# Maximum and minimum Y axis values on our coordinates graph
GRAPH_MAX_MM = 100
GRAPH_MIN_MM = -50

# Maximum and minimum Y axis values on our paravaginal gap graph
PARAVAG_MAX_MM = 100
PARAVAG_MIN_MM = -10

# Which graphs should we generate?
SHOW_COORDINATE_GRAPH = True
SHOW_PARAVAG_GRAPH = True

# Which points should we include in our graphed display?
SHOW_REFERENCE_POINTS = True

