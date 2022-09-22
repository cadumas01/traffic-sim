import matplotlib.pyplot as plt
import numpy as np
import json
import sys

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

    lats = []
    lons = []

    for node_vals in data["nodes"]["connections"].values():
        lats.append(node_vals["lat"])
        lons.append(node_vals["lon"])


    print(lats)
    print(lons)
    fig.set_figheight(4.5)
    fig.set_figwidth(8)
    ax.set_ylim(bottom=0, top=900)
    ax.set_xlim(left=0, right=1600)
    ax.scatter(np.array(lons), np.array(lats),s=1)

    road = list(data["ways"]["roads"].values())[2]
    print(road["name"])

    road_nodes = road["noderefs"]


    lons = [300,320,340,350,290] 
    lats = [300,350,310,360,370]

    attraction_lons = []
    attraction_lats = []

    for ref in road_nodes:
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


    ax.plot(lons, lats, color="r")
    ax.scatter(np.array(attraction_lons), np.array(attraction_lats),s=10, color="orange")

    plt.savefig(file_name.replace("json", "png"))