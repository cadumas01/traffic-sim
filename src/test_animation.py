import pygame
from pygame import gfxdraw
import numpy as np
from network import Network
import json
import random
import sys
import time
from traveler import Traveler


def main():
    f = open("maps/brighton.json", encoding="utf-8")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    net = Network(data)
    print(net) 
     

    engine = Engine(net, 0)
    engine.loop()


class Engine:
    def __init__(self, network, time_steps, config={}):
        # Simulation to draw
        self.network = network

        # Set default configurations
        self.set_default_config()

        self.travelers = []
        self.time_steps = time_steps

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)



    def random_color(self):
        self.road_color = ((self.road_color[2] - 1) % 255, 255, (self.road_color[2] + 1) % 255 )
        
    def set_default_config(self):
        """Set default configuration"""
        self.width = 1600
        self.height = 900
        self.bg_color = (250, 250, 250)
        self.road_color = (0,0,0)

        self.fps = 30
        self.zoom = 0
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False


    def loop(self, loop=None):
        """Shows a window visualizing the simulation and runs the loop function."""
        
        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()

        # Fixed fps
        clock = pygame.time.Clock()

        # To draw text
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)

        time_step = 0
        self.draw(time_step)
        pygame.display.flip()
        while True:

            # Generate Travelers (right now, every second)
            if time_step % self.fps == 0:
                self.gen_travelers(random.randint(50,100))
                
                # Also recalculate Traffic for future travelers
                self.network.make_graph()
       

            # Draw 
            self.draw(time_step)
            pygame.display.update()
            # Update to next state
            for traveler in self.travelers:
                traveler.increment()
                if traveler.is_done:
                    self.travelers.remove(traveler)

                    traveler.current_way_seg.num_cars =- 1
                    del traveler

            clock.tick(self.fps)
            time_step += 1

            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    sys.exit(0)
            


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))



    # accepts a road of type WaySegment
    def draw_road(self, road, color):
        width = int(road.width / 5) + 4

        r = 0 
        g = 0
        b = 0

        for piece in road.pieces:    
            pygame.draw.line(self.screen, (r,g,b), self.to_pygame(piece[2].x1, piece[2].y1), self.to_pygame(piece[2].x2, piece[2].y2), width=width)




    def draw_roads(self):
        for road in self.network.way_segments["roads"].values():
            self.draw_road(road, color=self.road_color)
            
            # Test draw attractions
            for attraction in road.attractions.values():
                green = (attraction.weight * 10) % 255
                pygame.draw.circle(self.screen, (0,green,0), self.to_pygame(attraction.lon,attraction.lat), radius=3)

            

    def draw_intersections(self):
        for intersection_id in self.network.intersections:
            x = 0
            y = 0
            if intersection_id in self.network.data["nodes"]["attractions"]:
                x = self.network.data["nodes"]["attractions"][intersection_id]["lon"]
                y = self.network.data["nodes"]["attractions"][intersection_id]["lat"]
            
                pygame.draw.circle(self.screen, (0,0,255), self.to_pygame(x,y), radius=4)
            else:
                x = self.network.data["nodes"]["connections"][intersection_id]["lon"]
                y = self.network.data["nodes"]["connections"][intersection_id]["lat"]
            
                pygame.draw.circle(self.screen, (0,200,255), self.to_pygame(x,y), radius=3)


    def draw_traveler(self, traveler):
        x, y = traveler.current_way_seg.evaluate(traveler.current_t)
        
        # JANKY TEMP FIX
        if (x, y) != (None, None):
            if traveler.speed() < 1:
                pygame.draw.circle(self.screen, (255,0,255), self.to_pygame(x,y), radius=2)
            else:
                pygame.draw.circle(self.screen, (255,0,0), self.to_pygame(x,y), radius=2)



    def draw_travelers(self):
        for traveler in self.travelers:
            self.draw_traveler(traveler)


    def draw(self,t):
        self.background(*self.bg_color)

        # Draw Clock
        self.draw_clock(t)

        self.draw_roads()
        self.draw_intersections()
        self.draw_travelers()

      

    # Takes array of nodes, creates x travelers at random across the nodes
    def gen_travelers(self, n):

        # Generate n trips with gravity model
        trips = self.network.random_trips_pairs(n)

        for trip in trips:
            origin_node = trip[0]
            origin_way_seg = self.get_way_seg(origin_node)
            origin_intersection = self.find_nearest_intersection(origin_node, origin_way_seg)

            end_node = trip[1]
            end_way_seg = self.get_way_seg(end_node)
            end_intersection = self.find_nearest_intersection(end_node, end_way_seg)

            t = origin_way_seg.attractions[origin_node].t
            end_t = end_way_seg.attractions[end_node].t
            path = []

            try: # sometimes there is no path between these two intersections so just break out and try again
                edges = self.network.shortest_path(origin_intersection, end_intersection)
            except:
                continue


            for edge in edges.edges:
                path.append(self.network.way_segments["roads"][edge[1]])
            if end_way_seg not in path:
                path.append(end_way_seg)

            # Path should include first way_segment (if it doesn't then add it) - NEW IDEA, MAYBE REMOVE
            if origin_way_seg != path[0]:
                path.insert(0, origin_way_seg)


            #print(f"\ncreating new traveler with end t = {end_t}, path = {path}")
            traveler = Traveler(self.network, "Car", t, end_t, origin_way_seg, path, False, False)
            self.travelers.append(traveler)
            

    def find_nearest_intersection(self, attraction_id, way_seg):
        t = way_seg.attractions[attraction_id].t
        total_t = way_seg.t_len
        if t / total_t < 0.5:
            return way_seg.start_ref
        else:
            return way_seg.end_ref

    # Loops through every road in the map. For every way_segment in every road, 
    # if the given node exists in its dictionary of nodes, return that way_segment
    def get_way_seg(self, node_id):
        for way_segment in self.network.way_segments["roads"].values():
            if node_id in way_segment.attractions:
                return way_segment


    def draw_clock(self,t):
        font = pygame.font.SysFont(None, 24)
        img = font.render(f"time (ticks)= {t}", True, (0,0,0))
        self.screen.blit(img, (20, 20))

    # converts coordinates to pygame coordinates (bottom left origin to top left origin)
    def to_pygame(self, x, y):
        return (x, self.height - y)

if __name__=="__main__":

    main()

   