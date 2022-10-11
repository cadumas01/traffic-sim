import way_segment as ws
import json
from intersection import Intersection


# contains a dictionary of way segments
class Network:

    def __init__(self, data):
        self.data = data
        self.way_segments = {}  # a dictionary of roads and nonroads where each is a dcitionary of waysegments (indexed via id where id is startref_endref)
        self.assemble_ways()

        # add all attractions to appropriate way seg
        self.add_attractions()

        self.intersections = {}
        self.add_intersections() # dictionary indexed via noderef that the intersection is associated to

    # pass noderefs of a single way and return array of waysegments split at intersections (need to work on this)
    def noderefs_to_waysegs(self, way_id, category, noderefs, split, reverse_way):
        waysegs = []
        segment_start_index = 0
        # need to split at stop lights/ intersections -FINISH
        for i in range(len(noderefs)):
            if noderefs[i] in self.data["nodes"]["attractions"] or i == len(noderefs) -1: # attractions, break up the segment, or end of segment
                noderefs_segment = noderefs[segment_start_index:i+1]

                waysegs.append(ws.WaySegment(way_id, category, noderefs_segment, self.data, split, reverse_way))
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
                    way_segs += self.noderefs_to_waysegs(way_id, category, list(reversed(noderefs)), split, reverse_way=True)

                # right-way way_segments
                way_segs += self.noderefs_to_waysegs(way_id, category, noderefs, split, reverse_way=False)

                for way_seg in way_segs:
                    # print(f"way_seg_id = {way_seg.id}")
                    self.way_segments[category][way_seg.id] = way_seg
               

    # returns true if current road is a two way road
    def is_two_way(self, way_dict):
        return ("oneway" in way_dict and way_dict["oneway"] != "no") or ("lanes" in way_dict and int(way_dict["lanes"]) >= 2)


    # associates each attraction node with its closest way segment (and appropriate connection node)
    def add_attractions(self):
        for noderef, attraction in self.data["nodes"]["attractions"].items():
            min_val = 100000
            min_t = -1
            way_seg_index = -1

            # maybe use vectorized operations??
            for way_seg_id in self.way_segments["roads"]: # loop through each of the roads
                way_segment = self.way_segments["roads"][way_seg_id]
                minimum, t = way_segment.min_node_distance(attraction["lon"], attraction["lat"])
                if minimum < min_val:
                    min_val = minimum
                    min_t = t
                    way_seg_index = way_seg_id
                                      
            self.way_segments["roads"][way_seg_id].add_attraction(noderef, min_t)


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
            self.intersections[node_ref] = Intersection(node_ref, outgoing_way_segment_refs, incoming_way_segment_refs)

        #print('\n'.join(['\t'.join([str(len(cell)) for cell in row]) for row in table]))
        # for intersection in list(self.intersections.values()):
        #     print(intersection)


    
        

    def __str__(self):
        s = ""
        s += f"Network containing:\n\t{len(self.way_segments['roads'])} road way_segments"
        s += f"\t{len(self.way_segments['nonroads'])} nonroad way_segments"
        s += f"\t{len(self.intersections)} intersections"

        return s



if __name__=="__main__":

    f = open("test-map.json")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    net = Network(data)
    print(net)
    

