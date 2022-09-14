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


    fig.set_figheight(4.5)
    fig.set_figwidth(8)
    ax.set_ylim(bottom=0, top=900)
    ax.set_xlim(left=0, right=1600)
    ax.scatter(np.array(lons), np.array(lats),s=1)


    plt.savefig(file_name.replace("json", "png"))