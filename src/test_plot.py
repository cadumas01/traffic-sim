import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import ways


# OUTDATED !!!
if __name__ == "__main__":
    fig, ax = plt.subplots()

    if len(sys.argv) != 2:
        print("usage: python3 JSONFILE")
        quit()

    file_name = sys.argv[1]
    f = open(file_name)
  
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    ways = ways.Ways(data)

    lats = []
    lons = []

    for node_vals in data["nodes"]["connections"].values():
        lats.append(node_vals["lat"])
        lons.append(node_vals["lon"])


    fig.set_figheight(4.5)
    fig.set_figwidth(8)
    ax.set_ylim(bottom=0, top=900)
    ax.set_xlim(left=0, right=1600)
    ax.scatter(np.array(lons), np.array(lats),s=1)

    road = ways.ways["roads"][4]  # this a particular road


    lons = [] 
    lats = []

    attraction_lons = []
    attraction_lats = []

    for road_seg in road.way_segments:
        print("road seg = ", road_seg)
        for attraction in road_seg.attractions:
            print("appending")
            attraction_lats.append(attraction["lat"])
            attraction_lons.append(attraction["lon"])


    for ref in road.noderefs:
        node = None
        if ref in data["nodes"]["connections"]:
            node = data["nodes"]["connections"][ref]
        else:
            node = data["nodes"]["attractions"][ref]
            attraction_lons.append(node['lon'])
            attraction_lats.append(node['lat'])
            print("attraction node= ", node)

        lons.append(node["lon"])
        lats.append(node["lat"])


    # color attractions near our road orange
    ways.ways["roads"]

    ax.plot(lons, lats, color="r")
    print(f"attraction lons len = {len(attraction_lons)}")
    ax.scatter(np.array(attraction_lons), np.array(attraction_lats),s=10, color="orange")

    plt.savefig(file_name.replace("json", "png"))