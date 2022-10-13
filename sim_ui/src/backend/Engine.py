"""
At each time step:
1. Read data about population to determine which nodes to launch Travelers from
    (For now: randomly generate travelers)
2. Create new Traveler at origin node, give it a mode at random,
    generate a destination and give it the path to that destination
3. Increment all existing travelers
4. Check if each traveler is still on its current way_segment, if not, change its way segment,
    if it has reached its destination, remove it from existence
"""

import random
travelers = []

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
        traveler = new Traveler(mode, nodes[i], gen_path(nodes[i]), nodes[i].lat, nodes[i].lon)
        travelers.append(traveler)
        x -= 1

def increment_travelers():
    for traveler in travelers:
        x = traveler.get_x()
        y = traveler.get_y()
        traveler.increment()

# If the x and y coordinate of a traveler corresponds to the lat and lon
# of a node which is in the "intersections" dictionary of the Network return True
# else return False
# Need to figure out an efficient way to figure out if a travelers position is at the position
# of a node
def is_at_intersection():
    for traveler in travelers:
        x = traveler.get_x()
        y = traveler.get_y()
        for intersection in Network.intersections:
            if Network.data["nodes"]["attractions"][intersection.ref][lat] == x and 
               Network.data["nodes"]["attractions"][intersection.ref][lat] == y:
            traveler
