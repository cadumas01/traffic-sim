import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stage, Layer, Rect, Text } from 'react-konva';
import road_data from './dummy-streets.json';

function nodes_to_array(nodes) {
  const roads = []
  for (const node of Object.entries(nodes)) {
    roads.push(node)
  }
  return {
    roads
  }
}

const GEN_ROADS = nodes_to_array(road_data.nodes.connections);
const GEN_ATTRS = nodes_to_array(road_data.nodes.attractions);

const App = () => {
  const roads = React.useState(GEN_ROADS);
  const attrs = React.useState(GEN_ATTRS);
  console.log(attrs)
  const widthFactor = (window.innerWidth / 2) / 10
  const heightFactor = (window.innerHeight / 2) / 10
    return (
      <Stage width={window.innerWidth} height={window.innerHeight}>
        <Layer>
          <Text text="Test Map" fontSize={15} />
          {roads[0].roads.map((_, i) => (
          <Rect
            key={i}
            id={roads[0].roads[i][0]}
            x={roads[0].roads[i][1].lon * widthFactor}
            y={roads[0].roads[i][1].lat * heightFactor}
            width={25}
            height={25}
            fill="black"
          />
        ))}
          {attrs[0].roads.map((_, i) => (
          <Rect
            key={i}
            id={attrs[0].roads[i][0]}
            x={attrs[0].roads[i][1].lon * widthFactor}
            y={attrs[0].roads[i][1].lat * heightFactor}
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
  