import WaySegment as ws
import json


# pass noderefs of a single way and return array of waysegments split at intersections (need to work on this)
def noderefs_to_waysegs(noderefs, data):
    way = []
    segment_start_index = 0
    # need to split at stop lights/ intersections -FINISH
    for i in range(len(noderefs)):
        if noderefs[i] in data["nodes"]["attractions"] or i == len(noderefs) -1: # attractions, break up the segment, or end of segment
            #print(f"i = {i}, breaking up segment")
            noderefs_segment = noderefs[segment_start_index:i+1]
            way.append(ws.WaySegment(noderefs_segment, data))

            segment_start_index = i

    return way

if __name__=="__main__":

    f = open("beacon-street.json")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()


    roads = data["ways"]["roads"]

    # 2D array, each inner array is a way which is a collection of way segments
    ways = []

    # assemble ways 
    for road_id in roads:
        noderefs = data["ways"]["roads"][road_id]["noderefs"]

        ways.append(noderefs_to_waysegs(noderefs, data))

    # sample house id
    sample_house_id = "257578421"
    sample_house_x = data["nodes"]["attractions"][sample_house_id]["lon"]
    sample_house_y = data["nodes"]["attractions"][sample_house_id]["lat"]

    for way in ways:
        for way_seg in way:
            #print("----------------\n",way_seg)
            #print(way_seg.nodes_str())
            if way_seg.is_solution(sample_house_x, sample_house_y):
                print("Is solution")




