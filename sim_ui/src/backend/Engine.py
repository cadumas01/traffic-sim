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
import data from './backend/salisbury-road-just-roads.json';
travelers = []
network = Network(data)

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
        traveler = Traveler(mode, nodes[i], gen_path(nodes[i]))
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

def get_way_seg(node):
    network.way_segments
