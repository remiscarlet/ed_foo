from typing import Callable, List, Optional


class TopNStack[T]:
    def __init__(self, n: int, scoring_fn: Callable[[T], int]) -> None:
        """Creates a DS to keep track of the top N instances of T using key as the value function.

        Stack should be sorted high to low in the list (Eg, [10, 5, 1])
        """
        self.stack: List[T] = []
        self.n = n
        self.scoring_fn = scoring_fn

    def __repr__(self) -> str:
        return f"TopNStack({len(self.stack)})"

    def to_list(self) -> List[T]:
        return self.stack

    def insert(self, to_insert: T) -> None:
        """Inserts `to_insert` into the stack and pops the "lowest" item if stack exceeds size `self.n`"""
        insert_idx = 0
        if self.is_empty():
            self.stack.insert(insert_idx, to_insert)

        found = False
        for idx, item in enumerate(self.stack):
            if self.scoring_fn(to_insert) > self.scoring_fn(item):
                insert_idx = idx
                found = True
                break

        if found:
            self.stack.insert(insert_idx, to_insert)

        if self.size() > self.n:
            self.stack.pop(-1)

    def pop(self) -> Optional[T]:
        if self.is_empty():
            return None
        return self.stack.pop(0)

    def is_empty(self) -> bool:
        return len(self.stack) == 0

    def size(self) -> int:
        return len(self.stack)
