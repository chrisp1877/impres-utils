from PIL import Image
import re
from uuid import uuid4
from typing import List, Tuple
from pathlib import Path, PurePath
import demo.demo_tags as dt
from demo.audio import Audio

class Step:

    #TODO check if step delaya is None if not specified
    def __init__(self, 
                elem = None,
                demo_dir: str = None,
                idx: int = -1,
                demo_idx: int = -1,
                img_path: str = "",
                hover_img_path: str = "",
                click_ins: str = "",
                talk_pt: str = "",
                audio_path: str = "",
                animated: bool = False,
                guided: bool = False,
                step_delay: float = 1.0, 
                XML: str = ""):
        self.root = elem
        self.idx = idx
        self.prop = dict.fromkeys(dt.STEP_PROPS.keys(), None)
        self.box = dict.fromkeys(dt.BOX_PROPS.keys(), None)
        if elem:
            props = elem.find("StartPicture")
            self.assets = Path(self, props.find("AssetsDirectory").text)
            self.img = PurePath(self.assets, props.find("PictureFile").text)
            self.time = props.find("Time").text
            if hover := hspot.find("MouseEnterPicture"):
                self.hover = PurePath(self.assets, hover.find("PictureFile").text)
                self.hover_time = hover.find("Time").text
                self.mouse_hover = (int(hover.find(dt.MOUSE_X).text), int(hover.find(dt.MOUSE_Y).text))
            else:
                self.hover = None
            self.mouse = (int(props.find(dt.MOUSE_X).text), int(props.find(dt.MOUSE_Y).text))
            self.set_props(props=props, set_init_props=True, set_box_props=True)
        self.asset_path = ""
        self.id = ""
        self.set_image(img_path, hover_img_path)
        self.tp = StepInstruction(talk_pt)
        self.ci = StepInstruction(click_ins)
        self.set_audio(audio_path)
        if XML != "":
            self.from_XML(XML)

    def set_props(self, prop_key = None, set_init_props = False, set_box_props = True):
        props = self.root.find("StartPicture")
        if set_init_props:
            for prop, prop_dict in dt.STEP_PROPS.items():
                prop_tag, prop_type = prop_dict["tag"], prop_dict["type"]
                self.prop[prop] = prop_type(self.root.find(prop_tag).text)
        if set_box_props:
            for box_key, box_dict in dt.BOX_PROPS.items():
                if props.find(tag := box_dict["tag"]):
                    box_props = {**box_dict["props"], **dt.DIRS}
                    self.box[box_key] = dict.fromkeys(box_props[box_key].keys(), [])
                    for prop, prop_vals in box_props.items():
                        prop_tag, prop_type = prop_vals[prop]["tag"], prop_vals[prop]["type"]
                        self.box[box_key][prop].append(prop_type(props.find(prop_tag).text))

    def set_clickbox(self, nw: Tuple[int, int], se: Tuple[int, int]):
        nw, ne, se, sw = nw_point, (se[0], nw[1]), se_point, (nw[0], se[1])
    
    def set_click_location(self, pt: Tuple[int, int]):
        pass

    def set_highlight(self, nw_point: Tuple[int, int], se_point: Tuple[int, int]):
        pass

    def set_guided(self, guided: bool):
        pass

    def set_image(self, img: str = "", hover_img: str = ""):
        pass

    def set_audio(soundbite: str):
        pass

    def key_ci_phrase_match(self, phrase: str):
        pass

    def get_img_names(self, full_path=False) -> Tuple[str, str]:
        if self.hover:
            return (self.img, self.hover) if full_path else (self.img.name, self.hover.name)
        if full_path:
            num = int(re.search(r'\d+', self.img.name))
            hover_name = self.img.name.replace(str(num), str(num+1))
            hover_path = Path(self.assets, hover_name)
            return (self.img, hover_path) if full_path else (self.img.name, hover_name)

            

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.tp

#-----------------------------------------StepInstruction----------------------------#

class StepInstruction(Step):

    delimiters = [r"\n", " ", ".", ",", ":"]

    def __init__(self, val: str = ""):
        self.val = val
        if val:
            self.prod_notes = self.get_prod_notes()
            self.is_bracketed = self.is_bracketed()
            self.lines = val.splitlines()
            self.num_lines = len(self.lines)

    def __str__(self):
        return self.text

    def is_bracketed(self) -> bool:
        return re.match(r"\[(\w+)\]", self.text)

    def get_prod_notes(self) -> List[str]:
        return self.key_phrase_match(notes, bracketed=True) if notes else []

    def words(self, line: int = None):
        string = self.text if line else self.lines[line]
        return [word.lower() for word in re.findall(r'\w+', string)]

    def unique(self, line: int = None):
        return set(self.words()) if not line else set(self.words(line))

    def word_count(self, line: int = None):
        return sum(1 for _ in self.words(line))

    def iter(self, item="word_and_punc"):
        if item == "word_and_punc":
            return (el for el in re.findall(r"[\w']+|[.,!?;]", self.text))
        if item == "word":
            return self.__iter__()
        if item == "character":
            return len(self.text)
        return self.iter()

    def __len__(self):
        " Returns number of words in talking point "
        return self.word_count()

    def __iter__(self):
        " Returns generator over all of the words and punctuation separately in talking point "
        return (word.lower() for word in re.findall(r'\w+', string))
        