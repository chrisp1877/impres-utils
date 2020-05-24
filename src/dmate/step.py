from PIL import Image
import re
from uuid import uuid4
from typing import List, Tuple
from pathlib import Path, PurePath
import dmate.demo_tags as dt
from dmate.audio import SoundBite
from dmate.script import TextBox

class Step:

    #TODO check if step delaya is None if not specified
    def __init__(self, 
                elem = None,
                next_step = None,
                demo_dir: str = None,
                idx: int = -1,
                demo_idx: int = -1,
                img_path: str = "",
                hover_img_path: str = "",
                click_instr: str = "",
                talking_pt: str = "",
                audio_path: str = "",
                animated: bool = False,
                guided: bool = False,
                step_delay: float = 1.0):
        self.root = elem
        self.next = self.root.getnext()
        self.idx = idx
        self.demo_idx = demo_idx
        self.demo_dir = demo_dir
        if elem is None:
            self.asset_path = ""
            self.id = ""
            self.set_image(img_path, hover_img_path)
        self.tp, self.ci = TextBox(talking_pt), TextBox(click_instr)
        self.loaded = self.load()

    def load(self, prop_key = None, set_init_props = True, set_box_props = True, ci="", tp=""):
        self.ci.text = ci if ci else self.ci.text
        self.tp.text = tp if tp else self.tp.text
        props = self.root.find("StartPicture")
        self.prop = {k:None for k in {*dt.STEP_PROPS}}
        self.box = {k:dict.fromkeys({*v["props"], *dt.DIRS}, None) for k, v in dt.BOX_PROPS.items()}
        self.assets = Path(self.demo_dir, props.find("AssetsDirectory").text)
        self.img = PurePath(self.assets, props.find("PictureFile").text)
        self.time = props.find("Time").text
        if (hover := props.find("MouseEnterPicture")) is not None and hover.text is not None:
            self.hover = PurePath(self.assets, hover.find("PictureFile").text)
            self.hover_time = hover.find("Time").text
            self.mouse_hover = (float(hover.find(dt.MOUSE_X).text), float(hover.find(dt.MOUSE_Y).text))
        else:
            self.hover = None
        self.mouse = (float(props.find(dt.MOUSE_X).text), float(props.find(dt.MOUSE_Y).text))
        self.xml_tp_counter = 0
        props = self.root.find("StartPicture")
        if set_init_props:
            for prop, prop_dict in dt.STEP_PROPS.items():
                prop_tag, prop_type = prop_dict["tag"], prop_dict["type"]
                prop_val = self.root.find(prop_tag)
                if prop_val is not None and (prop_text := prop_val.text) is not None:
                    self.prop[prop] = prop_type(prop_text)
                else:
                    self.prop[prop] = None
        if set_box_props:
            for box_key, box_dict in dt.BOX_PROPS.items():
                if self.root.find(tag := box_dict["tag"]) is not None:
                    box_props = {**box_dict["props"], **dt.DIRS}
                    for box in self.root.findall(tag[:-1]):
                        for prop, prop_vals in box_props.items():
                            prop_tag, prop_type = prop_vals["tag"], prop_vals["type"]
                            box_prop = box.find(prop)
                            if box_prop is not None and (box_text := box_prop.text) is not None:
                                    self.box[box_key][prop].append(prop_type(box_text))
                            else:
                                self.box[box_key][prop].append(None)
        self.loaded = True

    def set_clickbox(self, nw: Tuple[int, int], se: Tuple[int, int]):
        nw, ne, se, sw = nw, (se[0], nw[1]), se, (nw[0], se[1])
    
    def set_click_location(self, pt: Tuple[int, int]):
        pass

    def set_highlight(self, nw_point: Tuple[int, int], se_point: Tuple[int, int]):
        pass

    def set_guided(self, guided: bool):
        pass

    def set_image(self, img: str = "", hover_img: str = ""):
        pass

    def set_delay(self, length: float = 1.0, off: bool = False):
        if off:
            self.root.find("StepDelay").attributes["xsi:nil"] = "true"
        else:
            self.root.find("StepDelay").text = str(length)
        self.prop["delay"] = length

    def set_audio(self, soundbite: str):
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

    def set_text(self, tp: str = "", ci: str = "", img: str = ""):
        self.tp.text = tp
        self.ci.text = ci
        if tp != "":
            self.tp.words = self.tp.get_words()
            self.tp.uniquee = self.tp.unique()

    def set_image(self, img: str):
        # BACK UP IMAGE TO ANOTHER FOLDER BEFORE SAVING
        pass

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return str(self.tp)

    def __call__(self, tp: str = None, ci: str = None, img: str = None):
        pass
    


        