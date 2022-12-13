# About
Simulate traffic on traffic on any section of Open Street Map! Inspired by [A-B-street](https://github.com/a-b-street)


Urban traffic simulator using OpenStreetMaps, Python, and PyGame.
- To-scale traveler speeds and map
- Uses gravity model to determine traveler generation and destination
    - Flexible destination weighting
- Models congestion using road width and speed limit measurements, along with density of modeled travelers.
- Uses Dijkstra's shortest path algorithm for routefinding.
   - Accounts for congestion to update traffic speeds and routefinding



# Demo 

![Demo](gifs/traffic-sim-cropped.gif)

*Standard traffic sim window focused on a section of Brighton, MA. Street networks are outlined in black; travelers (people) in red; intersections in blue; attractions (destinations) in green.*


# Dependencies

Python3

Dijkstar
- ```pip install Dijkstar```

numpy
- ```pip install numpy```

Pygame
- ```pip install pygame```

# How to Run

1. ``` cd  src/ ```
2. Adjust ```main.py``` such that input map, screen width, and screen height are as desired
3. ```python3 main.py```
  - Pygame window will open soon after (may take some time depending on size of map)

# Structure
1. Initial XML Received from OpenStreetMaps
2. Parsed into readable and relevant JSON by xml_streets_to_json.py
 - JSON includes dictionary of "nodes" (points in space)
 - Nodes are split into two categories:
    - "connections" are points along a road (connecting one location to another)
    - "attractions" are other points on a map indicating places to be (residences, grocery stores, movie theaters)
 - "ways" are collections of nodes, like a full road or a building
    - Each way has a property of its "noderefs" the node ID of every node contained within it
4. The following classes are defined by our program:
   - Node: with property ID, type, longitude and latitude, and t
   - Intersection: When a single node is a part of multiple ways, we can identify it as an intersection (a place where ways, AKA roads, meet)
       - Properties noderef, list of outgoing way segments, list of incoming way segments
   - Way segment: The parts of a road between intersections
       - Each road has multiple way segments, split up by intersections
       - This is done to allow travelers to move onto another road or continue on their current road at each intersection (Dijkstra's algorithm)
   - Network: The collection of all intersections and way_segments that we observe in our data
   - Traveler: Representation of cars travelling on roads from origin to destination nodes
   - Engine: Runs the simulation

# Map JSON Schema
XML tags are parsed into JSON, into 3 dictionaries;
1. [Nodes](https://wiki.openstreetmap.org/wiki/Node) - Points in space, define places or make up ways
  - Subcategorized into "attractions" (more than just lon and lat) and connections (just lon and lat)
2. [Ways](https://wiki.openstreetmap.org/wiki/Way)- Ordered lists of nodes which define a linear features (Ex: roads, train lines, rivers, building boundaries, ...) 
  - Subcategorized into "roads", "rails" and "other"
3. [Relations](https://wiki.openstreetmap.org/wiki/Relation) - Ordered List of Nodes, Ways and/or Relations, describes a special relation between Nodes (Ex: No Left Turn here) 
  - look more into: [multipolygons](https://wiki.openstreetmap.org/wiki/Relation:multipolygon)

In each dictionary, individual elements are indexed by id. From there all of the properties of each element are indexed by descriptor. For "ways" and "nodes" a subcategory type is also needed to index before indexing by node:
  - Ex:  ```my_attractions_node = json_dict["nodes"]["attractions"][NODE_ID_NUMBER]```
**Key Descriptors:**
- Ways have a "name" tag and contain and **ordered** list of nodes
Based on: https://wiki.openstreetmap.org/wiki/Elements

**Note:** dummy_streets.json doesn't have relations or ways for outlining buildings.

### Full Generic JSON Example below:
``` 
{
    "nodes":{
        "connections":{
            "ID": {
                "lat": "LATITUDE",
                "lon": "LONGITUDE"
            },
            "ID": {
                "lat": "LATITUDE",
                "lon": "LONGITUDE"
            },
            ...
        },
        "attractions":{
            "ID":{
                "lat": "LATITUDE",
                "lon": "LONGITUDE",
                "addr:city": "CITY",
                "addr:housenumber": "HOUSE NUMBER",
                "addr:postcode": "ZIP CODE",
                "addr:state": "STATE",
                "addr:street": "STREET ROAD",
                ...
            },
            "ID":{
                "lat": "LATITUDE",
                "lon": "LONGITUDE",
                "addr:housenumber": "HOUSE NUMBER",
                "addr:postcode": "ZIP CODE",
                "addr:state": "STATE",
                "addr:street": "STREET ROAD",
                ...
            }
        }
    },
    "ways": {
      "roads" :{
           "8814911": {
             "node-refs": [
                "NODE REF ID",
                "NODE REF ID",
                "NODE REF ID",
                ...
            ],
              "condition": "fair",
              "highway": "service",
              "lanes": "1",
              "massgis:way_id": "193636",
              "source": "massgis_import_v0.1_20071009101959",
              "width": "6.1"
        },
      },
      "nonroads" : {
           "ID": {
              "node-refs": [
                "NODE REF ID",
                "NODE REF ID",
                "NODE REF ID",
                ...
              ]
            },
      },
      "rails":  
            "ID": {
              "node-refs": [
                "NODE REF ID",
                "NODE REF ID",
                "NODE REF ID",
                ...
                ],
                "electrified": "ELECTRIFIED STATUS",
                "frequency": "FREQUENCY",
                "gauge": "GUAGE",
                "massgis:geom_id": "GEOM ID",
                "name": "NAME",
                "railway": "RAIL TYPE",
                "railway:preferred_direction": "FORWARD OR BACKWARD",
            }
    }
    "relations": {
        "9670662": {
            "addr:housenumber": "HOUSE NUMBER",
            "addr:street": "STREET NAME",
            "building": "YES OR NO",
            "type": "multipolygon",
            "members": [
                {
                    "type": "way",
                    "ref": "NODE REFERENCE",
                    "role": "outer"
                },
                {
                    "type": "way",
                    "ref": "NODE REFERENCE",
                    "role": "outer"
                }
            ]
        },
        ...
    }
}
```

# Resources / Inspiration
- https://towardsdatascience.com/how-to-simulate-traffic-on-urban-networks-using-sumo-a2ef172e564
- https://www.duckietown.org/
- https://github.com/a-b-street
- https://developer.ibm.com/tutorials/wa-build2dphysicsengine/
- https://path.berkeley.edu/research/traffic-simulation
