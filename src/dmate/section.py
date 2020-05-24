from uuid import uuid4
from typing import List, Tuple
from dmate.step import Step
from dmate.audio import SoundBite
from dmate.script import Script
from pathlib import Path, PurePath

class Section:

    def __init__(self,
                 elem = None,
                 next_sect = None,
                 demo_dir: str = None,
                 idx: int = -1, 
                 demo_idx: int = -1, 
                 title: str = "", 
                 audio: str = "",
                 is_special: bool = False):
        """
        Object to hold section data. If initializing from elem in etree, must provide
        elem, overall index in demo (idx), and section index (sect_i).
        """
        self.root = elem
        self.next = next
        self.demo_idx = idx
        self.length = 0
        self.demo_dir = demo_dir
        self.idx = idx
        if elem is None:
            self.demo_idx = demo_idx
            self.idx = idx
            self.title = title if title != "" else ("Section " + str(idx))
        self.is_special = is_special
        self.steps: List[Step] = []
        self.load()
        
    def load(self, elem=None):
        self.id = self.root.find("ID").text
        self.title = self.root.find('XmlName').find('Name').text
        self.assets = Path(str(self.demo_dir) + "_Assets", self.id)
        if soundbite := self.root.find("SoundBite"):
            self.audio_path = Path(str(self.assets), soundbite.find("File").text)
            self.audio_dur = soundbite.find("DurationTicks").text
        else:
            self.audio_path, self.audio_dur = None, None
        self.steps = []
        for i, step in enumerate(self.root.findall('Steps/Step')):
            sect_step = Step(elem=step, idx=i, demo_idx=i+self.demo_idx, demo_dir=self.demo_dir)
            self.steps.append(sect_step)
            self.length += 1
            if i > 0:
                self.steps[i-1].next = self.steps[i]
        self.loaded = True

    def append_step(self, step: Step):
        pass

    def insert_step(self, step: Step, before=True):
        pass

    def duplicate_tep(self, step_i: int):
        pass

    def remove_step(self, step_i: int):
        pass

    def set_animated(self, key: str = None):
        for step in self:
            step[""]

    def set_guided(self):
        for step in self:
            step.set_guided(True)

    def set_step_instructions(self, ci: str, tp: str):
        for i, step in enumerate(self):
            step.set_text(ci, tp)

    def iter(self, item="step"):
        if item == "step": #or this doesn't work TODO
            for step in self.steps:
                yield step
        if item == "step_xml": #this doesn't work TODO
            for step in self.root.iter('Step'):
                yield step
        else:
            return self.iter()

    # make this a generator?
    def __iter__(self):
        return SectionIterator(self)
    
    def __next__(self):
        pass

    def __getitem__(self, step_i: int):
        return self.steps[step_i]

    def __setitem__(self, step_i: int, step: Step):
        self.steps[step_i] = step

    def __delitem__(self, step_i):
        del self.steps[step_i]

    def __len__(self):
        return self.length

#-----------------------------------------------------------------

class SectionIterator:

    def __init__(self, sect):
        self.steps = sect.steps
        self.len = len(sect)
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < self.len:
            item = self.steps[self.idx]
        else:
            raise StopIteration
        self.idx += 1
        return item