import sys, os
import lxml.etree as ET
import re
from typing import List, Tuple
from pathlib import Path, PurePath
from itertools import islice
from copy import deepcopy
from demo.section import Section
from demo.step import Step
from demo.script import Script
from demo.audio import Audio

#----------------------------DEMO------------------------------------#

class Demo:

    def __init__(self, 
                demo_path: str = "", 
                script_path: str = "", 
                audio_dir: str = "", 
                is_sectioned: bool = False):
        self.demo_path = Path(demo_path)
        self.demo_dir = self.demo_path.parent
        self.assets = Path(demo_path + "_Assets")
        self.root = ET.parse(demo_path, ET.XMLParser(strip_cdata=False)).getroot()
        self.id = self.root.find("ID").text
        self.title = self.root.find("DemoName").text
        self.is_sectioned = is_sectioned
        self.title = "" #TODO    
        self.resolution = (1920, 1080) #TODO
        self.length = 0
        self.sections: List[Section] = []
        for i, sect in enumerate(self.root.iter('Chapter')):
            print(i)
            section = Section(elem=sect, demo_dir=self.demo_dir, idx=i, demo_idx=self.length)
            self.length += len(section)
            self.sections.append(section)
        self.load(script_path, audio_dir)
        self._debug()

    def _debug(self):
        pass

    def reset_demo(self):
        pass

    def load(self, script_path: str = "", audio_path: str = ""):
        """
        Takes a directory path pointing to a DemoMate script .doc file as input
        Returns a list of tuples for each step in demo, where first element of pair contains
        section #, click instructions, and secon element contains talking points (where applicable)
        """
        if script_path:
            try:
                script = Script(script_path)
            except:
                self.script = None
                print("Script import failed.")
            else:
                if self.matches_script(script):
                    self.script = script
                    print("Script successfully imported!")
                else:
                    self.script = None
                    print("Script import failed.")
        if audio_path:
            try:
                self.audio = Audio(audio_path)
            except:
                self.audio = None
                print("Audio import failed.")
            else:
                print("Audio successfully imported!")

    def add_audio(self):
        pass

    
    def process_sections(self, add_audio: bool =True):
        self.handle_misplaced_sections()
        audio = zip(self.audio_files, self.audio_durations) if add_audio else iter()
        get_prod_notes = lambda tp: self.key_tp_phrase_match(re.findall(r"\[([A-Za-z0-9_]+)\]", tp))
        tp_streak, tp_left, prev_tp_i = -1, -1, -1
        """ while(True) -> break if no next -> do not increment if step deleted """
        for i, tp in enumerate(self.iter("has_talking_point")):
            deleted, duped, animated, is_section_step = check_prod_mods(i)
            step_i = self.step_i[i]
            if self.is_valid_tp(tp):
                num_lines = num_lines(tp)
                if num_lines > 1 and not is_section_step:
                    self.handle_multiline_tp(i, num_lines, next(audio), tp_left, tp_streak)
                    continue
                if i - prev_tp_i > 1 or prev_tp_i == -1:
                    tp_left = self.consecutive_tp(i)
                    tp_streak = tp_left + 1
                if step_i > 0 and tp_streak == tp_left + 1 and not is_section_step:
                    self.insert_section(i)
                if step_i == 0 and tp_streak != tp_left + 1:
                    self.merge_section(i, to="prev")
                self.attach_audio(i, next(audio), step=tp_left!=0)
                tp_left -= 1
                prev_tp_i = i
            prev_step_section_step = True if is_section_step else False
        self.is_sectioned = True

        def check_prod_mods(i, count: int = 0):
            prod_notes = get_prod_notes(i)
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
                return 0, self.steps_until_tp(idx), tp_streak - consec_tp #consec_tp, steps_until_tp, tp_streak
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
            if self.step_i[i] != 0:
                self.insert_section(idx)
            self.insert_section(idx+1)
        return is_type(delete_step), is_type(duplicate), is_type(set_animated), is_type(section_step)

    def key_tp_phrase_match(self, notes: List[str], bracketed=True) -> List[str]:
        """
        Key words and phrases to be checked within bracketed notes 
        """
        key_unbracketed_phrases = {
            "thank you": "", 
            "welcome": "",
            "for our purposes": ""
        }
        key_bracketed_phrases = ["this step", "this slide", "objectives overlay", "insert title", "insert end", "insert", "delete this step"]
        phrases = key_bracketed_phrases if bracketed else key_unbracketed_phrases
        return (set(phrase for phrases in phrases if note in phrase for note in notes))

    def handle_misplaced_sections(self):
        """
        Finds beginning of sections which have no valid talking points, and merges them
        """
        for i, sect in self.iter_sect():
            if not self.is_valid_tp(self.tp[i]):
                self.merge_section(idx=i, to="prev")

    def attach_audio(self, idx: int, audio: Tuple[str, str], step=False):
        step = self.steps[idx]
        assets = Path(step.find("StartPicture").find("AssetsDirectory").text)
        asset_path = PurePath(self.demo_path.parent, assets)
        audio_file, audio_dur = audio
        audio_dur *= 1000
        audio_path = Path(audio_file)
        moved_audio = audio_path.rename(PurePath(assets), "SoundBite.mp3")
        idx = step.getparent().index("StepFlavor")
        audio_xml = ET.Element("SoundBite")
        ET.SubElement(audio_xml, "File").text = "SoundBite.mp3"
        ET.SubElement(audio_xml, "TickDuration").text = str(audio_dur)
        step.getparent().insert(idx+1, audio_xml)
        if step:
            pass
        else:
            pass

    def add_audio_to_demo(self, step, audio):
        if len(list(self.tp)) != len(list(audio)):
            raise Exception("Number of soundbites mismatched with number of talking points")

    def merge_section(self, idx: int,  to: str = "prev"):
        sect_i = self.sect_i[idx]
        pass

    def insert_section(self, idx: int):
        step_i, sect_i = self.step_i[idx], self.sect_i[idx]
        step = self.steps[idx]
        for i, step_i in iter(self.step_i[idx]):
            step = self.steps[idx]
            self.sect_i[i] += 1
            if self.sect_i[i] == sect_i:
                self.step_i[i] = 0 + i
            section = self.steps.getparent().getparent().find('XmlName').find('Name').text
            #work on
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
        new_guid = str(uuid.uuid4())
        step = self.steps[idx]
        step_xml = deepcopy(step.tostring())
        idx = step.getparent().index(step) if before else step.getparent().index(step) + 1
        step.getparent().insert(idx, step_xml)
        asset_path = PurePath(Path(self.demo_path.parent), Path(step.find("StartPicture/AssetsDirectory").text))
        if as_pacing:
            is_active = step.getparent().getparent().find("IsActive").text
            step_delay = step.find("StepDelay").text
        return step

    def conscutive_tp(self, idx: int, counter: int = 0, tp: bool = True):
        curr_tp = self.is_valid_tp(self.tp[idx])
        next_tp = self.is_valid_tp(self.tp[idx+counter])
        if counter == 0 and ((not curr_tp and tp) or (curr_tp and not tp)):
            return -1
        if (next_tp and not tp) or (not next_tp and tp):
            return counter
        return self.consecutive_tp(idx, counter+1, tp)

    def set_XML_section_name(self, idx: int, name: str, until: int = 0):
        for i in self.steps[idx], self.steps[idx+until]:
            self.step[idx].getparent().getparent().find("XmlName").find("Name").text = name

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
            self.tree.write(Path(path), xml_declaration=True, encoding='utf=8')
        else:
            self.tree.write(self.demo_path, xml_declaration=True, encoding='utf=8')

    def search(self, phrase: str, action: str = None):
        pass

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

    def matches_script(self, script: Script, debug: bool = True) -> bool:
        # make advanced algorithm to check non strict sect idx and step idx, optional
        if (len(self)) != (len(script)):
            print("Demo has {} steps, script has {} steps."
                    .format(len(self), len(script)))
            return False
        if len(self.sections) != script.num_sections:
            print("Demo has same number of steps, \
                    but has {} sections, while script has {} sections."
                    .format(len(self.sections), script.num_sections))
            return False
        sect_lens = []
        for i, sect in enumerate(self.sections):
            sect_lens.append(len(sect))
            if (len(sect)) != len(script.tp):
                print("Demo and script have same number \
                    of steps and sections, but the lengths of sections are unequal. \
                    Stopped at section {} ({}): script has {} steps, demo has {} steps."
                    .format(i, sect.title, len(sect), len(script.tp)))
                return False
        if debug:
            print(len(script), len(script.num_sections), [len(s) for s in self.sections])
        return True

    def iter(self, element="step", sect_i: int = -1, sect_title: str = ""):
        if element == "step":
            return (step for step in sect for sect in self.sections)
        if element == "section":
            return (sect for sect in self.sections)
        if element == "section_steps":
            key = sect_i if sect_title == "" else sect_title
            return (step for step in self.sections[key])
        if element == "section_xml":
            return (self.root.iter('Chapter'))
        if element == "assets":
            return (folder for folder in self.assets)
        if element == "asset":
            for folder in self.iter("assets"):
                step_folder = Path(self.asset_path, folder)
                yield (PurePath(step_folder, filename) for filename in step_folder)
        if element == "image" or "step_soundbite":
            suffix = ".Png" if element == "image" else ".mp3"
            return (path for path in self.iter("asset") if path.name.endswith(suffix))
        if element == "audio_file":
            return (audio_path for audio_path in self.audio)
        if element == "has_talking_point":
            return (step for step in self.iter() if step.tp.valid_tp())
        if element == "has_click_instruction":
            return (step for step in self.iter() if len(step.ci) != 0)
        if element == "step_xml":
            for chapter in self.root.iter('Chapter'):
                yield (step for step in chapter.iter('Steps'))
        else:
            return self.iter()

    def __iter__(self):
        return (section for section in self.sections)

    def __str__(self):
        return str(list(self.get_all_steps()))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.length

    def __getitem__(self, idx: int):
        # consider adding step-getting functionality
        return self.sections[idx]

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass