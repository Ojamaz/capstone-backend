import React, { useState, useEffect } from "react";
import Graph      from "./components/Graph";
import axios      from "axios";
import "./App.css";

export default function App() {
  /* ─── UI state ────────────────────────────── */
  const [topics , setTopics ] = useState([]);
  const [topic  , setTopic  ] = useState("");
  const [range  , setRange  ] = useState([1500, 2025]);

  /* fetch list for the drop-down once */
  
  useEffect(() => {
  axios.get("http://localhost:8000/topics").then(res => {
    const names = res.data.map(t => t.name).sort();
    setTopics(["(All topics)", ...names]);          // ← prepend option
    setTopic  ("");                                 // ← start with ALL
  });
}, []);

  return (
    <div className="App">
      <h2>Scientific Discoveries Graph</h2>

      {/* ── simple control panel ───────────────── */}
      <div className="panel">
      <select value={topic} onChange={e => setTopic(e.target.value)}>
        {topics.map(t => (
          <option key={t} value={t === "(All topics)" ? "" : t}>
            {t}
          </option>
        ))}
      </select>

        <span style={{margin:"0 6px"}}>Year ≤ {range[1]}</span>
        <input
          type="range" min="1500" max="2025" step="1"
          value={range[1]}
          onChange={e => setRange([1500, +e.target.value])}/>
      </div>

      {/* ── the force-graph ────────────────────── */}
      <Graph
        topic   ={topic}
        minYear ={range[0]}
        maxYear ={range[1]}
      />
    </div>
  );
}
