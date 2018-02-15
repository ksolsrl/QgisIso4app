# -*- coding: utf-8 -*-

#******************************************************************************
# ---------------------------------------------------------
# Call iso4app isodistance/isochrone service
#
# Copyright (C) 2008-2010 Maurizio Moscati (info@k-sol.it)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************
import os
import sys
import tempfile
import gettext
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import json
import requests
from iso4appService import iso4CallService


class iaAction(QAction):
 def __init__(self,name,iface,dlg):
  QAction.__init__(self,self.name(),iface.mainWindow())
  self.iface=iface
  self.dlg=dlg
  self.canvas=iface.mapCanvas()
  self.setWhatsThis(self.desc())
  self.setToolTip(self.desc())
  QObject.connect(self,SIGNAL("triggered()"),self.doit)
  return None
 def doit(self):
  self.tool=iaTool(self.iface,self.dlg)
  self.canvas.setMapTool(self.tool)
  return None
  
class iaTool(QgsMapTool):
 def __init__(self,iface,dlg):
  self.aQgsMapTool= QgsMapTool.__init__(self,iface.mapCanvas())
  self.iface=iface
  self.dlg=dlg
  self.canvas=iface.mapCanvas()
  return None

 def canvasReleaseEvent(self,e):
  QgsMessageLog.logMessage('canvasReleaseEvent start', 'iso4app')
  point = self.canvas.getCoordinateTransform().toMapPoint(e.pos().x(),e.pos().y())
  iso4CallService(self.iface,self.canvas,self.dlg,point)
  return None  
  
  