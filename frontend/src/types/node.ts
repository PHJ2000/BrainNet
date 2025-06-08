// types/node.ts
export interface Node {
  id: string;
  content: string;
  status: "ACTIVE" | "GHOST";
  x: number;
  y: number;
  depth: number;
  order: number;
  tags: string[];
}
