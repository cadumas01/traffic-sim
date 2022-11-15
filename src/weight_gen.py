import numpy as np

def add_building_to_attractions(new_elements):
    non_roads = new_elements["ways"]["non-roads"]
    relations = new_elements["relations"]
    attractions = new_elements["attractions"]
    for way_id in non_roads:
        if "building" in non_roads[way_id].values():
            coords = mean_of_way_nodes(new_elements, way_id)
            non_roads[way_id]["lon"] = coords[0]
            non_roads[way_id]["lat"] = coords[1]
            del non_roads[way_id]["noderefs"]
            attractions[way_id] = non_roads[way_id]
    for relation_id in relations:
        if "building" in relations[relation_id].values():
            coords = mean_of_relation_nodes(new_elements, relation_id)
            relations[relation_id]["lon"] = coords[0]
            relations[relation_id]["lat"] = coords[1]
            del relations[relation_id]["members"]
            attractions[relation_id] = relations[relation_id]

def mean_of_way_nodes(new_elements, way_id):
    non_roads = new_elements["ways"]["non-roads"]
    connections = new_elements["nodes"]["connections"]
    lons = []
    lats = []
    for node_ref in non_roads[way_id]["noderefs"]:
        if node_ref in connections:
            lons.append(connections[node_ref]["lon"])
            lats.append(connections[node_ref]["lat"])
    return[np.mean(lons), np.mean(lats)]

def mean_of_relation_nodes(new_elements, relation_id):
    relations = new_elements["relations"]
    connections = new_elements["connections"]
    lons = []
    lats = []
    for member in relations[relation_id]["members"]:
        node_id = member["ref"]
        if node_id in connections:
            lons.append(connections[node_id]["lon"])
            lats.append(connections[node_id]["lat"])
    return[np.mean(lons), np.mean(lats)]