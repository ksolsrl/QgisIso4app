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
from builtins import object
import os
import sys
import tempfile
import gettext
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
import json
import requests


class iso4CallService(object):
 def __init__(self,iface,canvas,dlg,pointTriggered,epsgCodeInput,epsgCodeCanvas,layerXPoint,layerXPolygon,attributeName4Layer,attributeValue4Layer,overWrittenDistance):
  self.iface=iface
  self.dlg=dlg
  self.attributeName4Layer=attributeName4Layer
  self.attributeValue4Layer=attributeValue4Layer
  self.epsgCode=epsgCodeInput
  self.epsgCodeCanvas=epsgCodeCanvas
  self.canvas=canvas
  self.pointTriggered=pointTriggered
  self.layerXPoint=layerXPoint
  self.layerXPolygon=layerXPolygon
  self.rc=-1
  self.rcMessageCritical=''
  self.layernamePoly=''
  self.layernamePin=''
  self.overWrittenDistance=overWrittenDistance
  #aggiungere i parametri per lo street network TODO, poi gestire la chiamata con parametro visualizationType=street_network_no_range e gestire output
  self.callIsoline()
  return None
 def __str__(self):
  return self.rc
  
 def callIsoline(self):
  QgsMessageLog.logMessage('callIsoline place_iso start', 'iso4app')
  point = self.canvas.getCoordinateTransform().toMapPoint(self.pointTriggered.x(),self.pointTriggered.y())
  pointc = self.canvas.getCoordinateTransform().toMapCoordinates(self.pointTriggered.x(),self.pointTriggered.y())
    
  QgsMessageLog.logMessage('callIsoline start', 'iso4app')
  point = self.canvas.getCoordinateTransform().toMapPoint(self.pointTriggered.x(),self.pointTriggered.y())
  pointc = self.canvas.getCoordinateTransform().toMapCoordinates(self.pointTriggered.x(),self.pointTriggered.y())
  
  lng=self.pointTriggered.x()
  lat=self.pointTriggered.y()
  
  #crs = QgsCoordinateReferenceSystem()
  #fornisce il corrente epsgCode (sistema di coordinate) settato sulla canvas
  #epsgCodeCanvas=self.canvas.mapRenderer().destinationCrs().authid()
  
  QgsMessageLog.logMessage('callIsoline epsgCode:'+self.epsgCode, 'iso4app')
  currentCoordSystemInputPoint=QgsCoordinateReferenceSystem(self.epsgCode)
  gpsCoordSystemIso4App=QgsCoordinateReferenceSystem("EPSG:4326")
  transformer = QgsCoordinateTransform(currentCoordSystemInputPoint,gpsCoordSystemIso4App,QgsProject.instance())
  pt = transformer.transform(self.pointTriggered)
   
  if self.dlg.checkBoxLogging.isChecked():
   QgsMessageLog.logMessage('callIsoline lng:'+repr(lng)+' lat:'+repr(lat)+ ' pt.y:'+repr(pt.y())+ ' pt.x:'+repr(pt.x()), 'iso4app')
  
  #chiamata al servizio iso4app  rest
  aiKey=self.dlg.lineApiKey.text()
  speedLimit=self.dlg.lineSpeed.text()
  rbIsodistanceAir=self.dlg.radioButtonIsodistanceAir.isChecked()
  rbIsochrone=self.dlg.radioButtonIsochrone.isChecked()
  rbPolygon=self.dlg.radioButtonPolygon.isChecked()
  rbStreetNetwork=self.dlg.radioButtonStreetNetwork.isChecked()
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
  checkBoxFastestRoute=self.dlg.checkBoxFastestRoute.isChecked()
  checkBoxPopulation=self.dlg.chkPopulation.isChecked()

  visualizationType=""

  if rbIsodistanceAir==True:
   restUrl='http://www.iso4app.com/rest/1.3/airDistance.json?licKey='+aiKey
   distances=getMeterDistance(self)
   restUrl=restUrl+'&value='+distances   
   restUrl=restUrl+'&lat='+repr(pt.y())
   restUrl=restUrl+'&lng='+repr(pt.x())
   mobility='air'
  else:
   restUrl='http://www.iso4app.com/rest/1.3/isoline.json?licKey='+aiKey

   if rbIsochrone==True:
    restUrl=restUrl+'&type=isochrone'
    valueIsochrone = self.dlg.comboSeconds.currentText()
    minutes=int(valueIsochrone.split(' ')[0])
    seconds=minutes*60
    if self.overWrittenDistance is not None:
     seconds=self.overWrittenDistance*60
    distances=repr(seconds) 
   else:
    restUrl=restUrl+'&type=isodistance'
    distances=getMeterDistance(self)
   
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
  
   if checkBoxFastestRoute:
    restUrl=restUrl+'&fastestRouting=true'
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
  
   if rbPolygon:
    restUrl=restUrl+'&visualizationType=polygon'
    if checkBoxPopulation:
     restUrl=restUrl+'&addPopIfAvailable=true'
   if rbStreetNetwork==True:
    restUrl=restUrl+'&visualizationType=street_network_no_range'
  
  
  if self.dlg.checkBoxLogging.isChecked():
   QgsMessageLog.logMessage('callIsoline restUrl:'+restUrl, 'iso4app')
  
  try:
   response = requests.get(restUrl)
   if self.dlg.checkBoxLogging.isChecked():
    QgsMessageLog.logMessage('callIsoline response.text:'+response.text, 'iso4app')

   root = json.loads(response.text);

   wayName=root['startPoint']['way']
   startPoint=root['startPoint']['coordinates']
   startPointApprox=root['startPoint']['approximation']
   
   #{"exterior":[[12.4742976,41.9861831],[12.4769622,41.9865956],
   if rbPolygon==True:
    coordinates=root['polygons'][0]['exterior']
   
   #nel caso di street network senza range prendo solo il primo range che contiene parts che è un array di edges
   #"streetNetwork":{"ranges":[{"info":"1 600","color":"#404040","parts":[{"edges":[[12.512538,41.9498362],[12.5115384,41.9492004],[12.51159,41.949029]]},{"edges":[[12.5146503
   if rbStreetNetwork==True:
    coordinates=root['streetNetwork']['ranges'][0]['parts']
   
   
   aQgsPoint=QgsPoint(float(startPoint.split(' ')[1]),float(startPoint.split(' ')[0]))
   
   isoType=root['type']
   distance=root['value']
   unit='seconds'
   if isoType=='ISODISTANCE':
    unit='meters'

   if isoType=='ISODISTANCEBYAIR':
    unit='meters'

   epsgCodeCanvasNumber=int(self.epsgCodeCanvas.split(':')[1])
   if self.dlg.checkBoxLogging.isChecked():
    QgsMessageLog.logMessage('callIsoline epsgCodeCanvas:'+self.epsgCodeCanvas, 'iso4app')
    QgsMessageLog.logMessage('callIsoline epsgCodeCanvasNumber:'+repr(epsgCodeCanvasNumber), 'iso4app')

   currentCoordSystemOutputCanvas=QgsCoordinateReferenceSystem(self.epsgCodeCanvas)
   transformerReverse = QgsCoordinateTransform(gpsCoordSystemIso4App,currentCoordSystemOutputCanvas,QgsProject.instance())
   
   aQgsPointReverse = transformerReverse.transform(float(startPoint.split(' ')[1]),float(startPoint.split(' ')[0]))
   polyB = QgsFeature()

   
   popValue=''   
   if rbPolygon==True:
    visualizationType="(Polygon)"
    points =[]
    for isoCoord in coordinates:
     pointA=QgsPoint(isoCoord[0],isoCoord[1])
     ptReverse = transformerReverse.transform(isoCoord[0],isoCoord[1])
     ptReverseXY=QgsPointXY(ptReverse)
     points.append(ptReverseXY)

    polygon = QgsGeometry.fromPolygonXY([points])
    polyB.setGeometry(polygon)
    #nel ramo polygon verifico anche se è stata chiesta la popolazione
    if checkBoxPopulation:
     if root['indicator'] is not None:
      popValue=int(root['indicator']['v'])
     QgsMessageLog.logMessage('callIsoline indicator pop:'+repr(popValue), 'iso4app')
   #finito ramo Polygon
   
   if rbStreetNetwork==True:
    visualizationType="(Street Network)"
    streets =[]
    for edges in coordinates:
     points =[]
     
     if self.dlg.checkBoxLogging.isChecked():
      #{'edges': [[12.512538, 41.9498362], [12.5125736, 41.9498313],
      QgsMessageLog.logMessage('callIsoline rbStreetNetwork:'+repr(edges), 'iso4app')

     edgesCoordinates=edges['edges']
     for isoCoord in edgesCoordinates:
      if self.dlg.checkBoxLogging.isChecked():
       QgsMessageLog.logMessage('callIsoline isoCoord:'+repr(isoCoord), 'iso4app')
      pointA=QgsPoint(isoCoord[0],isoCoord[1])
      ptReverse = transformerReverse.transform(isoCoord[0],isoCoord[1])
      ptReverseXY=QgsPointXY(ptReverse)
      points.append(ptReverseXY)
     QgsMessageLog.logMessage('callIsoline prima di QgsLineString:', 'iso4app')
     streets.append(points)
    
    streetsGeom= QgsGeometry.fromMultiPolylineXY(streets)
    polyB.setGeometry(streetsGeom)
   #finito ramo street network
   
   #creazione layer virtual
   if wayName=='':
    wayName='way unknow'
   
   self.layernamePoly=isoType+visualizationType+': ' +repr(distance)+' '+unit+'. Coord: '+startPoint
   self.layernamePin='PIN: '+' Coord: '+startPoint+' ('+wayName+')'

   try:
    self.canvas.mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem(epsgCodeCanvasNumber))
   except:
    self.canvas.mapRenderer().setDestinationCrs(QgsCoordinateReferenceSystem(epsgCodeCanvasNumber))
   
   dprovPoly=self.layerXPolygon.dataProvider()
   dprovPoly.addFeatures([polyB])
   
   if self.dlg.checkBoxLogging.isChecked():
    QgsMessageLog.logMessage('callIsoline addFeatures:'+repr(polyB.geometry().asJson()), 'iso4app')
   

   #aggiunta attributi comunque aggiungo quelli fissi
   self.layerXPolygon.startEditing() 
   dprovPoly.addAttributes([ QgsField("IsolineType", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineDistance", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineDistanceUnit", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineMobility", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineStartPointLat", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineStartPointLng", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineInputStartPointLat", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineInputStartPointLng", QVariant.String)])
   dprovPoly.addAttributes([ QgsField("IsolineStartPointApproximation", QVariant.String)])
   #controllo aggiunta attributi del layer origine nel caso massivo
   if self.attributeName4Layer!='':
    dprovPoly.addAttributes([ QgsField(self.attributeName4Layer, QVariant.String)])
   dprovPoly.addAttributes([ QgsField("VisualizationType", QVariant.String)])   
   dprovPoly.addAttributes([ QgsField("Population", QVariant.String)])
     
    
   self.layerXPolygon.updateFields()
   lastFeature=None
   QgsMessageLog.logMessage('callIsoline lastFeature=None:', 'iso4app')
   for feature in self.layerXPolygon.getFeatures():
    QgsMessageLog.logMessage('callIsoline for feature:', 'iso4app')
    lastFeature=feature
   if lastFeature is not None:
    QgsMessageLog.logMessage('callIsoline featureIdCycle:'+repr(lastFeature.id()), 'iso4app')
    attrIsolineType = 'IsolineType'
    feature[attrIsolineType] = 1
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineType] : isoType}})
    attrIsolineDistance = 'IsolineDistance'
    feature[attrIsolineDistance] = 2
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineDistance] : distances}})
    attrIsolineUnit = 'IsolineDistanceUnit'
    feature[attrIsolineUnit] = 3
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineUnit] : unit}})
    attrIsolineMobility = 'IsolineMobility'
    feature[attrIsolineMobility] = 4
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineMobility] : mobility}})
    attrIsolineLat = 'IsolineStartPointLat'
    feature[attrIsolineLat] = 5
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineLat] : aQgsPoint.y()}})
    attrIsolineLng = 'IsolineStartPointLng'
    feature[attrIsolineLng] = 6
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsolineLng] : aQgsPoint.x()}})
    attrIsoline = 'IsolineInputStartPointLat'
    feature[attrIsoline] = 7
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsoline] : pt.y()}})
    attrIsoline = 'IsolineInputStartPointLng'
    feature[attrIsoline] = 8
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsoline] : pt.x()}})
    attrIsoline = 'IsolineStartPointApproximation'
    feature[attrIsoline] = 9
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsoline] : startPointApprox}})
    if self.attributeName4Layer!='':
     feature[self.attributeName4Layer] = 10
     dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[self.attributeName4Layer] : self.attributeValue4Layer}})
    attrIsoline = 'VisualizationType'
    feature[attrIsoline] = 11
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsoline] : visualizationType}})
    attrIsoline = 'Population'
    feature[attrIsoline] = 12
    dprovPoly.changeAttributeValues({lastFeature.id() : {dprovPoly.fieldNameMap()[attrIsoline] : popValue}})
         

   self.layerXPolygon.commitChanges() 
   dprovPoly.updateExtents()
   
   #aggiunta punto a layer se diverso da null
   if self.layerXPoint is not None:
    dprovPin=self.layerXPoint.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPointXY(aQgsPointReverse))
    dprovPin.addFeatures([feat])

    #QgsMessageLog.logMessage('callIsoline addFeatures Point:'+repr(feat.geometry().asJson()), 'iso4app')
    dprovPin.updateExtents()
   
   self.rc=0

  except ValueError:
   self.iface.messageBar().pushMessage("Iso4App", response.text, level=Qgis.Critical)
   QgsMessageLog.logMessage('canvasReleaseEvent error:'+response.text, 'iso4app')
   QgsMessageLog.logMessage('canvasReleaseEvent error:'+repr(ValueError), 'iso4app')
   if len(response.text)>0:
    if "(370) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(160) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(170) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(180) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(190) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(191) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(192) (1032)" in response.text: 
     self.rcMessageCritical=response.text
    if "(195) (1032)" in response.text: 
     self.rcMessageCritical=response.text

  
  QgsMessageLog.logMessage('callIsoline end', 'iso4app')

def getMeterDistance(self):
  valueIsodistance = self.dlg.comboMeters.currentText()
  tmpValue=int(valueIsodistance.split(' ')[0])
  unit=valueIsodistance.split(' ')[1]
  if unit=='meters':
   meters=tmpValue
  if unit=='km':
   meters=tmpValue*1000
  if self.overWrittenDistance is not None:
   meters=self.overWrittenDistance

  distances=repr(meters) 
  return distances
