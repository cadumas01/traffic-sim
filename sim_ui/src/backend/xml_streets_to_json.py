# pip install xmltodict
import xmltodict
import json
import pprint
import sys


def xml_to_json(xml_file):
    with open(xml_file  + ".xml") as xml:
        raw_data = xmltodict.parse(xml.read())["osm"]

        # Make its own function
        # adjust naming of node to nodes, way to ways and relation to relations
        for k in ["node", "way", "relation"]:
           rename_key(raw_data, k, k+"s")

        # for each node, way and relation, take the id and use it as a key in the newly created dictionary
        for element_type in ["nodes", "ways", "relations"]:
            #print("raw_data[elementtype]=", raw_data[element_type])
            
            if element_type not in raw_data:
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

            for element in raw_data[element_type]: # elements is a list of dictionaries -> need to transform into dictionary of dictionaries
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
            del raw_data[element_type]
            raw_data[element_type] = new_elements

        with open(xml_file + ".json", 'w+', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)


# Removes "@" from any keys in the member value of an element
def handle_members(element):
    if "members" in element:
        members = element["members"]

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
        element["node-refs"] = refs


# Adjust how tags are organized and puts them higher up in the data structure with lon and lat
def handle_tags(element):
    # If a list of "tag" dictionaries exist, go into each one and adjust it so the key and value are just part of the regular dictionary
    if "tag" in element:
        # tags is a list of dictionaries, each with the format: {"@k": "some_key", "@v": "some_value"}
        # Must transorm this list of dictionaries as dictionary key value pairs in the regular dictionary
        tags = element["tag"]
        print("tags = " , tags)

        # if there is only 1 tag, it is just a dictionary
        if type(tags) is dict:
            key = tags["@k"]
            value = tags["@v"]
        else:
            # if multiple tags, there is a list of tags
            for tag in tags:
                print("tag = ", tag)
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

    xml_to_json("salisbury-road-just-roads")
    xml_to_json("beacon-street")
    xml_to_json("salisbury-road-large")