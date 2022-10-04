import way_segment as ws
import json

# contains a list of way_segment
class Way:
    def __init__(self, data, noderefs):
        self.data = data
        self.noderefs = noderefs
        self.way_segments = self.noderefs_to_waysegs()  # list of way segments
        
    
    # pass noderefs of a single way and return array of waysegments split at intersections (need to work on this)
    def noderefs_to_waysegs(self):
        waysegs = []
        segment_start_index = 0
        # need to split at stop lights/ intersections -FINISH
        for i in range(len(self.noderefs)):
            if self.noderefs[i] in self.data["nodes"]["attractions"] or i == len(self.noderefs) -1: # attractions, break up the segment, or end of segment
                #print(f"i = {i}, breaking up segment")
                noderefs_segment = self.noderefs[segment_start_index:i+1]
                waysegs.append(ws.WaySegment(noderefs_segment, self.data))
                segment_start_index = i

        return waysegs




# ways contains a list of ways
class Ways:

    def __init__(self, data):
        self.data = data
        self.ways = {}  # Ways is a dictionary of roads and nonraods where each is a list where each element is a way 
        self.assemble_ways()

        # add all attractions to appropriate way seg
        self.add_attractions()


    # creates waysegs and adds to list (under appropriate category type)
    def assemble_ways(self): 
        for category in ["roads", "nonroads"]:
            for way_id in self.data["ways"][category]:
                noderefs = self.data["ways"][category][way_id]["noderefs"]
                if category in self.ways:
                    self.ways[category].append(Way(self.data, noderefs))
                else:
                    self.ways[category] = [Way(self.data, noderefs)]


    # associates each attraction node with its closest way segment (and appropriate connection node)
    def add_attractions(self):
        for noderef, attraction in self.data["nodes"]["attractions"].items():
            min_val = 100000
            way_segment_index = -1
            min_t = -1
            way_index = -1
            way_seg_index = -1

            # maybe use vectorized operations??
            for i in range(len(self.ways["roads"])): # loop through each of the roads
                road = self.ways["roads"][i]
                for j in range(len(road.way_segments)):
                    minimum, t = (road.way_segments[j]).min_node_distance(attraction["lon"], attraction["lat"])
                    if minimum < min_val:
                        min_val = minimum
                        min_t = t
                        way_seg_index = j
                        way_index = i
                
            self.ways["roads"][way_index].way_segments[way_seg_index].add_attraction(noderef, min_t)
            print("just added a attraction noderef")


if __name__=="__main__":

    f = open("test-map.json")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    ways = Ways(data)
    print(ways.ways)



