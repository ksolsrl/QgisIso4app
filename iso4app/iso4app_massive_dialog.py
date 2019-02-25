# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iso4appDialog
                                 A QGIS plugin
 tetta
                             -------------------
        begin                : 2018-02-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by k-sol srl
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

from qgis.PyQt import QtWidgets,QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'iso4app_massive_dialog_base.ui'))

class iso4appMassiveDialog(QtWidgets.QDialog, FORM_CLASS):
 def __init__(self, parent=None):
  super(iso4appMassiveDialog, self).__init__(parent)
  self.setupUi(self)

 def closeEvent(self, event):
  self.pushButtonClose.click()