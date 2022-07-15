# -*- coding: utf-8 -*-
# Utility module to Convert GIS Shape files or GeoJSON to DHIS2 GML file
import hisengine.engine.core.hisApi as hisApi
import hisengine.engine.core.mappingUtils as mappingUtils
import hisengine.engine.core.hisUtils as hisUtils
import sys,argparse
import json,math
from pathlib import Path
import numpy as np, pandas as pd
from datetime import datetime, timedelta,date

def main(argv):
    parser = argparse.ArgumentParser(description="Transform GIS Shapefiles to GML or GeoJSON for DHIS2")
    parser.add_argument("-l","--secrets",help="Specify file (json)")
    parser.add_argument("-p","--params",default="id,name,shortName,code",help="Specify parameters e.g id,code,name")
    parser.add_argument("-f","--fileName",help="main file with GIS csv data  or substring")
    parser.add_argument("-g","--gmlFileName",help="GIS GML or GeoJSON file")
    parser.add_argument("-r","--ouProperty",default="name",help="DHIS2 OrgUnit matching property")
    parser.add_argument("-o","--gmlProperty",default="ID_0",help="GIS GML or GeoJSON matching property")
    parser.add_argument("-q","--gmlLeftProperty",default="OBJECTID",help="GIS GML or GeoJSON matching property from CSV GML")
    parser.add_argument("-d","--path",help="path to secrets file")
    parser.add_argument("-t","--coding",help="Conversion type: gml or geojson")
    parser.add_argument("-m","--dataPath",help="Folder to store processed data")
    parser.add_argument("-s","--sourceFormat",help="Data Source Format: gml or geojson")
    parser.add_argument("-e","--serverEnv",help="Server Environment to use for orgUnit comparison")
    parser.add_argument("-i","--level",default=None,help="The level that is being transformed")
    parser.add_argument("-c","--parent",help="UID of parent/ancestor in the level being transformed")
    parser.add_argument("-a","--filter",help="Additional filters separated by commas e.g name:$like:XOR,name:$like:XORI")

    args = parser.parse_args()
    api = hisApi.hisApi()
    mu = mappingUtils.mappingUtils()
    hu = hisUtils.hisUtils()
    path = None
    serverEnv = 'dev'
    dataPath = None
    secretsFile = None
    fileName = args.fileName
    coding = args.coding
    filter = []
    matchProperty = f"properties.{ args.gmlProperty}"
    matchLeftProperty = args.gmlLeftProperty
    matchGmlProperty = args.ouProperty
    if args.secrets is not None:
        secretsFile = args.secrets
    if args.serverEnv is not None:
        serverEnv = args.serverEnv
    if args.path is not None:
        path = args.path
    if args.path is None:
        print('Please provide the path to secrets file.')
        exit()
    if args.dataPath is None:
        print('Please provide the path to store GIS formatted data, Default is C:\dhis2_gis\ ')
        dataPath = 'C:\\dhis2_gis\\'
        #exit()
    if args.dataPath is not None:
        dataPath = args.dataPath
    if args.parent is not None:
        filter.append(f"ancestors.id:eq:{ args.parent}")
    if args.level is not None:
        filter.append(f"level:eq:{args.level}")
    if args.filter is not None:
        filter.extend([x for x in args.filter.split(',')])

    # Create data path for storing files, if it exists ignore
    Path(f"{dataPath}/dhis2gml").mkdir(parents=True, exist_ok=True) 
    Path(f"{dataPath}/dhis2gml/dhis2").mkdir(parents=True, exist_ok=True)   
    secrets = api.getAuth(path=path,secrets=secretsFile)
    session = api.getLoginSession(secrets[serverEnv]['username'],secrets[serverEnv]['password'],sid='DHIS2')
    if coding == 'match':
        params = {"paging":"false","fields":args.params,"filter":filter}
        dfGisCsv = hu.getPdFile(path=dataPath,folder="",fileName=fileName,type='csv')
        # Get sites/Facilities/orgUnits
        gis = api.getDHIS2Item(url=secrets[serverEnv]['url'],session=session,item='organisationUnits',params=params)
        dfGis = hu.getPdFile(values=gis['organisationUnits'],type='json')
        dfGis["MatchName"] = dfGis[matchGmlProperty].astype(str)
        matchedGis = pd.merge(dfGisCsv,dfGis,how="left",left_on=[f"MatchName"],right_on=["MatchName"])
        hu.createResultFile(values=matchedGis,path=dataPath,folder='dhis2gml',filename='{}_{}_{}'.format(fileName,'csv',datetime.now().strftime('%Y-%m')),type='csv')
    if coding == 'gml':
        dfGisCsv = hu.getPdFile(path=dataPath,folder="dhis2gml",fileName=fileName,type='csv')
        # Get sites/Facilities/orgUnits
        if args.gmlFileName is None:
            print(f"Please provide a GML file.")
            exit()
        matchedGis = pd.merge(dfGisCsv,dfGis,how="left",left_on=[f"MatchName"],right_on=["name"])
        hu.createResultFile(values=matchedGis,path=dataPath,folder='dhis2gml',filename='{}_{}_{}'.format(fileName,'dhis2_gis_gml_',datetime.now().strftime('%Y-%m')),type='xml')
    if coding == 'geojson':
        dfGisCsv = hu.getPdFile(path=dataPath,folder="dhis2gml",fileName=fileName,type='csv')
        if args.gmlFileName is None:
            print(f"Please provide a GeoJson file.")
            exit()
        params = {"paging":"false","fields":":owner,!lastUpdatedBy,!user,!createdBy","filter":filter}
        # Get sites/Facilities/orgUnits
        gis = api.getDHIS2Item(url=secrets[serverEnv]['url'],session=session,item='organisationUnits',params=params)
        dfGis =gis['organisationUnits']
        with open(f"{dataPath}/{args.gmlFileName}.json",'r') as geo:
            geojson = json.load(geo)
            dfGisGeoJson = pd.json_normalize(geojson["features"])
            dfGisGeoJson.drop_duplicates(inplace=True)
            dfGisCsv.drop_duplicates(inplace=True)
            dfGisGeoJson["OBJECTIDMATCH"] = dfGisGeoJson[matchProperty].astype(str)
            dfGisCsv["OBJECTIDMATCH"] = dfGisCsv[matchLeftProperty].astype(str)
            matchedGis = pd.merge(dfGisCsv,dfGisGeoJson,how="left",left_on=["OBJECTIDMATCH"],right_on=["OBJECTIDMATCH"])
            matchedGisGeojson = matchGML(data=dfGis,ous=json.loads(matchedGis.to_json(orient='records')))
            with open(f"{dataPath}/dhis2gml/dhis2/{args.gmlFileName}_geojson_{datetime.now().strftime('%Y-%m')}.json",'w') as f:
                json.dump({"organisationUnits":matchedGisGeojson}, f, ensure_ascii=False, indent=2)
    if coding == 'geojson_matched':
        if args.gmlFileName is None:
            print(f"Please provide a GeoJson file.")
            exit()
        params = {"paging":"false","fields":":owner,!lastUpdatedBy,!user,!createdBy","filter":filter}
        # Get sites/Facilities/orgUnits
        gis = api.getDHIS2Item(url=secrets[serverEnv]['url'],session=session,item='organisationUnits',params=params)
        dfGis =gis['organisationUnits']
        with open(f"{dataPath}/{args.gmlFileName}.json",'r') as geoMatched:
            geojson = json.load(geoMatched)
            dfGisGeoJson = pd.json_normalize(geojson["features"])
            dfGisGeoJson["id"] = dfGisGeoJson[matchProperty].astype(str)
            dfGisGeoJson.drop_duplicates(inplace=True)
            matchedGisGeojson = matchGML(data=dfGis,ous=json.loads(dfGisGeoJson.to_json(orient='records')))
            with open(f"{dataPath}/dhis2gml/dhis2/{args.gmlFileName}_geojson_{datetime.now().strftime('%Y-%m')}.json",'w') as fm:
                json.dump({"organisationUnits":matchedGisGeojson}, fm, ensure_ascii=False, indent=2)
def matchGML(data=[],ous=[]):
    newMap=[]
    for d in data:
        for o in ous:
            if 'id' in o:
                if d['id'] == o['id']:
                    d['geometry'] = {
                        'type': o['geometry.type'],
                        'coordinates': o['geometry.coordinates']
                    }
                    newMap.append(d)
                else:
                    pass
            else:
                pass
    return newMap
if __name__ == "__main__":
    main(sys.argv[1:])
