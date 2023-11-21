from typing import List, Optional


class Node:
    pattern: str
    part: str
    children: List["Node"]
    is_wild: bool

    def __init__(
        self,
        pattern: str = "",
        part: str = "",
        children: List["Node"] = [],
        is_wild=False,
    ):
        self.pattern = pattern
        self.part = part
        self.children = children
        self.is_wild = is_wild

    def insert(self, pattern: str, parts: List[str], height: int):
        if len(parts) == height:
            self.pattern = pattern
            return

        part = parts[height]
        child = self.match_child(part)
        if child is None:
            is_wild = part[0] == ":" or part[0] == "*"
            child = Node(part=part, is_wild=is_wild)
            self.children.append(child)
        child.insert(pattern, parts, height + 1)

    def search(self, parts: List[str], height: int) -> Optional["Node"]:
        if len(parts) == height or self.part.startswith("*"):
            if not self.pattern:
                return None
            return self

        part = parts[height]
        children = self.match_children(part)

        for child in children:
            result = child.search(parts, height + 1)
            if result:
                return result

        return None

    def match_child(self, part: str) -> Optional["Node"]:
        for child in self.children:
            if child.part == part or child.is_wild:
                return child
        return None

    def match_children(self, part: str) -> List["Node"]:
        nodes = []
        for child in self.children:
            if child.part == part or child.is_wild:
                nodes.append(child)
        return nodes
