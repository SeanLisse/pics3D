#! /usr/bin/env python
# Author: Sean Lisse
# This code contains all user-editable options for the PICS3D code.

from PICS3D_libraries.Options import enum, AXIS_CODING_IS
from pylab import rcParams

# *****************************************************************
# Statistics computation and graphing options
# *****************************************************************

# Should we compute statistics for points on the edges of the structure?
COMPUTE_LEFT_EDGES = True
COMPUTE_RIGHT_EDGES =  True
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
GRAPH_WIDTH = 10
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
AXIS_TO_GRAPH=AXIS_CODING_IS

# Maximum and minimum Y axis values on our coordinates graph
COORDINATE_GRAPH_MAX_MM = 100
COORDINATE_GRAPH_MIN_MM = -50

# Maximum and minimum Y axis values on our paravaginal gap graph
PARAVAG_GRAPH_MAX_MM = 100
PARAVAG_GRAPH_MIN_MM = -50

# Maximum and minimum Y axis values on our width graph
WIDTH_GRAPH_MIN_MM = 0
WIDTH_GRAPH_MAX_MM = 70

# Add 8 artificial cube corners to the graph to force the same scaling on all graphs.  Set to False to not draw.
PAD_GRAPH = False

# Which graphs should we generate?
SHOW_COORDINATE_GRAPH = True
SHOW_PARAVAG_GRAPH = True
SHOW_WIDTH_GRAPH = True

# Which data should we show on the graphs?
SHOW_INDIVIDUAL_VALUES = False
SHOW_RANGE_VALUES = True

# Should we draw P_IS lines?
DRAW_PS_IS_LINES = True
DRAW_PARAVAG_GAP_LINES = True

# Which points should we include in our graphed display?
SHOW_REFERENCE_POINTS = True

# *****************************************************************
#  Additional Range Comparison Graphing Options
# *****************************************************************

RANGE_ONE_COLOR = 'darkred'
RANGE_TWO_COLOR = 'darkblue'