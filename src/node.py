class Node:
    def __init__(self, id, type, t, lon, lat, weight=None):
        self.id = id
        self.type = type
        self.t = t # t value along appropriate way_segment
        self.lon = lon
        self.lat = lat
        self.weight = weight
