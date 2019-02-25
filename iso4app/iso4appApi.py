from __future__ import absolute_import
import os
import sys
import tempfile
import gettext
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from .iso4appUtils import iaAction

class isoline(iaAction):
 def __init__(self,iface,dlg):
  iaAction.__init__(self,self.name(),iface,dlg)
  QgsMessageLog.logMessage('iaAction.__init__', 'iso4app')
  return None
 def name(self):
  return "Set parameters"
 def desc(self):
  return "Ask Isochrone/Isodostance"

class massiveIsoline(iaAction):
 def __init__(self,iface,dlg):
  iaAction.__init__(self,self.name(),iface,dlg)
  QgsMessageLog.logMessage('iaAction.__init__', 'iso4app')
  return None
 def name(self):
  return "Massive Isoline Calculation"
 def desc(self):
  return "Massive Isoline Calculation. For each point found in the selected layer an isoline will be calculated."
