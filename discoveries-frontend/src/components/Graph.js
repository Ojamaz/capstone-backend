import React, { useEffect, useState, useCallback, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";
import drawHex from "./Hexagon";

//--------------- CONFIG  --------------------------
//  change visuals
// 
const CFG = {
  API_BASE        : "http://localhost:8000",
  TOPIC_HEX_SIZE  : 200,
  DISC_HEX_SIZE   : 10,
  GLOW_BLUR       : 300,
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

  /* -------- reload graph when filters change */
  useEffect(() => {
       const url = topic
         ? `${CFG.API_BASE}/graph?topic=${encodeURIComponent(topic)}` +
           `&min_year=${minYear}&max_year=${maxYear}`
         : `${CFG.API_BASE}/graph?min_year=${minYear}&max_year=${maxYear}`;
        
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

     // fix id's and position children
    const angleStep = (2 * Math.PI) / list.length || 1;
    const ring = 80 + Math.sqrt(list.length) * 20;
    const newNodes  = list.map((d, i) => ({

      id: `${node.id}::${d.name.replace(/[^a-z0-9]/gi, "_")}`,  // unique ID
      parent: node.id,
      level: 1,
      label: d.name,
      year: d.year,
      url: d.url,
      branch: node.branch,
      fx: node.x + ring * Math.cos(angleStep * i) + (Math.random() - 0.5) * 10,
      fy: node.y + ring * Math.sin(angleStep * i) + (Math.random() - 0.5) * 10,
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
  
    // ── dynamic size so the hex fits the text ───────────────
    let size;
    if (node.level === 0) {
      const w = ctx.measureText(node.label).width;
      size = Math.min(CFG.TOPIC_HEX_SIZE, 10 + w * 0.35);

    } else {
    size = CFG.DISC_HEX_SIZE;
    }

  
    // glow only on level-0
    drawHex(ctx, node, size, col, node.level === 0 ? col : undefined);
  
    // tooltip text -------------------------------------------------
    node.__title = node.level === 0
      ? node.label
      : `${node.label} (${node.year ?? "n/a"})`;
  
    // label --------------------------------------------------------
    ctx.font = `${node.level === 0 ? 10 : CFG.FONT_SIZE_L1}px Arial`;
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const maxWidth = node.level === 0 ? 70 : 40;  // max text width in px
    let label = node.label;

    // shrink label to fit hex size
    while (ctx.measureText(label).width > maxWidth && label.length > 0) {
      label = label.slice(0, -1);
    }
    if (label !== node.label) {
      label += "…";
    }

    ctx.fillText(label, node.x, node.y);

  }, []);

  return (
    <ForceGraph2D
      ref              ={ref}
      graphData        ={data}
      nodeCanvasObject ={draw}
      nodePointerAreaPaint={(n, c, ctx) =>
        drawHex(ctx, n,
          n.level === 0 ? Math.min(70, 10 + ctx.measureText(n.label).width * 0.35)
                        : CFG.DISC_HEX_SIZE,
          c
        )
      }                      
      onNodeClick      ={handleClick}
      cooldownTicks    ={40}
      onEngineStop     ={()=>ref.current.zoomToFit(400)}
      backgroundColor  ="#111"
    />
  );
}
