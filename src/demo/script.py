import docx
from pathlib import Path, PurePath
from itertools import islice
from typing import List, Tuple

class Script:

    def __init__(self, path: str):
        self.path = Path(path)
        self.script_doc = docx.Document(self.path)
        self.tp, self.ci = list(), list()
        self.num_sections = 0
        self.length = 0
        # make this into generator?
        for i, table in enumerate(self.script_doc.tables):
            self.tp.append(list())
            self.ci.append(list())
            data = islice(zip(table.column_cells(1), table.column_cells(2)), 1, None)
            self.num_sections += 1
            for j, (ci, tp) in enumerate(data):
                self.tp[i].append(tp.text)
                self.ci[i].append(ci.text)
                self.length += 1

    def duplicate_step(self, idx: int):
        pass

    def write(self, path: str):
        pass

    def iter(self, item="ci_and_tp"):
        if item == "ci_and_tp":
            for i, sect_tp_ in enumerate(self.tp):
                for j, (ci, tp) in enumerate(zip(self.ci, self.tp)):
                    yield (i, j, ci, tp)
        if item == "step_idx":
            yield(i for i, _ in enumerate(self.tp))
        if item == "tp":
            for i, sect_tp in enumerate(self.tp):
                for j, tp in enumerate(sect_tp):
                    yield (i, j, tp)
        if item == "ci":
            for i, sect_ci in enumerate(self.ci):
                for j, ci in enumerate(sect_ci):
                    yield (i, j, ci)
        if item == "sect_ci":
            yield (sect_ci for sect_ci in self.ci)
        if item == "sect_tp":
            yield (sect_tp for sect_tp in self.tp)
        if item == "sect_ci_and_tp":
            yield ((sect_ci, sect_tp) for sect_ci, sect_tp in zip(self.ci, self.tp))


    def __len__(self):
        return self.length

    def __getitem__(self, key: Tuple[int, int] ) -> Tuple[str, str]:
        """ Returns talking point for index value passed """ 
        return self.ci[key[0]][key[1]], self.tp[key[0]][key[1]]

    def __setitem__(self, key: Tuple[int, int, int], text: str) -> None:
        if key[2] == 0:
            self.ci[key[0]][key[1]] = text
        if key[2] == 1:
            self.tp[key[0]][key[1]] = text

    def __delitem__(self, key: Tuple[int, int, int]) -> None:
        if key[2] == 0:
            del self.ci[key[0]][key[1]]
        if key[2] == 1:
            del self.tp[key[0]][key[1]]

    def __str__(self):
        return str(self.ci), str(self.tp)

    def __iter__(self):
        for i, sect_tp_ in enumerate(self.tp):
            for j, (ci, tp) in enumerate(zip(self.ci, self.tp)):
                yield (i, j, ci, tp)