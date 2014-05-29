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

# How long should the std dev whiskers be?  (length = std_dev * STD_DEV_GRAPH_MULTIPLIER)
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

# Set the view direction (in degrees)
## "elevation stores the elevation angle in the z plane. azimuth stores the azimuth angle in the x,y plane."

## 0,0 = Side view
GRAPH_VIEW_ELEVATION = 0
GRAPH_VIEW_AZIMUTH = 0

## 90,0 = Top view
# GRAPH_VIEW_ELEVATION = 90
# GRAPH_VIEW_AZIMUTH = 0

# ## 45,-45 = Oblique View
# GRAPH_VIEW_ELEVATION = 45
# GRAPH_VIEW_AZIMUTH = -45


# Default color for pelvic points
DEFAULT_COLOR=[0.5,0.5,0.75]

REFERENCE_POINT_COLOR = [0,0,0]

# Used for sequential_color_fn
SEQ_COLOR_FN_STEP_SIZE = 0.1

# CONSTANTS
COLOR_STRAT = COLORIZATION_OPTIONS.SEQUENTIAL

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

# Which summary graphs should we generate?
SHOW_COORDINATE_GRAPH = True
SHOW_PARAVAG_GRAPH = True
SHOW_WIDTH_GRAPH = True

# Which data should we show on the summary graphs?
SHOW_INDIVIDUAL_VALUES = True
SHOW_RANGE_VALUES = True

# Should we draw P_IS lines?
DRAW_PS_IS_LINES = False
DRAW_PARAVAG_GAP_LINES = False

# Which points should we include in our graphed display?
SHOW_REFERENCE_POINTS = False

# Should we show the graph axes?
DRAW_AXIS_LABELS = True

# *****************************************************************
#  Additional Range Comparison Graphing Options
# *****************************************************************

RANGE_ONE_COLOR = 'darkred'
RANGE_TWO_COLOR = 'darkblue'