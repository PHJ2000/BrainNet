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
  findChildrenIds,
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
  pos_x: number;
  pos_y: number;
  parentId?: string;
  depth: number;
  order: number;
  opacity?: number;
  frozen?: boolean;
  status?: "ACTIVE" | "GHOST";
  generated?: boolean;
  tags?: string[];
  // 자동 크기 조절용
  width?: number;   // 👈 추가!
  height?: number;  // 👈 추가!
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
function measureNodeSize(label: string, maxWidth = 220, font = "bold 18px Arial") {
  // 텍스트 줄수와 최대 가로길이에 따라 width, height 산출
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d")!;
  ctx.font = font;

  // 줄 단위로 나누기 (text-wrap용)
  const words = label.split(' ');
  let lines: string[] = [];
  let curLine = '';

  for (let word of words) {
    const testLine = curLine ? curLine + ' ' + word : word;
    if (ctx.measureText(testLine).width > maxWidth && curLine) {
      lines.push(curLine);
      curLine = word;
    } else {
      curLine = testLine;
    }
  }
  if (curLine) lines.push(curLine);

  const widest = Math.max(...lines.map(l => ctx.measureText(l).width), 70);
  const width = Math.min(Math.max(widest + 40, 110), 350); // min/max clamp
  const height = lines.length * 26 + 30; // 한 줄 26px, +패딩

  return { width, height };
}

/* ──────────── 그래프 컴포넌트 ─────────── */
export default function Graph({ projectId }: GraphProps) {
  const cyRef = useRef<HTMLDivElement>(null);
  const cyInstance = useRef<Core | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [tagPopoverOpen, setTagPopoverOpen] = useState(false); // 태그 팝오버/모달
  const [highlightTag, setHighlightTag] = useState<string | null>(null); // 현재 하이라이팅할 태그 id

  /* ----- 상태 ----- */
  const [nodes, setNodes] = useState<NodeMeta[]>([]);
  const nodesRef = useRef(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  /* ----- 태그 초기 로드 ----- */
  useEffect(() => {
    listTags(projectId)
      .then((tagList) => {
        // id를 string으로 변환해서 저장
        setTags(tagList.map(tag => ({ ...tag, id: String(tag.id) })));
      })
      .catch((e) => console.error("listTags", e));
  }, [projectId]);

  /* fetchNodes → setNodes 하는 useEffect 안을 이렇게 교체 */
  useEffect(() => {
    fetchNodes(projectId)
      .then(async (list) => {
        if (list && Array.isArray(list) && list.length > 0) {
          console.log("서버에서 받은 노드 리스트:", list);
        }
        const metas: NodeMeta[] = list.map((n) => {
          const { width, height } = measureNodeSize(n.content ?? "");
          return {
            id: String(n.id),
            label: n.content,
            pos_x: n.pos_x,
            pos_y: n.pos_y,
            parentId: n.parent_id ? String(n.parent_id) : undefined,
            depth: n.depth,
            order: n.order_index,
            status: n.state,
            opacity: n.state === "GHOST" ? 0.3 : 1,
            frozen: true,
            width,            // ⬅️ 반영
            height,           // ⬅️ 반영
            tags: (n.tags ?? []).map(String),
          };
        });

        setNodes(metas);
        nodesRef.current = metas;

        if (cyInstance.current) {
          cyInstance.current.elements().remove();
          addToCy(metas);
        }
      })
      .catch(console.error);
  }, [projectId]);


  const [ctxNodeId, setCtxNodeId] = useState<string | null>(null);
  const showMenu = useNodeMenu();


  //태그 하이라이팅
  useEffect(() => {
    const cy = cyInstance.current;
    if (!cy) return;

    // 모두 초기화(하이라이트 해제)
    cy.nodes().forEach((node) => {
      node.removeClass("highlighted");
    });

    if (highlightTag) {
      cy.nodes().forEach((node) => {
        const nodeData = nodesRef.current.find((n) => n.id === node.id());
        if (nodeData?.tags?.includes(highlightTag)) {
          node.addClass("highlighted");
        }
      });
    }
  }, [highlightTag]);
  /* ----- util ----- */
  const radius = 150;
  const polarToXY = (cx: number, cy: number, r: number, rad: number) => ({
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  });

  const addToCy = (arr: NodeMeta[]) => {
    const cy = cyInstance.current;
    if (!cy) return;
    const eles: ElementDefinition[] = arr.flatMap((n) => {
      // 이미 width, height가 있으므로 재계산 필요 없음
      return [
        {
          data: { id: n.id, label: n.label, width: n.width, height: n.height, tag: (n.tags ?? []).map(String) },
          position: { x: n.pos_x, y: n.pos_y },
          style: { opacity: n.opacity ?? 1 },
        },
        ...(n.parentId
          ? [{
            data: {
              id: `e-${n.parentId}-${n.id}`,
              source: n.parentId,
              target: n.id,
            },
          }]
          : []),
      ];
    });
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

    // 현재 노드와 모든 자식 노드 id 구하기
    const allNodeIds = [ctxNodeId, ...findChildrenIds(nodesRef.current, ctxNodeId)];


    try {
      // 모든 노드에 태그를 attachW
      await attachTag(projectId, realId, ctxNodeId);
      setNodes((ns) =>
        ns.map((n) =>
          allNodeIds.includes(n.id)
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

    // 현재 노드와 모든 자식 노드 id 구하기
    const allNodeIds = [ctxNodeId, ...findChildrenIds(nodesRef.current, ctxNodeId)];

    try {
      await attachTag(projectId, tagId, ctxNodeId);
      setNodes((ns) =>
        ns.map((n) =>
          allNodeIds.includes(n.id)
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
      const dir = gp ? Math.atan2(parent.pos_y - gp.pos_y, parent.pos_x - gp.pos_x) : 0;
      angles.push(dir - Math.PI / 6, dir + Math.PI / 6);
    }

    /* ── AI 제안 호출 ── */
    const aiGhosts: NodeMeta[] = [];
    try {
      // AI 노드가 필요한 개수(aiCnt)만큼 반복
      for (let i = 0; i < aiCnt; i++) {
        const { x, y } = polarToXY(parent.pos_x, parent.pos_y, radius, angles[i]);
        // 서버에 AI 노드 1개 생성 요청 (각각의 위치/순서/parent_id로)
        const srvNodes: NodeOut[] = await apiCreateAINodes(projectId, parent.label, {
          pos_x: x,
          pos_y: y,
          depth: parent.depth + 1,
          order: i,
          parent_id: /^\d+$/.test(parent.id) ? Number(parent.id) : undefined,
        });
        // 응답값이 항상 1개라고 가정(혹시라도 여러 개면 0번째만 사용)
        const srv = srvNodes[0];
        aiGhosts.push({
          id: String(srv.id),
          label: srv.content,
          pos_x: x, // 혹은 srv.pos_x
          pos_y: y, // 혹은 srv.pos_y
          parentId: parent.id,
          depth: srv.depth,
          order: srv.order_index,
          opacity: 0.3,
          status: "GHOST",
          frozen: false,
          ...measureNodeSize(srv.content),
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
      const { x, y } = polarToXY(parent.pos_x, parent.pos_y, radius, angles[idx]);

      /* 🌟 ❷ 서버에 빈 노드 저장 (content = "") */
      const blank = await createNode(projectId, {
        content: "?",
        pos_x: x,
        pos_y: y,
        depth: parent.depth + 1,
        order: idx,
        parent_id: Number(parent.id),

      });
      const parentTags = parent.tags ?? [];
      blanks.push({
        id: String(blank.id),
        label: "?",          // UI 표시만 ?
        pos_x: x,
        pos_y: y,
        parentId: parent.id,
        depth: blank.depth,
        order: blank.order_index,
        opacity: 0.3,
        status: "GHOST",     // 프론트에서 GHOST 표현
        frozen: false,
        ...measureNodeSize("?"),
        tags: [...parentTags],
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
    meta.status = "ACTIVE";
    meta.frozen = true;
    cyInstance.current?.$id(meta.id).style("opacity", 1);
  };

  /* ───── 헬퍼 ───── */
  // const isNumericId = (s: string) => /^\d+$/.test(s);

  /* ───── handleTap 교체 ───── */
  const handleTap = async (e: cytoscape.EventObject) => {
    const oldId = e.target.id();
    const cur = nodesRef.current.find((n) => n.id === oldId);
    if (!cur) return;

    /* 1) AI GHOST (서버에 이미 있음) → 바로 activate */
    if (cur.status === "GHOST") {
      if (cur.label === "?") {
        // 서버에 빈 노드로만 생성된 경우 → 사용자 입력 받아서 내용 갱신
        const input = window.prompt("노드 내용을 입력하세요", cur.label);
        if (!input) return;

        try {
          const saved = await updateNode(projectId, Number(cur.id), {
            content: input,
            pos_x: cur.pos_x,
            pos_y: cur.pos_y,
          });

          const cy = cyInstance.current!;
          const nodeEle = cy.$id(cur.id);
          nodeEle.data("label", saved.content);
          nodeEle.style("opacity", 1);

          cur.label = saved.content;
          cur.opacity = 1;
          cur.status = "ACTIVE";
          cur.frozen = true;

          await spawnChildren(cur);
        } catch (err) {
          console.error(err);
        }
      } else {
        // AI 생성된 노드 → 바로 activate
        await activateNodeLocal(cur);
      }
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

    // ... handleTap 내에서 label이 바뀐 경우
    const { width, height } = measureNodeSize(newLabel);
    cur.label = newLabel;
    cur.width = width;
    cur.height = height;
    cyInstance.current?.$id(cur.id).data({
      label: newLabel,
      width,
      height,
    });
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
      "style": [
        {
          "selector": "node",
          "style": {
            "shape": "roundrectangle",
            // ACTIVE: "#f1f5fe"(연파랑), GHOST: "#e6f0ff"(밝은 블루톤)
            "background-color": "mapData(status, 'ACTIVE', '#f1f5fe', 'GHOST', '#e6f0ff')",
            "border-width": 0,
            "label": "data(label)",
            // ACTIVE: "#374151", GHOST: "#6366f1"(인디고)이나 "#94a3b8"(연그레이블루)
            "color": "mapData(status, 'ACTIVE', '#374151', 'GHOST', '#94a3b8')",
            "font-weight": "600",
            "font-size": 17,
            "letter-spacing": "0.01em",
            "text-valign": "center",
            "text-halign": "center",
            "padding": "20px",
            "border-radius": "19px",
            "width": "data(width)",
            "height": "data(height)",
            "text-wrap": "wrap",
            "text-max-width": 210,
            "opacity": "mapData(status, 'ACTIVE', 1, 'GHOST', 0.90)",   // 더 밝게
            "transition-property": "background-color, color, opacity",
            "transition-duration": "0.2s"
          }
        },
        {
          "selector": "node:selected",
          "style": {
            "background-color": "#c7d2fe", // 강조색
            "box-shadow": "0 2px 32px 0 rgba(99, 102, 241, 0.17)",
            "color": "#3730a3",
            "border-width": 2,
            "border-color": "#6366f1",
            "opacity": 1,
          }
        },
        {
          selector: "node.highlighted",
          style: {
            "background-color": "#fcd34d", // 노란색 하이라이트
            "border-color": "#fbbf24",
            "border-width": 5,
            "z-index": 9999,
            "transition-property": "background-color, border-color, color",
            "transition-duration": "0.18s",
            "box-shadow": "0 0 22px 5px #fde68a77",
          }
        },
        {
          "selector": "edge",
          "style": {
            "width": 2.5,
            "line-color": "#b4b8f5",
            "target-arrow-color": "#b4b8f5",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "opacity": 0.8,
          },
        },
      ],
    });

    cyInstance.current = cy;
    addToCy(nodesRef.current);

    cy.on("tap", "node", handleTap);
    //위치 변경시 이벤트
    cy.on("dragfree", "node", async (event) => {
      const node = event.target;
      const id = node.id();
      const pos = node.position();

      try {
        await updateNode(projectId, id, { pos_x: pos.x, pos_y: pos.y });
        // NodeUpdatePayload 타입에 맞게 전달
      } catch (err) {
        console.error("노드 위치 업데이트 실패", err);
      }
    });

    cy.on("cxttap", "node", (ev) => {
      const nodeId = ev.target.id();
      setCtxNodeId(nodeId);
      const nativeEvent = ev.originalEvent;
      if (nativeEvent) {
        nativeEvent.preventDefault();
        nativeEvent.stopPropagation();
        // next tick에 showMenu 실행 (state 반영 이후)
        setTimeout(() => {
          showMenu({
            event: nativeEvent,
            props: { nodeId },
          });
        }, 0);
      }
    });

    return () => {
      cy.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  /* ----- 렌더 ----- */
  return (
    <>
      <div
        ref={cyRef}
        style={{
          width: "100%",
          height: "100%",
          background: "linear-gradient(135deg, #f0f4ff 0%, #f9fafe 100%)",
        }}
      />
      {/* 플로팅 버튼 */}
      <button
        style={{
          position: "absolute",
          bottom: 28,
          right: 32,
          zIndex: 10,
          padding: "12px 30px",
          borderRadius: "9999px",
          background: "linear-gradient(135deg, #6366f1 60%, #a78bfa 100%)",
          color: "white",
          fontWeight: 800,
          fontSize: 20,
          letterSpacing: 2,
          boxShadow: "0 4px 18px 0 rgba(99,102,241,0.13)",
          border: "none",
          cursor: "pointer",
          transition: "filter .18s",
          textTransform: "uppercase",
        }}
        onClick={() => setTagPopoverOpen((open) => !open)}
      >
        TAG
      </button>

      {/* 태그 리스트 팝오버 */}
      {
        tagPopoverOpen && (
          <div
            className="absolute bottom-[84px] right-8 z-30 bg-white rounded-xl shadow-xl border w-56 flex flex-col p-2"
            style={{ animation: "fadeIn .22s" }}
          >
            {tags.length === 0 ? (
              <div className="py-6 text-center text-gray-400">태그 없음</div>
            ) : (
              tags.map((tag) => (
                <button
                  key={tag.id}
                  className={`
              w-full px-4 py-2 my-1 rounded text-left font-medium
              ${highlightTag === tag.id ? "bg-indigo-100 text-indigo-700" : "hover:bg-gray-50"}
            `}
                  onClick={() =>
                    setHighlightTag((prev) => (prev === tag.id ? null : tag.id))
                  }
                >
                  {tag.name}
                </button>
              ))
            )}
          </div>
        )
      }

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
