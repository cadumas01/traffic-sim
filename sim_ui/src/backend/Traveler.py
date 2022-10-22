class Traveler:

    # Each traveler receives 
    # mode = mode of traveler
    # current_t = t value of traveler on its current way segment
    # end_t = the t value of the destination node on that node's way segment
    # current_way_segment = the way_segment it is currently on
    # path = the array of all of the way_segments the traveler will visit from its starting to ending intersection
    # at_destination = boolean set to false until the traveler reaches the end of its path
    # is_done = boolean set to false until at_destination is true and traveler reaches the t value of its end node

    def __init__(self, mode, current_t, end_t, current_way_seg, path, at_destination, is_done):
        self.mode = mode
        self.current_t = current_t
        self.end_t = end_t
        self.current_way_seg = current_way_seg
        self.path = path
        self.at_destination = at_destination
        self.is_done = is_done
        self.speed = current_way_seg.maxspeed * (1 - current_way_seg.weight)

    # Increment traveler t value by speed 
    # Speed is way_seg.maxspeed * (1 - way_seg.weight)
    # Lower weight = faster road, so a lower weight means a higher speed
    def increment_pos(self):
        self.t += self.speed

    def increment_path(self):
        for i in range(len(self.path)):
            if self.path[i] == self.current_way_seg:
                self.current_way_seg = self.path[i + 1]
    
    def increment(self):
        if self.at_destination == True:
            if self.t >= self.end_t:
                self.is_done = True
        else:
            if self.t + self.speed >= self.current_way_seg.t_len:
                self.t = (self.t - self.current_way_seg.t_len) + self.speed
                self.increment_path()
        self.increment_pos()
        if self.path.next is None and self.at_destination == False:
            self.at_destination = True
            