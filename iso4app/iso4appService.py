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


class iso4CallService:
 def __init__(self,iface,canvas,dlg, pointTriggered):
  self.iface=iface
  self.dlg=dlg
  self.canvas=canvas
  self.pointTriggered=pointTriggered
  self.callIsoline()
  return None
 def callIsoline(self):
  QApplication.setOverrideCursor(Qt.WaitCursor)
  QgsMessageLog.logMessage('place_iso start', 'iso4app')
  point = self.canvas.getCoordinateTransform().toMapPoint(self.pointTriggered.x(),self.pointTriggered.y())
  pointc = self.canvas.getCoordinateTransform().toMapCoordinates(self.pointTriggered.x(),self.pointTriggered.y())
  QgsMessageLog.logMessage('place_iso end:'+repr(point.x())+' '+repr(point.y()), 'iso4app')
  
  QgsMessageLog.logMessage('canvasReleaseEvent start', 'iso4app')
  point = self.canvas.getCoordinateTransform().toMapPoint(self.pointTriggered.x(),self.pointTriggered.y())
  pointc = self.canvas.getCoordinateTransform().toMapCoordinates(self.pointTriggered.x(),self.pointTriggered.y())
  
  lng=self.pointTriggered.x()
  lat=self.pointTriggered.y()
  
  #crs = QgsCoordinateReferenceSystem()
  #fornisce il corrente epsgCode (sistema di coordinate) settato sulla canvas
  epsgCode=self.canvas.mapRenderer().destinationCrs().authid()
  QgsMessageLog.logMessage('canvasReleaseEvent epsgCode:'+epsgCode, 'iso4app')
  currentCoordSystem=QgsCoordinateReferenceSystem(epsgCode)
  gpsCoordSystem=QgsCoordinateReferenceSystem(4326)
  transformer = QgsCoordinateTransform(currentCoordSystem,gpsCoordSystem)
  pt = transformer.transform(self.pointTriggered)
   
  if self.dlg.checkBoxLogging.isChecked():
   QgsMessageLog.logMessage('canvasReleaseEvent lng:'+repr(lng)+' lat:'+repr(lat)+ ' pt.y:'+repr(pt.y())+ ' pt.x:'+repr(pt.x()), 'iso4app')
  
  #chiamata al servizio iso4app  rest
  aiKey=self.dlg.lineApiKey.text()
  speedLimit=self.dlg.lineSpeed.text()
  rbIsochrone=self.dlg.radioButtonIsochrone.isChecked()
  comboMeters=self.dlg.comboMeters.currentIndex()
  comboSeconds=self.dlg.comboMeters.currentIndex()
  comboApprox=self.dlg.comboApprox.currentIndex()
  comboConcavity=self.dlg.comboConcavity.currentIndex()
  comboBuffering=self.dlg.comboBuffering.currentIndex()
  comboSpeedType=self.dlg.comboSpeedType.currentIndex()
  comboTravelType=self.dlg.comboTravelType.currentIndex()
  
  checkBoxAllowBikeOnPedestrian=self.dlg.checkBoxAllowBikeOnPedestrian.isChecked()
  checkBoxAllowPedBikeOnTrunk=self.dlg.checkBoxAllowPedBikeOnTrunk.isChecked()
  checkBoxAvoidTolls=self.dlg.checkBoxAvoidTolls.isChecked()
  checkBoxRestrictedArea=self.dlg.checkBoxRestrictedArea.isChecked()
  checkBoxReduceQueueTime=self.dlg.checkBoxReduceQueueTime.isChecked()

  restUrl='http://www.iso4app.net/rest/1.3/isoline.json?licKey='+aiKey
  if rbIsochrone==True:
   restUrl=restUrl+'&type=isochrone'
   valueIsochrone = self.dlg.comboSeconds.currentText()
   minutes=int(valueIsochrone.split(' ')[0])
   seconds=minutes*60
   distances=repr(seconds) 
  else:
   restUrl=restUrl+'&type=isodistance'
   valueIsodistance = self.dlg.comboMeters.currentText()
   tmpValue=int(valueIsodistance.split(' ')[0])
   unit=valueIsodistance.split(' ')[1]
   if unit=='meters':
    meters=tmpValue
   if unit=='km':
    meters=tmpValue*1000
   distances=repr(meters) 
   
  restUrl=restUrl+'&value='+distances
  restUrl=restUrl+'&lat='+repr(pt.y())
  restUrl=restUrl+'&lng='+repr(pt.x())
 
  approxValue=self.dlg.comboApprox.currentText()
  approx=int(approxValue.split(' ')[0])
  restUrl=restUrl+'&approx='+ repr(approx)
  
  if comboTravelType==0:
   mobility='motor_vehicle'
  if comboTravelType==1:
   mobility='bicycle'
  if comboTravelType==2:
   mobility='pedestrian'
   
  restUrl=restUrl+'&mobility='+mobility

  if comboSpeedType==0:
   speedType='very_low'
  if comboSpeedType==1:
   speedType='low'
  if comboSpeedType==2:
   speedType='normal'
  if comboSpeedType==3:
   speedType='fast'
   
  restUrl=restUrl+'&speedType='+speedType

  if checkBoxReduceQueueTime:
   restUrl=restUrl+'&reduceQueue=true'
  if checkBoxAvoidTolls:
   restUrl=restUrl+'&avoidTolls=true'
  if checkBoxRestrictedArea==False:
   restUrl=restUrl+'&restrictedAreas=false'
  if checkBoxAllowPedBikeOnTrunk:
   restUrl=restUrl+'&pedestrianAnbBikeOnTrunk=true'
  if checkBoxAllowBikeOnPedestrian:
   restUrl=restUrl+'&bicycleOnPedestrian=true'
  if speedLimit!='':
   restUrl=restUrl+'&speedLimit='+speedLimit

  restUrl=restUrl+'&buffering='+repr(comboBuffering)
  restUrl=restUrl+'&concavity='+repr(comboConcavity)
  restUrl=restUrl+'&caller=Qgis'
  
  if self.dlg.checkBoxLogging.isChecked():
   QgsMessageLog.logMessage('canvasReleaseEvent restUrl:'+restUrl, 'iso4app')
  
  try:
   response = requests.get(restUrl)
   if self.dlg.checkBoxLogging.isChecked():
    QgsMessageLog.logMessage('canvasReleaseEvent response.text:'+response.text, 'iso4app')

   root = json.loads(response.text);
   coordinates=root['polygons'][0]['exterior']
   wayName=root['startPoint']['way']
   startPoint=root['startPoint']['coordinates']
   
   aQgsPoint=QgsPoint(float(startPoint.split(' ')[1]),float(startPoint.split(' ')[0]))

   isoType=root['type']
   distance=root['value']
   unit='seconds'
   if isoType=='ISODISTANCE':
    unit='meters'
   points =[]
   transformerReverse = QgsCoordinateTransform(gpsCoordSystem,currentCoordSystem)
   for isoCoord in coordinates:
    pointA=QgsPoint(isoCoord[0],isoCoord[1])
    ptReverse = transformerReverse.transform(pointA)
    points.append(ptReverse)

   aQgsPointReverse = transformerReverse.transform(aQgsPoint)	
   
   polygon = QgsGeometry.fromPolygon([points])  
   polyB = QgsFeature()
   polyB.setGeometry(polygon)
   
   #creazione layer virtual
   if wayName=='':
    wayName='way unknow'
   layernamePoly=isoType+': ' +repr(distance)+' '+unit+'. Coord: '+startPoint
   layernamePin='PIN: '+' Coord: '+startPoint+' ('+wayName+')'   
   vlyrPoly = QgsVectorLayer("Polygon?crs=EPSG:3857", layernamePoly, "memory")
   vlyrPin =  QgsVectorLayer("Point?crs=EPSG:3857&field=id:integer&field=description:string(120)&field=x:double&field=y:double&index=yes",layernamePin,"memory")

   #crs = vlyr.crs()
   #crs.createFromId(3857)
   try:
    self.canvas.mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem(3857))
   except:
    self.canvas.mapRenderer().setDestinationCrs(QgsCoordinateReferenceSystem(3857))
   
   vlyrPoly.setCrs(QgsCoordinateReferenceSystem(3857))
   vlyrPin.setCrs(QgsCoordinateReferenceSystem(3857))
   dprovPin = vlyrPin.dataProvider()
   dprovPoly = vlyrPoly.dataProvider()
   
   fc = int(dprovPin.featureCount())
   QgsMessageLog.logMessage('canvasReleaseEvent fc:'+repr(fc), 'iso4app')
   feat = QgsFeature()
   feat.setGeometry(QgsGeometry.fromPoint(aQgsPointReverse))
   feat.setAttributes([fc,  'Coord: '+startPoint+' ('+wayName+')', aQgsPointReverse.x(), aQgsPointReverse.y()])
   dprovPin.addFeatures([feat])
   dprovPoly.addFeatures([polyB])
   
   dprovPoly.updateExtents()
   dprovPin.updateExtents()
   #add layer      
   #QgsMapLayerRegistry.instance().addMapLayers([dprovPoly])  
   vlyrPoly.setLayerTransparency(50)
   QgsMapLayerRegistry.instance().addMapLayers([vlyrPin,vlyrPoly])  
   #QgsMapLayerRegistry.instance().addMapLayers([vlyrPin])  
   self.canvas.refresh()
  except ValueError:
   self.iface.messageBar().pushMessage("Iso4App", response.text, level=QgsMessageBar.CRITICAL)
   QgsMessageLog.logMessage('canvasReleaseEvent error:'+repr(ValueError), 'iso4app')
  
  QApplication.restoreOverrideCursor()
  QgsMessageLog.logMessage('canvasReleaseEvent end', 'iso4app')
  return None
  
