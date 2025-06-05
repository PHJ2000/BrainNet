"use client";

import { useEffect, useRef, useState, memo } from "react";
import cytoscape, { Core, ElementDefinition } from "cytoscape";
import { v4 as uuidv4 } from "uuid";
import {
  createAINodes as apiCreateAINodes,
  NodeOut,
  createNode,        // ✅ 추가
  activateNode as apiActivateNode,
  updateNode,        // ✅ 추가
  fetchNodes,
} from "./nodeApi";  // ← 변경
import {
  listTags,
  attachTag,
  detachTag,
  createTag,
} from "@/features/projects/tagApi";
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
  depth: number;
  order: number;
  opacity?: number;
  frozen?: boolean;
  status?: "ACTIVE" | "GHOST";
  generated?: boolean;
  tags?: string[];
};

export interface GraphProps {
  projectId: number;
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
          <Item
            key={t.id}
            disabled={nodeTags.includes(t.id)}
            onClick={() => onAdd(t.id)}
          >
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
  const [nodes, setNodes] = useState<NodeMeta[]>([]);
  const nodesRef = useRef(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

/* fetchNodes → setNodes 하는 useEffect 안을 이렇게 교체 */
useEffect(() => {
  fetchNodes(projectId)
    .then(async (list) => {
      const metas: NodeMeta[] = list.map((n) => ({
        id: String(n.id),
        label: n.content,
        x: n.pos_x,
        y: n.pos_y,
        parentId: n.parent_id ? String(n.parent_id) : undefined,
        depth: n.depth,
        order: n.order_index,
        status: n.state,
        opacity: n.state === "GHOST" ? 0.3 : 1,
        frozen: true,
      }));

      const next: NodeMeta[] = metas;
      setNodes(next);
      nodesRef.current = next;

      /* 2️⃣ Cytoscape 화면을 갈아끼우기 */
      if (cyInstance.current) {
        cyInstance.current.elements().remove(); // 전부 지우고
        addToCy(next);                          // 새 노드·엣지 추가
      }
    })
    .catch(console.error);
}, [projectId]);


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

  /* ----- AI·빈 노드 생성 로직 ----- */
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

    /* ── AI 제안 호출 ── */
    const aiGhosts: NodeMeta[] = [];
    try {
      const srvNodes: NodeOut[] = await apiCreateAINodes(projectId, parent.label, {
        x: parent.x,
        y: parent.y,
        depth: parent.depth + 1,
        order: 0,
        parent_id: /^\d+$/.test(parent.id) ? Number(parent.id) : undefined,
      });

      const take = Math.min(aiCnt, srvNodes.length);
      for (let i = 0; i < take; i++) {
        const srv = srvNodes[i];
        const { x, y } = polarToXY(parent.x, parent.y, radius, angles[i]);
        aiGhosts.push({
          id: String(srv.id),
          label: srv.content,
          x,
          y,
          parentId: parent.id,
          depth: srv.depth,
          order: srv.order_index,
          opacity: 0.3,
          status: "GHOST",
          frozen: false,
        });
      }
    } catch (e) {
      console.error(e);
    }

    /* ── 빈(GHOST) 노드 ── */
    const blanks: NodeMeta[] = [];
    const blankCnt = childCnt - aiGhosts.length;
    for (let i = 0; i < blankCnt; i++) {
      const idx = aiGhosts.length + i;
      const { x, y } = polarToXY(parent.x, parent.y, radius, angles[idx]);

      /* 🌟 ❷ 서버에 빈 노드 저장 (content = "") */
      const blank = await createNode(projectId, {
        content: "?",
        x,
        y,
        depth: parent.depth + 1,
        order: idx,
        parent_id: Number(parent.id),
      });

      blanks.push({
        id: String(blank.id),
        label: "?",          // UI 표시만 ?
        x,
        y,
        parentId: parent.id,
        depth: blank.depth,
        order: blank.order_index,
        opacity: 0.3,
        status: "GHOST",     // 프론트에서 GHOST 표현
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
  const activateNodeLocal = async (meta: NodeMeta) => {
  try {
    await apiActivateNode(projectId, Number(meta.id)); // ✅
  } catch (e) {
    console.error(e);
    return;
  }

  meta.opacity = 1;
  meta.status  = "ACTIVE";
  meta.frozen  = true;
  cyInstance.current?.$id(meta.id).style("opacity", 1);
};

/* ───── 헬퍼 ───── */
// const isNumericId = (s: string) => /^\d+$/.test(s);

/* ───── handleTap 교체 ───── */
const handleTap = async (e: cytoscape.EventObject) => {
  const oldId = e.target.id();
  const cur   = nodesRef.current.find((n) => n.id === oldId);
  if (!cur) return;

  /* 1) AI GHOST (서버에 이미 있음) → 바로 activate */
  if (cur.status === "GHOST") {
    await activateNodeLocal(cur);
    return;
  }

  // /* 2) 서버에 아직 없는 노드(루트·“?”) → prompt + createNode */
  // if (cur.status === "GHOST") {
  //   const input = window.prompt("노드 내용을 입력하세요", cur.label);
  //   if (!input) return;

  //   try {
  //     const saved = await createNode(projectId, {
  //       content: input,
  //       x: cur.x,
  //       y: cur.y,
  //       depth: cur.depth,
  //       order: cur.order,
  //       parent_id: cur.parentId ? Number(cur.parentId) : null,
  //     });

  //     /* ──── 🔽 여기부터 기존 코드 대신 넣으세요 ──── */
  //     const newId = String(saved.id);
  //     const cy = cyInstance.current!;
  //     const oldEle   = cy.$id(oldId);          // placeholder
  //     const position = oldEle.position();      // 좌표 보존

  //     // ① placeholder 삭제
  //     oldEle.remove();

  //     // ② 새 노드 + (부모 엣지) 추가
  //     const newEles: ElementDefinition[] = [
  //       { data: { id: newId, label: saved.content }, position },
  //     ];
  //     if (cur.parentId) {
  //       newEles.push({
  //         data: {
  //           id: `e-${cur.parentId}-${newId}`,
  //           source: cur.parentId,
  //           target: newId,
  //         },
  //       });
  //     }
  //     cy.add(newEles);

  //     // ③ 프론트 상태 업데이트
  //     cur.id     = newId;
  //     cur.label  = saved.content;
  //     cur.status = "ACTIVE";
  //     cur.opacity = 1;
  //     cur.frozen  = true;

  //     // ④ 자식 노드 생성으로 이어가기
  //     await spawnChildren(cur);

  //     /* ──── 🔼 여기까지 ──── */

  //   } catch (err) {
  //     console.error(err);
  //   }
  //   return;
  // }

  /* 3) 이미 ACTIVE + 숫자 ID → 라벨 수정(updateNode) */
  const newLabel = window.prompt("노드 내용을 수정하세요", cur.label);
  if (!newLabel || newLabel === cur.label) return;

  try {
    await updateNode(projectId, Number(cur.id), { content: newLabel });
    cur.label = newLabel;
    cyInstance.current?.$id(cur.id).data("label", newLabel);

    /* ✅ 내용이 바뀐 첫 클릭이라면 spawnChildren */
    if (!cur.generated) {
      await spawnChildren(cur);
    }

  } catch (err) {
    console.error(err);
  }
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
            // "shape": "roundrectangle",             // ← 둥근 사각형
            "background-color": "#0074D9",
            label: "data(label)",
            color: "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 12,
            opacity: "data(opacity)" as any,
            // "width": "label",                      // ← 텍스트 길이에 맞게
            // "height": "label",                     // ← 텍스트 높이에 맞게
            // "padding": "10px",                     // ← 텍스트와 테두리 간격
            // "border-radius": "10px",               // ← 더 둥글게 하고 싶으면 조절
            // "min-width": 50,                       // ← 최소 너비(옵션)
            // "min-height": 30,                      // ← 최소 높이(옵션)
            // "text-wrap": "wrap",                   // ← 긴 내용 줄바꿈
            // "text-max-width": 100                  // ← 줄바꿈시 최대 폭(px)
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
        event: ev.originalEvent as MouseEvent,
        props: { nodeId },
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
