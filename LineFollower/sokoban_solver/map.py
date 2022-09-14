from typing import List


class Map:
    def __init__(self, textual_representation):
        self.name = ""
        self.map = []
        self._textual_representation_to_map(textual_representation)

    def _textual_representation_to_map(self, textual_representation: List[str]) -> None:
        for line in textual_representation:
            if line.startswith(";"):
                self.name = line.strip("; ")
            else:
                self.map.append([e for e in line])

    def print(self) -> None:
        for row in self.map:
            print(row)

    def enumerated(self) -> List[List[int]]:
        enumerated_layout = []
        for row in self.map:
            enumerated_layout.append([])
            for elem in row:
                if elem == ' ':
                    enumerated_layout[-1].append(0)    # empty
                elif elem == '#':
                    enumerated_layout[-1].append(1)    # wall
                elif elem == '$':
                    enumerated_layout[-1].append(2)    # diamond
                elif elem == '.':
                    enumerated_layout[-1].append(3)    # goal
                elif elem == '*':
                    enumerated_layout[-1].append(4)    # diamond in goal
                elif elem == '@':
                    enumerated_layout[-1].append(5)    # player

        return enumerated_layout
