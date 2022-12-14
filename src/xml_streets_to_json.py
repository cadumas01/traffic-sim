# pip install xmltodict
import xmltodict
import json
import pprint
import sys
import math
import numpy as np




# main function
def xml_streets_to_json(file=None,screen_width=1600,screen_height=900):
    print(f"screen_width = {screen_width}, screen_height = {screen_height}")

    # default files
    if file == None:
        file= "maps/cleveland-circle.osm" 
    
    streets_data = xml_to_streets_data(file)

    # adjusts lon / lat coords to screen coords
    normalized_street_data = normalize_coords(streets_data, screen_width, screen_height) 

    write_json(normalized_street_data, file[:-4])



def get_min_max_lon_lat(streets_data):
    min_lon = 10000
    min_lat = 10000

    max_lon = -10000
    max_lat = -10000
       
    # First loops to find mins and maxes and create scale factors
    for sub_category_dict in streets_data["nodes"].values():
        for node in sub_category_dict.values():

            lat = float(node["lat"])
            node["lat"] = lat

            lon = float(node["lon"])
            node["lon"] = lon


            if lat < min_lat:
                min_lat = lat
            elif lat > max_lat:
                max_lat = lat

            if lon < min_lon:
                min_lon= lon
            elif lon > max_lon:
                max_lon = lon

    return min_lon, max_lon, min_lat, max_lat

# normalizes coords to 
def normalize_coords(streets_data,screen_width,screen_height):

    min_lon, max_lon, min_lat, max_lat =  get_min_max_lon_lat(streets_data)

    mid_lat = (max_lat + min_lat) / 2
    width = lon_to_x(max_lon, mid_lat) - lon_to_x(min_lon, mid_lat)
    height = max_lat - min_lat

 
    occupied_horizontal_space = .9375 * screen_width # for width = 1600, occupied horiz space = 1500

  
    occupied_vertical_space = occupied_horizontal_space * height/ width

    vert_margin  = (screen_height - occupied_vertical_space) / 2 # determined by leftover space
    horiz_margin = (screen_width - occupied_horizontal_space) /2

    # add occupied space data to bounds dict in json file
    streets_data["display_bounds"] = {}
    streets_data["display_bounds"]["occupied_vertical_space"] = occupied_vertical_space
    streets_data["display_bounds"]["occupied_horizontal_space"] = occupied_horizontal_space



    # width should be 1400
    # height will be scaled normally as well, so variable height (since width:height ratio is not constant), buffer will be added to make it constant

    # Lat and lon to x,y for small area
    # https://stackoverflow.com/questions/16266809/convert-from-latitude-longitude-to-x-y

    # Normalize lon and lat to be x and y on a 1400 wide by 700 tall grid, plus 100 pixel margins (top, bottom, left, right) = 1600 wide, by 900 tall grid
    for sub_category_dict in streets_data["nodes"].values():
        for node in sub_category_dict.values():
            lon = node["lon"]
            lat = node["lat"]

            # Centering lon and lat
            # if Westmost lon is west of lon=0, move everything to right
            # If Westmost lon is east of lon=0, move everything to left
            if min_lon < 0:
                node["lon"] = (lon_to_x(lon, mid_lat)  - lon_to_x(min_lon, mid_lat))  * occupied_horizontal_space/width + horiz_margin
            else:
                node["lon"] = (lon_to_x(lon, mid_lat)  + lon_to_x(min_lon, mid_lat)) * occupied_horizontal_space/width + horiz_margin
    
            # if Northmost lat is south of lat=0, move everything up
            # If Northmost lat is north of lon=0, move everything to down  
            # Must subtract everything from height_scale=900 so because (0,0) is top left and positive y is down
            if min_lat < 0:
                # OLD WAY of ADJUSTING WHERE ORIGIN IS BEFORE PLOTTING
                # node["lat"] = height_scale - ((lat + min_lat ) * occupied_vertical_space / height + vert_margin)
                node["lat"] = ((lat + min_lat ) * occupied_vertical_space / height + vert_margin)
            else:
                # OLD WAY of ADJUSTING WHERE ORIGIN IS BEFORE PLOTTING
                # node["lat"] = height_scale - ((lat - min_lat) * occupied_vertical_space / height + vert_margin)
                node["lat"] = ((lat - min_lat) * occupied_vertical_space / height + vert_margin)

    return streets_data



def lon_to_x(lon, mid_lat):
    return  lon * math.cos(math.radians(mid_lat))

def lat_to_y(lat, earth_radius):
    return  lat

# cleans xml file and reorganizes into dictionary
def xml_to_streets_data(map_file):
    with open(map_file, encoding="utf-8") as f:
        streets_data = xmltodict.parse(f.read())["osm"]

        # Make its own function
        # adjust naming of node to nodes, way to ways and relation to relations
        for k in ["node", "way", "relation"]:
           rename_key(streets_data, k, k+"s")

        # for each node, way and relation, take the id and use it as a key in the newly created dictionary
        for element_type in ["nodes", "ways", "relations"]:
            
            if element_type not in streets_data:
                continue

            new_elements = {} # a dictionary(elements) of dictionarys(individual element)

            # nodes has two sub dictionaries: connections and attractions
            if element_type == "nodes":
                new_elements["connections"] = {}
                new_elements["attractions"] = {}

            if element_type == "ways":
                new_elements["roads"] = {}
                new_elements["nonroads"] = {}
                new_elements["rails"] = {}

            for element in streets_data[element_type]: # elements is a list of dictionaries -> need to transform into dictionary of dictionaries
                id = element["@id"]

                # remove unnecessary keys/values for each element
                for k in ["@id", "@uid", "@user", "@changeset", "@timestamp","@version", "@visible"]:
                    if k in element:
                        del element[k]  

                # dictionary of cumulative attraction weights by category
                sum_attraction_weights = {}


                # remove any "@" from keys
                element = remove_AT_from_keys(element)
            
                # handle node refs
                handle_node_refs(element)

                handle_tags(element)

                rename_key(element,"member", "members")

                # If the element is of "relation type", go into the "member" value and remove @s from tags
                handle_members(element)

                # Categorizes nodes into "connections"(just lat and lon) or "attractions"
                if element_type == "nodes":
                    if len(element) == 2: # if the element is a node and just has lon and lat, it is a connection
                        new_elements["connections"][id] = element
                    else:
                        new_elements["attractions"][id] = element
                        attraction_weight, category = set_weight_and_category(new_elements["attractions"], id)

                        if category not in sum_attraction_weights:
                            sum_attraction_weights[category] = 0
                        else:
                            sum_attraction_weights[category] += attraction_weight
                
                # Categorizes ways into "roads" and "nonroads" - key insight: roads have a "width" or "highway"
                elif element_type == "ways":
                    if "width" in element or "highway" in element: # roads
                        new_elements["roads"][id] = element
                    elif "railway" in element: # rails
                        new_elements["rails"][id] = element
                    else:
                        new_elements["nonroads"][id] = element

                else:
                    # add refined element to new dict of elements, for relations
                    new_elements[id] = element
            
            # delete old elements list and add new elements list
            del streets_data[element_type]
            streets_data[element_type] = new_elements

         #streets_data["sum_attraction_weight"] = sum_attraction_weights
         
        for element in streets_data["ways"]["nonroads"]:
            if add_building_to_attractions(streets_data, element, "nonroads") == True:
                update_weights_and_category(streets_data, element, sum_attraction_weights)

        for element in streets_data["relations"]:
            if add_building_to_attractions(streets_data, element, "relations") == True:
                update_weights_and_category(streets_data, element, sum_attraction_weights)

        if "bounds" in streets_data:
            streets_data["bounds"] = remove_AT_from_keys(streets_data["bounds"])

        return streets_data

# for each (attraction) node, set weight and category based on attributes of the node
# returns weight, category
def set_weight_and_category(elements, node):

    category = ""

    if "amenity" in elements[node]:
        node_quality = elements[node]["amenity"]
        if node_quality == "school" or \
            node_quality == "college":
            weight = 100
        elif node_quality == "place_of_worship":
            weight = 50
        elif node_quality == "restaurant" or \
            node_quality == "bar" or \
                node_quality == "cafe":
            weight = 25
        elif node_quality == "bank" or \
            node_quality == "library" or \
                node_quality == "fire_station" or \
                    node_quality == "bicycle_rental":
            weight = 15
        else:
            weight = 1
        
        category = "amenity"
    elif "public_transport" in elements[node]:
        node_quality = elements[node]["public_transport"]
        if node_quality == "station" or \
            node_quality == "stop_position" or \
                node_quality == "platform":
            weight = 10
        else:
            weight = 1

        category = "public_transport"
    elif "leisure" in elements[node]:
        node_quality = elements[node]["leisure"]
        if node_quality == "park":
            weight = 20
        else:
            weight = 1
        
        category = "leisure"
    elif "shop" in elements[node]:
        node_quality = elements[node]["shop"]
        if node_quality == "alcohol" or \
            node_quality == "bakery" or \
                node_quality == "convenience":
            weight = 15
        else:
            weight = 1
        
        category = "shop"
    elif "addr:housenumber" in elements[node]:
        weight = 20
        
        category = "residence"
    else:
        weight = 1
        category = "other"

    elements[node]["weight"] = weight
    elements[node]["category"] = category

    return weight, category
        
# add building in "relations" or "ways" -> "non-roads" to dictionary of attraction nodes
def add_building_to_attractions(streets_data, node_id, type):

    if type == "nonroads":
        dict_location = streets_data["ways"][type]
        node_location = "noderefs"
    else:
        # type will be "relations"
        dict_location = streets_data[type]
        node_location = "members"

    attractions = streets_data["nodes"]["attractions"]

    if "building" in dict_location[node_id]:

        # avg position of nodes that make up the way or relation
        coords = get_non_node_coords(streets_data, node_id, type)

        # new entry to be added to attractions
        new_attraction = {}

        new_attraction.update(dict_location[node_id])

        new_attraction["lon"] = coords[0]
        new_attraction["lat"] = coords[1]
        del new_attraction[node_location]

        # add entry to attractions
        attractions[node_id] = new_attraction
        
        return True

    else:
        return False

# get mean of node coords in non-node structure (relation or way)
def get_non_node_coords(streets_data, node_id, type):

    if type == "nonroads":
        dict_location = streets_data["ways"][type]
        node_location = "noderefs"
    else:
        # type will be "relations"
        dict_location = streets_data[type]
        node_location = "members"

    connections = streets_data["nodes"]["connections"]

    lons = []
    lats = []

    # get node_ref of entry in dictionary 
    for node_ref in dict_location[node_id][node_location]:
        
        if type == "relations":
            
            # relation is of the form:
            # members: [ {"type": way,
            #             "ref": 695843987,
            #             "role": "outer"} ]

            nonroads = streets_data["ways"]["nonroads"]
            way_ref = node_ref["ref"]
            # now we're looking at way_ref = members -> "ref"
            # eg: 695843987

            # way_ref may be a way in "ways" -> "nonroads" 
            # in this case we loop through the noderefs in the noderefs of that way
            if way_ref in nonroads:
                for node_ref in nonroads[way_ref]["noderefs"]:
                    if node_ref in connections:
                        lons.append(float(connections[node_ref]["lon"]))
                        lats.append(float(connections[node_ref]["lat"]))
            
            # way_ref may also be just a node in connections
            # in this case we only need to append lon and lat values for that single node
            else:
                if way_ref in connections:
                    lons.append(float(connections[node_ref]["lon"]))
                    lats.append(float(connections[node_ref]["lat"]))

        # if the non-node structure is of type "nonroads" we simply add values for each connection node
        else:
            if node_ref in connections:
                lons.append(float(connections[node_ref]["lon"]))
                lats.append(float(connections[node_ref]["lat"]))

    return[np.mean(lons), np.mean(lats)]

def update_weights_and_category(streets_data, element, sum_attraction_weights):
    attraction_weight, category = set_weight_and_category(streets_data["nodes"]["attractions"], element)

    if category not in sum_attraction_weights:
        sum_attraction_weights[category] = 0
    else:
        sum_attraction_weights[category] += attraction_weight

def write_json(dictionary, file_name):
    with open(file_name + ".json", 'w+', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)


# Removes "@" from any keys in the member value of an element
def handle_members(element):
    if "members" in element:
        members = element["members"]

        if type(members) is dict:
            members = [members]

        for i in range(len(members)):
            members[i] = remove_AT_from_keys(members[i])


# for "ways" there is a list of dictonaries, each containing a single key-value pair with reference to a node
# Must put all node references in an ordered list
def handle_node_refs(element): 
    if "nd" in element:
        refs = []
        for d in element["nd"]:
            ref = d["@ref"]
            refs.append(ref)               

        # delete element["nd"], rename key to "node-refs" and set element["node-refs"] to the orderd list of refs
        del element["nd"]
        element["noderefs"] = refs


# Adjust how tags are organized and puts them higher up in the data structure with lon and lat
def handle_tags(element):
    # If a list of "tag" dictionaries exist, go into each one and adjust it so the key and value are just part of the regular dictionary
    if "tag" in element:
        # tags is a list of dictionaries, each with the format: {"@k": "some_key", "@v": "some_value"}
        # Must transorm this list of dictionaries as dictionary key value pairs in the regular dictionary
        tags = element["tag"]

        # if there is only 1 tag, it is just a dictionary
        if type(tags) is dict:
            key = tags["@k"]
            value = tags["@v"]
        else:
            # if multiple tags, there is a list of tags
            for tag in tags:
                key = tag["@k"]
                value = tag["@v"]
            
                # Add a key value pair to the main element dictionary
                element[key] = value
    
        # key/value pairs extracted, delete "tag" list of dictionaries
        del element["tag"]


# returns a dictionary with the new_key instead of the old key
def rename_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)
        

# returns new dictionary with ATs removesd
def remove_AT_from_keys(dictionary):
    def remove_AT(s):
        return s.replace("@", "")

    keys = list(map(remove_AT, dictionary.keys()))

    return dict(zip(keys,list(dictionary.values()))) 



if __name__ == "__main__":
    xml_streets_to_json()
