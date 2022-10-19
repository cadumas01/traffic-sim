import pygame
from pygame import gfxdraw
import numpy as np
from network import Network
import json
import random
import sys


def main():
    f = open("test-map.json", encoding="utf-8")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    net = Network(data)
    print(net)  

    engine = Engine(net)
    engine.loop()


class Engine:
    def __init__(self, network, config={}):
        # Simulation to draw
        self.network = network

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

    def random_color(self):
        self.road_color = ((self.road_color[2] - 1) % 255, 255, (self.road_color[2] + 1) % 255 )
        
    def set_default_config(self):
        """Set default configuration"""
        self.width = 1400
        self.height = 700
        self.bg_color = (250, 250, 250)
        self.road_color = (0,0,0)

        self.fps = 60
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

        self.draw()
        pygame.display.flip()
        while True:
            
            self.draw()

           # self.random_color()

            pygame.display.update()
            clock.tick(40)

            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    sys.exit(0)

           

            

    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""
        def loop(sim):
            sim.run(steps_per_update)
        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width/2 + (x + self.offset[0])*self.zoom),
            int(self.height/2 + (y + self.offset[1])*self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width/2)/self.zoom),
            int(-self.offset[1] + (y - self.height/2)/self.zoom)
        )


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))


    # accepts a road of type WaySegment
    def draw_road(self, road, color):
        width = int(road.width / 4)
        for piece in road.pieces:
        
            pygame.draw.line(self.screen, color, (piece[2].x1, piece[2].y1), (piece[2].x2, piece[2].y2), width=width)

    def draw_roads(self):
        for road in self.network.way_segments["roads"].values():
            self.draw_road(road, color=self.road_color)
            
           

    def draw_intersections(self):
        for intersection_id in self.network.intersections:
            x = 0
            y = 0
            if intersection_id in self.network.data["nodes"]["attractions"]:
                x = self.network.data["nodes"]["attractions"][intersection_id]["lon"]
                y = self.network.data["nodes"]["attractions"][intersection_id]["lat"]
            
                pygame.draw.circle(self.screen, (0,0,255), (x,y), radius=4)
            else:
                x = self.network.data["nodes"]["connections"][intersection_id]["lon"]
                y = self.network.data["nodes"]["connections"][intersection_id]["lat"]
            
                pygame.draw.circle(self.screen, (0,200,255), (x,y), radius=3)


    def draw(self):
    
        self.background(*self.bg_color)
      
        self.draw_roads()
        self.draw_intersections()

        test_path = ['3199087788', '8545220735', '8545220746', '63577798', '63582073', '4257913364', '9641895410', '63532720', '69495662', '63592289', '4258760804', '63581737', '8545220749']

        shortest_path = self.network.shortest_path('61573639', '63554801')

        print(shortest_path.edges)
        for edge in shortest_path.edges:
            way_segment = self.network.way_segments["roads"][edge[1]]
            self.draw_road(way_segment, (250,0,0))


        
        # # FIX - intersections are not properly linked
        # while start_intersection != end_intersection:
        #     print("etst = ", self.network.intersections[start_intersection].next_way_segment)
        #     way_segment_id = self.network.intersections[start_intersection].next_way_segment[end_intersection]
        #     way_segment = self.network.way_segments["roads"][way_segment_id]
            
        #     self.draw_road(way_segment, 250,0,0)
        #     # point to next node along the way
        #     start_intersection = way_segment.end_ref

           






if __name__=="__main__":

    main()

   