from uuid import uuid4
from typing import List, Tuple
from demo.step import Step, Audio
from pathlib import Path, PurePath

class Section:

    def __init__(self,
                 elem = None,
                 demo_dir: str = None,
                 idx: int = -1, 
                 demo_idx: int = -1, 
                 title: str = "", 
                 steps: List[Step] = [], 
                 audio: str = "",
                 is_special: bool = False):
        """
        Object to hold section data. If initializing from elem in etree, must provide
        elem, overall index in demo (idx), and section index (sect_i).
        """
        self.root = elem
        self.demo_idx = idx
        self.steps = steps
        self.length = 0
        if elem is not None:
            self.id = elem.find("ID").text
            self.title = elem.find('XmlName').find('Name').text
            self.assets = Path(str(demo_dir) + "_Assets", self.id)
            if soundbite := elem.find("SoundBite"):
                self.audio_path = Path(self.asset_dir, soundbite.find("File"))
                self.audio_dur = soundbite.find("DurationTicks")
            for i, step in enumerate(self.iter("step_xml")):
                self.steps.append(Step(elem=step, idx=i, demo_idx=i+self.demo_idx))
                self.length += 1
        else:
            self.steps = steps
            self.demo_idx = demo_idx
            self.idx = idx
            self.title = title if title != "" else ("Section " + str(idx))
            
        self.is_special = is_special
        

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

    def iter(self, item="step"):
        if item == "step":
            yield(step for step in self.steps)
        if item == "step_xml":
            yield(step for step in self.root.iter('Step'))
        yield self.iter()

    def __iter__(self):
        yield(step for step in self.steps)
    
    def __next__(self):
        pass

    def __getitem__(self, step_i: int):
        return self.steps[step_i]

    def __setitem__(self, step_i: int, step: Step):
        self.steps[step_i] = step

    def __delitem__(self, step_i):
        del self.steps[step_i]

    def __len__(self):
        return sum(1 for _ in self.__iter__())