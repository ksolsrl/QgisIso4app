# QgisIso4app
Qgis plugin for iso4app service. Isochrone/Isodistance.
This version is compatible with QGIS 3.X.
The Iso4App API is a service based onto OSM data; it's purpose is to provide isolines (isodistances and isochrones) to be used 
in geographic analysis.
Support for walk, car, bike isolines. Predefined speed levels and customizable speed value.Flags to reduce queue time and avoid tolls.
Flag to includes restricted access areas. Flag to allow bicycles on pedestrian areas. 
Customizable concavity level, from convex to higher concave polygon (9 concavity level).
Customizable buffering level.
![Qgis iso4app plugin](http://www.iso4app.com/images/qgis_plugin_example.png)

![Qgis iso4app parameters](http://www.k-sol.it/iso4app/qgis_plugin_parameters_new.png)

New feature Output types: now you can shown the street network instead of polygon:
![Qgis iso4app street_network](http://www.k-sol.it/iso4app/qgis_street_network_new.png)

New feature Demographics->Add populaton: if avaiable te population inside the isoline poligon will be added as attibute table:
![Qgis iso4app population](http://www.k-sol.it/iso4app/qgis_population.png)

New Isodistances with Fastest Route option. You can check this option for isodistances/motor vehicle. Without this option the shortest path will be calculated, all route will be taken. Checking this option the fastest route will be taken and the polygon will be smaller, this is because usually the fastest roads are longer than the other roads. We suggest to use this option for transport planning.

The combo-box for time/distance are now editable so you can write your preferred time/distances manually Ex. 332 meters. Please write using the correct format. 

New massive isolines calculation feature is now available.

You can invoke the new menu Iso4app->Massive Isoline Calculation:

![Qgis iso4app plugin](http://www.k-sol.it/iso4app/new_iso4app_menu.png)

The massive isoline calculation panel will be displayed.

You have to select a layer (in this example MyLayer), if the layer contains points they will be listed.
For automatic layer name based on attributes value select an attribute from the combo, otherwise write your preferred layer name. 
In addition you can select an attribute to add, for each polygon, in the attribute tables, so you can link the polygons to your points.
You can also select a attribute to use as a distance. This attribute will be read as meters if isodistances or minutes if isochrones.

![Qgis iso4app plugin](http://www.k-sol.it/iso4app/MassiveIsolineCalculationNew.png)

An example of attribute table created for the new layer:

![Qgis iso4app plugin](http://www.k-sol.it/iso4app/TableAttributes.png)


WARNING: THE LAYERS CREATED BY THIS PLUGIN ARE MEMORY LAYERS IF YOU CLOSE QGIS THEY ARE NOT SAVED. IN ORDER TO SAVE ISO4APP LAYERS YOU CAN USE THE OPTION MAKE PERMANENT AVAILABLE ON RIGHT-CLICKING ON THE LAYER.
