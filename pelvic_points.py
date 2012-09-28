# This code is designed to load in a set of 
from numpy import *
import scipy as sci
import os

from collections import OrderedDict

NO_DEBUG=0
BASIC_DEBUG=1
DETAILED_DEBUG=2

debug_level=NO_DEBUG
# debug_level=BASIC_DEBUG
# debug_level=DETAILED_DEBUG

def debugprint(info, level=1):
	if(level <= debug_level): 
		print(info)

# Create a dictionary to contain our fidicual points.  Each point will be indexed by name, and will be a 3-tuple of X,Y,Z values.
fiducial_points=OrderedDict()

FIDUCIAL_EXTENSIONS=['.acsv']

class fiducial:
	''' Represents a Slicer fiducial point, with name, x, y, and z values. '''
	def __init__(self,_name,_x,_y,_z): 
		self.name = _name
		self.x = _x
		self.y = _y
		self.z = _z 
		self.vec = zeros((3))

		self.vec[0] = float(_x)
		self.vec[1] = float(_y)
		self.vec[2] = float(_z)

		debugprint("String _x:" + str(self.x), DETAILED_DEBUG)
		debugprint("float(_x):" + str(float(self.x)), DETAILED_DEBUG)



def load_fiducial_from_dir(dirname = os.curdir):


	if not(os.path.isdir(dirname)):
		if os.path.isfile(dirname):
			return load_fiducial_from_file(dirname)
		else:
			raise ValueError("Error at line " + __line__ + ": " + dirname + " is not a valid directory or file.")
	
	# Walk the directory tree starting at dirname.  Find all the files with '.ascv' in their name.
	for root, dirs, files in os.walk(dirname):
		for name in files:
			is_fiducial_file=False
			
			for pattern in FIDUCIAL_EXTENSIONS:
				if (pattern in name):
					is_fiducial_file=True
					debugprint("Found file " + name + " with pattern " + pattern, BASIC_DEBUG)

			if (is_fiducial_file):					
				new_fid = load_fiducial_from_file(os.path.join(root,name))
				if (new_fid != None):
					fiducial_points[new_fid.name] = new_fid
				else: 
					debugprint("Invalid return from attempting to load from file " + os.path.join(root,name), BASIC_DEBUG)
			else: 
				debugprint("Ignoring file " + name + " as it does not fit any of our patterns.", BASIC_DEBUG)
				

def load_fiducial_from_file(filename):
	if not(os.path.isfile(filename)): 
		raise ValueError("Error at line " + __line__ + ": " + filename + " is not a valid file name.")

	debugprint("Loading file " + filename, DETAILED_DEBUG)	

	with open(filename) as openfile:
		debugprint("Reading file " + openfile.name, DETAILED_DEBUG)	

		name_set=False
		x_set=False		
		y_set=False
		z_set=False

		for line in openfile:
			if ('# Name = ' in line):
				name=line.rstrip()[8:]
				name_set=True
			if ('point|' in line):
				split_line=line.split('|')
				if (len(split_line) <> 6):
					debugprint("Invalid coordinate line in file " + filename + ".",BASIC_DEBUG)
					return(None)			

				word_count=0
				for word in split_line:
					if word_count==0: pass # This should just be the 'point' label
					if word_count==1: 
						x=float(word)
						x_set=True
					if word_count==2: 
						y=float(word)
						y_set=True
					if word_count==3: 
						z=float(word)
						z_set=True

					word_count+=1

		if not(name_set and x_set and y_set and z_set):
			debugprint("Unknown Error attempting to set coordinates from file " + filename + ".",BASIC_DEBUG)
			return(None)
		else:			
			return fiducial(name,x,y,z)			

if __name__ == '__main__':
	debugprint('Now starting pelvic points program',BASIC_DEBUG)
	load_fiducial_from_dir()

	for key in fiducial_points.iterkeys():
		fid = fiducial_points[key]
		print("Found point " + fid.name + " at x:" + str(fid.x) + ", y:" + str(fid.y) + ", z:" + str(fid.z))
		debugprint(fid.vec, DETAILED_DEBUG)
				
	debugprint('Now leaving pelvic points program',BASIC_DEBUG)

