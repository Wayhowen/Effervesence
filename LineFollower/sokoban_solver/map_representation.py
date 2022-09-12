from typing import List


class Map:
    def __init__(self, textual_representation):
        self.name = ""
        self.map = []
        self._textual_representation_to_map(textual_representation)
        
    def _textual_representation_to_map(self, textual_representation: List[str]):
        for line in textual_representation:
            if line.startswith(";"):
                self.name = line.strip("; ")
            else:
                self.map.append([e for e in line])
        
    
    def print(self) -> str:
        for row in self.map:
            print(row)