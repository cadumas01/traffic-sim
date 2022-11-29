from cmath import cos
import way_segment as ws
import json
from intersection import Intersection
from node import Node
from dijkstar import Graph, find_path
from scipy import stats
import numpy as np
from sklearn.utils.extmath import cartesian
from itertools import product
import random



# contains a dictionary of way segments
class Network:

    def __init__(self, data):
        self.data = data
        self.way_segments = {}  # a dictionary of roads and nonroads where each is a dictionary of waysegments (indexed via id where id is startref_endref)
        self.intersections = {} 

        self.assemble_ways()

        # add all attractions to appropriate way seg and to self
        self.attractions = {}
        self.add_attractions()

        # dictionary of intersections indexed by noderef
        self.add_intersections() # dictionary indexed via noderef that the intersection is associated to

        self.make_graph()

        # attractions random variable. maps attraction (really index of attraction in list, use self.attraction_to_index) to weighted probability
        self.gen_weighted_attractions()

        # generates a new randomvariable (returns a random trip with probabilities calculated using gravity model)
        self.gen_gravity_model_trips()


    # checks if node is part of two separate ways
    def node_is_intersection(self, noderef):

        if noderef in self.intersections:
            return True
        else:

            # attractions ON the road are usually stop lights or stop signs
            if noderef in self.data["nodes"]["attractions"]:
                self.intersections[noderef] = None
                return True

            count = 0

            for way_segment in self.data["ways"]["roads"].values():
                if noderef in way_segment["noderefs"]:
                    count += 1
        
            # if more than a single way uses a node, it is an intersection
            if count > 1:
                self.intersections[noderef] = None
                return True
            else:
                return False


        # add intersection to self.intersections dictionary (leave the value blank as this will be filled in later)

    # pass noderefs of a single way and return array of waysegments split at intersections (need to work on this)
    def noderefs_to_waysegs(self, way_id, category, noderefs, split):
        waysegs = []
        segment_start_index = 0

        for i in range(len(noderefs)):

            # if we have a way_segment (bounded by two different nodes) or the way ends make a new way segment
            if (self.node_is_intersection(noderefs[i]) and segment_start_index != i) or i == len(noderefs) -1: # attractions, break up the segment, or end of segment
                noderefs_segment = noderefs[segment_start_index:i+1]

                waysegs.append(ws.WaySegment(way_id, category, noderefs_segment, self.data, split))
                segment_start_index = i

        return waysegs

    # creates waysegs and adds to list (under appropriate category type)
    def assemble_ways(self): 
        for category in ["roads", "nonroads"]:
            self.way_segments[category] = {}

            for way_id in self.data["ways"][category]:
                noderefs = self.data["ways"][category][way_id]["noderefs"]

                way_segs = []
                split = False

                # potential reverse-way way_segments
                if self.is_two_way(self.data["ways"][category][way_id]):
                    split = True
                    # split number of lanes in half and create a second set of one-way way segments in opposite direction
                    # If way_segment A has id: nodei_nodej. Then reverse of way_segment A has id: nodej_nodei
                    way_segs += self.noderefs_to_waysegs(way_id, category, list(reversed(noderefs)), split)

                # right-way way_segments
                way_segs += self.noderefs_to_waysegs(way_id, category, noderefs, split)

                for way_seg in way_segs:
                    self.way_segments[category][way_seg.id] = way_seg
               

    # returns true if current road is a two way road
    def is_two_way(self, way_dict):
        return ("oneway" in way_dict and way_dict["oneway"] != "no") or ("lanes" in way_dict and int(way_dict["lanes"]) >= 2)


    
    # associates each attraction node with its closest way segment (and appropriate connection node)
    def add_attractions(self):
        for noderef, attraction in self.data["nodes"]["attractions"].items():
            min_val = 100000
            min_t = -1
            min_way_seg_id = -1

            # maybe use vectorized operations??
            for way_seg_id in self.way_segments["roads"]: # loop through each of the roads
                way_segment = self.way_segments["roads"][way_seg_id]
                minimum, t = way_segment.min_node_distance(attraction["lon"], attraction["lat"])
                if minimum < min_val:
                    min_val = minimum
                    min_t = t
                    min_way_seg_id = way_seg_id

            attract_dict = self.data["nodes"]["attractions"][noderef]

            attraction_weight = attract_dict["weight"] # maybe update to .5 its value if we also create an attraction for the reverse road
         
        
            # Since a two lane road is really 2 one way way_segments we must also associate an attraction to the 
            # corresponding opposite way_segment (i.e. reverse the nodes in the way segment id)
            reverse_id = self.reverse_way_seg_id(min_way_seg_id)
            if reverse_id in self.way_segments["roads"]:
                attraction_weight = attraction_weight / 2
                # min_t is the t_value for the proper direction way_segment so if 
                # t_len = 5 and on proper_way_segment, t= 1 then for reverse, t=4
                t_value = self.way_segments["roads"][reverse_id].t_len - min_t

                dup_attraction = Node(noderef, "attraction", t_value, attract_dict["lon"], attract_dict["lat"], attraction_weight)
                self.way_segments["roads"][reverse_id].add_attraction(dup_attraction) 
                
                self.attractions[reverse_id] = dup_attraction


            attraction = Node(noderef, "attraction", min_t, attract_dict["lon"], attract_dict["lat"], attraction_weight)
            self.way_segments["roads"][min_way_seg_id].add_attraction(attraction)
            # add attraction to network object
            self.attractions[min_way_seg_id] = attraction
            

    # creates intersections between touching way_segments
    # see diagram in shared google folder
    def add_intersections(self):
        temp = []        # temporary list of all nodes which start or end a way_segment

        for way_seg in self.way_segments["roads"].values():
            temp += [way_seg.start_ref, way_seg.end_ref]

        # list(set) of all nodes which start or end a way_segment
        start_end_nodes = list(set(temp))
      
        n = len(start_end_nodes)

        # maps table index to node_ref
        index_to_ref = {i: start_end_nodes[i] for i in range(n)}

        # maps node_ref to table index
        ref_to_index = {start_end_nodes[i]: i for i in range(n)}

        # n x n table (adjacency matrix) where each row corresponds to a start node and each col corresponds end node. table[r][c] represents the list of way segments which has end points r (start) and c (end)
        table = [[[] for c in range(n) ] for r in range(n)] 

        for way_seg_id, way_seg in self.way_segments["roads"].items():
            r = ref_to_index[way_seg.start_ref]
            c = ref_to_index[way_seg.end_ref]
           
            table[r][c].append(way_seg_id) 


        # "sum" the way_segments in each row,r, and those are the way_segments associated with start/end node (intersection) with id index_to_ref[r]
        for i in range(len(table)):

            # sum rows to get outgoing way_segments
            row = table[i]
            outgoing_way_segment_refs = sum(list(filter(None, row )), []) # flattened 2d list into 1d list

            # sum cols to get incoming way_segments
            col = [row[i] for row in table]
            incoming_way_segment_refs = sum(list(filter(None, col )), [])

            node_ref = index_to_ref[i]

            # create new intersection and add to dictionary of intersections (key is noderef)
            # should just be updating the value with a prexiting key that we put into dictionary when splitting ways into way_segments
            self.intersections[node_ref] = Intersection(node_ref, outgoing_way_segment_refs, incoming_way_segment_refs)


    # Makes Dijkstrar Graph reprsentation where nodes are Insersection refs and edges are way_segment refs with corrseponding weights
    def make_graph(self):
        self.graph = Graph()

        # go through each (road) way segment and find the two intersections it is bounded by 
        # (indexed via noderefs which each correspond to an Intersection object)
        for road in self.way_segments["roads"].values():
            # add edge to graph from start intersection to end intersection where the edge is:(waysegment weight,  waysegment id) 
            self.graph.add_edge(road.start_ref, road.end_ref, (road.weight, road.id))
        

    # returns PathInfo for shortest path
    def shortest_path(self, start_intersection_ref, end_intersection_ref):
        def cost_func(u, v, edge, prev_edge):
            weight, name = edge
            return weight

        return find_path(self.graph, start_intersection_ref, end_intersection_ref, cost_func=cost_func)
        


    ''' 
    Creates a scipy random variable with probabilities of choosing any attraction in the network
    event values are really indices of attractions (since easier to work with numeric events)
    '''
    def gen_weighted_attractions(self):
        # At this point, no distinguishing between different attraction types
        sum_weight = sum([a.weight for a in self.attractions.values()])

        attractions_list = list(self.attractions.values())
        self.index_to_attraction= {i: attractions_list[i].id for i in range(len(attractions_list))}

        probabilities = [a.weight/sum_weight for a in attractions_list]
      
        self.weighted_attractions = stats.rv_discrete(name='weighted_attractions', values=(range(len(attractions_list)), probabilities))

    
    # for each pair of attractions, returns probability of picking that pair (as end/destination or vice versa)
    def gen_gravity_model_trips(self):
        self.attractions_list = list(self.attractions.values())

        # indexed via index
        def gravity_score(index_pair_str) -> float:
           
            a1 = int(index_pair_str[0])
            a2 = int(index_pair_str[1])
            if self.attractions_list[a1].id == self.attractions_list[a2].id:
                return 0.0 # no traveling from self to self
            else:  
                return (self.attractions_list[a1].weight) * (self.attractions_list[a2].weight) 

        # indexed via (a1_index, a2_index)
        pair_indices = np.array([[(i,j) for j in range(len(self.attractions_list))] for i in range(len(self.attractions_list))])

        pair_weights = np.apply_along_axis(gravity_score, 2, pair_indices)
        
        # sum of all weights
        sum_weight = np.sum(pair_weights)
        sum_weight_arr = sum_weight * np.ones_like(pair_weights)
        pair_probs = pair_weights / sum_weight_arr

        # used by random_trip_pair()
        self.flat_pair_probs = pair_probs.reshape(1, pair_probs.size)[0]

        # used by random_trip_pair()
        self.flat_pair_indices = [(pair[0],pair[1]) for pair in pair_indices.reshape(pair_probs.size, -1)]
 
            
    
    # returns a randomly generated trip pair (from weighted)
    def random_trips_pairs(self, k):
        trips_indices = random.choices(self.flat_pair_indices, self.flat_pair_probs, k=k)

        trips = []
        for (i,j) in trips_indices:
            trips.append((self.index_to_attraction[i], self.index_to_attraction[j]))
        return trips




    def __str__(self):
        s = ""
        s += f"Network containing:\n\t{len(self.way_segments['roads'])} road way_segments"
        s += f"\t{len(self.way_segments['nonroads'])} nonroad way_segments"
        s += f"\t{len(self.intersections)} intersections"
        s += f"\t{len(self.attractions)} attractions"

        return s


    def reverse_way_seg_id(self, way_seg_id):
        parts = way_seg_id.split("_")
        return f"{parts[1]}_{parts[0]}"


if __name__=="__main__":

    f = open("test-map.json", encoding="utf-8")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    net = Network(data)
    

    


