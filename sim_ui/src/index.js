import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stage, Layer, Rect, Text } from 'react-konva';
import road_data from './backend/salisbury-road-just-roads.json';

// Takes a JSON dict group (nodes) and pushes its elements into an Array
function dict_to_array(group) {
  var array = []
  for (const element of Object.entries(group)) {
    array.push(element)
  }
  return {
    array
  }
}

// Takes an array of Node ids (way) and an array of nodes (nodes) and returns an array of
// the x and y coordinates of the nodes in the way
function way_points(nodes, way) {
  var points = []
  for (const node of Object.entries(way)) {
    //console.log(nodes[0].array)
    console.log(nodes[0].array)
    console.log(node[1])
    console.log(nodes[0].array.includes(node[1]))
    if (nodes[0].array.includes(node[1])) {
      console.log("LETS FUCKING GO")
    }
    console.log(node)
  }
  return points;
}

const GEN_ROADS = dict_to_array(road_data.nodes.connections)
const GEN_ATTRS = dict_to_array(road_data.nodes.attractions)
const GEN_WAYS = dict_to_array(road_data.ways.roads)

const App = () => {
  const roads = React.useState(GEN_ROADS)
  const attrs = React.useState(GEN_ATTRS)
  const ways = React.useState(GEN_WAYS)
  for (let i = 0; i < ways[0].array.length; i++) {
    var points = way_points(roads, ways[0].array[i][1].node_refs)
  }
  const widthFactor = 1 / 2
  const heightFactor = 1 / 2
    return (
      <Stage width={window.innerWidth} height={window.innerHeight}>
        <Layer>
          <Text text="Test Map" fontSize={15} />
          {roads[0].array.map((_, i) => (
          <Rect
            key={i}
            id={roads[0].array[i][0]}
            x={roads[0].array[i][1].lon * widthFactor}
            y={roads[0].array[i][1].lat * heightFactor}
            width={5}
            height={5}
            fill="black"
          />
        ))}
          {attrs[0].array.map((_, i) => (
          <Rect
            key={i}
            id={attrs[0].array[i][0]}
            x={attrs[0].array[i][1].lon * widthFactor}
            y={attrs[0].array[i][1].lat * heightFactor}
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
  