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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'iso4app_dialog_base.ui'))


class iso4appDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(iso4appDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
		
    def closeEvent(self, event):
     self.button_box.click()