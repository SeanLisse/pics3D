# Hack to ensure we include BOTH this module and PICS3D_libraries in the python search path.

import sys
import os

sys.path.insert(0, sys.path[0] + os.sep + "..")

# print("PATH IS:" + str(sys.path))