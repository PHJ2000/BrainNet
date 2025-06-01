"use client";

import { useEffect, useRef, useState } from "react";
import cytoscape, { Core, ElementDefinition } from "cytoscape";
import { v4 as uuidv4 } from "uuid";
import { fetchNodes, createNode } from "./nodeApi";

type NodeMeta = {
  id: string;
  label: string;
  x: number;
  y: number;
  parentId?: string;
  opacity?: number;
  frozen?: boolean;
};

type GraphProps = {
  projectId: string;
};

export default function Graph({ projectId }: GraphProps) {
  const cyRef = useRef<HTMLDivElement>(null);
  const cyInstance = useRef<Core | null>(null);

  const [nodes, setNodes] = useState<NodeMeta[]>([]);
  const nodesRef = useRef<NodeMeta[]>(nodes);

  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  const addToCy = (elements: NodeMeta[]) => {
    const cy = cyInstance.current;
    if (!cy) return;

    const newEles: ElementDefinition[] = elements.flatMap((node) => [
      {
        data: {
          id: node.id,
          label: node.label,
          opacity: node.opacity ?? 1,
        },
        position: { x: node.x, y: node.y },
      },
      ...(node.parentId
        ? [
            {
              data: {
                id: `e-${node.parentId}-${node.id}`,
                source: node.parentId,
                target: node.id,
              },
            },
          ]
        : []),
    ]);

    console.log("🧹 Adding to Cytoscape:", newEles);

    cy.add(newEles);
    cy.fit();
  };

  const handleCreateInitialNode = async () => {
    const word = prompt("최착 아이디어를 입력하세요:");
    if (!word) return;

    const newNode = {
      id: uuidv4(),
      label: word,
      x: 300,
      y: 300,
      opacity: 1,
      frozen: true,
    };

    await createNode(projectId, {
      content: word,
      x: newNode.x,
      y: newNode.y,
      depth: 0,
      order: 0,
    });

    setNodes([newNode]);
    nodesRef.current = [newNode];
    addToCy([newNode]);
  };

  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cytoscape({
      container: cyRef.current,
      elements: [],
      layout: { name: "preset" },
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#0074D9",
            label: "data(label)",
            opacity: "data(opacity)" as any,
            color: "white",
            "text-valign": "center",
            "text-halign": "center",
            width: 40,
            height: 40,
            "font-size": 12,
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#ccc",
            "target-arrow-color": "#ccc",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
    });

    cyInstance.current = cy;

    const load = async () => {
      const raw = await fetchNodes(projectId);
      const formatted = raw.map((n: any) => ({
        id: n.id,
        label: n.content,
        x: n.x,
        y: n.y,
        opacity: n.status === "ACTIVE" ? 1 : 0.3,
        frozen: n.status === "ACTIVE",
        parentId: null,
      }));

      console.log("📦 formatted nodes", formatted);

      setNodes(formatted);
      nodesRef.current = formatted;
      addToCy(formatted);
    };

    load();

    cy.on("tap", "node", async (evt) => {
      const node = evt.target;
      const id = node.id();
      const currentNode = nodesRef.current.find((n) => n.id === id);
      if (!currentNode || currentNode.frozen) return;

      const word = prompt("노드 내용을 입력하세요:");
      if (!word) return;

      const newNode = {
        id: uuidv4(),
        label: word,
        x: currentNode.x + 100,
        y: currentNode.y + 50,
        parentId: currentNode.id,
        opacity: 1,
        frozen: true,
      };

      await createNode(projectId, {
        content: word,
        x: newNode.x,
        y: newNode.y,
        depth: 0,
        order: 0,
      });

      setNodes((prev) => [...prev, newNode]);
      nodesRef.current.push(newNode);
      addToCy([newNode]);
    });

    return () => {
      cy.destroy();
    };
  }, [projectId]);

  return (
    <div style={{ position: "relative", width: "100%", height: "600px" }}>
      <div
        ref={cyRef}
        style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
      />
      {nodes.length === 0 && (
        <button
          onClick={handleCreateInitialNode}
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "#2563eb",
            color: "white",
            padding: "8px 16px",
            borderRadius: "4px",
          }}
        >
          + 아이디어 추가
        </button>
      )}
    </div>
  );
} 