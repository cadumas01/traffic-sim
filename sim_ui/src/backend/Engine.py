"""
At each time step:
1. Read data about population to determine which nodes to launch Travelers from
    (For now: randomly generate travelers)
2. Create new Traveler at origin node, give it a mode at random,
    generate a destination and give it the path to that destination
3. Check if any traveler is on an intersection
    If so, increment its path. If it has reached its destination, delete it
4. Increment all existing travelers
"""

import random
import json
from network import Network
from traveler import Traveler

file = open('salisbury-road-large.json')
data = json.load(file)

travelers = []
network = Network(data)

class Engine:
    def __init__(self, t):
        while t > 0:
            self.gen_travelers(data["nodes"]["attractions"].keys(), 5)
            for traveler in travelers:
                traveler.increment()
                if traveler.is_done == True:
                    travelers.remove(traveler)
                    del traveler
            t -= 1

    # Takes array of nodes, creates x travelers at random across the nodes
    def gen_travelers(self, nodes, x):
        while x > 0:
            i = random.randint(0, len(nodes) - 1)
            origin_node = nodes[i]
            origin_way_seg = self.get_way_seg(origin_node)
            origin_intersection = self.find_nearest_intersection(origin_node, origin_way_seg)
            k =  random.randint(0, len(nodes) - 1)
            end_node = nodes[k]
            end_way_seg = self.get_way_seg(end_node)
            end_intersection = self.find_nearest_intersection(end_node, end_way_seg)
            t = origin_way_seg.attractions[origin_node].t
            end_t = end_way_seg.attractions[end_node].t
            traveler = Traveler("Car", t, end_t, origin_way_seg, network.shortest_path(origin_intersection, end_intersection), False, False)
            travelers.append(traveler)
            x -= 1

    def find_nearest_intersection(attraction_id, way_seg):
        t = way_seg.attractions[attraction_id].t
        total_t = way_seg.t_len
        if t / total_t < 0.5:
            return way_seg.start_ref
        else:
            return way_seg.end_ref

    # Loops through every road in the map. For every way_segment in every road, 
    # if the given node exists in its dictionary of nodes, return that way_segment
    def get_way_seg(node):
        for way_segment in network.way_segments["roads"]:
            if node in network.way_segments["roads"][way_segment].attractions.keys():
                return way_segment