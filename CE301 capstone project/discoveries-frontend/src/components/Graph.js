// src/components/Graph.js
import React, { useEffect, useState, useCallback, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";
import drawHex from "./Hexagon";

export default function Graph() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [branchColor, setBranchColor] = useState({}); // branch => colour

  const graphRef = useRef();

  /*  Fetch topics once --------------------------------------- */
  useEffect(() => {
    axios.get("http://localhost:8000/graph").then(async (res) => {
      const topics = res.data.nodes.filter((n) => n.level === 0);

      const colorCache = {};
      await Promise.all(
        [...new Set(topics.map((t) => t.branch))].map(async (b) => {
          const { data } = await axios.get(
            `http://localhost:8000/colour/${encodeURIComponent(b)}`
          );
          colorCache[b] = data.color;
        })
      );
      setBranchColor(colorCache);
      setGraphData(res.data);
    });
  }, []);

  /*  On node click -> replace with its discoveries ------------ */
  const handleClick = useCallback(async (node) => {
    if (node.level !== 0) return;

    const { data } = await axios.get(
      `http://localhost:8000/discoveries/${encodeURIComponent(node.id)}`
    );

    const angleStep = (2 * Math.PI) / data.length;
    const newNodes = data.map((d, idx) => ({
      id: `${node.id}::${d.name}`,
      parent: node.id,
      url: d.url,
      label: d.name,
      year: d.year,
      fx: node.x + 60 * Math.cos(angleStep * idx),
      fy: node.y + 60 * Math.sin(angleStep * idx),
      level: 1
    }));

    const newLinks = newNodes.map((n) => ({
      source: node.id,
      target: n.id
    }));

    setGraphData((prev) => ({
      nodes: [...prev.nodes, ...newNodes],
      links: [...prev.links, ...newLinks]
    }));
  }, []);

  /* 3️⃣  Custom drawing (hex + glow + text) ----------------------- */
  const drawNode = useCallback(
    (node, ctx) => {
      const color =
        node.level === 0
          ? branchColor[node.branch] || "#888"
          : "#ffffff";

      const glow = node.level === 0 ? color : undefined;

      drawHex(ctx, node, node.level === 0 ? 14 : 8, color, glow);

      node.__title = node.level === 0 ? node.id : node.label;

      ctx.font = "7px Arial";
      ctx.textAlign = "center";
      ctx.fillStyle = node.level === 0 ? "#fff" : "#000";
      const label = node.level === 0 ? node.id : node.label;
      ctx.fillText(label.slice(0, 12), node.x, node.y + 3);
    },
    [branchColor]
  );



  return (
    <>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeCanvasObject={drawNode}
        nodePointerAreaPaint={(node, color, ctx) =>
          drawHex(ctx, node, node.level === 0 ? 14 : 8, color)
        }
        onNodeClick={handleClick}
        cooldownTicks={40}
        onEngineStop={() => {
          graphRef.current && graphRef.current.zoomToFit(400);
        }}
        backgroundColor="#111"
      />
      
    </>
  );
}
