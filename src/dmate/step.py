from PIL import Image
import re
from uuid import uuid4
from typing import List, Tuple, Dict
from pathlib import Path, PurePath
import dmate.demo_tags as dt
from dmate.audio import SoundBite
from dmate.script import TextBox
import shutil
from copy import deepcopy

class Step:

    #TODO check if step delaya is None if not specified
    def __init__(self, 
                elem = None,
                copy: bool = False,
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
        if not copy:
            self.root = elem
        else:
            self.root = deepcopy(elem)
        self.idx = idx
        self.demo_idx = demo_idx
        self.demo_dir = demo_dir
        self.tp, self.ci = TextBox(talking_pt), TextBox(click_instr)
        self.loaded = self.load()

    def load(self, prop_key = None, set_init_props = True, set_box_props = True, ci="", tp=""):
        self.ci.text = ci if ci else self.ci.text
        self.tp.text = tp if tp else self.tp.text
        self.props = self.root.find("StartPicture")
        self.assets = Path(self.demo_dir, self.props.find("AssetsDirectory").text)
        self.img = PurePath(self.assets, self.props.find("PictureFile").text)
        self.time = self.props.find("Time").text
        if (hover := self.props.find("MouseEnterPicture")) is not None and hover.text is not None:
            self.hover = PurePath(self.assets, hover.find("PictureFile").text)
            self.hover_time = hover.find("Time").text
            self.mouse_hover = (float(hover.find(dt.MOUSE_X).text), float(hover.find(dt.MOUSE_Y).text))
        else:
            self.hover = None
        self.mouse = (float(self.props.find(dt.MOUSE_X).text), float(self.props.find(dt.MOUSE_Y).text))
        if (soundbite := self.root.find("SoundBite")) is not None:
            self.audio = SoundBite(elem=soundbite, asset_path=str(self.assets))
        else:
            self.audio = None 
        if set_init_props:
            for prop, prop_dict in dt.STEP_PROPS.items():
                prop_tag, prop_type = prop_dict["tag"], prop_dict["type"]
                prop_val = self.root.find(prop_tag)
                if prop_val is not None and (prop_text := prop_val.text) is not None:
                    setattr(self, prop, prop_type(prop_text))
                else:
                    setattr(self, prop, None)
        if set_box_props: #TODO make work
            for box_key, box_dict in dt.BOX_PROPS.items():
                setattr(self, box_key, {k:[] for k in {*box_dict["props"], *dt.DIRS}})
                if (self.props.find(tag := box_dict["tag"])) is not None:
                    box_props = {**box_dict["props"], **dt.DIRS}
                    for box in self.props.findall(tag+"/"+tag[:-1]):
                        for prop, prop_vals in box_props.items():
                            prop_tag, prop_type = prop_vals["tag"], prop_vals["type"]
                            try:
                                box_text = prop_type(box.find(prop_tag).text)
                                getattr(self, box_key)[prop].append(box_text)
                            except:
                                pass
                if box_key == 'hotspot':
                    if (getattr(self, box_key)['x1'][0] == dt.DEMO_RES[0] and 
                        getattr(self, box_key)['y1'][0] == dt.DEMO_RES[1]):
                        self.animated = True
                    else:
                        self.animated = False
        self.loaded = True

    def set_box_dims(self, box: str, x: Tuple[int, int], y: Tuple[int, int]):
        """
        Input: Box type (str, ex "hotspot"), (x0, x1) int tuple, (y0, y1) int tuple
        Output: None. Sets step.box["prop"][dimension] to input value.
        """
        if box in getattr(self, "box"):
            getattr(self, "box")["x0"], getattr(self, "box")["x1"] = x
            getattr(self, "box")["y0"], getattr(self, "box")["y1"] = x
    
    def set_click_location(self, pt: Tuple[int, int]):
        pass

    def set_guided(self, guided: bool):
        pass

    def set_delay(self, length: float = 1.0, off: bool = False):
        if off:
            self.root.find("StepDelay").attributes["xsi:nil"] = "true"
        else:
            self.root.find("StepDelay").text = str(length)
        setattr(self, "delay", length)

    def key_ci_phrase_match(self, phrase: str):
        pass

    def get_img_names(self, full_path=False) -> Tuple[str, str]:
        if self.hover:
            return (self.img, self.hover) if full_path else (self.img.name, self.hover.name)
        if full_path:
            num = self.img.name.rsplit()[1][:-4]
            hover_name = self.img.name.replace(str(num), str(num+1))
            hover_path = Path(self.assets, hover_name)
            return (self.img, hover_path) if full_path else (self.img.name, hover_name)
        return (self.img, self.hover)

    def set_text(self, tp: str = "", ci: str = "", img: str = ""):
        self.tp.text = tp
        self.ci.text = ci
        if tp != "":
            self.tp.words = self.tp.get_words()

    def set_audio(self, soundbite: SoundBite):
        source = soundbite.path
        dest = Path(self.assets, 'SoundBite.mp3')
        if not self.assets.exists():
            self.assets.mkdir()
        if not dest.exists():
            shutil.copy(str(source), str(dest))
        index = self.root.index(self.root.find("StepFlavor"))+1
        self.root.insert(index, soundbite.get_root())
        self.audio = SoundBite(self.root.find("SoundBite"), asset_path=str(self.assets))

    def set_image(self, img_path: str):
        # BACK UP IMAGE TO ANOTHER FOLDER BEFORE SAVING
        if not self.assets.exists():
            self.assets.mkdir()
        if Path(self.img).exists():
            backup = Path(self.img.parent, self.img.name+"_backup.png") #check this
            shutil.copy(str(self.img), str(backup))
        shutil.copy(img_path, str(self.img))
        
    def set_animated(self):
        getattr(self, 'hotspot')['x0'][0] = 0
        getattr(self, 'hotspot')['x1'][0] = dt.DEMO_RES[0]
        getattr(self, 'hotspot')['y0'][0] = 0
        getattr(self, 'hotspot')['y1'][0] = dt.DEMO_RES[1]
        for dir_key, ddict in dt.DIRS.items():
            hspot = self.props.find(f"Hotspots/Hotspot/{ddict[dir_key]['tag']}")
            hspot.text = str(getattr(self, 'hotspot')[dir_key][0])
        setattr(self, 'has_mouse', False)
        self.root.find(dt.STEP_PROPS['has_mouse']['tag']).text = 'false'

    def remove_audio(self):
        pass

    def add_audio(self):
        pass

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return str(self.tp)

    def __call__(self, tp: str = None, ci: str = None, img: str = None):
        pass
    


        