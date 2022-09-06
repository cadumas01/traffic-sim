# About
An urban traffic simulator designed to changes in traffic with variable street designs.

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
1. Nodes - Points in space, define places or make up ways [defined further here](https://wiki.openstreetmap.org/wiki/Node)
2. Ways - Ordered lists of nodes which define a linear features (Ex: roads, train lines, rivers,...) [defined further here](https://wiki.openstreetmap.org/wiki/Way )
3. Relations - Ordered List of Nodes, describes a special relation between Nodes (Ex: No Left Turn here) [defined further here](https://wiki.openstreetmap.org/wiki/Relation)

In each dictionary, individual elements are indexed by id. From there all of the properties of each element are indexed by descriptor.
**Key Descriptors:**
- Ways have a "name" tag and contain and **ordered** list of nodes
Based on: https://wiki.openstreetmap.org/wiki/Elements


# Inital Map Rendering
Option 1:
1. Render all nodes first
 - There are generally two types of Nodes:
    1. **Connections**: Single line nodes, no tags - These are usually part of a way
    2. **Attractions**: Multi line nodes, with tags - These are usually attractions / buildings
2. Then render ways and relations (kind of like connecting the dots)
All Nodes will be accessed at least once here. Simplest. 

Option 2 - Cole's choice: 
1. Loop through all nodes in JSON processing phase and categorize as nodes into two cateogires (connections or attractions)
2. Render roads by forming lines/curves in roads with connection nodes
3. Only render attractions

# React App
- Download NodeJS (https://nodejs.org/en/download/)
- npx create-react-app sim_ui
- 

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
