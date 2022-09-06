# About
An urban traffic simulator designed to changes in traffic with variable street designs.

# Planning
1. Build map with GUI
 - Get small street section in XML tag form
 - Recreate that in JS / Typescript with React App
 - Static map view to start
 
2. Model Traffic on a Street 
- Model Trafffic in Python and pass JSON objects to JS Frontend

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
