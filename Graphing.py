import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

DEFAULT_COLOR=[0.5,0.5,0.75]

# Figure and Axes objects to contain our plots
fig = plt.figure()
ax = fig.add_subplot('111',projection='3d')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

def default_color(fiducial): 
    ''' Default coloration function. Clone this and alter it to customize your coloration when graphing. '''
    return DEFAULT_COLOR

def show_graph():
    ''' Display the graph.  Call this after adding all scatterpoints to it. '''
    plt.show()

def add_scatterpoint(name, x, y, z, newcolor):
    ''' Add a new scatterpoint to the graph.  Name is currently ignored. '''
    ax.scatter(x,y,z, marker='o', label=name, color=newcolor)

def add_fiducials_to_graph(fid_list, color_fn = default_color):
    ''' Add all fiducials in the dictionary fid_list to the graph.  Color code using the function color_fn which takes a fiducial as an argument. '''
    for key in fid_list.iterkeys():
        fid = fid_list[key]
        add_scatterpoint(fid.name, fid.x, fid.y, fid.z, color_fn(fid))
