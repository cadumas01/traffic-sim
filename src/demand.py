

def get_node_weight(streets_data):
    for node in streets_data["node"]["attraction"]:
        if "amenity" in node:
            node_quality = node["amenity"]
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
        elif "public_transport" in node:
            node_quality = node["public_transport"]
            if node_quality == "station" or \
                node_quality == "stop_position" or \
                    node_quality == "platform":
                weight = 10
            else:
                weight = 1
        elif "leisure" in node:
            node_quality = node["leisure"]
            if node_quality == "park":
                weight = 20
            else:
                weight = 1
        elif "shop" in node:
            node_quality = node["shop"]
            if node_quality == "alcohol" or \
                node_quality == "bakery" or \
                    node_quality == "convenience":
                weight = 15
            else:
                weight = 1
        elif "addr:housenumber" in node:
            weight = 20
        else:
            weight = 1
        node["weight"] = weight
