import React from "react";
import Graph from "./components/Graph";
import "./App.css";

function App() {
  return (
    <div className="App">
      <h2 style={{ color: "#eee", textAlign: "center" }}>
        Scientific Discoveries Graph
      </h2>
      <Graph />
    </div>
  );
}

export default App;
