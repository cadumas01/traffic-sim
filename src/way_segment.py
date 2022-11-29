import math
from node import Node
import re

# defines a class, wag_segment, which is a consists of a parametric piecewise function
# outlining the "domain" of a given road_segment
# has properties defined by a way in the resepctive json file
# contains travelers (roads contain cars, bikelanes contain bikes etc.)
# a way may be split into many different way_segments deliminated by intersections in roads
class WaySegment:

    # Need to add all properites like speed, width, and a container for travelers
    def __init__(self, way_id, category, noderefs, data, split=False, engine_fps=30):
        self.way_id = way_id      # way_id is the id of the way which this waysegmenet is part of (should NOT be used as index since may not be unique)
        self.category = category  # way category which this way segment belongs to (road or nonroad)
        self.data = data 

        # used to find speed in t_unit / tick (from mph)
        self.engine_fps = engine_fps

        # multiply some t_len by this constant (determined by input data) to convert to ft 
        self.t_unit_to_ft = self.t_unit_to_ft()

        # ordered list of dictionaries for each node. Essentially same as json dictionary (for a node) but with id added as value instead of key
        self.load_nodes(noderefs, data) # generates (self.nodes)

        # these are the two intersections the way segment is bounded by
        self.start_ref = self.nodes[0]['noderef']
        self.end_ref = self.nodes[-1]['noderef']

        # way segment id is startref_endref and sometimes startref_endref_r if the waysegment is a 2 way road split into two 1 way roads
        self.id = ""
        self.set_id()


        self.noderefs = noderefs # ordered list of each noderef that makes up the way_segment
        self.gen_piecewise_function(self.nodes) # generates list of pieces (self.pieces)
        self.attractions = {} # dict of all attraction nodes associated to a way segment and indexed by id
        # MAYBE CHANGE ATTRACTIONS TO DICTIONARY index by t value???

        # Used for determining weight (when num_cars > capacity then weight goes up)
        self.num_cars = 0 # start value

        self.set_width()

      
        self.set_max_speed() # adjust 
        self.lanes = 1


        ''' 
        Dynamical System for determining congestion (allowable speed and thus weight of way_segment):

            allowblespeed_{t+1} = f1(capacity_t)
            capacity_{t+1}      = f2(ft_per_car_t)
            ft_per_cat_{t+1}    = f3(allowablespeed_t)

        We must set initial states for these fields
        '''
        self.allowable_speed = self.max_speed # determined by traffic conidtions, at most max_speed
        self.ft_per_car = self.set_ft_per_car()
        self.capacity = self.get_capacity() # also sets capacity

        self.set_lanes(split)

        self.set_weight() # edge weight, lower weight means: shorter road, higher speed, more lanes

        

    

    # Gets maxspeed (in mph) from json file and converts to t_unit / tick
    ''' 
        max_speed is in units of t_unit / tick. We must convert mph to t_unit / tick

            1 foot / sec = 0.681818 mph

            30 ticks / 1 sec

            1 * t_unit_to_ft / 1 t_unit

            max_speed [in mph] / ( (30 ticks / 1 sec) * (t_unit_to_ft / 1 t_unit) * (0.681818) = ( t_unit / tick)  ==> max_speed [in t_unit / sec]           
    '''
    def set_max_speed(self):
        if self.category != "roads":
            self.max_speed = 1
        else:
            way_data = self.data["ways"][self.category][self.way_id]
            max_speed_mph = 30 # default - maybe change
            if "maxspeed" in way_data:
                max_speed_mph = int(re.sub("[^0-9]", "", way_data["maxspeed"])) # remove any non digits and convert to int
            
            # convert to t_unit / tick
            self.max_speed = max_speed_mph / (self.engine_fps * (self.t_unit_to_ft) * (0.681818))



    ''' We know from the data json file the actual coordinate bounds of the map and the pixel bounds'''
    def t_unit_to_ft(self):

        lat_dist_deg = (float(self.data["bounds"]["minlat"]) - float(self.data["bounds"]["maxlat"])) # in degrees
        lon_dist_deg = (float(self.data["bounds"]["minlon"]) - float(self.data["bounds"]["maxlon"]))

        lat_dist_ft = lat_dist_deg *  364173

        lon_dist_ft = math.cos(float(self.data["bounds"]["minlat"])) * lon_dist_deg * 364173

        actual_diag_dist = math.sqrt((lat_dist_ft) ** 2 + (lon_dist_ft) ** 2)
        display_diag_dist = math.sqrt((self.data["display_bounds"]["occupied_vertical_space"]) **2 + float(self.data["display_bounds"]["occupied_vertical_space"]) **2)
    

        return actual_diag_dist / display_diag_dist


     # evaluates a function (returns a solution of x,y) for a value of t
    def evaluate(self, t):
        if t > self.t_len or t < 0:
            return None, None # no solution, t out of range
        else:
            for piece in self.pieces:
                if t >= piece[0] and t <= piece[1]:
                    # we subtract the lower t bound for that given piece so that the t is normalized to that piece
                    return piece[2].evaluate(t)

    
    def is_solution(self, x_test, y_test): 
        for piece in self.pieces:
            if piece[2].is_solution(x_test, y_test): # If any x,y is a solution on any piece, return true
                return True

        return False


    def set_width(self):
        if 'width' in self.data["ways"][self.category][self.way_id]:
            self.width = float(self.data["ways"][self.category][self.way_id]['width'])
        else:
            self.width = 2 # temp


    def set_id(self):
        s = str(f"{self.start_ref}_{self.end_ref}")  
        self.id = s


    # sets number of lanes
    def set_lanes(self, split):
        way_obj = self.data["ways"][self.category][self.way_id]
        lanes_temp = 0
        if "lanes" in way_obj:
            lanes_temp = int(way_obj["lanes"])
        else:
            lanes_temp = 1 # return 1 lane if no lanes field present

        if split == True:
            lanes_temp = max(1, lanes_temp // 2)
        
        self.lanes = lanes_temp


    ''' Used to determine how much space is needed per car (used to find capacity)
        - Assumes higher max_speed requires more space (more space between cars on highway and at higher speeds)
        - Minimum following distance is used to determine length per car (increases with speed) https://www.smartmotorist.com/safe-following-distance
        - assumes a car length of 15 ft
    '''
    def set_ft_per_car(self):
        following_distance_multiplier = self.allowable_speed / 20 # for each additional 20 mph, multiplier increases by 1
        return (self.allowable_speed * following_distance_multiplier + 15)


    
    # the longer the road and more lanes, the more cars can fit
    def get_capacity(self):
        self.capacity = math.ceil(self.lanes * self.t_unit_to_ft * (self.t_len) / self.ft_per_car)
        return self.capacity


    # is max speed when num_cars <= capacity, otherwise (there is traffic) and speed decreases
    def get_allowable_speed(self):
       
        if self.num_cars <= self.get_capacity():
            self.allowable_speed = self.max_speed
        else: # some decreasing function with respect to num_cars
            self.allowable_speed = self.max_speed * (self.get_capacity() / self.num_cars)
        
        # Once we have calculated the new allowable speed, must update ft_per_car
        self.set_ft_per_car()

        return self.allowable_speed


    # very simple - need to adjust
    # weight should be low (good) when length is short and allowable_speed (speed cars/travelers can actually travel at) is high
    def set_weight(self):
        self.weight = (self.t_len / (self.get_allowable_speed()) )


    def __str__(self):
        string = f"WaySegment with id = {self.id}:\n"

        for piece in self.pieces:
            string += str(piece[2]) + "\n"

        # string += "with attractions at t = \n"
        # for attraction in self.attractions.values():
        #     string += "\t" + str(attraction.t) + "\n"

        return string
        

    def nodes_str(self):
        string = "WaySegment nodes:\n"
        
        for node in self.nodes:
            string += str(node) + "\n"
        return string

    # generates a piecewise parametric function
    def gen_piecewise_function(self, nodes):

        # generates a linear parametric function between nodes[i] and nodes[i+1]
        t = 0
        # each element of pieces is a tuple (lowerbound, upperbound, function)
        # we really need a dictionary that has an interval as a key
        pieces = [] # 

        for i in range(0, len(nodes) - 1):

            # lons are x and lats are y
            x1 = nodes[i]["lon"]
            y1 = nodes[i]["lat"]

            x2 = nodes[i+1]["lon"]
            y2 = nodes[i+1]["lat"]

            # create ParametricLinearFunc objects and keep them in the list

            t_lowerbound = t
            func = ParametricLinearFunc(x1,y1,x2,y2,t)
            t_upperbound = func.t_range[1]

            # assign t value to each of the nodes
            nodes[i]["t"] = t_lowerbound
            nodes[i+1]["t"] = t_upperbound # useless operation unless i == len(nodes) - 1

            t = t_upperbound

            pieces.append((t_lowerbound, t_upperbound, func))

        self.t_len = t
        self.pieces = pieces
    

    # !!! Convert this TO NODE type Node
    # returns list of dictionaries  containing all fields for a node
    def load_nodes(self, noderefs, data):
        nodes = []

        for noderef in noderefs:   
            node = {"noderef": noderef}
            if noderef in data["nodes"]["attractions"]:  # Replace this part with a database query if we go that route
                node.update(data["nodes"]["attractions"][noderef])
            else:
                node.update(data["nodes"]["connections"][noderef])

            nodes.append(node)


        self.nodes = nodes

    # takes a Node object
    def add_attraction(self, attraction):
        self.attractions[attraction.id] = attraction

    # def add_attraction(self, noderef, t_value):
    #     attract_dict = self.data["nodes"]["attractions"][noderef]

    #     attraction = Node(noderef, "attraction", t_value, attract_dict["lon"], attract_dict["lat"], attract_dict["weight"])
    #     self.attractions[noderef] = attraction



    # Find min distance of a [attraction] node to a way segment node 
    def min_node_distance(self, lon, lat):
        minimum =  1000000
        t= 0

        for node in self.nodes:
            dist = math.sqrt((node["lon"] - lon) ** 2 + (node["lat"] - lat) **2) 
            if dist < minimum:
                minimum = dist
                t = node["t"]

        return minimum, t


# defines a linear math function between (x1,y1) and (x2,y2)
# theta is angle of slope (x axis is base) 
class ParametricLinearFunc:
    def __init__(self, x1,y1,x2,y2,t_lowerbound=0):
        self.angle = get_angle(x1,y1,x2,y2)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.t_range = (t_lowerbound, t_lowerbound + distance(x1,y1,x2,y2)) # [lowerbound, upperbound]
    
    # evaluates a function (returns a solution of x,y) for a value of t
    def evaluate(self, t):
        if t > self.t_range[1] or t < self.t_range[0]:
            return None, None # no solution, t out of range
        else:
            # must normalize t to actual t length (subtract lower bound)
            x = (t - self.t_range[0]) * math.cos(self.angle) + self.x1 # Need to deal with None angles!!!
            y = (t - self.t_range[0]) * math.sin(self.angle) + self.y1  
            return x, y
    
    def is_solution(self, x_test, y_test): # checks whether (x_test,y_test) lie on line
        # start at x1,y2 and check if slope with input x,y form same angle as with x2,y2
        # check is x is in range of x1 and x2 and if y is in range of y1 and y2

        angle_test = get_angle(self.x1, self.y1 , x_test, y_test)
        
        # if angle matches, make sure x (or y) is in range 
        # checks if t produced is within actual t range
        if angle_test == self.angle: # maybe include some sort of of wiggle room???
            t_test = (x_test - self.x1) / math.cos(angle_test) # not working
            return (t_test >= self.t_range[0] and t_test <= self.t_range[1])

        return False


    def __str__(self):
        return f"({self.x1},{self.y1}) to ({self.x2},{self.y2}), angle={self.angle}, t=[{self.t_range}]"

''' 
gets angle between line and x axis (in radians) 
Assumes (0,0) is bottom left and standard unit circle angles 
(I.e going from bottom left to top right will be an angle between 0 and pi/4)
'''
def get_angle(x1,y1,x2,y2):
    if x2-x1 == 0: # either vertical up or vertical down
        if y2 < y1: # vertical down:
            return 3*math.pi/2
        else:
            return math.pi/2
    else:
        angle = math.atan((y2-y1)/(x2-x1))

        
        ''' 
        Originally, angle for quad 3 is treated as same as angle for quad 1 and quad2 is treated same as quad 4. must adjust that
        '''
        if (x2 -x1) < 0:
            return angle + math.pi # add pi
    
        else: #quads 1 and 4
            return angle



def distance(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)




if __name__=="__main__":
    way_seg = ParametricLinearFunc(10,10,10,20)
    print(way_seg.t_range)
    print(way_seg)
    print(way_seg.evaluate(2))
    print(way_seg.is_solution(10,15))
