# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iso4app
                                 A QGIS plugin
 iso4app
                              -------------------
        begin                : 2018-02-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Maurizio Moscati
        email                : info@k-sol.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from time import sleep
from builtins import str
from builtins import range
from builtins import object
import os
import sys
import tempfile
import gettext
from . import resources
import datetime
from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction,QMenu,QApplication,QTableWidget,QTableWidgetItem,QProgressBar,QProgressDialog
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from .iso4app_dialog import iso4appDialog
from .iso4appApi import isoline
from .iso4appApi import massiveIsoline
from .iso4appService import iso4CallService
from . import iso4app_dialog
from . import iso4app_massive_dialog


class MainPlugin(object):
 def __init__(self, iface):
  self.iface = iface
  self.dlg=iso4app_dialog.iso4appDialog()
  self.massiveDlg=iso4app_massive_dialog.iso4appMassiveDialog()
  self.toolbar = self.iface.addToolBar(u'wfsOutputExtension')
  self.canvas=iface.mapCanvas()
  self.isoTool = QgsMapToolEmitPoint(self.canvas)
  self.selectedLayer=None  
  self.isoDescr=''
  self.stopRunning=0
  self.timeStampLastMassiveRunning=datetime.datetime.now() 

 def name(self):
  return "Iso4App"
 def initGui(self):
  QgsMessageLog.logMessage('initGui start', 'iso4app')  
  self.isoline = isoline(self.iface,self.dlg)
  self.massiveIsoline = massiveIsoline(self.iface,self.massiveDlg)
  
  self.requestAK = QAction("Request Api Key",self.iface.mainWindow())
  self.requestAK.triggered.connect(self.clickRequestApiKey)

  icon_path = ':/plugins/iso4app/icon.png'
  self.action = QAction(QIcon(":/plugins/iso4app/icon.png"), "Iso4App", self.iface.mainWindow())
  self.action.triggered.connect(self.run)
  result = self.isoTool.canvasClicked.connect(self.place_iso)
  self.iface.addToolBarIcon(self.action)

  #connessione menù alla azione isoline
  self.menu=QMenu("Iso4App")
  self.menu.addActions([self.isoline])
  self.menu.addActions([self.massiveIsoline])
  menuBar = self.iface.mainWindow().menuBar()
  menuBar.addMenu(self.menu)
  self.menu.addSeparator()
  self.menu.addAction(self.requestAK)
  
  self.isoline.triggered.connect(self.clickParameters)
  self.massiveIsoline.triggered.connect(self.clickMassiveIsolines)
  
  self.dlg.radioButtonIsochrone.toggled.connect(self.eventRbIsocrone)
  self.dlg.radioButtonIsodistance.toggled.connect(self.eventRbIsodistance)
  self.dlg.comboTravelType.currentIndexChanged.connect(self.eventCbTravelType)
  self.dlg.comboSpeedType.currentIndexChanged.connect(self.eventCbSpeedType)
  self.dlg.button_box.clicked.connect(self.eventOkButton)
  self.dlg.radioButtonPolygon.toggled.connect(self.eventRbPolygon)
  self.dlg.radioButtonStreetNetwork.toggled.connect(self.eventRbStreetNetwork)
  self.dlg.lnkAvailableCountries.clicked.connect(self.eventLnkAvailableCountries)
    
  #MASSIVE
  self.massiveDlg.pushButtonClose.clicked.connect(self.eventButtonCloseMassive)
  self.massiveDlg.comboBoxLayers.currentIndexChanged.connect(self.eventCbBoxLayers)
  self.massiveDlg.comboBoxAttributeAsDistance.currentIndexChanged.connect(self.eventCbBoxAttributesAsDistance)
  self.massiveDlg.comboBoxAttributes.currentIndexChanged.connect(self.eventCbBoxAttributes)
  self.massiveDlg.pushButtonCalculate.pressed.connect(self.disableButtonGroup)
  self.massiveDlg.pushButtonCalculate.released.connect(self.calculate_massive_isolines)
  
  #
  self.dlg.comboTravelType.addItem('Motor vehicle')
  self.dlg.comboTravelType.addItem('Bicycle')
  self.dlg.comboTravelType.addItem('Pedestrian')
  #
  self.dlg.comboApprox.addItem('50 m')
  self.dlg.comboApprox.addItem('100 m')
  self.dlg.comboApprox.addItem('200 m')
  self.dlg.comboApprox.addItem('300 m')
  self.dlg.comboApprox.addItem('400 m')
  self.dlg.comboApprox.addItem('500 m')
  self.dlg.comboApprox.addItem('600 m')
  self.dlg.comboApprox.addItem('700 m')
  self.dlg.comboApprox.addItem('800 m')
  self.dlg.comboApprox.addItem('900 m')
  self.dlg.comboApprox.addItem('1000 m')
  #
  self.dlg.comboConcavity.addItem('0 (convex)')
  self.dlg.comboConcavity.addItem('1 ')
  self.dlg.comboConcavity.addItem('2 ')
  self.dlg.comboConcavity.addItem('3 ')
  self.dlg.comboConcavity.addItem('4 ')
  self.dlg.comboConcavity.addItem('5 ')
  self.dlg.comboConcavity.addItem('6 ')
  self.dlg.comboConcavity.addItem('7 ')
  self.dlg.comboConcavity.addItem('8 ')
  
  self.dlg.comboBuffering.addItem('0')
  self.dlg.comboBuffering.addItem('1')
  self.dlg.comboBuffering.addItem('2')
  self.dlg.comboBuffering.addItem('3')
  self.dlg.comboBuffering.addItem('4')
  self.dlg.comboBuffering.addItem('5')
  self.dlg.comboBuffering.addItem('6')
  self.dlg.comboBuffering.addItem('7')
  self.dlg.comboBuffering.addItem('8')
  
  self.dlg.comboSpeedType.addItem('Very low')  
  self.dlg.comboSpeedType.addItem('Low')  
  self.dlg.comboSpeedType.addItem('Normal')  
  self.dlg.comboSpeedType.addItem('Fast')  
  
  self.dlg.comboSeconds.addItem(repr(1)+' min')
  for min in range(2,301):
   self.dlg.comboSeconds.addItem(repr(min)+' mins') 
   
  for meters in range(50,1000):
   remM=meters % 10
   if remM == 0:
    self.dlg.comboMeters.addItem(repr(meters)+' meters') 

  for km in range(1,51):
   self.dlg.comboMeters.addItem(repr(km)+' km') 
  
  for km in range(55,101):
   remK=km % 5
   if remK == 0:
    self.dlg.comboMeters.addItem(repr(km)+' km') 
  
  for km in range(101,501):
   remK=km % 25
   if remK == 0:
    self.dlg.comboMeters.addItem(repr(km)+' km') 
  
  s = QSettings()
  apiKey=s.value("iso4app/apy-key", "87B7FB96-83DA-4FBD-A312-7822B96BB143")
  if apiKey=='':
   apiKey='87B7FB96-83DA-4FBD-A312-7822B96BB143'
  self.dlg.lineApiKey.setText(apiKey)
  rbIsochrone=s.value("iso4app/rbIsochrone", True)
  if rbIsochrone:
   self.dlg.radioButtonIsochrone.setChecked(True)
   self.dlg.radioButtonIsodistance.setChecked(False)
   self.dlg.comboMeters.setEnabled(False)
   self.dlg.comboSeconds.setEnabled(True)
  else:
   self.dlg.radioButtonIsochrone.setChecked(False)
   self.dlg.radioButtonIsodistance.setChecked(True)
   self.dlg.comboMeters.setEnabled(True)
   self.dlg.comboSeconds.setEnabled(False)
  
  rbPolygon=s.value("iso4app/rbPolygon", True)
  
  if rbPolygon:
   self.dlg.radioButtonPolygon.setChecked(True)
   self.dlg.radioButtonStreetNetwork.setChecked(False)
   self.dlg.chkPopulation.setEnabled(True)
  else:
   self.dlg.radioButtonStreetNetwork.setChecked(True)
   self.dlg.radioButtonPolygon.setChecked(False)
   self.dlg.chkPopulation.setEnabled(False)
  
  
  comboMeters=s.value("iso4app/comboMeters", 104)
  comboSeconds=s.value("iso4app/comboSeconds", 9)
  comboApprox=s.value("iso4app/comboApprox", 2)
  comboConcavity=s.value("iso4app/comboConcavity", 5)
  comboBuffering=s.value("iso4app/comboBuffering", 0)
  comboSpeedType=s.value("iso4app/comboSpeedType", 2)
  comboTravelType=s.value("iso4app/comboTravelType", 0)

  self.dlg.comboMeters.setCurrentIndex(int(comboMeters))
  self.dlg.comboSeconds.setCurrentIndex(int(comboSeconds))
  self.dlg.comboApprox.setCurrentIndex(int(comboApprox))
  self.dlg.comboConcavity.setCurrentIndex(int(comboConcavity))
  self.dlg.comboBuffering.setCurrentIndex(int(comboBuffering))
  self.dlg.comboSpeedType.setCurrentIndex(int(comboSpeedType))
  self.dlg.comboTravelType.setCurrentIndex(int(comboTravelType))
  
  checkBoxAllowBikeOnPedestrian=s.value("iso4app/checkBoxAllowBikeOnPedestrian", True)
  if checkBoxAllowBikeOnPedestrian:
   self.dlg.checkBoxAllowBikeOnPedestrian.setChecked(True)
  else:
   self.dlg.checkBoxAllowBikeOnPedestrian.setChecked(False)

  checkBoxAllowPedBikeOnTrunk=s.value("iso4app/checkBoxAllowPedBikeOnTrunk", True)
  if checkBoxAllowPedBikeOnTrunk:
   self.dlg.checkBoxAllowPedBikeOnTrunk.setChecked(True)
  else:
   self.dlg.checkBoxAllowPedBikeOnTrunk.setChecked(False)

  checkBoxAvoidTolls=s.value("iso4app/checkBoxAvoidTolls", True)
  if checkBoxAvoidTolls:
   self.dlg.checkBoxAvoidTolls.setChecked(True)
  else:
   self.dlg.checkBoxAvoidTolls.setChecked(False)

  checkBoxRestrictedArea=s.value("iso4app/checkBoxRestrictedArea", True)
  if checkBoxRestrictedArea:
   self.dlg.checkBoxRestrictedArea.setChecked(True)
  else:
   self.dlg.checkBoxRestrictedArea.setChecked(False)

  checkBoxReduceQueueTime=s.value("iso4app/checkBoxReduceQueueTime", True)
  if checkBoxReduceQueueTime:
   self.dlg.checkBoxReduceQueueTime.setChecked(True)
  else:
   self.dlg.checkBoxReduceQueueTime.setChecked(False)

  checkBoxFastestRoute=s.value("iso4app/checkBoxFastestRoute", False)
  if checkBoxFastestRoute:
   self.dlg.checkBoxFastestRoute.setChecked(True)
  else:
   self.dlg.checkBoxFastestRoute.setChecked(False)

  checkPopulation=s.value("iso4app/chkPopulation", False)
  if checkPopulation:
   self.dlg.chkPopulation.setChecked(True)
  else:
   self.dlg.chkPopulation.setChecked(False)
   
  checkBoxLogging=s.value("iso4app/checkBoxLogging", False)
  if checkBoxLogging:
   self.dlg.checkBoxLogging.setChecked(True)
  else:
   self.dlg.checkBoxLogging.setChecked(False)
  
  if rbIsochrone:
   self.dlg.checkBoxFastestRoute.setEnabled(False)
  else:
   idx=self.dlg.comboTravelType.currentIndex()
   if idx==0:
    self.dlg.checkBoxFastestRoute.setEnabled(True)
   else:
    self.dlg.checkBoxFastestRoute.setEnabled(False)
   
  if self.dlg.checkBoxLogging.isChecked():
   QgsMessageLog.logMessage('apiKey:'+apiKey, 'iso4app')
   QgsMessageLog.logMessage('rbIsochrone:'+str(self.dlg.radioButtonIsochrone.isChecked()), 'iso4app')
   QgsMessageLog.logMessage('comboMeters:'+repr(comboMeters), 'iso4app')
   QgsMessageLog.logMessage('comboSeconds:'+repr(comboSeconds), 'iso4app')
   QgsMessageLog.logMessage('comboApprox:'+repr(comboApprox), 'iso4app')
   QgsMessageLog.logMessage('comboConcavity:'+repr(comboConcavity), 'iso4app')
   QgsMessageLog.logMessage('comboBuffering:'+repr(comboBuffering), 'iso4app')
   QgsMessageLog.logMessage('comboSpeedType:'+repr(comboSpeedType), 'iso4app')
   QgsMessageLog.logMessage('comboTravelType:'+repr(comboTravelType), 'iso4app')
   QgsMessageLog.logMessage('checkBoxAllowBikeOnPedestrian:'+str(checkBoxAllowBikeOnPedestrian), 'iso4app')
   QgsMessageLog.logMessage('checkBoxAllowPedBikeOnTrunk:'+str(checkBoxAllowPedBikeOnTrunk), 'iso4app')
   QgsMessageLog.logMessage('checkBoxAvoidTolls:'+str(checkBoxAvoidTolls), 'iso4app')
   QgsMessageLog.logMessage('checkBoxRestrictedArea:'+str(checkBoxRestrictedArea), 'iso4app')
   QgsMessageLog.logMessage('checkBoxFastestRoute:'+str(checkBoxFastestRoute), 'iso4app')
   QgsMessageLog.logMessage('checkBoxReduceQueueTime:'+str(checkBoxReduceQueueTime), 'iso4app')
   QgsMessageLog.logMessage('chkPopulation:'+str(checkPopulation), 'iso4app')
   QgsMessageLog.logMessage('rbStreetNetwork:'+str(self.dlg.radioButtonStreetNetwork.isChecked()), 'iso4app')
   QgsMessageLog.logMessage('rbPolygon:'+str(self.dlg.radioButtonPolygon.isChecked()), 'iso4app')
   
  
  QgsMessageLog.logMessage('initGui end', 'iso4app')  
  
 def clickRequestApiKey(self):
  QDesktopServices.openUrl(QUrl('http://www.iso4app.com#getapikey'))
 
 def place_iso(self, pointTriggered, button):
  try: 
   epsgCodeInput=self.canvas.mapSettings().destinationCrs().authid()
   epsgCodeCanvas=self.canvas.mapSettings().destinationCrs().authid()
  except:
   epsgCodeInput=self.canvas.mapRenderer().destinationCrs().authid()
   epsgCodeCanvas=self.canvas.mapRenderer().destinationCrs().authid()
  
  layernamePoly='tmp polygn layer'
  layernamePin='tmp point layer'
  if self.dlg.radioButtonStreetNetwork.isChecked()==True:
   vlyrPoly = QgsVectorLayer("multilinestring?crs="+epsgCodeCanvas, layernamePoly, "memory")
  if self.dlg.radioButtonPolygon.isChecked()==True:
   vlyrPoly = QgsVectorLayer("Polygon?crs="+epsgCodeCanvas, layernamePoly, "memory")

  vlyrPin =  QgsVectorLayer("Point?crs="+epsgCodeCanvas+"&field=id:integer&field=description:string(120)&field=x:double&field=y:double&index=yes",layernamePin,"memory")
  QApplication.setOverrideCursor(Qt.WaitCursor)
  instancei4a=None
  try:
   instancei4a=iso4CallService(self.iface,self.canvas,self.dlg,pointTriggered,epsgCodeInput,epsgCodeCanvas,vlyrPin,vlyrPoly,'','',None)
   vlyrPoly.setName(instancei4a.layernamePoly)
   vlyrPin.setName(instancei4a.layernamePin)
   vlyrPoly.setOpacity(0.5)
   if self.dlg.radioButtonStreetNetwork.isChecked()==True:
    renderer=vlyrPoly.renderer()
    rendererPin=vlyrPin.renderer()
    pinColor=rendererPin.symbol().color().name()
    symbolTmp=QgsLineSymbol.createSimple({'name':'LINE SYMBOL','width':'1', 'color':pinColor})
    renderer.setSymbol(symbolTmp)

   QgsProject.instance().addMapLayers([vlyrPin,vlyrPoly])  
  except Exception as inst:
   QgsMessageLog.logMessage('Error:'+str(inst), 'iso4app')
   
  QApplication.restoreOverrideCursor() 
  self.canvas.refresh()
  
  return None  
  
  
 def clickParameters(self):
  self.dlg.exec_()
 def clickMassiveIsolines(self):
  #logica
  
  rbIsochrone=self.dlg.radioButtonIsochrone.isChecked()
  rbStreetNetwork=self.dlg.radioButtonStreetNetwork.isChecked()
  rbPolygon=self.dlg.radioButtonPolygon.isChecked()
  comboMeters=self.dlg.comboMeters.currentIndex()
  comboSeconds=self.dlg.comboMeters.currentIndex()
  comboApprox=self.dlg.comboApprox.currentIndex()
  comboConcavity=self.dlg.comboConcavity.currentIndex()
  comboBuffering=self.dlg.comboBuffering.currentIndex()
  comboSpeedType=self.dlg.comboSpeedType.currentIndex()
  comboTravelType=self.dlg.comboTravelType.currentIndex()
  checkBoxAvoidTolls=self.dlg.checkBoxAvoidTolls.isChecked()
  checkBoxRestrictedArea=self.dlg.checkBoxRestrictedArea.isChecked()
  checkBoxReduceQueueTime=self.dlg.checkBoxReduceQueueTime.isChecked()  
  checkBoxAllowBikeOnPedestrian=self.dlg.checkBoxAllowBikeOnPedestrian.isChecked()
  checkBoxAllowPedBikeOnTrunk=self.dlg.checkBoxAllowPedBikeOnTrunk.isChecked()
  checkBoxFastestRoute=self.dlg.checkBoxFastestRoute.isChecked()
  checkBoxPopulation=self.dlg.chkPopulation.isChecked()
  speedLimit=self.dlg.lineSpeed.text()
  self.massiveDlg.labelCriticalMsg.setText('')

  otherParam=''
  if checkBoxAvoidTolls:
   otherParam+=' Avoid Tolls: YES. '
  else:
   otherParam+=' Avoid Tolls: NO. '
  if checkBoxRestrictedArea:
   otherParam+=' Include Restricted Area: YES. '
  else:
   otherParam+=' Include Restricted Area: NO. '
  
  isoDescr=''
  fastestRoutingText=''
  if rbIsochrone:
   isoDescr+='ISOCHRONE'
   valueIsoline = self.dlg.comboSeconds.currentText()
   if comboSpeedType==0:
    speedType=' Speed:Very Low'+'.'
   if comboSpeedType==1:
    speedType=' Speed:Low'+'.'
   if comboSpeedType==2:
    speedType=' Speed:Normal'+'.'
   if comboSpeedType==3:
    speedType=' Speed:Fast'+'.'
   if checkBoxReduceQueueTime:
    otherParam+=' Reduce queue time: YES. '
   else:
    otherParam+=' Reduce queue time: NO. '
   if speedLimit!='':
    otherParam+=' Speed Limit:'+speedLimit+'.'
  else:
   isoDescr+='ISODISTANCE'
   speedType=''
   valueIsoline = self.dlg.comboMeters.currentText()
   if checkBoxFastestRoute:
    fastestRoutingText=' Fastest Routing: YES. '
   
  if rbStreetNetwork:
   isoDescr+='(StreetNetwork)'
  else:
   isoDescr+='(Polygon)'
   
  isoDescr+=' '+valueIsoline+'.'
  if comboTravelType==0:
   mobility='Motor Vehicle'
  if comboTravelType==1:
   mobility='Bicycle'
   if checkBoxAllowPedBikeOnTrunk:
    otherParam+=' Bicycle on Trunk: YES. '
   else:
    otherParam+=' Bicycle on Trunk: NO. '
   if checkBoxAllowBikeOnPedestrian:
    otherParam+=' Bicycle on Pedestrian path: YES. '
   else:
    otherParam+=' Bicycle on Pedestrian path: NO. '
   
  if comboTravelType==2:
   mobility='Pedestrian'
   if checkBoxAllowPedBikeOnTrunk:
    otherParam+=' Pedestrian on Trunk: YES. '
   else:
    otherParam+=' Pedestrian on Trunk: NO. '
  otherParam+=' Concavity:'+repr(comboConcavity)+'. '
  otherParam+=' Buffering:'+repr(comboBuffering)+'. '
  
  isoDescr+=' Mobility:'+mobility+'.'
  isoDescr+=fastestRoutingText
  
  approxValue=self.dlg.comboApprox.currentText()
  isoDescr+=' Start Point Appoximation:'+approxValue+'.'
  isoDescr+=speedType
  isoDescr+=otherParam
  
  if checkBoxPopulation:
   isoDescr+=' Population=YES '
  else:
   isoDescr+=' Population=NO '
 
  self.massiveDlg.labelIsolineDescription.setText(isoDescr)
  self.isoDescr=isoDescr
  
  layersNames = []
  self.massiveDlg.comboBoxLayers.clear()
  self.massiveDlg.tableWidgetPoints.clear()
  self.massiveDlg.tableWidgetPoints.setRowCount(0)
  self.massiveDlg.comboBoxLayers.addItem('Select a layer...')
  
  
  mapLayers=QgsProject.instance().mapLayers()
  #for i in list(QgsProject.instance().mapLayers().values()):
  for i in mapLayers.values():
   #lName=i.name().encode('utf-8')
   lName=i.name()
   layersNames.append(lName)
   #QgsMessageLog.logMessage('calculate_massive_isolines lName:'+repr(lName), 'iso4app')
   self.massiveDlg.comboBoxLayers.addItem(lName)
  
  self.massiveDlg.exec_() 
  
 def unload(self):
  pass
  
 def eventCbSpeedType(self):
  manageSpeed(self)

 def eventRbPolygon(self):
   self.dlg.comboConcavity.setEnabled(True)
   self.dlg.comboBuffering.setEnabled(True)
   self.dlg.chkPopulation.setEnabled(True)
   
 def eventRbStreetNetwork(self):
   self.dlg.comboConcavity.setEnabled(False)
   self.dlg.comboBuffering.setEnabled(False)
   self.dlg.chkPopulation.setEnabled(False)
 
 def eventRbIsocrone(self):
  isChecked=self.dlg.radioButtonIsochrone.isChecked()
  self.dlg.checkBoxFastestRoute.setEnabled(False)
  manageSpeed(self)

 def eventRbIsodistance(self):
  idx=self.dlg.comboTravelType.currentIndex()
  if idx==0:
   self.dlg.checkBoxFastestRoute.setEnabled(True)

 def eventCbTravelType(self):
  idx=self.dlg.comboTravelType.currentIndex()
  self.dlg.checkBoxAllowBikeOnPedestrian.setEnabled(False)
  self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(False)
  self.dlg.checkBoxFastestRoute.setEnabled(True)
  if idx==1:
   self.dlg.checkBoxAllowBikeOnPedestrian.setEnabled(True)
   self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(True)
   self.dlg.checkBoxFastestRoute.setEnabled(False)
  if idx==2:
   self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(True)
   self.dlg.checkBoxFastestRoute.setEnabled(False)
  if self.dlg.radioButtonIsochrone.isChecked():
   self.dlg.checkBoxFastestRoute.setEnabled(False)
  manageSpeed(self)

 def eventLnkAvailableCountries(self):
  QDesktopServices.openUrl(QUrl('http://www.iso4app.com/thematicMap.jsp'))
  
 def calculate_massive_isolines_test(self):
  rowCount=10
  for row in range(0,rowCount):
   progress=(float(row)/float(rowCount))
   iface.statusBarIface().showMessage("Processed:"+str(row)+ ' of:'+str(rowCount))
   sleep(1)
   self.iface.mainWindow().repaint()


 def calculate_massive_isolines(self):
  self.stopRunning=0
  timeStampNow=datetime.datetime.now()
  self.massiveDlg.labelCriticalMsg.setText('')
  lastTimeRunning=diffMillis(self.timeStampLastMassiveRunning,timeStampNow)
  if lastTimeRunning>1000:
   if self.massiveDlg.lineEditLayerName.text()!='':
    if self.selectedLayer is not None:
     epsgCodeInput=self.selectedLayer.crs().authid()
     QgsMessageLog.logMessage('calculate_massive_isolines epsgCodeInput:'+epsgCodeInput, 'iso4app')
     epsgCodeCanvas=self.canvas.mapSettings().destinationCrs().authid()
     layernamePoly=self.massiveDlg.lineEditLayerName.text()
     layernamePin='test pin'
     if self.dlg.radioButtonStreetNetwork.isChecked()==True:
      vlyrPoly = QgsVectorLayer("multilinestring?crs="+epsgCodeCanvas, layernamePoly, "memory")
     if self.dlg.radioButtonPolygon.isChecked()==True:
      vlyrPoly = QgsVectorLayer("Polygon?crs="+epsgCodeCanvas, layernamePoly, "memory")

     vlyrPin = None

     #gestione attributi su feature
     idxAttrbute4Layer=self.massiveDlg.comboBoxAttributes4Layer.currentIndex()
     attributeName4Layer=''
     attributeValue4Layer=''
     if idxAttrbute4Layer>0:
      attributeName4Layer=self.massiveDlg.comboBoxAttributes4Layer.currentText()
     idxAttributeAsDistance=self.massiveDlg.comboBoxAttributeAsDistance.currentIndex()

     okIso=0
     errIso=0
     QApplication.setOverrideCursor(Qt.WaitCursor)
     try:
      rowCount=self.massiveDlg.tableWidgetPoints.rowCount()
      for row in range(0,rowCount):
       if self.stopRunning==1: break
       coordWgsX = self.massiveDlg.tableWidgetPoints.item(row,1)
       coordWgsY = self.massiveDlg.tableWidgetPoints.item(row,2) 
       pointData=self.massiveDlg.tableWidgetPoints.item(row,4).data(0)
       colorLayer=self.massiveDlg.tableWidgetPoints.item(row,5)
       if idxAttrbute4Layer>0:
        attributeValue4Layer = self.massiveDlg.tableWidgetPoints.item(row,idxAttrbute4Layer+4).text()
        QgsMessageLog.logMessage('calculate_massive_isolines selezionato attributo indice:'+repr(idxAttrbute4Layer)+' valore:'+attributeValue4Layer, 'iso4app')
       overWrittenDistance=None
       goCalculation=False
       if idxAttributeAsDistance>0:
        valueDst=self.massiveDlg.tableWidgetPoints.item(row,idxAttributeAsDistance+4).text()
        if valueDst.isdigit():
         QgsMessageLog.logMessage('calculate_massive_isolines valueDst:'+valueDst, 'iso4app')
         overWrittenDistance=int(valueDst)
         QgsMessageLog.logMessage('calculate_massive_isolines overWrittenDistance:'+repr(overWrittenDistance)+ ' valueDst:'+valueDst, 'iso4app')
         goCalculation=True
       else:
        goCalculation=True

       if goCalculation:
        QgsMessageLog.logMessage('calculate_massive_isolines X:'+coordWgsX.text()+ ' Y:'+coordWgsY.text()+ ' type:'+str(type(pointData))+ ' overWrittenDistance:'+repr(overWrittenDistance), 'iso4app')
        instancei4a=iso4CallService(self.iface,self.canvas,self.dlg,pointData,epsgCodeInput,epsgCodeCanvas,vlyrPin,vlyrPoly,attributeName4Layer,attributeValue4Layer, overWrittenDistance)
        rc=instancei4a.rc
        rcMessageCritical=instancei4a.rcMessageCritical
        if rc==0:
         self.massiveDlg.tableWidgetPoints.item(row,3).setText('OK')
         okIso=okIso+1
        else:
         self.massiveDlg.tableWidgetPoints.item(row,3).setText('ERR')
         errIso=errIso+1
        if len(rcMessageCritical)>0:
         self.massiveDlg.labelCriticalMsg.setText('Massive elaboration STOPPED:'+rcMessageCritical)
         break

        self.massiveDlg.lineEditTotaPointOK.setText(repr(okIso))
        self.massiveDlg.lineEditTotaPointError.setText(repr(errIso))
        firstT = datetime.datetime.now() 
        sleep(1)
        iface.statusBarIface().showMessage("Processed:"+str(row+1)+ ' of:'+str(rowCount))
        self.iface.mainWindow().repaint()
       else:
        self.iface.mainWindow().repaint()
      
      iface.statusBarIface().clearMessage()
      if okIso>0:
       vlyrPoly.setOpacity(0.5)
       if self.dlg.radioButtonStreetNetwork.isChecked()==True:
        renderer=vlyrPoly.renderer()
        symbolTmp=QgsLineSymbol.createSimple({'name':'LINE SYMBOL','width':'1', 'color':colorLayer.text()})
        renderer.setSymbol(symbolTmp)

       QgsProject.instance().addMapLayers([vlyrPin,vlyrPoly])  
     except Exception as inst:
      QgsMessageLog.logMessage('Error:'+str(inst), 'iso4app')
 
     QApplication.restoreOverrideCursor()
     self.canvas.refresh()
    else:
     self.iface.messageBar().pushMessage("Iso4App", 'Selected Layer has not any points!', level=2)
   else:
    self.iface.messageBar().pushMessage("Iso4App", 'Layer name required!', level=2)
   #comunque riabilito
   self.massiveDlg.pushButtonClose.setEnabled(True)
   self.timeStampLastMassiveRunning=datetime.datetime.now() 
  else:   
   QgsMessageLog.logMessage('click pressed in massive running: SKIP:', 'iso4app')
   self.massiveDlg.pushButtonClose.setEnabled(True)
   
 def disableButtonGroup(self):
  QgsMessageLog.logMessage('disableButtonGroup triggered', 'iso4app')
  self.massiveDlg.pushButtonClose.setEnabled(False)
 
 def eventCbBoxAttributesAsDistance(self):
  if self.selectedLayer is not None:
   idx=self.massiveDlg.comboBoxAttributeAsDistance.currentIndex()
   self.massiveDlg.labelCriticalMsg.setText('')
   if idx>0:
    rowCount=self.massiveDlg.tableWidgetPoints.rowCount()
    attributeValuesNotNumeric=0
    attributeValuesNumeric=0
    for row in range(0,rowCount):
     value = self.massiveDlg.tableWidgetPoints.item(row,idx+4)
     if value.text().isdigit():
      attributeValuesNumeric=attributeValuesNumeric+1
     else:
      attributeValuesNotNumeric=attributeValuesNotNumeric+1
    if attributeValuesNotNumeric>0:
     self.massiveDlg.labelCriticalMsg.setText('Warning: you have choosed a value of an attribute as an isoline distance, however non numeric values are present, this points will be skipped on massive isoline calculation')
    self.massiveDlg.labelIsolineDescription.setText(self.isoDescr+ '  --> WARNING: DEFAUT DISTANCE WILL BE OVERWRITTEN BY THE ATTRIBUTE VALUE NAMED: '+ self.massiveDlg.comboBoxAttributeAsDistance.currentText())
  
 def eventCbBoxAttributes(self):
  suggestedLayerName=''
  if self.selectedLayer is not None:
   idx=self.massiveDlg.comboBoxAttributes.currentIndex()
   if idx>0:
    rowCount=self.massiveDlg.tableWidgetPoints.rowCount()
    for row in range(0,rowCount):
     value = self.massiveDlg.tableWidgetPoints.item(row,idx+4)
     if len(value.text())>0:
      suggestedLayerName+=value.text()+'_'
     if len(suggestedLayerName)>200:
      break
   self.massiveDlg.lineEditLayerName.setText(suggestedLayerName)

 def eventCbBoxLayers(self):
  
   idx=self.massiveDlg.comboBoxLayers.currentIndex()
   self.selectedLayer=None
   self.massiveDlg.tableWidgetPoints.clear()
   self.massiveDlg.comboBoxAttributes.clear()
   self.massiveDlg.comboBoxAttributes4Layer.clear()
   self.massiveDlg.comboBoxAttributeAsDistance.clear()
   self.massiveDlg.tableWidgetPoints.setRowCount(0)
   self.massiveDlg.lineEditLayerName.setText('')
   self.massiveDlg.lineEditTotaPoint.setText('')
   self.massiveDlg.lineEditTotaPointOK.setText('')
   self.massiveDlg.lineEditTotaPointError.setText('')
   if idx>0:
    selectedLayer = list(QgsProject.instance().mapLayers().values())[idx-1]
   
    epsgCodeInput=selectedLayer.crs().authid()
    currentCoordSystem=QgsCoordinateReferenceSystem(epsgCodeInput)
    gpsCoordSystem=QgsCoordinateReferenceSystem("EPSG:4326")
    transformer = QgsCoordinateTransform(currentCoordSystem,gpsCoordSystem,QgsProject.instance())
    
    attrNames=''
    numAttr=0
    self.massiveDlg.comboBoxAttributes.addItem('Select an attribute...')
    self.massiveDlg.comboBoxAttributes4Layer.addItem('Select an attribute...')
    self.massiveDlg.comboBoxAttributeAsDistance.addItem('Select an attribute...')
    try: 
     for field in selectedLayer.fields():
      attributeName=field.name() #.encode('utf-8')
      attrNames+=attributeName+';'
      numAttr=numAttr+1
      self.massiveDlg.comboBoxAttributes.addItem(attributeName)
      self.massiveDlg.comboBoxAttributes4Layer.addItem(attributeName)
      self.massiveDlg.comboBoxAttributeAsDistance.addItem(attributeName)
    except Exception as ex:
     QgsMessageLog.logMessage(str(ex),'iso4app')

    self.massiveDlg.tableWidgetPoints.setColumnCount(6+numAttr)
    self.massiveDlg.tableWidgetPoints.setColumnWidth(0,40)
    self.massiveDlg.tableWidgetPoints.setColumnWidth(3,50)
    self.massiveDlg.tableWidgetPoints.setColumnWidth(4,60)
    self.massiveDlg.tableWidgetPoints.setHorizontalHeaderLabels(('FID;LNG;LAT;STATUS;RESERVED;COLOR;'+attrNames).split(";"))
   
    if self.dlg.checkBoxLogging.isChecked():   
     QgsMessageLog.logMessage('Info Layer:'+repr(idx)+ ' '+selectedLayer.name()+' epsg:'+repr(epsgCodeInput), 'iso4app') 
    try: 
     iter = selectedLayer.getFeatures()
     idxRow=0
     newSuggestedLayerName='isoline_'
     QgsMessageLog.logMessage('before :', 'iso4app') 
     loopNum=0
     colorLayer="#93604e"
     for feature in iter:
      geom = feature.geometry()
      #geomTypeString=self.iface.QgsWKBTypes.displayString(int(geom.wkbType()))
      QgsMessageLog.logMessage('geom:', 'iso4app') 
      QgsMessageLog.logMessage('geom.type()'+repr(geom.type()), 'iso4app')
      #if geom.type() == QGis.WKBPoint:
      if geom.type() == 0:
       if loopNum==0:
        rendererMassive=selectedLayer.renderer()
        colorLayer=rendererMassive.symbol().color().name()
        QgsMessageLog.logMessage('eventCbBoxLayers:'+colorLayer ,'iso4app') 

       loopNum=loopNum+1
       pointOnLayer = geom.asPoint()
       pt = transformer.transform(pointOnLayer)
       QgsMessageLog.logMessage('point:'+str(pointOnLayer)+ ' '+str(pt), 'iso4app') 
       itemPointX = QTableWidgetItem(str(pt.x())) 
       itemPointY = QTableWidgetItem(str(pt.y())) 
       itemId = QTableWidgetItem(str(feature.id()))  
       itemStatus = QTableWidgetItem(' ')
       itemQgisPoint = QTableWidgetItem(str(feature.id())) 
       itemQgisPoint.setData(0,geom.asPoint())
       itemQgisLayerColor = QTableWidgetItem(str(colorLayer))
       QgsMessageLog.logMessage('dopo itemQgisLayerColor' , 'iso4app') 
       self.massiveDlg.tableWidgetPoints.insertRow(idxRow)
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,0,itemId)
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,1,itemPointX)
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,2,itemPointY) 
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,3,itemStatus)
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,4,itemQgisPoint) 
       self.massiveDlg.tableWidgetPoints.setItem(idxRow,5,itemQgisLayerColor) 
       QgsMessageLog.logMessage('dopo tableWidgetPoints itemQgisLayerColor' , 'iso4app')
       if numAttr>0:
        prgTable=6 
        valueAttr=''
        for field in selectedLayer.fields(): 
         if type(feature[field.name()])==int:
          valueAttr=repr(feature[field.name()])
         if type(feature[field.name()])==int:
          valueAttr=repr(feature[field.name()])
         if type(feature[field.name()])==bool:
          valueAttr=str(feature[field.name()])
         if type(feature[field.name()])==float:
          valueAttr=str(feature[field.name()])
         if type(feature[field.name()])==str:
          valueAttr=feature[field.name()]
         if type(feature[field.name()])==str:
          valueAttr=feature[field.name()]
         #QgsMessageLog.logMessage('type feature:'+type(feature[field.name()]) , 'iso4app') 
         self.massiveDlg.tableWidgetPoints.setItem(idxRow,prgTable,QTableWidgetItem(valueAttr))
         prgTable=prgTable+1
        
       idxRow=idxRow+1
      else:
       QgsMessageLog.logMessage('no point', 'iso4app') 
     if idxRow>0:
      self.selectedLayer=selectedLayer
     self.massiveDlg.lineEditTotaPoint.setText(repr(idxRow))
    except Exception as ex:
     QgsMessageLog.logMessage('Warning: selected layer has not any feature.'+str(ex) ,'iso4app')
 
 def eventButtonCloseMassive(self):
  QgsMessageLog.logMessage('eventButtonCloseMassive' ,'iso4app')
  self.massiveDlg.close()
  self.canvas.setMapTool(self.isoTool)
 
 def eventOkButton(self):
  QgsMessageLog.logMessage('eventOkButton' ,'iso4app')
  s = QSettings()
  
  if len(self.dlg.lineApiKey.text())!=36 :
   self.dlg.lineApiKey.setText('87B7FB96-83DA-4FBD-A312-7822B96BB143')
   
  s.setValue("iso4app/apy-key", self.dlg.lineApiKey.text())
  s.setValue("iso4app/rbIsochrone", self.dlg.radioButtonIsochrone.isChecked())
  
  s.setValue("iso4app/comboMeters", self.dlg.comboMeters.currentIndex())
  s.setValue("iso4app/comboSeconds", self.dlg.comboSeconds.currentIndex())
  s.setValue("iso4app/comboApprox", self.dlg.comboApprox.currentIndex())
  s.setValue("iso4app/comboConcavity", self.dlg.comboConcavity.currentIndex())
  s.setValue("iso4app/comboBuffering", self.dlg.comboBuffering.currentIndex())
  s.setValue("iso4app/comboSpeedType", self.dlg.comboSpeedType.currentIndex())
  s.setValue("iso4app/comboTravelType", self.dlg.comboTravelType.currentIndex())
  
  s.setValue("iso4app/checkBoxAllowBikeOnPedestrian", self.dlg.checkBoxAllowBikeOnPedestrian.isChecked())
  s.setValue("iso4app/checkBoxAllowPedBikeOnTrunk", self.dlg.checkBoxAllowPedBikeOnTrunk.isChecked())
  s.setValue("iso4app/checkBoxAvoidTolls", self.dlg.checkBoxAvoidTolls.isChecked())
  s.setValue("iso4app/checkBoxRestrictedArea", self.dlg.checkBoxRestrictedArea.isChecked())
  s.setValue("iso4app/checkBoxReduceQueueTime", self.dlg.checkBoxReduceQueueTime.isChecked())
  s.setValue("iso4app/checkBoxLogging", self.dlg.checkBoxLogging.isChecked())
  s.setValue("iso4app/checkBoxFastestRoute", self.dlg.checkBoxFastestRoute.isChecked())
  s.setValue("iso4app/rbPolygon", self.dlg.radioButtonPolygon.isChecked())
  s.setValue("iso4app/chkPopulation", self.dlg.chkPopulation.isChecked())
  s.setValue("iso4app/rbStreetNetwork", self.dlg.radioButtonStreetNetwork.isChecked())
  self.dlg.close()
  self.canvas.setMapTool(self.isoTool)
  
 def run(self):
  self.canvas.setMapTool(self.isoTool)

 def unload(self):
  # Remove the plugin menu item and icon
  self.iface.removePluginMenu("Iso4App",self.action)
  self.iface.removeToolBarIcon(self.action)

def diffMillis(firstT,currT):
 diff = currT - firstT
 millis = diff.days * 24 * 60 * 60 * 1000
 millis += diff.seconds * 1000
 millis += diff.microseconds / 1000
 return millis
 
def manageSpeed(self):
 idxTT=self.dlg.comboTravelType.currentIndex()
 idxST=self.dlg.comboSpeedType.currentIndex()
 isChecked=self.dlg.radioButtonIsochrone.isChecked()
 self.dlg.labelInfo.setText('')
 self.dlg.lineSpeed.setText('')
 if isChecked==1:
  self.dlg.comboSpeedType.setEnabled(True)
  self.dlg.checkBoxReduceQueueTime.setEnabled(True)
  self.dlg.lineSpeed.setEnabled(True)
  if idxTT==1:
   if idxST==0:
    self.dlg.lineSpeed.setText('8')
   if idxST==1:
    self.dlg.lineSpeed.setText('12')
   if idxST==2:
    self.dlg.lineSpeed.setText('16')
   if idxST==3:
    self.dlg.lineSpeed.setText('40')
    self.dlg.labelInfo.setText('High default speed value! Please adjust it')
  if idxTT==2:
   if idxST==0:
    self.dlg.lineSpeed.setText('3')
   if idxST==1:
    self.dlg.lineSpeed.setText('4.4')
   if idxST==2:
    self.dlg.lineSpeed.setText('5.4')
   if idxST==3:
    self.dlg.lineSpeed.setText('20')
    self.dlg.labelInfo.setText('High default speed value! Please adjust it')
 else:
  self.dlg.comboSpeedType.setEnabled(False)
  self.dlg.checkBoxReduceQueueTime.setEnabled(False)
  self.dlg.lineSpeed.setEnabled(False)
  
 return None
def progdialog(progress):
 dialog = QProgressDialog()
 dialog.setWindowTitle("Progress")
 dialog.setLabelText("text")
 bar = QProgressBar(dialog)
 bar.setTextVisible(True)
 bar.setValue(progress)
 dialog.setBar(bar)
 dialog.setMinimumWidth(300)
 dialog.show()
 return dialog, bar

 