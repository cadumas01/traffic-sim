class Traveler:

    # Each traveler receives 
    # network = the network which it is a part of
    # mode = mode of traveler
    # current_t = t value of traveler on its current way segment
    # end_t = the t value of the destination node on that node's way segment
    # current_way_segment = the way_segment_id it is currently on
    # path = the array of all of the way_segments the traveler will visit from its starting to ending intersection
    # at_destination = boolean set to false until the traveler reaches the end of its path
    # is_done = boolean set to false until at_destination is true and traveler reaches the t value of its end node

    def __init__(self, network, mode, current_t, end_t, current_way_seg, path, at_destination, is_done):
        self.network = network
        self.mode = mode
        self.current_t = current_t
        self.end_t = end_t

        self.current_way_seg = current_way_seg
        current_way_seg.num_cars +=1 


        self.path = path
        self.at_destination = at_destination # same thing as is_done?
        self.is_done = is_done

        self.step_size = 1
    # Increment traveler t value by speed 
  

    ####### DO SOME LOOKUP CONVERSION FROM NETWORK TO GET WAYSEG OBJECT FROM WAY_SEG_ID #########


    # check the allowable speed of the waysegment (some function of how many cars there are on the road vs. capacity)
    def speed(self):
        return self.current_way_seg.get_allowable_speed()


    def increment_pos(self):
        self.current_t += self.speed() * self.step_size

    def increment_path(self):
        prev_way_seg = self.path.pop(0)
        self.current_way_seg = self.path[0]

        # remove traveler from old way segment and add it to new way segment
        prev_way_seg.num_cars =- 1
        self.current_way_seg.num_cars =+ 1

        #self.speed = self.current_way_seg.max_speed
    
    def increment(self):
        
        # if we are on the final way segment and have passed the end t, we arrived
        if len(self.path) == 1 and self.current_t + self.speed() * self.step_size >= self.end_t:
            self.is_done = True
            self.at_destination = True
            return

        if self.at_destination == True:
            if self.current_t >= self.end_t:
                self.is_done = True
        else: # need to transfer way_segments 
            if self.current_t + self.speed() * self.step_size >= self.current_way_seg.t_len:
                self.current_t = (self.current_t - self.current_way_seg.t_len) * (self.path[1].get_allowable_speed()) / self.speed() 
                self.increment_path()

        self.increment_pos()
        if self.path is None and self.at_destination == False:
            self.at_destination = True

    def __str__(self):
        return f"Traveler: Current Way Segment = {self.current_way_seg.id}, Current t = {self.current_t}"
            