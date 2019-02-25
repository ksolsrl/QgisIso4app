# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iso4app
                                 A QGIS plugin
 iso4app
                             -------------------
        begin                : 2018-02-07
        copyright            : (C) 2018 by kk
        email                : info@k-sol.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import

def name():
    return "Iso4app isochrone/isodistance plugin"

def description():
    return "Creates isochrone/isodistance on the map." 

def version():
    return "Version 1.0"

def icon():
    return "icon.png"

def qgisMinimumVersion():
    return "2.18.16"

def author():
    return "K-SOL SRL"

def email():
    return "info@k-sol.it"


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load iso4app class from file iso4app.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .iso4app import MainPlugin
    return MainPlugin(iface)
