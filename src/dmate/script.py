import docx
from pathlib import Path, PurePath
from itertools import islice
from typing import List, Tuple
import sys
from etc.utils import validate_path
import re

class Script:

    def __init__(self, path: str = ""):
        self.file = path
        self.tp: List[TextBox] = []
        self.ci: List[TextBox] = []
        self.num_sections = 0
        self.length = 0
        self.num_ci, self.num_tp = 0, 0
        self.loaded = self.load(path)
        
    def load(self, path: str = "", verbose: bool = True) -> bool:
        if not path or not validate_path(path, "file", ".docx", "Script", "open"):
            print("Script failed to import. Invalid path provided.")
            return False
        self.path = Path(path)
        try:
            self.doc = docx.Document(self.path)
        except:
            if verbose:
                print("Document is invalid DemoMate script file.")
            self.doc = None
            return False
        else:
            for i, table in enumerate(self.doc.tables):
                prev_len = 0
                data = islice(zip(table.column_cells(1), table.column_cells(2)), 1, None)
                self.num_sections += 1
                for j, (ci, tp) in enumerate(data):
                    self.tp.append(TextBox(tp.text))
                    self.ci.append(TextBox(ci.text))
                    self.length += 1
                    if ci.text:
                        self.num_ci += 1
                    if tp.text:
                        self.num_tp += 1
            if verbose:
                print("Script: Finished loading, with {} sectons, {} steps"
                        .format(self.num_sections, len(self.tp)))
        return True

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

    def __getitem__(self, key: Tuple[int, str]):
        """ Returns talking point for index value passed """ 
        if key[1] is None:
            return self.tp[key[0]]
        if key[1] == "ci":
            return self.ci[key[0]]
        if key[1] == "tp":
            return self.tp[key[0]]
        return self.tp[key[0]]

    def __setitem__(self, key: Tuple[int, str], text) -> None:
        if type(text) is str:
            if key[1] == "ci":
                self.ci[key[0]] = text
            if key[1] == "tp":
                self.tp[key[0]] = text
        if type(text) is tuple:
            if type(text[0]) is str and type(text[1]) is str:
                self.ci[key[0]], self.tp[key[0]] = text

    def __delitem__(self, key: Tuple[int, str]) -> None:
        self.__setitem__(key, "")

    def __str__(self):
        return str(self.ci)+", "+str(self.tp)

    def __eq__(self, other):
        # consider implementing check for the case of other being a demo
        return(self.tp == other.tp and self.ci == other.ci
               for (tp, ci), (other_tp, other_ci) in zip(self, other))

    def __iter__(self):
        return ((ci, tp) for (ci, tp) in zip(self.ci, self.tp))

#-----------------------------------------StepInstruction----------------------------#

class TextBox:

    delimiters = [r"\n", " ", ".", ",", ":"]

    def __init__(self, text: str = ""):
        self.text = text
        if text:
            self.words = self.get_words(line=None)
            self.prod_notes = self.get_prod_notes()
            self.only_notes = self.is_bracketed()
            self.lines = text.splitlines()
            self.num_lines = len(self.lines)
            self.is_special = False
            self.empty = False
        else:
            self.words = []
            self.prod_notes = []
            self.empty = True

    def __call__(self):
        return self.text

    def __str__(self):
        return self.text

    def is_bracketed(self) -> bool:
        match = re.match(r"\[(\w+)\]", self.text)
        return bool(match)

    def get_words(self, line: int = None):
        if self.text:
            string = self.text if line is None else self.lines[line]
            words = re.findall(r'\w+', self.text)
            low = [word.lower() for word in words]
            return low

    def unique(self, line: int = None):
        if self.words:
            return set(self.words)
        else:
            return set(self.get_words())

    def word_count(self, line: int = None):
        if self.text:
            freq = dict.fromkeys(self.unique(), 1)
            for word in freq.keys():
                freq[word] += 1
            return freq
        return {}

    def get_non_prod_words(self):
        raise NotImplementedError()

    def is_valid(self):
        return self.text != "" and not self.bracketed and not self.is_special

    def get_prod_notes(self):
        if self.text:
            return self.key_tp_phrase_match(re.findall(r"\[([A-Za-z0-9_]+)\]", self.text))
        return []

    def key_tp_phrase_match(self, notes: List[str], bracketed=True) -> List[str]:
        key_unbracketed_phrases = {
            "thank you": "", 
            "welcome": "",
            "for our purposes": ""
        }
        key_bracketed_phrases = ["this step", "this slide", "objectives overlay", "insert title", "insert end", "insert", "delete this step"]
        phrases = key_bracketed_phrases if bracketed else key_unbracketed_phrases
        matches = []
        for note in notes:
            for phrase in phrases:
                if note in phrase:
                    matches.append(phrase)
        return matches
        

    def iter(self, item="step"):
        if item == "word_and_punc":
            return(el for el in re.findall(r"[\w']+|[.,!?;]", self.text))
        if item == "word":
            return self.__iter__()
        if item == "character":
            return(char for char in self.text)
        return self.iter()

    def __len__(self) -> int:
        " Returns number of words in talking point "
        return self.word_count()

    def __bool__(self) -> int:
        return self.text != ""

    def __iter__(self):
        " Returns generator over all of the words and punctuation separately in talking point "
        return (word.lower() for word in re.findall(r'\w+', string))