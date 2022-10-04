class Traveler:

    # Each origin node should have a property that is the way segment associated with it
    # Are residential buildings the only origin nodes?
    # Proposal: Maybe we don't add way_segment into the initial JSON 
    # (which is purely for organizing the existing data)
    # But we need a function that goes through all of the attraction nodes that are also origin nodes
    # And determines what way_segment they fall under 

    # String mode (car, bike, pedestrian)
    # Dict origin_node 
    """
    origin_node: {
        "lat": x,
        "lon": y,
        "way_segment": segment (of type WaySegment)
    }
    """
    # Array path of dict elements giving lon and lat of travelers location at given time step
    # Or this could be something where we figure out which way_segments the traveler is going to travel on
    # Then when you find out that the traveler is no longer on their current segment you can increment 
    # 'path' and you'll see the next way_segment it needs to get onto
    """
    path: [
        "01": {
            "lon": 2,
            "lat": 1,
        }
        "02": {
            "lon": 3,
            "lat": 1
        }
        "03": {
            "lon": 4,
            "lat": 1
        }
    ]
    """
    """
    path: [
        strathmore_rd_brookline_01,
        clinton_path,
        beacon_st_brookline_inbound_08, 
        beacon_st_brookline_inbound_09, 
        beacon_st_brookline_inbound_10
    ]
    """
    # Potential intersection schema
    """
    intersections: {
        "beacon_street_englewood_01": {
            "lat": 4
            "lon": 1
            "way_segments": [
                beacon_st_brookline_inbound_08, 
                beacon_st_brookline_outbound_08,
                englewood_ave_01
            ]
        }
    }
    """
    # Should each way_segment have a property list of adjacent segments? 
    # Or it could have a property of which intersections it's bounded by and each intersection
    # Can have the property of which way_segments are connected to it
    def __init__(self, mode, origin_node, path, x, y):
        self.mode = mode
        self.origin_node = origin_node
        self.path = gen_path(origin_node) 
        self.x = origin_node.lon
        self.y = origin_node.lat

    def get_current_way_segment(x, y):
        return way_segment(x, y)

    # Has an origin node, gets a destination node, finds shortest path between them
    # Finds shortest path by some witchcraft
    def gen_path(node):
        path = []
        dest_node = gen_destination(node)
        segment = node.way_segment
        dest_segment = dest_node.way_segment
        while (segment != dest_segment) {
            path.append(segment)
            intersection = segment.intersection
            segment = intersection.way_segment
        }
        return path
        
    # Takes origin node, calculates prob of traveler going to any given destination from this origin
    # Randomly picks a destination based on those probabilities
    def gen_destination(node):
        return dest_node
        