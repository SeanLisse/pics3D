#! /usr/bin/env python
# Author: Sean Lisse
# This code is designed to load in a set of fiducials from a directory tree

from Utilities import debugprint
from Utilities import debug_levels
# import VectorMath

from Fiducials import fiducial_points
from Fiducials import fiducial

from os import path
from os import walk
from os import curdir

FIDUCIAL_EXTENSIONS=['.acsv']
		
def load_fiducials_from_dir(dirname = curdir):
	if not(path.isdir(dirname)):
		if path.isfile(dirname):
			return load_fiducial_from_file(dirname)
		else:
			raise ValueError("Error: " + dirname + " is not a valid directory or file.")
	
	# Walk the directory tree starting at dirname.  Find all the files with '.ascv' in their name.
	for root, dirs, files in walk(dirname):
		for name in files:
			is_fiducial_file=False
			
			for pattern in FIDUCIAL_EXTENSIONS:
				if (pattern in name):
					is_fiducial_file=True
					debugprint("Found file " + name + " with pattern " + pattern, debug_levels.BASIC_DEBUG)

			if (is_fiducial_file):					
				new_fid = load_fiducial_from_file(path.join(root,name))
				if (new_fid != None):
					fiducial_points[new_fid.name] = new_fid
				else: 
					debugprint("Invalid return from attempting to load from file " + path.join(root,name), debug_levels.ERRORS)
			else: 
				debugprint("Ignoring file " + name + " as it does not fit any of our patterns.", debug_levels.BASIC_DEBUG)
				

def load_fiducial_from_file(filename):
	''' Load a fiducial point from a file (usually .acsv format) '''
	
	if not(path.isfile(filename)): 
		raise ValueError("Error: " + filename + " is not a valid file name.")

	debugprint("Loading file " + filename, debug_levels.DETAILED_DEBUG)	

	with open(filename) as openfile:
		debugprint("Reading file " + openfile.name, debug_levels.DETAILED_DEBUG)	

		name_set=False
		x_set=False		
		y_set=False
		z_set=False

		for line in openfile:
			if ('# Name = ' in line):
				name=line.rstrip()[8:]
				name=name.lstrip()
				name_set=True
			if ('point|' in line):
				split_line=line.split('|')
				if (len(split_line) <> 6):
					debugprint("Invalid coordinate line in file " + filename + ".",debug_levels.ERRORS)
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
			debugprint("Unknown Error attempting to set coordinates from file " + filename + ".",debug_levels.ERRORS)
			return(None)
		else:			
			return fiducial(name,x,y,z)			

#####################
### DEFAULT MAIN PROC
#####################

if __name__ == '__main__':
	
	from Fiducials import print_all_fiducials
	
	debugprint('Now starting directory sweep for fiducials',debug_levels.BASIC_DEBUG)
	load_fiducials_from_dir()

	print_all_fiducials()
				
	debugprint('Now leaving directory sweep.',debug_levels.BASIC_DEBUG)

