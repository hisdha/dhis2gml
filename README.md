
# GIS Import for DHIS2

[Full Documentation](https://liascript.github.io/course/?https://github.com/hisdha/dhis2gml/blob/master/README.md)
## How to create CSV,GML and GeoJSON files
 - Go to [https://www.mapshaper.org](https://www.mapshaper.org)
 - Upload the shapefiles zip
 - Note that the shapefiles consists of files with extension .shp,.shx,.prj,.cpg,.dbf, etc

 One possible method is the use of MapShaper which is an online tool which can be used to generalize geographical data. To use MapShaper, simply upload your shapefile to the site. Then, at the centre bottom you see a slider that starts at 0%. It is usually acceptable to drag it up to about 80%. In the left menu you can check "show original lines" to compare the result and you may want to give a different simplification method a try. When you are happy with the result, click "export" in the top right corner. Then check the first of the four options called "Shapefile - polygons", click "create" and wait for the download buttons to appear. Now, download the two files to your local computer and overwrite the existing ones. Move on to the next step with your new simplified shapefile.

Step 2 - Convert the shapefile to GML

The recommended tool for geographical format conversions is called =="ogr2ogr"==. This should be available for most Linux distributions sudo apt-get install gdal-bin. For Windows, go to [http://fwtools.maptools.org](http://fwtools.maptools.org/)and download "FWTools", install it and open up the FWTools command shell. During the format conversion we also want to ensure that the output has the correct coordinate projection (called EPSG:4326 with geographic longitude and latitude). For a more detailed reference of geographic coordinates, please refer to this site. If you have already reprojected the geographic data to the geographic latitude/longitude (EPSG:4326) system, there is no need to explicitly define the output coordinate system, assuming that ogr2ogr can determine the input spatial reference system. Note that most shapefiles are using the EPSG:4326 system. You can determine the spatial reference system by executing the following command.


```
ogrinfo -al -so filename.shp

```
Assuming that the projection is reported to be EPSG:27700 by ogrinfo, we can transform it to ==EPSG:4326== by executing the following command.


```
ogr2ogr -s_srs EPSG:27700 -t_srs EPSG:4326 -f GML filename.gml filename.shp

```
If the geographic data is already in EPSG:4326, you can simply transform the shapefile to GML by executing the following command.


```
ogr2ogr -f GML filename.gml filename.shp

```
You will find the created GML file in the same folder as the shapefile.

### CSV
 - Click Export and select all, tick CSV

### GeoJSON
 - Click Export and select all, tick GeoJSON

### GML
 - Click Export and select all, tick shapefiles

## Install the GML to DHIS2 Script
### Install requirements
```
python -m pip install hisengine-1.0-py3-none-any.whl

```
### Install script

### Script options
```
  -l or --secrets Specify file (json)
  -p or --params Specify parameters e.g id,code,name. The default is "id,name,shortName,code"
  -f or --fileName The main file with GIS csv data  or substring e.g -f "data"
  -g or --gmlFileName",help="GIS GML or GeoJSON file
  -r or --ouProperty",default="name",help="DHIS2 OrgUnit matching property
  -o or --gmlProperty",default="ID_0",help="GIS GML or GeoJSON matching property
  -q or --gmlLeftProperty",default="OBJECTID",help="GIS GML or GeoJSON matching property from CSV GML
  -d or --path",help="path to secrets file
  -t or --coding",help="Conversion type: gml or geojson
  -m or --dataPath",help="Folder to store processed data
  -s or --sourceFormat",help="Data Source Format: gml or geojson
  -e or --serverEnv",help="Server Environment to use for orgUnit comparison
  -i or --level",default=None,help="The level that is being transformed
  -c or --parent",help="UID of parent/ancestor in the level being transformed
  -a or --filter",help="Additional filters separated by commas e.g name:$like:XOR,name:$like:XORI
```
## Match the CSV with DHIS2 orgUnits

## Match the CSV with GeoJSON

## Validate DHIS2 import

## Import DHIS2 import

## Create complete datasets from metadata

 ### Get dataset
``
https://url/api/dataSets.json?paging=false&fields=:owner,!lastUpdatedBy,!createdBy,!sharing,!attributeValues&filter=id:in:[]
``

 ### Get data elements
https://url/api/dataElements.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=id:in:[]
 ### Get categoryCombos
  - Find which categoryCombos are used in data elements
 https://url/api/dataElements.json?paging=false&fields=categoryCombo[id]&filter=id:in:[de1,de2,de3,...]
  - Extract categoryCombo id from objects that look this
    {
      "categoryCombo": {
        "id": "catComboid"
      }
    }
  - Retrieve the categoryCombo metadata
https://url/api/categoryCombos.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=id:in:[catcombo1,catcombo2,...]


 ### Get Categories
  - Retrieve metadata for categories

https://url/api/categories.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=categoryCombos.id:in:[catcombo1,catcombo2,...]

 ### Get CategoryOptions
https://url/api/categoryOptions.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=categories.categoryCombos.id:in:[catcombo1,catcombo2,...]

 ### Get CategoryOptionCombos
https://url/api/categoryOptionCombos.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=categoryCombo.id:in:[catcombo1,catcombo2,...]

 ### Get indicators
https://url/api/indicators.json?paging=false&fields=:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=id:in:[]

 ### Get Indicator Types
https://url/api/indicatorTypes.json?paging=false&fields=*,:owner,!attributeValues,!lastUpdatedBy,!createdBy,!sharing&filter=id:in:[]

