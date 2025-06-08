"use client";

import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";


export default function BackgroundGraph({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: "node",
          style: {
            width: 8,
            height: 8,
            backgroundColor: "#93c5fd",
            opacity: 0.4,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1,
            "line-color": "#60a5fa",
            opacity: 0.2,
          },
        },
      ],
      layout: { name: "preset" },
      zoomingEnabled: false,
      userZoomingEnabled: false,
      userPanningEnabled: false,
    });

    const addNode = () => {
  const id = `${Date.now()}-${Math.random()}`;
  const x = Math.random() * cy.width();
  const y = Math.random() * cy.height();

  cy.add({ group: "nodes", data: { id }, position: { x, y } });

  const node = cy.$(`#${id}`);

  // ✅ animate opacity
  node.style("opacity", 0);
  node.animate({ style: { opacity: 0.4 } }, { duration: 500 });

  // ✅ 연결
  const nodes = cy.nodes();
  if (nodes.length > 1) {
    const target = nodes[Math.floor(Math.random() * (nodes.length - 1))];
    cy.add({
      group: "edges",
      data: { id: `e-${id}`, source: id, target: target.id() },
    });
  }

  // ✅ animate position 이동
  const dx = Math.random() * cy.width();
  const dy = Math.random() * cy.height();

  node.animate(
    { position: { x: dx, y: dy } },
    {
      duration: 2000,
      easing: "ease-in-out",
    }
  );

  // ✅ 사라지게
  setTimeout(() => {
    node.animate({ style: { opacity: 0 } }, { duration: 500 });
    setTimeout(() => node.remove(), 600);
  }, 4000);
};


    const interval = setInterval(addNode, 600);

    return () => {
      clearInterval(interval);
      cy.destroy();
    };
  }, []);


  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full z-0 bg-gradient-to-r from-gray-100 to-blue-100"
      style={{
      width: "100vw",
      height: "100vh",
      pointerEvents: "none",
    }}
    >{children}</div>
  );
}
