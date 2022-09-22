import WaySegment as ws
import json

if __name__=="__main__":

    f = open("beacon-street.json")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()


    roads = data["ways"]["roads"]

    # 2D array, each inner array is a way which is a collection of way segments
    ways = []

    for road_id in roads:
        noderefs = data["ways"]["roads"][road_id]["noderefs"]


        ways.append(ws.WaySegment(noderefs, data))
        # need to split at stop lights/ intersections -FINISH

    
    for way in ways:
        print(way)