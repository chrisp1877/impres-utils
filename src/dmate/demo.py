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
from dmate.audio import Audio
from etc.utils import validate_path, timefunc, logger
from collections import deque, namedtuple
from PIL import Image
import shutil

#----------------------------DEMO------------------------------------#

class Demo:

    def __init__(self, 
                path: str = "", 
                script_path: str = "", 
                audio_dir: str = "", 
                is_sectioned: bool = False,
                audio_attached: bool = False):
        self.file = path
        self.script_path = script_path
        self.audio_dir = audio_dir
        self.is_sectioned = is_sectioned
        self.audio_attached = audio_attached
        self.title = "" 
        self.res = (1920, 1080) #TODO make changeable?
        self.len, self.sect_len = 0, 0
        self.sections: List[Section] = []
        self.steps: List[Step] = []
        try:
            self.loaded = self.load(path)
        except BaseException as exc:
            logger.error("Demo failed to import. %s", str(exc))
            self.loaded = False

    @validate_path #~329ms
    def load(self, path: str = ""): #w/o dq: 584ms, dq:
        """
        Takes a directory path pointing to a DemoMate script .doc file as input
        Returns a list of tuples for each step in demo, where first element of pair contains
        section #, click instructions, and secon element contains talking points (where applicable)
        """
        self.path = Path(path)
        parser = ET.XMLParser(strip_cdata=False, remove_blank_text=True)
        try:
            self.tree = ET.parse(path, parser)
            self.root = self.tree.getroot()
        except:
            print("Demo failed to import. Demo file might be corrupted or in use.")
            return False
        else:
            self.dir = str(Path(path).parent)
            self.assets = Path(path + "_Assets")
            self.sections = []
            self.id = self.root.find("ID").text
            self.title = self.root.find("DemoName").text
            for i, sect in enumerate(self.root.findall('Chapters/Chapter')):
                section = Section(elem=sect, demo_dir=self.file, idx=i, demo_idx=self.len)
                self.len += len(section)
                self.sections.append(section)
            self.steps =[step for sect in self for step in sect]
            print(f"Imported demo with {len(self)} sections and {len(self.steps)} steps.")
        self.script = Script(self.script_path)
        if self.script.loaded:
            if self.matches_script(self.script):
                print("Script: Matches demo. Script imported successfully.")
                self.set_text(self.script)
        else:
            if (exp_script := self.path.with_suffix('.docx')).exists():
                self.script = Script(str(exp_script))
                if self.script.loaded:
                    if self.matches_script(self.script):
                        print("Script: Matches demo. Script imported successfully.")
                        self.set_text(self.script)
        self.audio = Audio(self.audio_dir)
        if self.audio.loaded:
            if self.matches_audio(self.audio, by_tp=True):
                self.set_audio(self.audio)

    def matches_script(self, script: Script = None, naive: bool = True) -> bool:
        # make advanced algorithm to check non strict sect idx and step idx, optional
        if script is None:
            script = self.script
        if (self.len) != (len(script)):
            print("Script does not match demo. Demo has {} steps, script has {} steps.\n"
                    .format(len(self), len(script)))
            return False
        if len(self.sections) != script.num_sections and not naive:
            print("""Script does not match demo.Demo has same number of steps,
                    but has {} sections, while script has {} sections.\n"""
                    .format(len(self.sections), script.num_sections))
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
                    return False
        print("Script length, demo length: " + str(len(script)) + ", " + str(self.len))
        return True

    def matches_audio(self, audio: Audio = None, by_tp: bool = True):
        if not self.is_sectioned:
            self.process_sections()
        if audio is None:
            audio = self.audio
        demo_audio_len = sum(1 for _ in self.iter_audio_step(by_tp))
        if len(audio) == demo_audio_len:
            print(f"Audio: Matches demo. Both have {len(audio)} soundbites.")
            return True
        print(f"""Warning: Audio does not match demo. Audio has {len(audio)} 
                soundbites, demo should have {demo_audio_len} soundbites.""")
        return False

    def add_audio(self, start:int = 0, end: int = -1):
        if not self.is_sectioned:
            self.process_sections()
        if self.audio_attached:
            return
        #TODO: Implement functionality to PROMPT to use alternates when they appear instead of skipping
        audio_i = 0
        for i, (step, is_step_audio) in enumerate(self.iter_audio_step()):
            sb = self.audio[audio_i]
            num = sb.path.name.rsplit(".")[0].rsplit("_")[1]
            if "a" in num:
                audio_i += 1
                sb = self.audio[audio_i]
            if start > i or (end != -1 and end < 1):
                continue
            if is_step_audio:
                step.set_audio(sb)
            else:
                for sect in self.sections:
                    if sect.demo_idx == step.demo_idx:
                        sect.set_audio(sb)
            audio_i += 1
        self.audio_attached = True

    def set_text(self, script: Script = None):
        print('setting text')
        if script is None:
            script = self.script
        for step, (ci, tp) in zip(self.iter_step(), script):
            step.set_text(ci=ci.text, tp=tp.text)

    def set_audio(self, audio: Audio = None):
        if audio is None:
            audio = self.audio
        for step, soundbite in zip(self.iter_audio_step(by_tp=True), audio):
            #step.set_audio(soundbite) TODO
            pass

    def reset_demo(self):
        pass

    def word_freq(self):
        words: Dict[str, int] = {}
        for step in self.iter_instr(tp=True):
            for word in step.tp.word_count():
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        return words

    def check_sectioning(self, ignoe):
        for i, sect in self.iter_sect():
            for j, step in sect:
                if j == 0:
                    pass
            pass

    def section_demo(self):
        sect_n, step_n = [], []
        current = []
        for i, sect in enumerate(self.sections):
            for j, step in enumerate(sect):
                if step.tp.is_valid():
                    current.append(step)

    def process_sections(self, add_audio: bool =True):
        return
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
                    #tp_left = self.consecutive_tp(i)
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
        #self.attach_audio(idx=idx, audio=audio, step=False)
        if consec_tp and tp_streak:
            return 0,  tp_streak - consec_tp #consec_tp, steps_until_tp, tp_streak
        return 0, 0, 0

    def handle_prod_notes(self, idx: int, prod_notes: List[str], delete=False):
        duplicate = ['this step', 'objectives']
        set_animated = ['']
        delete_step = ['']
        section_step = ['']
        # is_type = lambda type: any(note in type for note in prod_notes)
        # if is_type(delete_step):
        #     del(self[idx])
        # if is_type(duplicate):
        #     self.duplicate_step(idx)
        #     self.set_animated_step(idx)
        # if is_type(set_animated):
        #     self.set_animated_step(idx)
        # if is_type(section_step): #a step that is supposed to be only one of section, i.e. title
        #     if list(iter(self.iter_step()))[idx] != 0:
        #         self.insert_section(idx)
        #     self.insert_section(idx+1)
        # return is_type(delete_step), is_type(duplicate), is_type(set_animated), is_type(section_step)

    def handle_misplaced_sections(self):
        """
        Finds beginning of sections which have no valid talking points, and merges them
        """
        for i, sect in self.iter_sect():
            if not self.is_valid_tp(self.tp[i]):
                self.merge_section(idx=i, to="prev")


    def merge_section(self, idx: int,  to: str = "prev"):
        pass

    def insert_section(self, idx: int):
        pass

    def add_pacing(self):
        pass

    def set_animated_step(self, idx: int):
        pass

    def handle_scroll_steps(self, idx: int):
        pass

    # roadblock: ID? 
    def duplicate_step(self, idx: int, as_pacing: bool = False, before: bool = True):
        #new_guid = step.gen_guid()
        step = self.steps[idx]
        #step_xml = deepcopy()
        #idx = step.getparent().index(step) if before else step.getparent().index(step) + 1
        #step.getparent().insert(idx, step_xml)
        #asset_path = PurePath(Path(self.path.parent), Path(step.find("StartPicture/AssetsDirectory").text))
        #if as_pacing:
        #    is_active = step.getparent().getparent().find("IsActive").text
        #    step_delay = step.find("StepDelay").text
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

    def write(self, path: str = "", append: str = ""):
        tree = ET.ElementTree(self.root)
        if path:
            tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')
        elif append:
            new_path_name = self.path.name + append
            new_path = Path(self.dir, new_path_name)
            new_assets = Path(self.dir, new_path_name+"_Assets")
            tree.write(str(new_path), pretty_print=True, xml_declaration=True, encoding='utf-8')
            new_assets.mkdir()
            try:
                shutil.copytree(str(self.assets), str(new_assets))
            except:
                print("Couldn't copy")
            else:
                self.assets = new_assets
                self.path = new_path
        else:
            tree.write(str(self.path), pretty_print=True, xml_declaration=True, encoding='utf-8')

    def search(self, phrase: str, action: str = None):
        return self.root.findtext(phrase)

    def search_click_instructions(self, phrase: str, action: str = None):
        pass

    def update(self):
        pass

    def shell_assets(self, 
                    to_sect: List[str], 
                    bg_img_path: str, 
                    asset_new_coord: Tuple[int, int],
                    asset_new_size: Tuple[int, int],
                    shell_img_path: str = None,
                    shell_img_coord: Tuple[int, int] = None,
                    shell_img_size: Tuple[int, int] = None
                    ):
        #TODO Check for exceptions in GUI? Including bounds < 0
        #TODO Back up asset image in backup folder before overwriting?
        bound = lambda size, loc: tuple(map(sum, zip(size, loc)))
        exceeds_res = lambda bound: bound[0]>self.res[0] or bound[1]>self.res[1]
        sections = [s.lower() for s in to_sect]
        if exceeds_res(bound(asset_new_size, asset_new_coord)):
            raise Exception("Resized and relocated image beyond original boundaries")
        bg_img = Image.open(bg_img_path)
        if shell_img_path is not None:
            if exceeds_res(bound(shell_img_size, shell_img_coord)):
                raise Exception("Shell image dimensions beyond original boundaries")
            shell_img = Image.open(shell_img_path)
            shell_img_resize = shell_img.resize(shell_img_size, Image.ANTIALIAS)
            bg_img.paste(shell_img_resize, shell_img_coord, shell_img_resize.convert('RGBA'))
    
        rx, ry = tuple(map(lambda z: z[0]/z[1], zip(asset_new_size, self.res)))
        self.insert_img(to_sect, bg_img, "", asset_new_size, asset_new_coord)
        for step in self.iter_steps_in_sects(sections):
            step.transform_coords(scale=(rx, ry), offset=(asset_new_coord))
            for img in step.assets.glob("*.png"):
                curr_img = bg_img.copy()
                asset = Image.open(img)
                asset_resize = asset.resize(asset_new_size, Image.ANTIALIAS)
                curr_img.paste(asset_resize, asset_new_coord, asset_resize.convert('RGBA'))

    def insert_img(self, 
                    to_sect: List[str],
                    fg_img_obj: Image,
                    fg_img_path: str,
                    fg_img_size: Tuple[int, int],
                    fg_img_coord: Tuple[int, int]
                    ):
        #TODO Find elegant way to implement boudnary checking for insertion only
        #     consider putting insert_img in shell_assets before transforming dims?
        sections = [s.lower() for s in to_sect]
        fg_img = Image.open(fg_img_path)
        for step in self.iter_steps_in_sects(sections):
            for img in step.assets.glob("*.png"):
                curr_img = fg_img.copy()
                asset = Image.open(img)
                asset_resize = asset.resize(fg_img_size, Image.ANTIALIAS)
                curr_img.paste(asset_resize, fg_img_coord, asset_resize.convert('RGBA'))

    def clear_talking_points(self, i: int):
        pass

    def iter_step(self):
        for sect in self:
            for step in sect:
                yield step

    def iter_sect(self):
        return DemoSectionIterator(self)

    def iter_instr(self, ci: bool = True, tp: bool = True):
        #return(filter(lambda step: step.tp.text, self.iter_step()))
        for step in self.iter_step():
            if (tp and step.tp.text) or (ci and step.ci.text):
                yield step

    def iter_audio_step(self, by_tp: bool = True):
        # if not self.is_sectioned:
        #     self.process_sections()
        if not by_tp:
            for sect in self:
                if sect.audio is not None:
                    yield sect.steps[0], False
                else:
                    for step in sect:
                        yield step, True
        else:
            for sect in self: 
                if sect.is_special:
                    continue
                if len(sect) == 1:
                    yield sect.steps[0], True
                else:
                    if sect.steps[0].tp.text and not sect.steps[1].tp.text:
                        yield sect.steps[0], False
                    else:
                        for step in sect.steps:
                            yield step, True

    def iter_steps_in_sects(self, sections: List[str]):
        for sect in self:
            if sect != [] and sect not in sections:
                continue
            for step in sect:
                yield step
                
    def __iter__(self):
        return DemoSectionIterator(self)

    def __str__(self):
        return str(list(self.steps))

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        if type(idx) is int:
            return self.sections[idx]
        if type(idx) is tuple:
            return self.sections[idx[0]].steps[idx[1]]

    def __setitem__(self, idx, item):
        if type(idx) is int:
            if type(item) is Section:
                self.sections[idx] = item
        if type(idx) is tuple:
            if type(item) is Step:  
                self.sections[idx[0]].steps[idx[1]] = item

    def __delitem__(self, key):
        pass

    def xml(self):
        xml = ET.tostring(self.tree, pretty_print=True, xml_declaration=True, encoding='utf-8')
        return str(xml)

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
    #returns too many steps
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