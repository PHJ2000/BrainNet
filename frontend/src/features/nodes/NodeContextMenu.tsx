import { Menu, Item, Submenu, useContextMenu } from "react-contexify";
import "react-contexify/ReactContexify.css";

type Props = {
  nodeId: string | null;                   // 현재 우클릭 된 노드 id
  tags: { id: string; name: string }[];    // 전체 태그 목록
  nodeTags: string[];                      // 노드에 이미 달린 태그 id[]
  onAdd: (tagId: string) => void;
  onRemove: (tagId: string) => void;
};

export const NODE_MENU_ID = "node-ctx";

export default function NodeContextMenu({
  nodeId, tags, nodeTags, onAdd, onRemove,
}: Props) {
  // nodeId === null 이면 비활성화
  return (
    <Menu id={NODE_MENU_ID} animation="fade">
      <Submenu label="태그 달기…">
        {tags.map(t => (
          <Item key={t.id} onClick={() => onAdd(t.id)}>
            {t.name}
          </Item>
        ))}
        <Item onClick={() => onAdd("__new__")}>+ 새 태그</Item>
      </Submenu>

      {nodeTags.length > 0 && (
        <Submenu label="태그 떼기…">
          {nodeTags.map(tid => {
            const tg = tags.find(t => t.id === tid);
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
}

export function useNodeMenu() {
  const { show } = useContextMenu({ id: NODE_MENU_ID });
  return show;   // (e, props)
}
