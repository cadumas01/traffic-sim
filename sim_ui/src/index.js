import Konva from 'konva';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stage, Layer, Rect, Text, Line } from 'react-konva';
import road_data from './backend/salisbury-road-just-roads.json';

/*<Line
          points={points}
          stroke={'red'}
          tension={1}
          strokeWidth={3}
          /> */

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
  console.log(way)
  for (let i = way.length - 1; i >= 0; i--){
    points.push(nodes_hash.get(way[i]).lat)
    points.push(nodes_hash.get(way[i]).lon)
  }
  return points
}

// Helper function I used to check if I was gathering the correct coordinates for the nodes of each way
/* function way_array(nodes_hash, way) {
  var points = []
  for (let i = way.length - 1; i >= 0; i--){
    points.push(nodes_hash.get(way[i]))
  }
  return points
} */

const GEN_ROADS = dict_to_array(road_data.nodes.connections)
const GEN_ATTRS = dict_to_array(road_data.nodes.attractions)
const GEN_WAYS = dict_to_array(road_data.ways.roads)

const App = () => {
  const roads = React.useState(GEN_ROADS)
  const attrs = React.useState(GEN_ATTRS)
  const ways = React.useState(GEN_WAYS)
  const roads_hash = nodes_to_hash(roads[0])
  const points = way_points(roads_hash, ways[0][1][1].node_refs)
  points.map((_, i) => (
    points[i] = points[i] * 0.5
  ))
  const widthFactor = 0.5
  const heightFactor = 0.5

    return (
      <Stage width={window.innerWidth} height={window.innerHeight}>
        <Layer>
          <Text text="Test Map" fontSize={15} />
          <Line
          points={points}
          stroke="black"
          tension={1}
          strokeWidth={3}
          />
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
          {attrs[0].map((_, i) => (
          <Rect
            key={i}
            id={attrs[0][i][0]}
            x={attrs[0][i][1].lon * widthFactor}
            y={attrs[0][i][1].lat * heightFactor}
            width={30}
            height={30}
            fill="red"
          />
        ))}
        </Layer>
      </Stage>
    );
  };
  
  const container = document.getElementById('root');
  const root = createRoot(container);
  root.render(<App />);
  