from functools import cmp_to_key
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
            is_wild=False,
    ):
        self.pattern = pattern
        self.part = part
        self.children = []
        self.is_wild = is_wild

    def set(self, s: str):
        self.insert(s, split_pattern(s), 0)

    def get(self, s: str):
        return self.search(split_slash(s), 0)

    def insert(self, pattern: str, parts: List[str], height: int):
        if len(parts) == height:
            self.pattern = pattern
            return

        part = parts[height]
        is_wild, _, _ = wild_of(part)
        child = self.find_wild_child()
        if child and child.is_wild and is_wild:
            return

        child = self.find_specific_child(part)
        if child is None:
            child = Node(part=part, is_wild=is_wild)
            self.children.append(child)
        child.insert(pattern, parts, height + 1)
        self.sort()

    def search(self, parts: List[str], height: int) -> Optional["Node"]:
        _, _, is_multi = wild_of(self.part)
        if len(parts) == height or is_multi:
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

    # def match_child(self, part: str) -> Optional["Node"]:
    #     for child in self.children:
    #         if child.part == part or child.is_wild:
    #             return child
    #     return None

    def find_wild_child(self):
        for child in self.children:
            if child.is_wild:
                return child
        return None

    def find_specific_child(self, part):
        for child in self.children:
            if child.part == part:
                return child
        return None

    def match_children(self, part: str) -> List["Node"]:
        nodes = []
        for child in self.children:
            if child.part == part or child.is_wild:
                nodes.append(child)
        return nodes

    def sort(self):
        self.children = sorted(self.children, key=cmp_to_key(cmp))
        for i in self.children:
            i.sort()


def wild_of(s):
    if not s:
        return False, "", False
    if s[0] == '*':
        return True, s[1:], True
    if s[0] == ':':
        return True, s[1:], False
    if s[0] == '{' and s[-1] == '}':
        return True, s[1:-1], False
    if s.startswith('...'):
        return True, s[3:], True
    return False, "", False


def split_pattern(pattern):
    parts = []
    for part in pattern.split("/"):
        if part:
            _, _, is_multi = wild_of(part)
            if is_multi:
                break
            parts.append(part)
    return parts


def split_slash(s):
    parts = []
    for part in s.split("/"):
        if part:
            parts.append(part)
    return parts


def cmp(i: Node, j: Node):
    if not i.is_wild and j.is_wild:
        return -1
    elif i.is_wild and not j.is_wild:
        return 1
    else:
        return len(i.pattern) - len(j.pattern)
