# import numpy as np
from mpl_toolkits.mplot3d import Axes3D #Seemingly meaningless but forces projection='3d' to work!  Do not remove this line!
import matplotlib.pyplot as plt
from Fiducials import COORDS

# Default color for pelvic points
DEFAULT_COLOR=[0.5,0.5,0.75]

# Z coordinate for drawing columns to points (this defines the "base" of the column)
COLUMN_START=-50

class PelvicGraph(object):
    def __init__(self, name="Fiducials"):
        # Figure and Axes objects to contain our plots
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot('111',projection='3d')
        
        self._ax.set_xlabel('X ("Left-Right")')
        self._ax.set_ylabel('Y ("Anterior-Posterior")')
        self._ax.set_zlabel('Z ("Cranial-Caudal")')
        
        plt.title(name)

def default_color(fiducial): 
    ''' Default coloration function. Clone this and alter it to customize your coloration when graphing. '''
    return DEFAULT_COLOR

def show_all_graphs():
    ''' Display the graph.  Call this after adding all scatterpoints to it. '''
    plt.show()

def add_scatterpoint_to_graph(graph, name, x, y, z, newcolor="black"):
    ''' Add a new scatterpoint to the graph.  Name is currently ignored. '''
    graph._ax.scatter(x,y,z, marker='o', label=name, color=newcolor)

def add_line_to_graph(graph, pt1,pt2, newcolor):
    ''' Draws a line from [x1,y1,z1] to [x2,y2,z2] of color newcolor.'''
    graph._ax.plot([pt1[0],pt2[0]], [pt1[1],pt2[1]], [pt1[2],pt2[2]], color=newcolor)

def add_fiducials_to_graph(graph, vagprops, color_fn = default_color):
    
    fid_list = vagprops._fiducial_points
    
    ''' Add all fiducials in the dictionary fid_list to the graph.  Color code using the function color_fn which takes a fiducial as an argument. '''
    for key in fid_list.iterkeys():
        fid = fid_list[key]
        add_scatterpoint_to_graph(graph, fid.name, fid.coords[COORDS.X], fid.coords[COORDS.Y], fid.coords[COORDS.Z], color_fn(fid, vagprops))
        
## BELOW FN IS CURRRENTLY UNUSED.
def add_columns_to_graph(graph, fid_list, color_fn = default_color):
    ''' Add all fiducials in the dictionary fid_list to the graph as columns from Z=-50.  Color code using the function color_fn which takes a fiducial as an argument. '''
    
    for key in fid_list.iterkeys():
        fid = fid_list[key]
        add_line_to_graph(graph, fid.coords, [fid.coords[COORDS.X], fid.coords[COORDS.Y], COLUMN_START], color_fn(fid))
        
def add_legend_to_graph(graph, minlabel, maxlabel, mincolor, maxcolor):
    ''' Create a legend for the graph, using matched tuples of labels and colors (e.g. labels[0] gets colors[0]'''
       
    # Create fake lines to fool the legend.    
    minline = plt.Line2D(range(10), range(10), linestyle='-', label=minlabel, color=mincolor)
    maxline = plt.Line2D(range(10), range(10), linestyle='-', label=maxlabel, color=maxcolor)
    
    graph._ax.legend([minline,maxline], [minlabel,maxlabel], numpoints=2, loc="lower right")
    
def set_graph_boundaries(graph, min_x, max_x, min_y, max_y, min_z, max_z):
    
    # HACK HACK HACK
    # Because 3D axis boundary setting doesn't work well yet, we'll just draw a scatterpoint in black at each corner to force the issue.
    add_scatterpoint_to_graph(graph,"FakePoint", min_x, min_y, min_z)
    add_scatterpoint_to_graph(graph,"FakePoint", min_x, max_y, min_z)
    
    add_scatterpoint_to_graph(graph,"FakePoint", min_x, min_y, max_z)
    add_scatterpoint_to_graph(graph,"FakePoint", min_x, max_y, max_z)

    add_scatterpoint_to_graph(graph,"FakePoint", max_x, min_y, min_z)
    add_scatterpoint_to_graph(graph,"FakePoint", max_x, max_y, min_z)
    
    add_scatterpoint_to_graph(graph,"FakePoint", max_x, min_y, max_z)
    add_scatterpoint_to_graph(graph,"FakePoint", max_x, max_y, max_z)

    