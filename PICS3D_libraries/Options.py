#! /usr/bin/env python
# Author: Sean Lisse
# This code contains all user-editable (but infrequently changed) options for the PICS3D code.

from PICS3D_libraries.Utilities import enum

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

# SET WHICH AXIS CODING YOU WANT *HERE*
AXIS_CODING = AXIS_CODING_OPTIONS.pics3d

# Which axis is left-right?
AXIS_CODING_LR = None

# Which axis is superior-inferior?
AXIS_CODING_SI = None

# Which axis is front-back (antero-posterior)?
AXIS_CODING_AP = None  

if (AXIS_CODING == AXIS_CODING_OPTIONS.lisse):
    AXIS_CODING_LR = COORDS.X
    AXIS_CODING_SI = COORDS.Z
    AXIS_CODING_AP = COORDS.Y

if (AXIS_CODING == AXIS_CODING_OPTIONS.pics3d):
    AXIS_CODING_LR = COORDS.Z
    AXIS_CODING_SI = COORDS.Y
    AXIS_CODING_AP = COORDS.X