import osm2gmns as og
net = og.getNetFromFile(r'small_beacon.osm',network_types=('railway','aeroway','auto','walk','bike'),\
                        POI=True)
# This is the command that grid2demand's documentation said to use, 
# But it generated the error "KeyError: 'light_rail'"
#net = og.getNetFromFile(r'small_beacon.osm',network_types=('railway','aeroway','auto','walk','bike'),\
#                           POI=True,default_lanes=True,default_speed=True)
og.connectPOIWithNet(net)
og.outputNetToCSV(net, 'gmns_files')