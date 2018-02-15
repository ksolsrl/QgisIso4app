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
import os
import sys
import tempfile
import gettext
import resources
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Import the code for the dialog
from iso4app_dialog import iso4appDialog
#from clickFuUtils import cfAction
from iso4appApi import isoline
from iso4appService import iso4CallService
import iso4app_dialog
#from iso4app_registration import Ui_DialogRegister
#import iso4app_registration


class MainPlugin(object):
 def __init__(self, iface):
  self.iface = iface
  self.dlg=iso4app_dialog.iso4appDialog()
  self.toolbar = self.iface.addToolBar(u'wfsOutputExtension')
  self.canvas=iface.mapCanvas()
  self.isoTool = QgsMapToolEmitPoint(self.canvas)
  self.canvas.mapToolSet.connect(self.deactivate)    
  
 def name(self):
  return "Iso4App"
 def initGui(self):
  QgsMessageLog.logMessage('initGui start', 'iso4app')  
  #self.toolbar = self.iface.addToolBar("Iso4App")
  self.isoline = isoline(self.iface,self.dlg)
  
  self.requestAK = QAction("Request Api Key",self.iface.mainWindow())
  QObject.connect(self.requestAK,SIGNAL("triggered()"),self.clickRequestApiKey)

  icon_path = ':/plugins/iso4app/icon.png'
  self.action = QAction(QIcon(":/plugins/iso4app/icon.png"), "Iso4App", self.iface.mainWindow())
  QObject.connect(self.action, SIGNAL("triggered()"), self.run)
  result = QObject.connect(self.isoTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.place_iso)
  self.iface.addToolBarIcon(self.action)

  #connessione menù alla azione isoline
  self.menu=QMenu("Iso4App")
  self.menu.addActions([self.isoline])
  menuBar = self.iface.mainWindow().menuBar()
  menuBar.addMenu(self.menu)
  self.menu.addSeparator()
  self.menu.addAction(self.requestAK)
  
  QObject.connect(self.isoline,SIGNAL("triggered()"),self.clickParameters)
  self.dlg.radioButtonIsochrone.toggled.connect(self.eventRbIsocrone)
  self.dlg.comboTravelType.currentIndexChanged.connect(self.eventCbTravelType)
  self.dlg.comboSpeedType.currentIndexChanged.connect(self.eventCbSpeedType)
  self.dlg.button_box.clicked.connect(self.eventOkButton)
  
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
   
  for meters in range(400,1000):
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
  if rbIsochrone=='true':
   self.dlg.radioButtonIsochrone.setChecked(True)
   self.dlg.radioButtonIsodistance.setChecked(False)
  else:
   self.dlg.radioButtonIsochrone.setChecked(False)
   self.dlg.radioButtonIsodistance.setChecked(True)
  
  comboMeters=s.value("iso4app/comboMeters", 69)
  comboSeconds=s.value("iso4app/comboSeconds", 9)
  comboApprox=s.value("iso4app/comboApprox", 2)
  comboConcavity=s.value("iso4app/comboConcavity", 5)
  comboBuffering=s.value("iso4app/comboBuffering", 0)
  comboSpeedType=s.value("iso4app/comboSpeedType", 2)
  comboTravelType=s.value("iso4app/comboTravelType", 0)

  self.dlg.comboTravelType.setCurrentIndex(comboTravelType)
  self.dlg.comboSpeedType.setCurrentIndex(comboSpeedType)
  self.dlg.comboBuffering.setCurrentIndex(comboBuffering)
  self.dlg.comboConcavity.setCurrentIndex(comboConcavity)
  self.dlg.comboApprox.setCurrentIndex(comboApprox)
  self.dlg.comboSeconds.setCurrentIndex(comboSeconds)
  self.dlg.comboMeters.setCurrentIndex(comboMeters)

  checkBoxAllowBikeOnPedestrian=s.value("iso4app/checkBoxAllowBikeOnPedestrian", True)
  if checkBoxAllowBikeOnPedestrian=='true':
   self.dlg.checkBoxAllowBikeOnPedestrian.setChecked(True)
  else:
   self.dlg.checkBoxAllowBikeOnPedestrian.setChecked(False)

  checkBoxAllowPedBikeOnTrunk=s.value("iso4app/checkBoxAllowPedBikeOnTrunk", True)
  if checkBoxAllowPedBikeOnTrunk=='true':
   self.dlg.checkBoxAllowPedBikeOnTrunk.setChecked(True)
  else:
   self.dlg.checkBoxAllowPedBikeOnTrunk.setChecked(False)

  checkBoxAvoidTolls=s.value("iso4app/checkBoxAvoidTolls", True)
  if checkBoxAvoidTolls=='true':
   self.dlg.checkBoxAvoidTolls.setChecked(True)
  else:
   self.dlg.checkBoxAvoidTolls.setChecked(False)

  checkBoxRestrictedArea=s.value("iso4app/checkBoxRestrictedArea", True)
  if checkBoxRestrictedArea=='true':
   self.dlg.checkBoxRestrictedArea.setChecked(True)
  else:
   self.dlg.checkBoxRestrictedArea.setChecked(False)

  checkBoxReduceQueueTime=s.value("iso4app/checkBoxReduceQueueTime", True)
  if checkBoxReduceQueueTime=='true':
   self.dlg.checkBoxReduceQueueTime.setChecked(True)
  else:
   self.dlg.checkBoxReduceQueueTime.setChecked(False)

  checkBoxLogging=s.value("iso4app/checkBoxLogging", False)
  if checkBoxLogging=='true':
   self.dlg.checkBoxLogging.setChecked(True)
  else:
   self.dlg.checkBoxLogging.setChecked(False)

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
   QgsMessageLog.logMessage('checkBoxReduceQueueTime:'+str(checkBoxReduceQueueTime), 'iso4app')
  
  QgsMessageLog.logMessage('initGui end', 'iso4app')  
  
 def clickRequestApiKey(self):
  QDesktopServices.openUrl(QUrl('http://www.iso4app.com#getapikey'))
 
 def place_iso(self, pointTriggered, button):
  iso4CallService(self.iface,self.canvas,self.dlg,pointTriggered)
  return None  
  
  
 def clickParameters(self):
  self.dlg.exec_()
  
 def unload(self):
  pass
  
 def eventCbSpeedType(self):
  manageSpeed(self)
  
 def eventRbIsocrone(self):
  isChecked=self.dlg.radioButtonIsochrone.isChecked()
  manageSpeed(self)

 def eventCbTravelType(self):
  idx=self.dlg.comboTravelType.currentIndex()
  self.dlg.checkBoxAllowBikeOnPedestrian.setEnabled(False)
  self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(False)
  if idx==1:
   self.dlg.checkBoxAllowBikeOnPedestrian.setEnabled(True)
   self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(True)
  if idx==2:
   self.dlg.checkBoxAllowPedBikeOnTrunk.setEnabled(True)
  manageSpeed(self)

 def eventOkButton(self):
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
  
 def run(self):
  self.canvas.setMapTool(self.isoTool)

 def unload(self):
  # Remove the plugin menu item and icon
  self.iface.removePluginMenu("Iso4App",self.action)
  self.iface.removeToolBarIcon(self.action)

 def deactivate(self):
  QgsMessageLog.logMessage('deactivate'+repr(self.action.isChecked()), 'iso4app') 
 
def manageSpeed(self):
 idxTT=self.dlg.comboTravelType.currentIndex()
 idxST=self.dlg.comboSpeedType.currentIndex()
 isChecked=self.dlg.radioButtonIsochrone.isChecked()
 self.dlg.labelInfo.setText('')
 self.dlg.lineSpeed.setText('')
 if isChecked==1:
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
 return None
 
 