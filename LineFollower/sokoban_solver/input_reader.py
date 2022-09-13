from map_representation import Map

class InputReader:
    def __init__(self, file_path):
        self._raw_input = self._read_input(file_path)
        
        self._maps = self._map_input_to_representation()

    def _read_input(self, file_path):
        with open(file_path, "r") as map_file:
            lines = map_file.readlines()
            return [line.rstrip() for line in lines]
        
    def _map_input_to_representation(self):
        map_textual_representation = []
        maps = {}
        for index, line in enumerate(self._raw_input):
            if line.startswith(";") and index != 0:
                map = Map(map_textual_representation)
                maps[map.name] = map
                map_textual_representation = []
            if len(line) > 0:
                map_textual_representation.append(line)
        return maps

    def print_map(self, map_name: str):
        self._maps[map_name].print()
        
    def get_map(self, map_name: str) -> Map:
        return self._maps[map_name]


if __name__ == "__main__":
    ir = InputReader("map_input.txt")
    ir.print_map("Claire")
