import math

# defines a class, wag_segment, which is a consists of a parametric piecewise function
# outlining the "domain" of a given road_segment
# has properties defined by a way in the resepctive json file
# contains travelers (roads contain cars, bikelanes contain bikes etc.)
# a way may be split into many different way_segments deliminated by intersections in roads
class WaySegment:

    # Need to add all properites like speed, width, and a container for travelers
    def __init__(self, noderefs, json_obj):
        self.json_obj = json_obj
        self.nodes = self.load_nodes(noderefs, json_obj)
        self.pieces = self.gen_piecewise_function(self.nodes)


     # evaluates a function (returns a solution of x,y) for a value of t
    def evaluate(self, t):
        if t > self.t_upperbound or t < 0:
            return None, None # no solution, t out of range
        else:
            for piece in self.pieces:
                if t >= piece[0] and t <= piece[1]:
                    return piece[2].evaluate(t)

    
    def is_solution(self, x_test, y_test): 
        for piece in self.pieces:
            if piece[2].is_solution(x_test, y_test): # If any x,y is a solution on any piece, return true
                return True

        return False


    def __str__(self):
        string = "WaySegment:\n"

        print(self.pieces)
        for piece in self.pieces:
            string += str(piece[2]) + "\n"
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

            t = t_upperbound

            pieces.append((t_lowerbound, t_upperbound, func))

        self.t_upperbound = t
        return pieces
    

    # returns list of dictionaries  containing all fields for a node
    def load_nodes(self, noderefs, json_obj):

        nodes = []

        for noderef in noderefs:    
            if noderef in json_obj["nodes"]["attractions"]:  # Replace this part with a database query if we go that route
                nodes.append(json_obj["nodes"]["attractions"][noderef])
            else:
                nodes.append(json_obj["nodes"]["connections"][noderef])

        return nodes


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
            x = t * math.cos(self.angle) + self.x1 # Need to deal with None angles!!!
            y = t * math.sin(self.angle) + self.y1
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

# gets angle between line and x axis (in radians)
def get_angle(x1,y1,x2,y2):
    if x2-x1 == 0: # either vertical up or vertical down
        if y2 < y1: # vertical down:
            return 3*math.pi/2
        else:
            return math.pi/2
    else:
        return math.atan((y2-y1)/(x2-x1))

def distance(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


if __name__=="__main__":
    way_seg = ParametricLinearFunc(10,10,10,20)
    print(way_seg.t_range)
    print(way_seg)
    print(way_seg.evaluate(2))
    print(way_seg.is_solution(10,15))
