# pip install xmltodict
import xmltodict
import json
import pprint
import sys
import math


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
def normalize_coords(streets_data):

    min_lon, max_lon, min_lat, max_lat =  get_min_max_lon_lat(streets_data)

    mid_lat = (max_lat + min_lat) / 2
    width = lon_to_x(max_lon, mid_lat) - lon_to_x(min_lon, mid_lat)
    height = max_lat - min_lat

    width_scale = 1600
    occupied_horizontal_space = 1500

    height_scale = 900
    occupied_vertical_space = occupied_horizontal_space * height/ width

    vert_margin  = (height_scale - occupied_vertical_space) / 2 # determined by leftover space
    horiz_margin = (width_scale - occupied_horizontal_space) /2

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
                node["lat"] = height_scale - ((lat + min_lat ) * occupied_vertical_space / height + vert_margin)
            else:
                #
                node["lat"] = height_scale - ((lat - min_lat) * occupied_vertical_space / height + vert_margin)

    return streets_data



def lon_to_x(lon, mid_lat):
    return  lon * math.cos(math.radians(mid_lat))

def lat_to_y(lat, earth_radius):
    return  lat

# cleans xml file and reorganizes into dictionary
def xml_to_streets_data(xml_file):
    with open(xml_file  + ".xml") as xml:
        streets_data = xmltodict.parse(xml.read())["osm"]

        # Make its own function
        # adjust naming of node to nodes, way to ways and relation to relations
        for k in ["node", "way", "relation"]:
           rename_key(streets_data, k, k+"s")

        # for each node, way and relation, take the id and use it as a key in the newly created dictionary
        for element_type in ["nodes", "ways", "relations"]:
            #print("raw_data[elementtype]=", raw_data[element_type])
            
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
                for k in ["@id", "@uid", "@user", "@changeset", "@timestamp","@version"]:
                    del element[k] 

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
                
                # Categorizes ways into "roads" and "nonroads" - key insight: roads have a width
                elif element_type == "ways":
                    if "width" in element: # roads
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

        return streets_data


def write_json(dictionary, file_name):
    with open(file_name + ".json", 'w+', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)


# Removes "@" from any keys in the member value of an element
def handle_members(element):
    if "members" in element:
        members = element["members"]

        if type(members) is dict:
            members = [members]
        print("members = ", members)
        print(f"len(members) = {len(members)}")

        for i in range(len(members)):
            print(f"i={i}")
            print(f"len(members) = {len(members)}")
            print(f"members[i]={members[i]}, ")
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

    for f in ("salisbury-road-just-roads", "salisbury-road-large", "beacon-street", "comm-beacon"):
        print(f"\n {f}")
        write_json(normalize_coords(xml_to_streets_data(f)), f)
