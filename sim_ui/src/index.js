import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stage, Layer, Rect, Text } from 'react-konva';
import road_data from './dummy-streets.json';

function generate_road(nodes) {
  const roads = []
  for (const node of Object.entries(nodes)) {
    roads.push(node)
  }
  return {
    roads
  }
}

const INITIAL_STATE = generate_road(road_data.nodes.connections);

const App = () => {
  const roads = React.useState(INITIAL_STATE);
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
        </Layer>
      </Stage>
    );
  };
  
  const container = document.getElementById('root');
  const root = createRoot(container);
  root.render(<App />);
  