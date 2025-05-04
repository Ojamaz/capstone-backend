import React, { useEffect, useState, useCallback, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";
import drawHex from "./Hexagon";

//--------------- CONFIG  --------------------------
//  CONFIG  – tweak visual style & API base here
// 
const CFG = {
  API_BASE        : "http://localhost:8000",
  TOPIC_HEX_SIZE  : 20,
  DISC_HEX_SIZE   : 10,
  GLOW_BLUR       : 15,
  FONT_SIZE_L0   : 8,
  FONT_SIZE_L1   : 6,
  COLOURS         : {          // mirror backend
    Physics:"#00bcd4", Chemistry:"#ff9800", Biology:"#4caf50",
    Medicine:"#e91e63", Mathematics:"#9c27b0", Engineering:"#3f51b5",
    Technology:"#009688", "Earth Science":"#795548",
    History:"#607d8b", Unsorted:"#9e9e9e"
  }
};
// ---------------------------------------------------------------

export default function Graph({ topic, minYear, maxYear }) {
  const [data , setData ] = useState({nodes:[],links:[]});
  const ref   = useRef();

  /* -------- (re)load graph when filters change */
  useEffect(() => {
    if (!topic) return;
    const url =
        `${CFG.API_BASE}/graph?topic=${encodeURIComponent(topic)}` +
        `&min_year=${minYear}&max_year=${maxYear}`;
    axios.get(url).then(res => setData(res.data));
  }, [topic, minYear, maxYear]);

  /* -------- click big hex -> explode */
  const handleClick = useCallback(async node => {
    if (node.level !== 0) return;

     // fetch discoveries for this topic
    const url  = `${CFG.API_BASE}/discoveries/${encodeURIComponent(node.id)}`;
    const list = (await axios.get(url)).data;

    // don’t add the same topic twice
    if (list.length && data.links.some(l => l.source === node.id)) {
      return;
    }

     // 2️⃣ sanitize IDs and position children
    const angleStep = (2 * Math.PI) / list.length;
    const newNodes = list.map((d, i) => ({
      id: `${node.id}::${d.name.replace(/[^a-z0-9]/gi, "_")}`,  // safe, unique ID
      parent: node.id,
      level: 1,
      label: d.name,
      year: d.year,
      url: d.url,
      branch: node.branch,
      fx: node.x + 60 * Math.cos(angleStep * i),
      fy: node.y + 60 * Math.sin(angleStep * i)
    }));

    const newLinks = newNodes.map(n => ({
      source: node.id,
      target: n.id
    }));

    // merge into current graph
    setData(prev => ({
      nodes: [...prev.nodes, ...newNodes],
      links: [...prev.links, ...newLinks]
    }));
  }, [data]);
  
  /* -------- draw a node (hex + label) -------- */
  const draw = useCallback((node, ctx) => {
    // choose colour: branch colour for both levels
    const col  = CFG.COLOURS[node.branch] || "#888";
  
    // choose size
    const size = node.level === 0 ? CFG.TOPIC_HEX_SIZE : CFG.DISC_HEX_SIZE;
  
    // glow only on level-0
    drawHex(ctx, node, size, col, node.level === 0 ? col : undefined);
  
    // tooltip text -------------------------------------------------
    node.__title = node.level === 0
      ? node.label
      : `${node.label} (${node.year ?? "n/a"})`;
  
    // label --------------------------------------------------------
    ctx.font      = `${node.level === 0 ? CFG.FONT_SIZE_L0 : CFG.FONT_SIZE_L1}px Arial`;
    ctx.textAlign = "center";
    ctx.fillStyle = node.level === 0 ? "#fff" : "#000";
    ctx.fillText(node.label.slice(0, 14), node.x, node.y + 3);
  }, []);

  return (
    <ForceGraph2D
      ref              ={ref}
      graphData        ={data}
      nodeCanvasObject ={draw}
      nodePointerAreaPaint={(n, colour, ctx) =>
          drawHex(ctx, n,
                  n.level===0 ? CFG.TOPIC_HEX_SIZE : CFG.DISC_HEX_SIZE,
                  colour)}                                   // ← fixed param list
      onNodeClick      ={handleClick}
      cooldownTicks    ={40}
      onEngineStop     ={()=>ref.current.zoomToFit(400)}
      backgroundColor  ="#111"
    />
  );
}
