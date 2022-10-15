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
from network import Network
from traveler import Traveler

file = open('salisbury-road-just-roads.json')
data = json.load(file)
travelers = []
network = Network(data)

"""
def __init__(self, t):
    while t > 0:
        gen_travelers(dict_to_array(network.nodes.attractions), 5)
        is_at_intersection()
        increment_travelers()
        t -= 1
"""

# Converts JSON dict of nodes to array of nodes
def dict_to_array(nodes):
  array = []
  for node in nodes:
    array.append(node)
  return array

# Takes array of nodes, creates x travelers at random across the nodes
def gen_travelers(nodes, x):
    while x > 0:
        i = random.randint(0, len(nodes))
        mode_seed = random.randint(0, 3)
        mode = ""
        if mode_seed == 1:
            mode = "Car"
        elif mode_seed == 2:
            mode = "Bike"
        else:
            mode = "Walk"
        origin_node = nodes[i]
        traveler = Traveler(mode, origin_node, get_way_seg(origin_node), gen_path(origin_node))
        travelers.append(traveler)
        x -= 1

def increment_travelers():
    for traveler in travelers:
        traveler.increment_pos()

# for each traveler, check if traveler's current_node matches any of the entries
# in the Network intersections dictionary
# If yes, increment the traveler's path
# If traveler is at final destination, path cannot be incremented, 
# "increment_path()" returns 0, we delete the traveler from the model
def is_at_intersection():
    for traveler in travelers:
        traveler_node = traveler.current_node
        for intersection in network.intersections:
            if intersection.traveler_node:
                at_destination = traveler.increment_path()
                if at_destination == 0:
                    travelers.remove(traveler)
                    del traveler
                break

print(network.intersections)

# Loops through every road in the map. For every way_segment in every road, 
# if the given node exists in its dictionary of nodes, return that way_segment
def get_way_seg(node):
    for road in network.way_segments:
        for way_segment in road:
            if node in way_segment.nodes:
                return way_segment
