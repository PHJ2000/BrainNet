"use client";

import { useEffect, useRef, useState } from "react";
import cytoscape, { Core, ElementDefinition } from "cytoscape";
import { v4 as uuidv4 } from "uuid";
import { createAINodes as apiCreateAINodes } from "./nodeApi"; // ⬅️ 별칭!

/* ───────────── 타입 ───────────── */
export type NodeMeta = {
  id: string;
  label: string;
  x: number;
  y: number;
  parentId?: string;
  opacity?: number;           // 1(active) | 0.3(ghost)
  frozen?: boolean;
  status?: "ACTIVE" | "GHOST";
  generated?: boolean;        // 자식 제안 이미 만들었는지
};

export interface GraphProps { projectId: string; }

/* ──────────── 컴포넌트 ─────────── */
export default function Graph({ projectId }: GraphProps) {
  const cyRef        = useRef<HTMLDivElement>(null);
  const cyInstance   = useRef<Core | null>(null);
  const [nodes, setNodes] = useState<NodeMeta[]>([{
    id: "root",
    label: "주제를 입력하세요",
    x: 300, y: 300,
    opacity: 1,
    status: "ACTIVE",
    frozen: false,
  }]);
  const nodesRef = useRef(nodes);
  useEffect(() => { nodesRef.current = nodes; }, [nodes]);

  /* ───────── util ───────── */
  const radius = 150;
  const polarToXY = (cx:number, cy:number, r:number, rad:number) =>
    ({ x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) });

  const addToCy = (arr: NodeMeta[]) => {
    const cy = cyInstance.current; if (!cy) return;
    const eles: ElementDefinition[] = arr.flatMap(n => [
      {
        data: { id: n.id, label: n.label },
        position: { x: n.x, y: n.y },
        style: { opacity: n.opacity ?? 1 },
      },
      ...(n.parentId
        ? [{ data:{ id:`e-${n.parentId}-${n.id}`, source:n.parentId, target:n.id }}]
        : []),
    ]);
    cy.add(eles);
  };

  /* ─── GHOST → ACTIVE 확정 ─── */
  const activateNode = async (n: NodeMeta) => {
    n.opacity = 1; n.status = "ACTIVE"; n.frozen = true;
    cyInstance.current?.$id(n.id).style("opacity", 1);
    // TODO(선택): await fetch(`/projects/${projectId}/nodes/${n.id}/activate`, { method:"POST", credentials:"include" });
  };

  /* ─── 자식 제안 생성 ─── */
  const spawnChildren = async (parent: NodeMeta) => {
    if (parent.generated) return;               // 중복 방지
    const isRoot = !parent.parentId;
    const childCnt = isRoot ? 3 : 2;
    const aiCnt    = isRoot ? 2 : 1;
    const blankCnt = childCnt - aiCnt;

    /* 각도 배열 계산 */
    const angles: number[] = [];
    if (isRoot) {
      const base = -Math.PI/2;                 // 90° 위쪽부터
      for (let i=0;i<3;i++) angles.push(base + i*2*Math.PI/3); // 0·120·240°
    } else {
      const gp = nodesRef.current.find(x=>x.id===parent.parentId);
      const dir = gp ? Math.atan2(parent.y-gp.y, parent.x-gp.x) : 0;
      angles.push(dir - Math.PI/6, dir + Math.PI/6);           // ±30°
    }

    /* 1) AI 제안 노드 fetch (필요 수만큼) */
    const aiGhosts: NodeMeta[] = [];
    try {
      const res = await apiCreateAINodes(projectId, parent.label||"", parent.x, parent.y, 0, 0);
      // (res as any[]).slice(0, aiCnt).forEach((srv, i) => {
      const response = Array.isArray(res) ? res.slice(0, aiCnt) : [];
      for (let i = 0; i < aiCnt; i++) {
        const srv = response[i];  // 없으면 undefined
        const { x, y } = polarToXY(parent.x, parent.y, radius, angles[i]);
        aiGhosts.push({
          id:    srv?.id    ?? uuidv4(),
          label: srv?.content ?? `AI 제안 ${i+1}`,
          x, y,
          parentId: parent.id,
          opacity: 0.3,
          status: "GHOST",
          frozen: false,
        });
      // });
      }
    } catch(e){ console.error(e); }

    /* 2) 빈 노드 */
    const blanks: NodeMeta[] = Array.from({length: blankCnt}, (_,i)=>{
      const idx = aiCnt+i; const {x,y}=polarToXY(parent.x,parent.y,radius,angles[idx]);
      return {
        id: uuidv4(),
        label: "?",
        x, y,
        parentId: parent.id,
        opacity: 0.3,
        status: "GHOST",
        frozen: false,
      };
    });

    const children = [...aiGhosts, ...blanks];
    setNodes(p => { const next=[...p, ...children]; nodesRef.current=next; return next; });
    addToCy(children);

    parent.frozen = true;
    parent.generated = true;
  };

  /* ─── 클릭 핸들러 ─── */
  const handleTap = async (e: cytoscape.EventObject) => {
    const id = e.target.id();
    const cur = nodesRef.current.find(n=>n.id===id);
    if (!cur) return;

    if (cur.status==="GHOST") {                // 제안 확정
      await activateNode(cur);
      return;
    }
    if (cur.generated) return;                // 이미 확장됨
    // ── (NEW) 노드 라벨 편집 ──
    const newLabel = window.prompt("이 노드의 문장을 입력하세요", cur.label);
    if (!newLabel) return;                    // 취소면 종료
    cur.label = newLabel;
    cyInstance.current?.$id(id).data("label", newLabel);

    await spawnChildren(cur);                 // 자식 3개 만들기
  };

  /* ─── Cytoscape init ─── */
  useEffect(()=>{ if(!cyRef.current) return;
    const cy = cytoscape({
      container: cyRef.current,
      elements: [],
      layout: { name:"preset" },
      style:[
        { selector:"node", style:{
            "background-color":"#0074D9",
            "label":"data(label)",
            "color":"#fff",
            "text-valign":"center",
            "text-halign":"center",
            "font-size":12,
            "opacity":"data(opacity)" as any,
        }},
        { selector:"edge", style:{
            width:2, "line-color":"#ccc",
            "target-arrow-color":"#ccc","target-arrow-shape":"triangle",
            "curve-style":"bezier",
        }},
      ],
    });
    cyInstance.current = cy;
    addToCy(nodesRef.current);
    cy.on("tap","node",handleTap);

    // spawnChildren(nodesRef.current[0]).catch(console.error);

    return ()=>{cy.destroy();};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);

  return <div ref={cyRef} style={{width:"100%",height:"600px"}}/>;
}
