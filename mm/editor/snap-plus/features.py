__version__ = "$Id$"

# Features for GRiNS for G2, lite version

from compatibility import *
from FeatureSet import *
import sys

feature_set = [EXPORT_CMIF, EXPORT_SMIL2, EXPORT_QT, EXPORT_WMP,
               PLAYER_VIEW, STRUCTURE_VIEW,
               H_NIPPLES, H_VBANDWIDTH,
               ];

# These can be deprecated when I've multilated most of the source code.
#
version = 'Snap!'
compatibility = G2
compatibility_short = 'G2'
cmif = 0
lightweight = 1                       
editor = 1
level = 'lite'
license_features_needed = ('light', sys.platform)

grins_snap = 1