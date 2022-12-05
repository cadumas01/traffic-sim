# About
Urban traffic simulator using OpenStreetMaps, Python, and PyGame. Uses gravity model to determine traveler generation and destination. Uses Dijkstra's shortest path algorithm for routefinding. Models congestion using road width and speed limit measurements, along with density of modeled travelers.

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


# Planning
1. Build map with GUI
 - Get small street section in XML tag form
 - Recreate that in JS / Typescript with React App
   - xml2json parser: https://www.npmjs.com/package/xml2json
   - xml2js parser: https://www.npmjs.com/package/xml2js
   - Two ideas for rendering maps:
   1. Each street has its own ID, and a function that maps its location and length
   2. 
 - Static map view to start
 - Relational database for Nodes and Ways
 
2. Model Traffic on a Street 
- Model Trafffic in Python and pass JSON objects to JS Frontend
- Python is called by the JS Frontend when new information is needed

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
            },
      "other" : {
           "ID": {
              "node-refs": [
                "NODE REF ID",
                "NODE REF ID",
                "NODE REF ID",
                ...
              ]
            },
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

# Initial Map Rendering
Option 1:
1. Render all nodes first
 - There are generally two types of Nodes:
    1. **Connections**: Single line nodes, no tags - These are usually part of a way
    2. **Attractions**: Multi line nodes, with tags - These are usually attractions / buildings
      - Attraction nodes are at center of a building??
      - Their boundaries are designated by Relations (as a collection of ways) which form multigons
2. Then render ways and relations (kind of like connecting the dots)
3. As ways are formed, properties can be checked to see if they are part of roads or building walls or ...
All Nodes will be accessed at least once here. Simplest. 

Option 2: 
1. Loop through all nodes in JSON processing phase and categorize as nodes into two cateogires (connections or attractions)
2. Render roads by forming lines/curves in roads with connection nodes
4. Only render attractions
5. Render relations (building walls - surrounding a central building node?)

# Ideas 
- Goal: Create a simulation to maximize traveler throughput and costs of different street layouts with different transportation modes
- Could do simulation over generic city or use google earth to simulate traffic flow over already existing street patterns (and what modifications to street layout and/or transportation modes to increase efficiency)
- Could use google earth / maps to take real life city layout and put into number form
- Considerations: need to get real life traffic throughputs for various modes from somewhere, need to domino effect of adjusting one street on all others
- Consider human behavior / adoption of new transportation modes
- Consider adjusting costs / taxes /subsidies on certain transportation modes
- Could extend into macro solution above
- Consider induced demand
- We should use a mesoscopic model of traffic flow https://towardsdatascience.com/simulating-traffic-flow-in-python-ee1eab4dd20f
- Focus in on just one small segment of Boston (to start)
- Model traffic depending on time of day/day of the week (Traffic is different Tuesday at 9 AM than it is Saturday at 3 PM)
  - Simulation could run through hours in a day, changing the traffic flow diagram as it goes


# Resources / Inspiration
- https://towardsdatascience.com/how-to-simulate-traffic-on-urban-networks-using-sumo-a2ef172e564
- https://www.duckietown.org/
- https://github.com/a-b-street
  - More complete idea of what we are doing (possibly)
  - Utilize osm2street for street layout
  - Utilize https://github.com/asu-trans-ai-lab/grid2demand for corresponding baseline demand
- https://www.openstreetmap.org/#map=7/41.701/-72.136
  - Use this
- https://developer.ibm.com/tutorials/wa-build2dphysicsengine/
- https://path.berkeley.edu/research/traffic-simulation
