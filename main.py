from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


#Adjacency List 


@dataclass
class ALNode:
    node_id: str
    parent_id: Optional[str]
    name: str = ""


class AdjacencyListTree:
    def __init__(self) -> None:
        self.nodes: Dict[str, ALNode] = {}

    def add_node(self, node_id: str, parent_id: Optional[str], name: str = "") -> None:
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")

    
        if parent_id is not None and parent_id not in self.nodes:
            raise ValueError(f"Parent {parent_id} does not exist")

        self.nodes[node_id] = ALNode(node_id=node_id, parent_id=parent_id, name=name)

    def roots(self) -> List[str]:
        return [nid for nid, node in self.nodes.items() if node.parent_id is None]

    def children_of(self, parent_id: str) -> List[str]:
        return [nid for nid, node in self.nodes.items() if node.parent_id == parent_id]

    def __len__(self) -> int:
        return len(self.nodes)



#Materialized Path 


@dataclass
class MPNode:
 
    node_id: str
    path: str     
    name: str = ""


class MaterializedPathTree:
   
    def __init__(self, sep: str = "/") -> None:
        self.sep = sep
        self.nodes: Dict[str, MPNode] = {}

    def add_node(self, node_id: str, path: str, name: str = "") -> None:
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        if not path.startswith(self.sep):
            raise ValueError("Path must start with separator, e.g. '/A/B'")
        self.nodes[node_id] = MPNode(node_id=node_id, path=path, name=name)

    def __len__(self) -> int:
        return len(self.nodes)


# Конвертация

def convert_al_to_mp(al: AdjacencyListTree, sep: str = "/") -> MaterializedPathTree:
    mp = MaterializedPathTree(sep=sep)

    children_map: Dict[Optional[str], List[str]] = {}
    for nid, node in al.nodes.items():
        children_map.setdefault(node.parent_id, []).append(nid)


    for k in children_map:
        children_map[k].sort()

    def dfs_build(node_id: str, parent_path: str) -> None:
        if parent_path == sep:
            cur_path = f"{sep}{node_id}"
        else:
            cur_path = f"{parent_path}{sep}{node_id}"

        mp.add_node(node_id=node_id, path=cur_path, name=al.nodes[node_id].name)

        for child_id in children_map.get(node_id, []):
            dfs_build(child_id, cur_path)

    roots = children_map.get(None, [])
    for r in roots:
        dfs_build(r, sep)

    return mp



#Конвертация 2

def convert_mp_to_al(mp: MaterializedPathTree) -> AdjacencyListTree:
    al = AdjacencyListTree()

    items: List[Tuple[str, MPNode]] = list(mp.nodes.items())

    def depth(node: MPNode) -> int:
        parts = [p for p in node.path.split(mp.sep) if p]
        return len(parts)

    items.sort(key=lambda x: depth(x[1]))

    for node_id, node in items:
        parts = [p for p in node.path.split(mp.sep) if p]

        if not parts:
            raise ValueError(f"Bad path for node {node_id}: {node.path}")

        if parts[-1] != node_id:
            raise ValueError(
                f"Path mismatch: node_id={node_id} but last in path is {parts[-1]}"
            )

        if len(parts) == 1:
            parent_id = None
        else:
            parent_id = parts[-2]

        al.add_node(node_id=node_id, parent_id=parent_id, name=node.name)

    return al


#Пример

if __name__ == "__main__":
    al = AdjacencyListTree()
    al.add_node("A", None, "Root A")
    al.add_node("B", "A", "Node B")
    al.add_node("C", "A", "Node C")
    al.add_node("D", "B", "Node D")

    print("Adjacency List:")
    for nid, n in al.nodes.items():
        print(nid, "parent=", n.parent_id, "name=", n.name)

    mp = convert_al_to_mp(al)
    print("\nMaterialized Path:")
    for nid, n in mp.nodes.items():
        print(nid, "path=", n.path, "name=", n.name)

    al2 = convert_mp_to_al(mp)
    print("\nBack to Adjacency List:")
    for nid, n in al2.nodes.items():
        print(nid, "parent=", n.parent_id, "name=", n.name)
