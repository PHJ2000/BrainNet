"use client";

import { useEffect, useRef, useState, memo } from "react";
import cytoscape, { Core, ElementDefinition } from "cytoscape";
import { v4 as uuidv4 } from "uuid";
import { createAINodes as apiCreateAINodes } from "./nodeApi"; // AI 노드
import {
  listTags,
  attachTag,
  detachTag,
  createTag,
} from "@/features/projects/tagApi"; // 태그 API
import {
  Menu,
  Item,
  Submenu,
  useContextMenu,
} from "react-contexify";
import "react-contexify/ReactContexify.css";

/* ───────────── 타입 ───────────── */
export interface Tag {
  id: string;
  name: string;
  description?: string;
  color?: string;
  node_count: number;
  summary?: string;
}

export type NodeMeta = {
  id: string;
  label: string;
  x: number;
  y: number;
  parentId?: string;
  opacity?: number;
  frozen?: boolean;
  status?: "ACTIVE" | "GHOST";
  generated?: boolean;
  tags?: string[];            // ⬅️ 태그 id 배열
};

export interface GraphProps {
  projectId: string;
}

/* ──────────── Context-menu 컴포넌트 ─────────── */
const NODE_MENU_ID = "node-ctx";

interface CtxProps {
  nodeId: string | null;
  tags: Tag[];
  nodeTags: string[];
  onAdd: (tid: string) => void;
  onRemove: (tid: string) => void;
}

const NodeContextMenu = memo(function NodeContextMenu({
  nodeId,
  tags,
  nodeTags,
  onAdd,
  onRemove,
}: CtxProps) {
  return (
    <Menu id={NODE_MENU_ID} animation="fade">
      <Submenu label="태그 달기…">
        {tags.map((t) => (
          <Item key={t.id} disabled={nodeTags.includes(t.id)} onClick={() => onAdd(t.id)}>
            {t.name}
          </Item>
        ))}
        <Item onClick={() => onAdd("__new__")}>+ 새 태그</Item>
      </Submenu>

      {nodeTags.length > 0 && (
        <Submenu label="태그 떼기…">
          {nodeTags.map((tid) => {
            const tg = tags.find((t) => t.id === tid);
            return (
              <Item key={tid} onClick={() => onRemove(tid)}>
                {tg?.name ?? tid}
              </Item>
            );
          })}
        </Submenu>
      )}
    </Menu>
  );
});

function useNodeMenu() {
  const { show } = useContextMenu({ id: NODE_MENU_ID });
  return show;
}

/* ──────────── 그래프 컴포넌트 ─────────── */
export default function Graph({ projectId }: GraphProps) {
  const cyRef = useRef<HTMLDivElement>(null);
  const cyInstance = useRef<Core | null>(null);

  /* ----- 상태 ----- */
  const [nodes, setNodes] = useState<NodeMeta[]>([
    {
      id: "root",
      label: "주제를 입력하세요",
      x: 300,
      y: 300,
      opacity: 1,
      status: "ACTIVE",
    },
  ]);
  const nodesRef = useRef(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  const [tags, setTags] = useState<Tag[]>([]);
  const [ctxNodeId, setCtxNodeId] = useState<string | null>(null);
  const showMenu = useNodeMenu();

  /* ----- 태그 초기 로드 ----- */
  useEffect(() => {
    listTags(projectId)
      .then(setTags)
      .catch((e) => console.error("listTags", e));
  }, [projectId]);

  /* ----- util ----- */
  const radius = 150;
  const polarToXY = (cx: number, cy: number, r: number, rad: number) => ({
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  });

  const addToCy = (arr: NodeMeta[]) => {
    const cy = cyInstance.current;
    if (!cy) return;
    const eles: ElementDefinition[] = arr.flatMap((n) => [
      {
        data: { id: n.id, label: n.label },
        position: { x: n.x, y: n.y },
        style: { opacity: n.opacity ?? 1 },
      },
      ...(n.parentId
        ? [
          {
            data: {
              id: `e-${n.parentId}-${n.id}`,
              source: n.parentId,
              target: n.id,
            },
          },
        ]
        : []),
    ]);
    cy.add(eles);
  };

  /* ----- 태그 attach / detach ----- */
  const handleAddTag = async (tagId: string) => {
    if (!ctxNodeId) return;
    let realId = tagId;

    if (tagId === "__new__") {
      const name = window.prompt("새 태그 이름");
      if (!name) return;
      try {
        const t = await createTag(projectId, { name });
        setTags((ts) => [...ts, t]);
        realId = t.id;
      } catch (e) {
        console.error(e);
        return;
      }
    }

    try {
      await attachTag(projectId, realId, ctxNodeId);
      setNodes((ns) =>
        ns.map((n) =>
          n.id === ctxNodeId
            ? { ...n, tags: [...(n.tags ?? []), realId] }
            : n
        )
      );
    } catch (e) {
      console.error(e);
    }
  };

  const handleRemoveTag = async (tagId: string) => {
    if (!ctxNodeId) return;
    try {
      await detachTag(projectId, tagId, ctxNodeId);
      setNodes((ns) =>
        ns.map((n) =>
          n.id === ctxNodeId
            ? { ...n, tags: (n.tags ?? []).filter((t) => t !== tagId) }
            : n
        )
      );
    } catch (e) {
      console.error(e);
    }
  };

  /* ----- AI, 자식 노드 생성 로직 (기존) ----- */
  const spawnChildren = async (parent: NodeMeta) => {
    if (parent.generated) return;
    const isRoot = !parent.parentId;
    const childCnt = isRoot ? 3 : 2;
    const aiCnt = isRoot ? 2 : 1;
    const angles: number[] = [];
    if (isRoot) {
      const base = -Math.PI / 2;
      for (let i = 0; i < 3; i++) angles.push(base + (i * 2 * Math.PI) / 3);
    } else {
      const gp = nodesRef.current.find((x) => x.id === parent.parentId);
      const dir = gp ? Math.atan2(parent.y - gp.y, parent.x - gp.x) : 0;
      angles.push(dir - Math.PI / 6, dir + Math.PI / 6);
    }

    /* AI 제안 */
    const aiGhosts: NodeMeta[] = [];
    try {
      const res = await apiCreateAINodes(
        projectId,
        parent.label,
        parent.x,
        parent.y
      );
      const arr = Array.isArray(res) ? res.slice(0, aiCnt) : [];
      for (let i = 0; i < aiCnt; i++) {
        const srv = arr[i];
        const { x, y } = polarToXY(parent.x, parent.y, radius, angles[i]);
        aiGhosts.push({
          id: srv?.id ?? uuidv4(),
          label: srv?.content ?? `AI 제안 ${i + 1}`,
          x,
          y,
          parentId: parent.id,
          opacity: 0.3,
          status: "GHOST",
          frozen: false,
        });
      }
    } catch (e) {
      console.error(e);
    }

    /* 빈 노드 */
    const blanks: NodeMeta[] = [];
    const blankCnt = childCnt - aiGhosts.length;
    for (let i = 0; i < blankCnt; i++) {
      const idx = aiGhosts.length + i;
      const { x, y } = polarToXY(parent.x, parent.y, radius, angles[idx]);
      blanks.push({
        id: uuidv4(),
        label: "?",
        x,
        y,
        parentId: parent.id,
        opacity: 0.3,
        status: "GHOST",
        frozen: false,
      });
    }

    const children = [...aiGhosts, ...blanks];
    setNodes((p) => {
      const next = [...p, ...children];
      nodesRef.current = next;
      return next;
    });
    addToCy(children);
    parent.frozen = true;
    parent.generated = true;
  };

  /* ----- 노드 활성화 ----- */
  const activateNode = (n: NodeMeta) => {
    n.opacity = 1;
    n.status = "ACTIVE";
    n.frozen = true;
    cyInstance.current?.$id(n.id).style("opacity", 1);
  };

  /* ----- 클릭 & 우클릭 핸들러 ----- */
  const handleTap = async (e: cytoscape.EventObject) => {
    const id = e.target.id();
    const cur = nodesRef.current.find((n) => n.id === id);
    if (!cur) return;

    if (cur.status === "GHOST") {
      activateNode(cur);
      return;
    }

    if (cur.generated) return;

    const newLabel = window.prompt("노드 내용을 입력하세요", cur.label);
    if (!newLabel) return;
    cur.label = newLabel;
    cyInstance.current?.$id(id).data("label", newLabel);

    await spawnChildren(cur);
  };

  /* ----- cytoscape init ----- */
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
            "shape": "roundrectangle",             // ← 둥근 사각형
            "background-color": "#0074D9",
            label: "data(label)",
            color: "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 12,
            opacity: "data(opacity)" as any,
            "width": "label",                      // ← 텍스트 길이에 맞게
            "height": "label",                     // ← 텍스트 높이에 맞게
            "padding": "10px",                     // ← 텍스트와 테두리 간격
            "border-radius": "10px",               // ← 더 둥글게 하고 싶으면 조절
            "min-width": 50,                       // ← 최소 너비(옵션)
            "min-height": 30,                      // ← 최소 높이(옵션)
            "text-wrap": "wrap",                   // ← 긴 내용 줄바꿈
            "text-max-width": 100                  // ← 줄바꿈시 최대 폭(px)
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
    addToCy(nodesRef.current);

    cy.on("tap", "node", handleTap);

    /* 우클릭 메뉴 */
    cy.on("cxttap", "node", (ev) => {
      const nodeId = ev.target.id();
      setCtxNodeId(nodeId);
      showMenu({
        event: ev.originalEvent,   // 마우스 이벤트
        props: { nodeId }          // 커스텀 데이터
      });
    });

    return () => {
      cy.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ----- 렌더 ----- */
  return (
    <>
      <div ref={cyRef} style={{ width: "100%", height: "600px" }} />
      <NodeContextMenu
        nodeId={ctxNodeId}
        tags={tags}
        nodeTags={
          ctxNodeId
            ? nodesRef.current.find((n) => n.id === ctxNodeId)?.tags ?? []
            : []
        }
        onAdd={handleAddTag}
        onRemove={handleRemoveTag}
      />
    </>
  );
}
