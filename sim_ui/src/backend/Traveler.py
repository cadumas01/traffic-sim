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
        self.at_destination = at_destination # same thing as is_done?
        self.is_done = is_done
        # we'll finalize speed calculations later
        self.speed = current_way_seg.maxspeed

        self.step_size = 1
    # Increment traveler t value by speed 
  
    def increment_pos(self):
        self.current_t += self.speed * self.step_size

    def increment_path(self):
        self.path.pop(0)
        self.current_way_seg = self.path[0]
        self.speed = self.current_way_seg.maxspeed
    
    def increment(self):
        # if we are on the final way segment and have passed the end t, we arrived
        if len(self.path) == 1 and self.current_t + self.speed * self.step_size >= self.end_t:
            self.is_done = True
            self.at_destination = True
            return

        

        if self.at_destination == True:
            if self.current_t >= self.end_t:
                self.is_done = True
        else:
            if self.current_t + self.speed * self.step_size >= self.current_way_seg.t_len:
                self.current_t = (self.current_t - self.current_way_seg.t_len) * (self.path[1].maxspeed) / self.speed 
                self.increment_path()

        self.increment_pos()
        if self.path is None and self.at_destination == False:
            self.at_destination = True

    def __str__(self):
        return f"Traveler: Current Way Segment = {self.current_way_seg.id}, Current t = {self.current_t}"
            