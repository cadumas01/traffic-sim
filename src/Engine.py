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
import time

file = open('test-map.json', encoding="utf-8")
data = json.load(file)

network = Network(data)

class Engine:

    def __init__(self, ticks, network):
        self.network = network
        self.travelers = []
        for tick in range(ticks):
            
            if tick < 5:
                self.gen_travelers(list(data["nodes"]["attractions"].keys()), 5)
            print("XXXXXXXXXXX")
            print(f"Time: {tick}")
            print(f"len(travelers) = {len(self.travelers)}")
            for traveler in self.travelers:
                print("\n ", traveler)
                traveler.increment()
                if traveler.is_done:
                    print("removing traveler")
                    self.travelers.remove(traveler)
                    del traveler
            time.sleep(.01)

    # Takes array of nodes, creates x travelers at random across the nodes
    def gen_travelers(self, nodes, n):

        for _ in range(n):
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
            path = []

            try: # sometimes there is no path between these two intersections so just break out and try again
                edges = network.shortest_path(origin_intersection, end_intersection)
            except:
                continue


            for edge in edges.edges:
                path.append(self.network.way_segments["roads"][edge[1]])
            if end_way_seg not in path:
                path.append(end_way_seg)

            #print(f"\ncreating new traveler with end t = {end_t}, path = {path}")
            traveler = Traveler("Car", t, end_t, origin_way_seg, path, False, False)
            self.travelers.append(traveler)
            

    def find_nearest_intersection(self, attraction_id, way_seg):
        t = way_seg.attractions[attraction_id].t
        total_t = way_seg.t_len
        if t / total_t < 0.5:
            return way_seg.start_ref
        else:
            return way_seg.end_ref

    # Loops through every road in the map. For every way_segment in every road, 
    # if the given node exists in its dictionary of nodes, return that way_segment
    def get_way_seg(self, node_id):
        for way_segment in network.way_segments["roads"].values():
            #print(f"Here are {way_segment.id} atractions = {way_segment.attractions}")
            if node_id in way_segment.attractions:
                return way_segment

if __name__ == "__main__":
    engine = Engine(500, network)