from uuid import uuid4
from typing import List, Tuple
from dmate.step import Step
from dmate.audio import SoundBite
from dmate.script import Script
from etc.utils import timefunc
from pathlib import Path, PurePath
from copy import deepcopy
import shutil
from collections import deque

#TODO implement steps in deque
#TODO: Check performance of deque vs list

class Section:

    def __init__(self,
                 elem = None,
                 copy: bool = False,
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
        if not copy:
            self.root = elem
            self.children = self.root.find("Steps")
        else:
            self.root = deepcopy(elem)
            self.children = self.root.find("Steps")
        self.idx = idx
        self.demo_idx = demo_idx
        self.length = 0
        self.demo_dir = demo_dir
        if elem is None:
            self.demo_idx = demo_idx
            self.idx = idx
            self.title = title if title != "" else "Section %s" % str(idx)
        self.is_special = is_special
        self.steps: List[Step] = []
        self.load()
        
    def load(self):
        self.id = self.root.find("ID").text
        self.title = self.root.find('XmlName').find('Name').text
        self.assets = Path(self.demo_dir + "_Assets", self.id)
        if (soundbite := self.root.find("SoundBite")) is not None:
            self.audio = SoundBite(elem=soundbite, asset_path=self.assets)
        else:
            self.audio = None
        demo_parent = str(Path(self.demo_dir).parent)
        self.steps = deque()
        for i, step in enumerate(self.root.findall('Steps/Step')):
            sect_step = Step(elem=step, idx=i, demo_idx=i+self.demo_idx, demo_dir=demo_parent)
            self.steps.append(sect_step)
            self.length += 1
        self.loaded = True

    def extend(self, steps: deque):
        self.steps.extend(steps)
        self.children.extend(step.root for step in steps)

    def append(self, step: Step):
        self.steps.append(step)
        self.children.append(deepcopy(step.root))

    def pop(self):
        pop = self.steps.pop()
        self.children.remove(pop.root)
        return pop

    def popleft(self):
        pop = self.steps.popleft()
        self.children.remove(pop.root)

    def duplicate_step(self, idx: int, as_pacing: bool = False):
        dupe = deepcopy(self.steps[idx])
        if as_pacing:
            dupe.set_animated()
        self.steps.insert(idx, dupe)
        self.children.insert(idx, dupe.root)

    def delete_step(self, idx: int):
        self.steps.remove(self.steps[idx])
        self.children.remove(self.children[idx])

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

    def set_audio(self, soundbite: SoundBite):
        source = soundbite.path
        dest = Path(self.assets, 'SoundBite.mp3')
        if not self.assets.exists():
            self.assets.mkdir()
        if not dest.exists():
            shutil.copy(str(source), str(dest))
        self.root.append(soundbite.get_root())
        self.audio = SoundBite(self.root.find("SoundBite"), asset_path=self.assets)
        

    def iter(self, item="step"):
        if item == "step": #or this doesn't work TODO
            for step in self.steps:
                yield step
        if item == "step_xml": #this doesn't work TODO
            for step in self.root.iter('Step'):
                yield step
        else:
            return self.iter()

    def __iter__(self):
        return iter(self.steps)
    
    def __getitem__(self, step_i: int):
        return self.steps[step_i]

    def __setitem__(self, step_i: int, step: Step):
        self.steps[step_i] = step

    def __delitem__(self, step_i):
        del self.steps[step_i]

    def __len__(self):
        return self.length

    def __str__(self):
        return self.title

    def __repr__(self):
        return(f'''Section({str(self.title)}, idx={str(self.idx)}, demo_idx={str(self.demo_idx)})''')

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