import Konva from 'konva';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stage, Layer, Rect, Text, Line } from 'react-konva';
import road_data from './backend/salisbury-road-just-roads.json';

// Takes a JSON dict group (nodes) and pushes its elements into an Array
function dict_to_array(group) {
  var array = []
  for (const element of Object.entries(group)) {
    array.push(element)
  }
  return array
}

// Takes array of nodes and returns HashTable of {key: Node ID, val: Coords} 
function nodes_to_hash(array) {
  const ht = new Map()
  for (const node of Object.entries(array)) {
    ht.set(node[1][0], node[1][1])
  }
  return ht
}

// Takes an array of the Node IDs of a way, and a HashTable of the form {key: Node ID, val: Coords}
// Returns an array [x1, y1, x2, y2, x3, ...] of the x and y coordinates of the nodes in the way
function way_points(nodes_hash, way) {
  var points = []
  for (let i = way.length - 1; i >= 0; i--){
    points.push(nodes_hash.get(way[i]).lon)
    points.push(nodes_hash.get(way[i]).lat)
  }
  return points
}

function points_to_way_dict(hash, ways) {
  var array = []
  for (let i = 0; i < ways[0].length; i++) {
    const points = way_points(hash, ways[0][i][1].noderefs)
    points.map((_, i) => (
      points[i] = points[i] * 0.5
    ))
    array.push({
      points: points,
      detail: ways[0][i][1]
    })
  }
  return array
}

const GEN_ROADS = dict_to_array(road_data.nodes.connections)
const GEN_ATTRS = dict_to_array(road_data.nodes.attractions)
const GEN_WAYS_ROADS = dict_to_array(road_data.ways.roads)
const GEN_WAYS_NONROADS = dict_to_array(road_data.ways.nonroads)

/*
const roads:
roads is an array, roads[0] is an array of arrays, where each element in the array is a node
s.t. roads[0][0] = ["63522025", {lat: 600.8817859964461, lon: 509.173652912172}]
roads[0][0][0] is the node ID, roads[0][0][1] is the node coordinates

const attrs:
attrs

*/

const App = () => {
  const roads = React.useState(GEN_ROADS)
  const attrs = React.useState(GEN_ATTRS)
  console.log(attrs)
  const ways_roads = React.useState(GEN_WAYS_ROADS)
  const ways_nonroads = React.useState(GEN_WAYS_NONROADS)
  const roads_hash = nodes_to_hash(roads[0])
  const coord_array_roads = points_to_way_dict(roads_hash, ways_roads)
  const coord_array_nonroads = points_to_way_dict(roads_hash, ways_nonroads)
  const widthFactor = 0.5
  const heightFactor = 0.5
    return (
      <Stage width={window.innerWidth} height={window.innerHeight}>
        <Layer>
          <Text text="Test Map" fontSize={15} />
          {roads[0].map((_, i) => (
          <Rect
            key={i}
            id={roads[0][i][0]}
            x={roads[0][i][1].lon * widthFactor}
            y={roads[0][i][1].lat * heightFactor}
            width={5}
            height={5}
            fill="black"
          />
        ))}
          {coord_array_roads.map((_, i) => (
          <Line
          key={i.toString()}
          points={coord_array_roads[i].points}
          stroke="black"
          strokeWidth={parseInt(coord_array_roads[i].detail.width)}
          />
        ))}
          {coord_array_nonroads.map((_, i) => (
          <Line
          key={i.toString()}
          points={coord_array_nonroads[i].points}
          stroke="red"
          strokeWidth={5}
          />
        ))}
        </Layer>
      </Stage>
    );
  };
  
  const container = document.getElementById('root');
  const root = createRoot(container);
  root.render(<App />);
  