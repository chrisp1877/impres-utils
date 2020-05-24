import sys, os
import lxml.etree as ET
import re
from typing import List, Tuple
from pathlib import Path, PurePath
from itertools import islice
from copy import deepcopy
from dmate.section import Section
from dmate.step import Step
from dmate.script import Script, TextBox
from dmate.audio import AudioFolder
from etc.utils import validate_path, time

#----------------------------DEMO------------------------------------#

class Demo:

    def __init__(self, 
                path: str = "", 
                script_path: str = "", 
                audio_dir: str = "", 
                is_sectioned: bool = False):
        self.file = path
        self.script_file = script_path
        self.audio_dir = audio_dir
        self.is_sectioned = is_sectioned
        self.title = "" #TODO    
        self.resolution = (1920, 1080) #TODO
        self.len, self.sect_len = 0, 0
        self.sections: List[Section] = []
        self.loaded = self.load(path, script_path, audio_dir)
        self._debug()
        

    def matches_script(self, script: Script, debug: bool = True, naive: bool = True) -> bool:
        # make advanced algorithm to check non strict sect idx and step idx, optional
        if (self.len) != (len(script)):
            print("Demo has {} steps, script has {} steps.\n"
                    .format(len(self), len(script)))
            if not debug:
                return False
        if len(self.sections) != script.num_sections and not naive:
            print("""Demo has same number of steps,
                    but has {} sections, while script has {} sections.\n"""
                    .format(len(self.sections), script.num_sections))
            if not debug:
                return False
        sect_lens = []
        if not naive:
            for i, sect in enumerate(self.sections):
                sect_lens.append(len(sect))
                if (len(sect)) != len(script.tp):
                    print("""Demo and script have same number 
                        of steps and sections, but the lengths of sections are unequal. 
                        Stopped at section {} ({}): script has {} steps, demo has {} steps.\n"""
                        .format(i, sect.title, len(sect), len(script.tp)))
                    if not debug:
                        return False
                    continue
        if debug:
            print("Script length, demo length: " + str(len(script)) + ", " + str(self.len))
        return True

    def _debug(self):
        pass

    def reset_demo(self):
        pass

    def load(self, path: str = "", script_path: str = "", audio_path: str = "") -> bool:
        """
        Takes a directory path pointing to a DemoMate script .doc file as input
        Returns a list of tuples for each step in demo, where first element of pair contains
        section #, click instructions, and secon element contains talking points (where applicable)
        """
        if not validate_path(path, 'file', '.demo', 'Demo', 'open'):
            print("Demo failed to import.")
            return False
        self.path = Path(self.file)
        parser = ET.XMLParser(strip_cdata=False)
        try:
            self.root = ET.parse(path).getroot()
        except:
            print("Demo failed to import. Demo file might be corrupted or in use.")
            return False
        else:
            self.dir = str(Path(path).parent)
            self.assets = Path(Path(path + "_Assets"))
            self.sections = []
            self.id = self.root.find("ID").text
            self.title = self.root.find("DemoName").text
            for i, sect in enumerate(self.root.findall('Chapters/Chapter')):
                section = Section(elem=sect, demo_dir=self.dir, idx=i, demo_idx=self.len)
                self.len += len(section)
                self.sections.append(section)
            self.steps =[step for sect in self for step in sect]
            print(len(self.steps), id(self.steps[0]) == id(self.sections[0].steps[0]))
        if script_path:
            script = Script(script_path)
            if script.loaded:
                if self.matches_script(script):
                    print("Script imported successfully.")
                    for step, (ci, tp) in zip(self.iter_step(), script):
                        step.set_text(ci=ci.text, tp=tp.text)
                    self.script = script
            else:
                print("Script failed to import.")
        if audio_path:
            audio = AudioFolder(audio_path)
            if audio.loaded:
                self.audio = audio
                print("Audio folder imported successfully.")
            else:
                print("Audio failed to import.")
        return(self.audio.loaded and self.script.loaded)

    def add_audio(self):
        pass

    def process_sections(self, add_audio: bool =True):
        self.handle_misplaced_sections()
        audio = self.audio if add_audio else None
        tp_streak, tp_left, prev_tp_i = -1, -1, -1
        """ while(True) -> break if no next -> do not increment if step deleted """
        for i, step in enumerate(self.iter_instr()):
            tp = step.tp
            deleted, duped, animated, is_section_step = check_prod_mods(i)
            step_i = step.idx
            if tp.is_valid_tp():
                num_lines = tp.num_lines(tp)
                if num_lines > 1 and not is_section_step:
                    self.process_multiline_tp(i, num_lines, self.audio[i], tp_left, tp_streak)
                    continue
                if i - prev_tp_i > 1 or prev_tp_i == -1:
                    tp_left = self.consecutive_tp(i)
                    tp_streak = tp_left + 1
                if step_i > 0 and tp_streak == tp_left + 1 and not is_section_step:
                    self.insert_section(i)
                if step_i == 0 and tp_streak != tp_left + 1:
                    self.merge_section(i, to="prev")
                self.attach_audio(i, self.audio[i], step=tp_left!=0)
                tp_left -= 1
                prev_tp_i = i
            prev_step_section_step = True if is_section_step else False
        self.is_sectioned = True

        def check_prod_mods(step, count: int = 0):
            prod_notes = step.tp.get_prod_notes()
            if prod_notes:
                deleted, duped, animated, is_section_step = self.handle_prod_notes(i, prod_notes)
                if deleted:
                    return check_prod_mods(i+count)
            else:
                deleted, duped, animated, is_section_step = False, False, False, False
            return deleted, duped, animated, is_section_step

    def process_multiline_tp(self, idx: int, audio: Tuple[str, str], num_lines=2, consec_tp: int = None, tp_streak: int = None):
        self.insert_section(idx)
        self.duplicate_step(idx=idx, as_pacing=True, before=False)
        self.set_animated_step(idx=idx)
        self.attach_audio(idx=idx, audio=audio, step=False)
        if consec_tp and tp_streak:
            return 0,  tp_streak - consec_tp #consec_tp, steps_until_tp, tp_streak
        return 0, 0, 0

    def handle_prod_notes(self, idx: int, prod_notes: List[str], delete=False):
        duplicate = ['this step', 'objectives']
        set_animated = ['']
        delete_step = ['']
        section_step = ['']
        is_type = lambda type: any(note in type for note in prod_notes)
        if is_type(delete_step):
            del(self[idx])
        if is_type(duplicate):
            self.duplicate_step(idx)
            self.set_animated_step(idx)
        if is_type(set_animated):
            self.set_animated_step(idx)
        if is_type(section_step): #a step that is supposed to be only one of section, i.e. title
            if list(iter(self.iter_step()))[idx] != 0:
                self.insert_section(idx)
            self.insert_section(idx+1)
        return is_type(delete_step), is_type(duplicate), is_type(set_animated), is_type(section_step)

    def handle_misplaced_sections(self):
        """
        Finds beginning of sections which have no valid talking points, and merges them
        """
        for i, sect in self.iter_sect():
            if not self.is_valid_tp(self.tp[i]):
                self.merge_section(idx=i, to="prev")

    def attach_audio(self, idx: int, audio: Tuple[str, str], step=False):
        pass

    def add_audio_to_demo(self, step, audio):
        if len(list(self.tp)) != len(list(audio)):
            raise Exception("Number of soundbites mismatched with number of talking points")

    def merge_section(self, idx: int,  to: str = "prev"):
        pass

    def insert_section(self, idx: int):
        pass

    def add_pacing(self):
        pass

    def set_animated_step(self, idx: int):
        pass

    def get_talking_point_only(self, idx: int):
        pass

    def handle_scroll_steps(self, idx: int):
        pass

    # roadblock: ID? 
    def duplicate_step(self, idx: int, as_pacing: bool = False, before: bool = True):
        #new_guid = step.gen_guid()
        step = self.steps(idx)
        step_xml = deepcopy(step.tostring())
        idx = step.getparent().index(step) if before else step.getparent().index(step) + 1
        step.getparent().insert(idx, step_xml)
        asset_path = PurePath(Path(self.path.parent), Path(step.find("StartPicture/AssetsDirectory").text))
        if as_pacing:
            is_active = step.getparent().getparent().find("IsActive").text
            step_delay = step.find("StepDelay").text
        return step

    def consecutive_tp(self, step: Step, counter: int = 0, tp: bool = True):
        #curr_tp = step.tp.is_valid(self.tp[idx])
        #next_tp = step.tp.is_valid_tp(self.tp[idx+counter])
        #if counter == 0 and ((not curr_tp and tp) or (curr_tp and not tp)):
        #    return -1
        #if (next_tp and not tp) or (not next_tp and tp):
        #    return counter
        #return self.consecutive_tp(idx, counter+1, tp)
        pass

    

    def clear_script(self, step_i: int = None, sect_i: int = None, click: bool=True, tp: bool=True):
        if step_i is not None:
            if click:
                pass
            if tp:
                pass
        if sect_i is not None:
            if click:
                pass
            if tp:
                pass

    def write(self, path: str = ""):
        if path:
            self.root.write(Path(path), xml_declaration=True, encoding='utf=8')
        else:
            self.root.write(self.path, xml_declaration=True, encoding='utf=8')

    def search(self, phrase: str, action: str = None):
        return self.root.findtext(phrase)

    def search_click_instructions(self, phrase: str, action: str = None):
        pass

    def update(self):
        pass

    @staticmethod
    def is_in_brackets(self, talking_point: str):
        return re.match(r"\[(\w+)\]", talking_point)

    @staticmethod
    def get_prod_notes(self, tp: str) -> List[str]:
        notes = re.findall(r"\[([A-Za-z0-9_]+)\]", tp)
        if notes:
            return self.key_phrase_match(notes, bracketed=True)
        return []

    def shell_assets(self):
        pass

    def insert_img(self):
        pass

    def clear_talking_points(self, i: int):
        pass

    def iter_step(self):
        return DemoStepIterator(self)

    def iter_sect(self):
        return DemoSectionIterator(self)

    def iter_instr(self, ci: bool = True, tp: bool = True):
        return (step for step in self if (tp & step.tp.empty)|(ci & step.c.empty))
                
    def __iter__(self):
        return DemoSectionIterator(self)

    def __str__(self):
        return str(list(self.get_all_steps()))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.len

    def __getitem__(self, idx: int):
        return self.sections[idx]

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

#-----------------------------ITERATORS--------------------------------
#TODO: Learn a lot more about generators, implement same functionality
#       as these iterators but with generators in iter_sect() or iter_step()
#       functions in the main demo file.
#       Rigth now it just iteratively looks up items in a list... not too great
#TODO: Add parameters to return more fancy stuff

class DemoSectionIterator:

    def __init__(self, demo):
        self.sections = demo.sections
        self.len = len(demo.sections)
        self.idx = 0
        self.sect_idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < self.len:
            item = self.sections[self.idx]
        else:
            raise StopIteration
        self.idx += 1
        return item

class DemoStepIterator:

    def __init__(self, demo):
        self.sections = demo.sections
        self.sect_num = len(demo.sections)
        self.sect_idx = 0
        self.step_idx = 0
        self.step_len = len(demo)
        self.sect_len = len(self.sections[0])
        self.counter=0

    def __iter__(self):
        return self

    def __next__(self):
        if self.step_idx < self.sect_len:
            item = self.sections[self.sect_idx].steps[self.step_idx]
            self.step_idx += 1
        else:
            if self.sect_idx < self.sect_num-1:
                self.step_idx = 0
                self.sect_idx += 1
                self.sect_len = len(self.sections[self.sect_idx])
                item = self.sections[self.sect_idx].steps[self.step_idx]
            else:
                raise StopIteration
        self.counter += 1
        # if item.tp.text != "":
        #     print(self.sect_idx, self.step_idx, item.tp.text)
        return item