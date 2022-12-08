import json
import random
from xml_streets_to_json import xml_streets_to_json
from engine import Engine
from network import Network

# Parses map data, and runs simulation
def main():

    screen_width = 1400
    screen_height = 1000

    input_osm_file = "maps/brighton.osm"
    json_file = input_osm_file.replace(".osm", ".json")

    # parse map data
    xml_streets_to_json(input_osm_file, screen_width=screen_width, screen_height=screen_height)

    f = open(json_file, encoding="utf-8")
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    f.close()

    net = Network(data)
    print(net) 
     

    # some function determining how many travelers should be generated at a time step
    def n_travelers(t):
        if t / 30 > 10:
            return 100

        return random.randint(50,100)

    engine = Engine(net, 0, n_travelers, screen_width=screen_width, screen_height=screen_height)
    engine.loop()


if __name__=="__main__":

    main()