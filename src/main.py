import logging
import os
import re
import shutil
import sys
import timeit
from collections import deque, namedtuple
from copy import deepcopy
from functools import wraps
from itertools import islice
from pathlib import Path, PurePath
from typing import Dict, List, Tuple
import docx
import lxml.etree as ET
from mutagen.mp3 import MP3
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import (QFileSelector, QItemSelectionModel, Qt, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QButtonGroup, QComboBox, QDialog,
                             QDialogButtonBox, QDoubleSpinBox, QFileDialog,
                             QFormLayout, QFrame, QGraphicsScene, QGridLayout,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QListView, QListWidget,
                             QListWidgetItem, QMainWindow, QMenu, QMenuBar,
                             QMessageBox, QProgressBar, QProgressDialog,
                             QPushButton, QRadioButton, QSizePolicy,
                             QSpacerItem, QSpinBox, QStatusBar, QTableView,
                             QTabWidget, QTextEdit, QTreeView, QVBoxLayout,
                             QWidget)

#TODO; add default values for each

DEMO_RES = (1920, 1080)

STEP_IMG = "StartPicture"

STEP_PROPS = {
    "id": {
        "tag": "ID",
        "type": str,
    },
    "guided": {
        "tag": "IsGuided",
        "type": bool,
    },
    "has_mouse": {
        "tag": "IsPointerSuppressed",
        "type": bool,
    },
    "ci_xml": {
        "tag": "XmlInstruction/Instruction",
        "type": str,
    },
    "tp_xml": {
        "tag": "XmlScript/Script",
        "type": str,
    },
    "name": {
        "tag": "XmlName/Name",
        "type": str,
    },
    "transition": {
        "tag": "TransitionType",
        "type": str,
    },
    "bubble_dir": {
        "tag": "InstructionsOrientation",
        "type": str,
    },
    "delay": {
        "tag": "StepDelay",
        "type": float,
        "default": 1.0,
    }
}

BOX_PROPS = {
    "hotspot": {
        "tag": "Hotspots",
        "props": {}
    },
    "video": {
        "tag": "VideoRects", 
        "props": {
            "aspect_ratio_locked": {
                "tag": "IsAspectRatioLocked",
                "type": bool
            },
            "autoplay": {
                "tag": "PlaysAutomatically",
                "type": bool,
            },
            "file": {
                "tag": "Video/File",
                "type": str
            },
            "height": {
                "tag": "Video/Height",
                "type": int
            },
            "width": {
                "tag": "Video/Width",
                "type": int
            },
            "duration": {
                "tag":"Video/DurationTicks",
                "type": int
            }
        },
    },
    "jump": {
        "tag": "JumpRects",
        "props": {},
    },
    "text": {
        "tag": "TextRects",
        "props": {
            "text": {
                "tag": "Text",
                "type": str
            },
            "font": {
                "tag": "FontName",
                "type": str
            },
            "size": {
                "tag": "FontSize",
                "type": int,
            },
            "color": {
                "tag": "Color",
                "type": str,
            },
            "is_pw": {
                "tag": "IsPassword",
                "type": bool,
            },
            "pw_char": {
                "tag": "PasswordChar",
                "type": int
            }
        },
    },
    "highlight": {
        "tag": "HighlightRects",
        "props": {
            "color": {
                "tag": "BorderColor",
                "type": str,
            },
        },
            
    },
}
DIR_KEYS = ["x0", "y0", "x1", "y1"]

DIRS = {
    "x0": {"tag": "Left", "type": int}, 
    "y0": {"tag": "Top", "type": int}, 
    "x1": {"tag": "Right", "type": int},
    "y1": {"tag": "Bottom", "type": int}, 
}

MOUSE_X, MOUSE_Y = "MouseCoordinates/X", "MouseCoordinates/Y"


# Note: Only use Paths for when things are being opened.
# Store path attributes as their original string

logger = logging.Logger('catch_all')

def validate_path(func):
    def validate_path_wrapper(*args):
        path, path_str = Path(args[1]), args[1]
        func.__qualname__.split(".")
        obj, action = tuple(func.__qualname__.split("."))
        if "dir" not in action:
            filetype = "file"
            ext = ".demo" if obj == "Demo" else ".docx"
        else:
            action = action.split("_")[0]
            filetype, ext = "directory", ""
        err = lambda e: "Cannot {} {} {}: {} at location {}."\
                    .format(action, obj.capitalize(), filetype, e, path_str)
        if action == "load":
            if path_str == "":
                raise FileNotFoundError(err("Empty path."))
            if not path.exists():
                raise FileNotFoundError(err(f"No {filetype} exists"))
            if path.is_dir():
                if filetype =="file":
                    raise IsADirectoryError(err(f"Need {ext} file, not directory"))
                if not path.glob(ext):
                    raise NameError(err(f"No {ext} files found"))
            if path.is_file():
                if filetype == "directory":
                    raise NotADirectoryError(err("Found file, not directory"))
                if not path.name.endswith(ext):
                    raise NameError(err(f"File is not of type {ext}"))
        if action == "write": #empty string -> overwrie fail, is OK
            raise NotImplementedError()
        return(func(*args))
    return validate_path_wrapper
    
def debug(func):
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()] 
        signature = ", ".join(args_repr + kwargs_repr) 
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}") 
        return value
    return wrapper_debug

def timefunc(func):
    def wrap(*args):
        t0 = timeit.default_timer()
        func(*args)
        t1 = timeit.default_timer()
        print(f"Function '{func.__qualname__}, args: {args}:' took {1000*(t1-t0)}ms.")
    return wrap

#----------------------------DEMO------------------------------------#

class Audio:

    def __init__(self, path: str = ""):
        self.dir = path
        self.mp3: List[SoundBite] = []
        self.len = 0
        try:
            self.loaded = self.load_dir(path)
        except BaseException as exc:
            logger.error("Audio failed to import. %s", str(exc))
            self.loaded = False

    @validate_path
    def load_dir(self, path: str = ""):
        self.path = Path(path)
        for filepath in self.path.glob("*.mp3"):
            soundbite = SoundBite(path=str(filepath)) #guaranteed to load
            self.mp3.append(soundbite)
            self.len += 1
        print("Audio: Successfully loaded {} soundbites.".format(self.len))
        return True

    def iter_paths(self):
        return (p.resolve() for p in sorted(self.path.glob("*.mp3")))

    def iter_durations(self):
        return (MP3(audio).info.length for audio in self.iter_paths())

    def __len__(self):
        return self.len

    def __iter__(self):
        return (soundbite for soundbite in self.mp3)

    def __getitem__(self, idx: int):
        return self.mp3[idx]

    def __str__(self):
        pass

class SoundBite:

    """
    An object representing the audio data necessary to add audio to steps or sections
    in the DemoMate XML file. Will also hold functions which allow the actual audio
    to be constructed from its path, and manipulated in helpful ways.
    1 tick = 1 10/000th of a millisecond
    """

    def __init__(self, elem = None, asset_path: str = "", path: str = ""):
        self.root = elem
        if not elem:
            self.path = PurePath(path)
            self.dur =  int(MP3(str(self.path)).info.length * 10000000)
        elif asset_path:
            self.asset_path = asset_path
            self.path = PurePath(asset_path, elem.find("File").text)
            self.dur = int(MP3(str(self.path)).info.length * 10000000)
        
    def get_root(self):
        if self.root is None:
            self.root = ET.Element("SoundBite")
            sbfile = ET.SubElement(self.root, "File")
            sbdur = ET.SubElement(self.root, "DurationTicks")
            self.root.find("File").text = "SoundBite.mp3"
            self.root.find("DurationTicks").text = str(self.dur)
            return self.root
        else:
            return self.root

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        pass


class Script:

    def __init__(self, path: str = ""):
        self.file = path
        self.tp: List[TextBox] = []
        self.ci: List[TextBox] = []
        self.num_sections = 0
        self.length = 0
        self.num_ci, self.num_tp = 0, 0
        try:
            self.loaded = self.load(path)
        except BaseException as exc:
            self.loaded = False
            logger.error("Script failed to import. %s", str(exc))
        
    @validate_path
    def load(self, path: str = "") -> bool:
        self.path = Path(path)
        try:
            self.doc = docx.Document(self.path)
        except:
            raise NameError("Script is not a valid DemoMate script document.")
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
        print("Script: Finished loading, with {} sectons, {} steps"
                    .format(self.num_sections, len(self.tp)))
        return True

    def duplicate_step(self, idx: int):
        pass

    def section(self):
        pass

    def write(self, path: str):
        pass

    def iter_tp(self, item="ci_and_tp"):
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
            words = re.findall(r'\w+', self.text)
            low = [word.lower() for word in words]
            return low

    def word_count(self, line: int = None):
        if self.words is None:
            self.words = self.get_words(line)
        if self.text:
            freq = dict.fromkeys(set(self.words), 1)
            for word in freq.keys():
                freq[word] += 1
            return freq
        return {}

    def get_non_prod_words(self):
        raise NotImplementedError()

    def is_valid(self):
        return self.text != "" and not self.is_bracketed()

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

    def load(self):
        self.props = self.root.find("StartPicture")
        self.boxes = {k:dict.fromkeys({*v["props"], DIRS}, []) for k, v in BOX_PROPS.items()}
        self.assets = Path(self.demo_dir, self.props.find("AssetsDirectory").text)
        self.img = PurePath(self.assets, self.props.find("PictureFile").text)
        self.time = self.props.find("Time").text
        if (hover := self.props.find("MouseEnterPicture")) is not None and hover.text is not None:
            self.hover = PurePath(self.assets, hover.find("PictureFile").text)
            self.hover_time = hover.find("Time").text
            self.mouse_hover = (float(hover.find(MOUSE_X).text), float(hover.find(MOUSE_Y).text))
        else:
            self.hover = None
        self.mouse = (float(self.props.find(MOUSE_X).text), float(self.props.find(MOUSE_Y).text))
        if (soundbite := self.root.find("SoundBite")) is not None:
            self.audio = SoundBite(elem=soundbite, asset_path=str(self.assets))
        else:
            self.audio = None 
        for prop, prop_dict in STEP_PROPS.items():
            prop_tag, prop_type = prop_dict["tag"], prop_dict["type"]
            try:
                setattr(self, prop, prop_type(self.root.find(prop_tag).text))
            except:
                setattr(self, prop, None)
        for box_key, box_dict in BOX_PROPS.items():
            if (self.props.find(tag := box_dict["tag"])) is not None:
                box_props = {**box_dict["props"], **DIRS}
                for box in self.props.findall(tag+"/"+tag[:-1]):
                    for prop, prop_vals in box_props.items():
                        prop_tag, prop_type = prop_vals["tag"], prop_vals["type"]
                        try:
                            box_text = prop_type(box.find(prop_tag).text)
                            self.boxes[box_key][prop].append(box_text)
                        except:
                            pass
            if box_key == 'hotspot':
                if (self.boxes[box_key]['x1'][0] == DEMO_RES[0] and 
                    self.boxes[box_key]['y1'][0] == DEMO_RES[1]):
                    self.animated = True
                else:
                    self.animated = False
        self.loaded = True

    #TODO Sometimes mouse coords are ints, sometimes floats, in XML. check it out
    def set_mouse(self, x: float, y: float):
        self.mouse = (x, y)
        self.props.find(MOUSE_X).text = str(x)
        self.props.find(MOUSE_Y).text = str(y)
            
    def set_mouse_hover(self, x: float, y: float):
        self.mouse_hover = (x, y)
        self.props.find("MouseEnterPicture/"+MOUSE_X).text = str(x)
        self.props.find("MouseEnterPicture/"+MOUSE_X).text = str(y)


    def set_video_dims(self, x: int, y: int):
        self.props.find("VideoRects/VideoRect/Video/VideoHeight").text = str(y)
        self.props.find("VideoRects/VideoRect/Video/VideoWidth").text = str(x)
        self.boxes["video"]["width"], self.boxes["video"]["height"] = x, y
    
    def set_box_dims(self, box: str, x0 = None, y0 = None, x1 = None, y1 = None):
        """
        Input: Box type (str, ex "hotspot"), (x0, x1) int tuple, (y0, y1) int tuple
        Output: None. Sets step.box["prop"][dimension] to input value.
        """
        if box in self.boxes:
            tag = str(BOX_PROPS[box]["tag"])
            xmlbox = self.props.find(tag+"/"+tag[:-1])
            for i in range(len(getattr(self, "box")["x1"])):
                for d, dim in zip(DIR_KEYS, [x0, y0, x1, y1]):
                    self.boxes[box][d][i] = dim
                    xmlbox.find(DIRS[d]["tag"]).text = str(dim)

    def transform_coords(self, scale: Tuple[float, float], offset: Tuple[float, float]):
        """
        Transforms all coordinate-based and height/widgth/size based properties of
        this step by a provided scaling and offset factor
        """
        (rx, ry), (ox, oy) = scale, offset

        def transf(*coord: int, offset: bool = True):
            if not offset:
                return [int(rx*c) if i%2==0 else int(ry*c) for i,c in enumerate(coord)]
            return [int(rx*c+ox) if i%2==0 else int(ry*c+oy) for i,c in enumerate(coord)]

        for box, box_props in self.boxes.items():
            for i in range(len(box_props['x1'])):
                coords = transf(*[box_props[d][i] for d in DIR_KEYS])
                self.set_box_dims(box, *coords)
            if box == "video":
                w, h = transf(*[box_props["width"][i], box_props["height"][i]], False)
                self.set_video_dims(w, h)
            if box == "text":
                tag = "TextRects/TextRect/FontSize"
                self.boxes[box]["size"][i] *= (rx*ry + 1)
                self.props.find(tag).text = str(box_props["size"][i])
        self.set_mouse(self.mouse[0]*rx+ox, self.mouse[1]*ry+oy)
        if self.hover is not None:
            self.set_mouse_hover(self.mouse_hover[0]*rx*ox, self.mouse_hover[1]*ry*oy)
        
        

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

    def set_video(self, video_path: str):
        pass
        
    def set_animated(self):
        self.set_box_dims('hotspot', 0, 0, DEMO_RES[0], DEMO_RES[1])
        for dir_key, ddict in DIRS.items():
            hspot = self.props.find(f"Hotspots/Hotspot/{ddict[dir_key]['tag']}")
            hspot.text = str(getattr(self, 'hotspot')[dir_key][0])
        setattr(self, 'has_mouse', False)
        self.root.find(STEP_PROPS['has_mouse']['tag']).text = 'false'

    def iter_box_props(self):
        for box, box_props in self.boxes.items():
            for prop, vals in box_props.items():
                yield (prop, vals)
    
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

    # make this a generator?
    def __iter__(self):
        return iter(self.steps)
    
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

    def __str__(self):
        return self.title

    def __repr__(self):
        return(f'''Section({str(self.title)}, idx={str(self.idx)}, demo_idx={str(self.demo_idx)})''')

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






#SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

class ImpresysApplication(QApplication):

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ImpresysWindow()
        self.window.show()
        self.app.exec_()

class ImpresysWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.DEMO_PATH = ""
        self.SCRIPT_PATH = ""
        self.AUDIO_PATH = ""
        self.IMG_PATH = None
        self.SHELL_PATH = None
        self.SECTS = list()
        self.FG_LOC = [None, None]
        self.FG_SIZE = [None, None]
        self.SHELL_BG_SEPARATE = bool()
        self.SHELL_LOC = [None, None]
        self.SHELL_SIZE = [None, None]
        self.SECTS_SELECTED = set()
        self.STEPS_SELECTED = set()

        self.title = 'Impresys Utilities'
        self.left = 10
        self.top = 10
        self.width = 950
        self.height = 550
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        
        self.demo = None
        self.script = None
        self.audio = None

        self.centralwidget = QWidget(self)
        self.col_layout = QHBoxLayout(self.centralwidget)
        self.tab_widget = QTabWidget(self.centralwidget)
        self.entry_layout = QVBoxLayout()
        self.demo_pane = QVBoxLayout()
        self.demo_title = "No demo loaded"
        self.demo_tree = QTreeView()
        self.demo_info = QTreeView()
        self.demo_info.setFixedHeight(225)
        #self.demo_title = QLabel("No demo loaded")
        #self.demo_pane.addWidget(self.demo_title)
        self.demo_pane.addWidget(self.demo_tree)
        self.demo_pane.addWidget(self.demo_info)
        self.col_layout.addLayout(self.entry_layout)
        self.col_layout.addLayout(self.demo_pane)

        self.demo_layout = QHBoxLayout()
        self.demo_label = QLabel()
        self.demo_label.setText("Enter .demo file location:")
        self.demo_tbox = QLineEdit()
        self.demo_tbox.resize(150, 30)
        self.demo_btn = QPushButton('Browse...')
        self.demo_btn.setStatusTip('Browse for .demo file')
        self.demo_btn.clicked.connect(self.browse_demo)
        self.demo_layout.addWidget(self.demo_label)
        self.demo_layout.addStretch()
        self.demo_layout.addWidget(self.demo_tbox)
        self.demo_layout.addWidget(self.demo_btn)

        self.script_layout = QHBoxLayout()
        self.script_label = QLabel()
        self.script_label.setText("Enter script .docx location:")
        self.script_tbox = QLineEdit()
        self.script_tbox.resize(150, 30)
        self.script_btn = QPushButton('Browse...')
        self.script_btn.setStatusTip('Browse for .docx file')
        self.script_btn.clicked.connect(self.browse_script)
        self.script_layout.addWidget(self.script_label)
        self.script_layout.addStretch()
        self.script_layout.addWidget(self.script_tbox)
        self.script_layout.addWidget(self.script_btn)

        self.audio_layout = QHBoxLayout()
        self.audio_label = QLabel()
        self.audio_label.setText("Enter audio folder location:")
        self.audio_tbox = QLineEdit()
        self.audio_tbox.resize(150, 30)
        self.audio_btn = QPushButton('Browse...')
        self.audio_btn.setStatusTip('Browse for audio folder')
        self.audio_btn.clicked.connect(self.browse_audio)
        self.audio_layout.addWidget(self.audio_label)
        self.audio_layout.addStretch()
        self.audio_layout.addWidget(self.audio_tbox)
        self.audio_layout.addWidget(self.audio_btn)

        self.entry_layout.addLayout(self.demo_layout)
        self.entry_layout.addLayout(self.script_layout)
        self.entry_layout.addLayout(self.audio_layout)
        self.entry_layout.addWidget(self.tab_widget)

        self.addStatusBar()
        self.addMenuBar()
        self.configPreview()
        self.setTabs()
        self.setFirstTab()
        self.setSecondTab()
        self.setSectionTab()
        self.setAudioTab()
        self.setXmlTab()
        self.progBar = QProgressBar()
        self.entry_layout.addWidget(self.tab_widget)
        #self.entry_layout.addWidget(self.progBar, 1, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def addMenuBar(self):

        def additem(menu, icon, name, shortcut, tip, func=None):
            item = QAction(QIcon(icon), name, self)
            item.setShortcut(shortcut)
            item.setStatusTip(tip)
            if func is not None:
                item.triggered.connect(func)
            menu.addAction(item)
        
        mainMenu = self.menuBar()
        filem = mainMenu.addMenu('File')
        editm = mainMenu.addMenu('Edit')
        viewm = mainMenu.addMenu('View')
        toolsm = mainMenu.addMenu('Tools')
        aboutm = mainMenu.addMenu('About')
        helpm = mainMenu.addMenu('Help')

        additem(filem, 'open1.png', 'Import Demo', 'Ctrl+Shift+D', 'Import demo', self.browse_demo)
        additem(filem, 'open2.png', 'Import Script', 'Ctrl+Shift+S', 'Import script', self.browse_script)
        additem(filem, 'open3.png', 'Import Audio', 'Ctrl+Shift+A', 'Import audio', self.browse_audio)
        additem(filem, 'save.png', 'Save config', 'Ctrl+S', 'Save currently inputted variables to a text file', self.saveConfig)
        additem(filem, 'load.png', 'Load config', 'Ctrl+O', 'Load variables previously saved to a text file', self.loadConfig)
        additem(filem, 'exit24.png', 'Exit', 'Ctrl+Q', 'Exit application', self.close)

        additem(editm, "prefs.png", "Preferences", "Ctrl+P", "Change preferences for different utilites")

        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setShortcut('Ctrl+Shift+V')
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)
        viewm.addAction(viewStatAct)

        viewPrev = QAction('View preview', self, checkable=True)
        viewPrev.setShortcut('Ctrl+Shift+P')
        viewPrev.setStatusTip('View preview of shelling / insertion points')
        viewPrev.setChecked(True)
        viewPrev.triggered.connect(self.preview_img)
        viewm.addAction(viewPrev)

        aboutButton = QAction(QIcon("about1.png"), "About", self)
        aboutButton.setShortcut('Ctrl+A')
        aboutButton.setStatusTip('About application')
        aboutButton.triggered.connect(self.open_about)
        aboutm.addAction(aboutButton)

        helpButton = QAction(QIcon("help.png"), "Help", self)
        helpButton.setShortcut('Ctrl+H')
        helpButton.setStatusTip('Help for shelling and inserting')
        helpButton.triggered.connect(self.open_help)
        helpm.addAction(helpButton)

    def configPreview(self):
        self.shellLayout = QVBoxLayout()

    def setTabs(self):
        
        self.tab_widget.setObjectName("tabWidget")
        self.shellTab = QWidget()
        self.shellTab.setObjectName("shellTab")
        self.shellTab.setStatusTip("Performing shelling on demo assets")
        self.insTab = QWidget()
        self.insTab.setObjectName("insTab")
        self.insTab.setStatusTip("Insert an image into demo assets")
        self.xmlTab = QWidget()
        self.xmlTab.setObjectName("xmlTab")
        self.xmlTab.setStatusTip("Perform bulk XML edits on demo")

    def addStatusBar(self):
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("Shell or insert status")
        self.statusbar.showMessage("Ready for shelling/insertion")
        self.setStatusBar(self.statusbar)

    def setFirstTab(self):
        self.shellForm = QFormLayout(self.shellTab)
        self.shellForm.setVerticalSpacing(10)
        self.shellForm.setHorizontalSpacing(5)
        self.shellForm.setContentsMargins(15, 15, 15, 15)

        self.imgPreviewLayout = QGridLayout()
        self.imgPreview = QGraphicsScene()

        shell_labels = [
            "Filepath of background .png: ",
            "Browse for filepath of .png containing BG image with or without shelling. ",
            "Enter (x, y) coords of assets on shell: ",
            "Enter new size of asset image in shell:"
        ]

        self.image_paste_form(shell_labels, self.shellTab, self.shellForm)

        self.shellForm.addRow(QLabel())

        self.sh1 = QHBoxLayout()
        self.shell_label = QLabel(self.shellTab)
        self.shell_label.setText("Is shell in BG, or separate? :")
        self.num_paste = ['Combined', 'Separate']
        self.num_combo = QComboBox()
        self.extra_on = self.num_combo.currentIndex == 1
        self.num_combo.setFixedWidth(100)
        self.num_combo.addItems(self.num_paste)
        self.sh1.addWidget(self.shell_label)
        self.sh1.addStretch()
        self.sh1.addWidget(self.num_combo)
        self.shellForm.addRow(self.sh1)
        self.num_combo.currentIndexChanged.connect(self.toggle_extra_shell)

        # EXTRA SHELLING
        self.sh2 = QHBoxLayout()
        self.shell_dir_label = QLabel(self.shellTab)
        self.shell_dir_label.setText("Enter shell image location:")
        self.shell_img_tbox = QLineEdit(self.shellTab)
        self.browse_shell_btn = QPushButton('Browse...', self.shellTab)
        self.browse_shell_btn.setStatusTip('Browse for shelling .png')
        self.browse_shell_btn.clicked.connect(self.browse_shell)
        self.shell_dir_label.setEnabled(False)
        self.shell_img_tbox.setEnabled(False)
        self.browse_shell_btn.setEnabled(False)
        self.sh2.addWidget(self.shell_dir_label)
        self.sh2.addStretch()
        self.sh2.addWidget(self.shell_img_tbox)
        self.sh2.addWidget(self.browse_shell_btn)
        self.shellForm.addRow(self.sh2)

        self.sh3 = QHBoxLayout()
        self.sloc_label = QLabel(self.shellTab)
        self.sloc_label.setText("Enter (x, y) coords of shell on BG image: ")
        self.s_shlocx = QLineEdit(self.shellTab) #@FIELD
        self.s_shlocx.setFixedWidth(70)
        self.s_shlocy = QLineEdit(self.shellTab) #@FIELD
        self.s_shlocy.setFixedWidth(70)
        self.sx_lab = QLabel(self.shellTab)
        self.sx_lab.setText("X: ")
        self.sy_lab = QLabel(self.shellTab)
        self.sy_lab.setText("Y: ")
        self.sloc_label.setEnabled(False)
        self.s_shlocx.setEnabled(False)
        self.s_shlocy.setEnabled(False)
        self.sh3.addWidget(self.sloc_label)
        self.sh3.addStretch()
        self.sh3.addWidget(self.sx_lab)
        self.sh3.addWidget(self.s_shlocx)
        self.sh3.addSpacing(10)
        self.sh3.addWidget(self.sy_lab)
        self.sh3.addWidget(self.s_shlocy)
        self.shellForm.addRow(self.sh3)

        self.sh4 = QHBoxLayout()
        self.ssize_label = QLabel(self.shellTab)
        self.ssize_label.setText("Enter new size of shell on BG image: ")
        self.s_shsizex = QLineEdit(self.shellTab) #@FIELD
        self.s_shsizex.setFixedWidth(70)
        self.s_shsizey = QLineEdit(self.shellTab) #@FIELD
        self.s_shsizey.setFixedWidth(70)
        self.sx_labs = QLabel(self.shellTab)
        self.sx_labs.setText("X: ")
        self.sy_labs = QLabel(self.shellTab)
        self.sy_labs.setText("Y: ")
        self.ssize_label.setEnabled(False)
        self.s_shsizex.setEnabled(False)
        self.s_shsizey.setEnabled(False)
        self.sh4.addWidget(self.ssize_label)
        self.sh4.addStretch()
        self.sh4.addWidget(self.sx_labs)
        self.sh4.addWidget(self.s_shsizex)
        self.sh4.addSpacing(10)
        self.sh4.addWidget(self.sy_labs)
        self.sh4.addWidget(self.s_shsizey)
        self.shellForm.addRow(self.sh4)

        self.sh_sects_sel = QLineEdit(self.shellTab)
        self.shellForm.addRow(QLabel("Sections to apply shelling to (separated by commas, see Help): ", self.shellTab))
        self.shellForm.addRow(self.sh_sects_sel)

        self.sh_steps_sel = QLineEdit(self.shellTab)
        self.shellForm.addRow(QLabel("Steps to apply shelling to (by demo index, select in sidebar): ", self.shellTab))
        self.shellForm.addRow(self.sh_steps_sel)

        self.bottom_buttons(['Shell', 'Begin shelling'], self.shellTab, self.shellForm)

        self.shellLayout.addLayout(self.shellForm)
        self.shellLayout.addLayout(self.imgPreviewLayout)
        self.shellTab.setLayout(self.shellLayout)

        self.tab_widget.addTab(self.shellTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.shellTab), "Shell")

    def setSecondTab(self):
        self.insTab = QWidget()

        self.insForm = QFormLayout(self.insTab)
        self.insForm.setVerticalSpacing(10)
        self.insForm.setHorizontalSpacing(5)
        self.insForm.setContentsMargins(15, 15, 15, 15)

        self.insImgPreviewLayout = QGridLayout()
        self.insImgPreview = QGraphicsScene()

        ins_labels = [
            "Filepath of insertion .png: ",
            "Browse for filepath of .png containing insertion image",
            "Enter (x, y) coords of insertion image: ",
            "Enter new size of insertion image:"
        ]

        self.image_paste_form(ins_labels, self.insTab, self.insForm)

        self.insForm.addRow(QLabel())

        self.tab_widget.addTab(self.insTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.insTab), "Insert")

        self.ins_sects_sel = QLineEdit(self.insTab)
        self.insForm.addRow(QLabel("Sections to insert image into (separated by commas, see Help): ", self.insTab))
        self.insForm.addRow(self.ins_sects_sel)

        self.ins_steps_sel = QLineEdit(self.insTab)
        self.insForm.addRow(QLabel("Steps to apply insertion to (by demo index, select in sidebar): ", self.insTab))
        self.insForm.addRow(self.ins_steps_sel)

        self.bottom_buttons(['Insert', 'Begin insertion'], self.insTab, self.insForm)

    def setSectionTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.sectionTab = QWidget()
        self.sectionForm = QFormLayout(self.sectionTab)
        self.sectionForm.setVerticalSpacing(10)
        self.sectionForm.setHorizontalSpacing(5)
        self.sectionForm.setContentsMargins(15, 15, 15, 15)

        self.sectionForm.addRow("We can tell your demo is/is not sectioned...", self.sectionTab)

        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.sectionTab)
        reset_btn.setStatusTip('Reset demo to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Section", self.sectionTab)
        save_btn.setStatusTip('Begin sectioning')
        save_btn.clicked.connect(self.begin_sectioning) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.sectionForm.addRow(bot)

        self.tab_widget.addTab(self.sectionTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.sectionTab), "Sectioning")

    def setAudioTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.audioTab = QWidget()
        self.audioForm = QFormLayout(self.xmlTab)
        self.audioForm.setVerticalSpacing(10)
        self.audioForm.setHorizontalSpacing(5)
        self.audioForm.setContentsMargins(15, 15, 15, 15)

        self.audioForm.addRow("We can tell your demo has/does not have audio...", self.audioTab)

        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.audioTab)
        reset_btn.setStatusTip('Reset demo to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Add Audio", self.audioTab)
        save_btn.setStatusTip('Begin adding audio')
        save_btn.clicked.connect(self.add_audio) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.audioForm.addRow(bot)

        self.tab_widget.addTab(self.audioTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.audioTab), "Audio")

    def setXmlTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.xmlTab = QWidget()
        self.xmlForm = QFormLayout(self.xmlTab)
        self.xmlForm.setVerticalSpacing(20)
        self.xmlForm.setHorizontalSpacing(10)
        self.xmlForm.setContentsMargins(25, 25, 25, 25)

        self.xmlEditor = QTextEdit(self.xmlTab)
        self.xmlEditor.setStatusTip("This is where the XML bulk editor will live...")
        self.xmlForm.addRow(self.xmlEditor)
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.xmlTab)
        reset_btn.setStatusTip('Reset XML to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Save", self.xmlTab)
        save_btn.setStatusTip('Save current XML changes')
        save_btn.clicked.connect(self.ins_submit) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.xmlForm.addRow(bot)

        self.tab_widget.addTab(self.xmlTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.xmlTab), "XML")


    #----------UI ELEMENTS-----------------#

    def demo_browse_layout(self, tab):
        #@TODO Take demo textbox as parameter so you dont have to paste the demo browse layout
        # code into every tab
        d = QHBoxLayout()
        demo_dir_label = QLabel(tab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_tbox = QLineEdit(tab)
        self.demo_tbox.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', tab)
        self.browse_demo_btn.setStatusTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_tbox)
        d.addWidget(self.browse_demo_btn)
        return d

    def image_paste_form(self, labels, tab, form):
        '''
        Gets *singular* insertion/bg image for shelling
        and insertion, as well as the coordinates of
        translation and scaling for either the asset (shelling)
        or insertion image, and stores them in self variables
        '''
        #@TODO Take Img textbox as parameter so you dont have to repaste this in each tab
        # for the textbox to be filled out when an image is brwosed for
        browse = QHBoxLayout()
        dir_label = QLabel(labels[0], tab)
        if tab is self.shellTab:
            self.img_tbox1 = QLineEdit(tab)
        if tab is self.insTab:
            self.img_tbox2 = QLineEdit(tab)
        self.browse_img_btn = QPushButton('Browse...', tab)
        self.browse_img_btn.setStatusTip(labels[1])
        self.browse_img_btn.clicked.connect(self.browse_img)
        browse.addWidget(dir_label)
        browse.addStretch()
        browse.addWidget(self.img_tbox1 if tab is self.shellTab else self.img_tbox2)
        browse.addWidget(self.browse_img_btn)
        form.addRow(browse)

        loc = QHBoxLayout()
        loc_label = QLabel(labels[2], tab)
        if tab is self.shellTab:
            self.shlocx = QLineEdit(tab)
            self.shlocx.setFixedWidth(70)
            self.shlocy = QLineEdit(tab)
            self.shlocy.setFixedWidth(70)
        elif tab is self.insTab:
            self.inslocx = QLineEdit(tab)
            self.inslocx.setFixedWidth(70)
            self.inslocy = QLineEdit(tab)
            self.inslocy.setFixedWidth(70)
        x_lab = QLabel("X: ", tab)
        y_lab = QLabel("Y: ", tab)
        loc.addWidget(loc_label)
        loc.addStretch()
        loc.addWidget(x_lab)
        loc.addWidget(self.shlocx if tab is self.shellTab else self.inslocx)
        loc.addSpacing(10)
        loc.addWidget(y_lab)
        loc.addWidget(self.shlocy if tab is self.shellTab else self.inslocy)
        form.addRow(loc)

        resize = QHBoxLayout()
        size_label = QLabel(labels[3], tab)
        size_label.setText(labels[3])
        if tab is self.shellTab:
            self.shsizex = QLineEdit(tab)
            self.shsizex.setFixedWidth(70)
            self.shsizey = QLineEdit(tab)
            self.shsizey.setFixedWidth(70)
        elif tab is self.insTab:
            self.inssizex = QLineEdit(tab)
            self.inssizex.setFixedWidth(70)
            self.inssizey = QLineEdit(tab)
            self.inssizey.setFixedWidth(70)
        x_labs = QLabel("X: ", tab)
        y_labs = QLabel("Y: ", tab)
        resize.addWidget(size_label)
        resize.addStretch()
        resize.addWidget(x_labs)
        resize.addWidget(self.shsizex if tab is self.shellTab else self.inssizex)
        resize.addSpacing(10)
        resize.addWidget(y_labs)
        resize.addWidget(self.shsizey if tab is self.shellTab else self.inssizey)
        form.addRow(resize)

    def toggle_extra_shell(self, toggle):
        self.extra_on = (toggle == 1)
        print("Toggling extra shell...  toggled: " + str(self.extra_on))
        self.shell_dir_label.setEnabled(self.extra_on)
        self.shell_img_tbox.setEnabled(self.extra_on)
        self.browse_shell_btn.setEnabled(self.extra_on)
        self.sloc_label.setEnabled(self.extra_on)
        self.s_shlocx.setEnabled(self.extra_on)
        self.s_shlocy.setEnabled(self.extra_on)
        self.ssize_label.setEnabled(self.extra_on)
        self.s_shsizex.setEnabled(self.extra_on)
        self.s_shsizey.setEnabled(self.extra_on)

    def bottom_buttons(self, labels, tab, form):
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        self.close_btn = QPushButton('Cancel', tab)
        self.close_btn.setStatusTip('Close the program')
        self.close_btn.clicked.connect(self.close)
        self.submit_btn = QPushButton(labels[0], tab)
        self.submit_btn.setStatusTip(labels[1])
        if tab is self.shellTab:
            self.submit_btn.clicked.connect(self.shell_submit)
        elif tab is self.insTab:
            self.submit_btn.clicked.connect(self.ins_submit)
        bot.addWidget(self.close_btn)
        bot.addStretch()
        bot.addWidget(self.submit_btn)
        form.addRow(bot)

    # ------ FUNCTIONS --------------------#

    def begin_sectioning(self):
        pass

    def add_audio(self):
        pass

    def saveConfig(self):
        pass

    def loadConfig(self):
        pass

    def browse_demo(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .demo files", "","Demo files (*.demo);;All Files (*)", options=options)
        self.demo_tbox.setText(fileName)
        self.DEMO_PATH = fileName
        if fileName != "":
            self.load_demo()

    def browse_script(self, tnum):
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        """
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .docx files", "","Word files (*.docx);;All Files (*)")
        self.script_tbox.setText(fileName)
        self.SCRIPT_PATH = fileName
        if fileName != "" and self.DEMO_PATH != "":
            self.load_demo()

    def browse_audio(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderName, _ = QFileDialog.getExistingDirectory(self,"Browse for audio folder")
        self.audio_tbox.setText(folderName)
        self.AUDIO_PATH = folderName
        if folderName != "" and self.DEMO_PATH != "":
            self.load_demo()

    
    #TODO Add "Select all" to QTreeView through top left behavior
    #TODO Maybe subclass QTreeView for demo tree to allow for easier handling
    #     of checkbox emitting signals upon selection and de-selection?
    #TODO I'm sure there's already selected checkboxes being stored in a list
    #     somewhere, find a way to access it rather than making for loops everywhere
    def load_demo(self):
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        self.demo = Demo(path=self.DEMO_PATH, script_path=self.SCRIPT_PATH, audio_dir=self.AUDIO_PATH)
        self.xmlEditor.setText(self.demo.xml())
        self.demo_title = QLabel(self.demo.title)
        self.demo_model = QStandardItemModel(self.demo_tree)
        self.demo_model.setHorizontalHeaderLabels([self.demo.title, "Has TP", "Animated"])
        for i, sect in enumerate(self.demo):
            section = QStandardItem(sect.title)
            section.setColumnCount(3)
            section.setCheckable(True)
            section.setDragEnabled(True)
            section.setSelectable(True)
            section.setEditable(True)
            section.setDropEnabled(True)
            section.setFlags(section.flags() | Qt.ItemIsTristate \
                            | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            for j, step in enumerate(sect):
                qstep = QStandardItem(step.name)
                qstep.setCheckable(True)
                qstep.setSelectable(True)
                qstep.setDragEnabled(True)
                qstep.setDropEnabled(True)
                qtp = QStandardItem(str(step.tp.text is not ""))
                qan = QStandardItem(str(step.animated))
                qt = QStandardItem()
                section.appendRow([qstep, qtp, qan])
                section.setChild(j, qstep)
            self.demo_model.appendRow(section)
        self.demo_model.itemChanged.connect(self.displayInfo)
        self.demo_tree.setModel(self.demo_model)
        #TODO set demo tree selection model?

    def displayDemoInfo(self):
        #implement for TreeView selectionChanged, add this logic to modelitemlist itemChanged
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        demo_info = QStandardItemModel(self.demo_info)
        demo_info.setColumnCount(2)
        demo_info.setHorizontalHeaderLabels(["Property", "Value"])
        demo_info.appendRow(Q(["Title", self.demo.title]))
        demo_info.appendRow(Q(["ID", self.demo.id]))
        demo_info.appendRow(Q(["Demo path", str(self.demo.path)]))
        demo_info.appendRow(Q(["Script loaded", self.demo.script.loaded]))
        demo_info.appendRow(Q(["Audio loaded", self.demo.audio.loaded]))
        demo_info.appendRow(Q(["Number steps", len(self.demo.steps)]))
        demo_info.appendRow(Q(["Number sections", len(self.demo.sections)]))
        self.demo_info.setModel(demo_info)
            
    def displayInfo(self, item):
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        if item.checkState():
            index = self.demo_model.indexFromItem(item).row()
            item_info = QStandardItemModel(self.demo_info)
            if item.hasChildren():
                self.getChecked(item,True,index)
                sect = self.demo.sections[index]
                item_info.appendRow([QStandardItem("Title: "), QStandardItem(sect.title)])
                item_info.appendRow([QStandardItem("ID: "), QStandardItem(sect.id)])
                item_info.appendRow(Q(["Demo index: ", sect.demo_idx]))
                item_info.appendRow(Q(["Section index: ", sect.idx]))
                item_info.appendRow(Q(["Assets: ", str(sect.assets)]))
                item_info.appendRow(Q(["Audio: ", str(sect.audio)]))
            else:
                self.getChecked(item,False,index)
                sect_idx = self.demo_model.indexFromItem(item.parent()).row()
                step = self.demo.sections[sect_idx].steps[index]
                item_info.appendRow(Q(["Name: ", step.name]))
                item_info.appendRow(Q(["ID: ", step.id]))
                item_info.appendRow(Q(["Demo index: ", step.demo_idx]))
                item_info.appendRow(Q(["Step index: ", step.idx]))
                item_info.appendRow(Q(["Assets: ", str(step.assets)]))
                item_info.appendRow(Q(["Audio: ", str(step.audio)]))
                item_info.appendRow(Q(["Instructions: ", str(step.ci)]))
                item_info.appendRow(Q(["Talking Point: ", str(step.tp)]))
                for i, (attr, adict) in enumerate(STEP_PROPS.items()):
                    item_info.appendRow(Q([attr.capitalize()+": ", getattr(step, attr)]))
                for box, bdict in BOX_PROPS.items():
                    for i, (prop, bdictall) in enumerate(\
                        {**bdict["props"], **DIRS}.items()):
                        try:
                            tag = bdict[box]['tag'][:-1].capitalize()
                            proptag = bdictall[prop]['tag']
                            val = getattr(step,box)[prop]
                            item_info.appendRow(Q([f"{tag} {proptag}", str(val)]))
                        except:
                            pass
            self.demo_info.setModel(item_info)
            self.demo_info.setColumnWidth(0, 250)
            self.demo_info.setColumnWidth(1, 100)
            self.demo_info.setColumnWidth(1, 100)
        else:
            self.displayDemoInfo()

    def getChecked(self,item,item_is_sect,index):
        model = item.model()
        print(f"signal emitted! getChecked called! Is sect? {str(item_is_sect)} index: {index}")
        sel = self.demo_tree.selectedIndexes()
        print(sel)
        count = 0
        sel_sects, sel_steps = self.SECTS_SELECTED, self.STEPS_SELECTED
        #TODO I'm sure this logic is already all implemented in Qt already... find it
        #at least minimize redundant logic present here
        for rowi in range(model.rowCount()):
            sect = model.item(rowi)
            title = self.demo.sections[rowi].title
            sect_checked = sect.checkState()
            if sect_checked:
                sel_sects.add(title)
                #self.demo_tree.setExpanded(rowi, True)
            else:
                sel_sects.discard(title)
            for stepi in range(sect.rowCount()):
                step = sect.child(stepi, 0)
                step_checked = step.checkState()
                if sect_checked and item_is_sect:
                    step.setCheckState(True)
                    sel_steps.add(count)
                else:
                    if step_checked and item_is_sect:
                        step.setCheckState(False)
                        sel_steps.discard(count)
                    elif step_checked and not item_is_sect:
                        sel_steps.add(count)
                    else:
                        sel_steps.discard(count)
                count += 1
        if len(sel_sects):
            self.sects_sel.setText(str(sorted(sel_sects))[1:-1])
        else:
            self.sects_sel.setText("")
        if len(sel_steps):
            self.steps_sel.setText(str(sorted(sel_steps))[1:-1])
        else:
            self.steps_sel.setText("")
        self.SECTS_SELECTED, self.STEPS_SELECTED = sel_sects, sel_steps

    def getSelectedInfo(self, item):
        raise NotImplementedError()

    def browse_img(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        img_tmp = Image.open(fileName)
        iwidth, iheight = img_tmp.size
        self.img_tbox1.setText(fileName)
        self.img_tbox2.setText(fileName)
        self.shsizex.setText(str(iwidth))
        self.shsizey.setText(str(iheight))
        self.inssizex.setText(str(iwidth))
        self.inssizey.setText(str(iheight))
        self.IMG_PATH = fileName

    # FOR SECOND SHELL, I.E. IF EXTRA_ON=TRUE
    def browse_shell(self, tbox):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        img_tmp = Image.open(fileName)
        iwidth, iheight = img_tmp.size
        self.s_shsizex.setText(str(int(iwidth)))
        self.s_shsizey.setText(str(int(iheight)))
        self.s_shlocx.setText(str(int((1920-iwidth)/2)))
        self.s_shlocy.setText(str(int((1080-iheight)/2)))
        self.shell_img_tbox.setText(fileName)
        self.SHELL_PATH = fileName

    @pyqtSlot()
    def shell_submit(self):
        demo_dir = self.demo_tbox.text()
        bg_img_dir = self.img_tbox1.text()
        bg_img_loc = None
        bg_img_size = None
        if ((len(self.shlocx.text()) > 0 and len(self.shlocy.text()) > 0) and
           (len(self.shsizex.text()) > 0 and len(self.shsizey.text()) > 0)):
            bg_img_loc = (int(self.shlocx.text()), int(self.shlocy.text()))
            bg_img_size = (int(self.shsizex.text()), int(self.shsizey.text()))
        shell_img_tbox = None; shell_img_loc = None; shell_img_size = None;
        to_shell = [s.strip() for s in self.sh_sects_sel.text().split(",")]
        if self.extra_on:
            shell_img_tbox = self.shell_img_tbox.text()
            if ((len(self.s_shlocx.text()) > 0 and len(self.s_shlocy.text()) > 0) and
               (len(self.s_shsizex.text()) > 0 and len(self.s_shsizey.text()) > 0)):
                shell_img_loc = (int(self.s_shlocx.text()), int(self.s_shlocy.text()))
                shell_img_size = (int(self.s_shsizex.text()), int(self.s_shsizey.text()))
        print(demo_dir, bg_img_dir, bg_img_loc, bg_img_size, to_shell, self.extra_on, shell_img_tbox, shell_img_loc, shell_img_size)
        """
        self.shellProg = QProgressDialog("Shelling asset files...", "Cancel", 0, 100)
        self.shellProg.setWindowTitle("Impresys Utilities - Shelling...")
        self.shellProg.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.shellProg.setGeometry(10, 10, 300, 100)
        self.shellProg.show()
        """
        self.statusbar.showMessage("Shelling...")
        self.image_paste(demo_dir, bg_img_dir, bg_img_loc, bg_img_size, typ='shell', sect=to_shell, 
                         sep=self.extra_on, s_img_path=shell_img_tbox, s_img_loc=shell_img_loc, s_img_size=shell_img_size)
        self.statusbar.showMessage("Finished shelling!")
        #self.shellProg.setWindowTitle("Impresys Utilities - Shelling completed!")
        print("Shelling finished")

    @pyqtSlot()
    def ins_submit(self):
        demo_dir = self.demo_tbox2.text()
        fg_img_dir = self.img_tbox2.text()
        fg_img_loc = None
        fg_img_size = None
        to_ins = [s.strip() for s in self.ins_sects_sel.text().split(',')]
        if ((len(self.inslocx.text()) > 0 and len(self.inslocy.text()) > 0) and
           (len(self.inssizex.text()) > 0 and len(self.inssizey.text()) > 0)):
            fg_img_loc = (int(self.inslocx.text()), int(self.inslocy.text()))
            fg_img_size = (int(self.inssizex.text()), int(self.inssizey.text()))
        print(demo_dir, fg_img_dir, fg_img_loc, fg_img_size)
        self.statusbar.showMessage("Beginning insertion...")
        self.image_paste(demo_dir, fg_img_dir, fg_img_loc, fg_img_size, typ='insert', sect=to_ins)
        self.statusbar.showMessage("Insertion complete!")
        print("Insertion finished!")
        '''
        self.insProg = QProgressDialog("Inserting into asset files...", "Cancel", 0, 100)
        self.insProg.setWindowTitle("Impresys Utilities - Inserting...")
        self.insProg.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.insProg.setGeometry(10, 10, 300, 100)
        '''
        #self.image_paste(props...)

    def open_about(self):
        about = QDialog(self)
        about.setWindowTitle("About Impresys Utils")
        about.setGeometry(20, 20, 400, 300)
        about.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        about.layout = QFormLayout()
        about.layout.setContentsMargins(40, 40, 40, 40)
        about.layout.addRow(QLabel("Author: Chris Pecunies", about))
        about.layout.addRow(QLabel("2020", about))
        about.exec_()

    def open_help(self):
        helpd = QDialog(self)
        helpd.setWindowTitle("Impresys Utils Help")
        helpd.setGeometry(20, 20, 400, 300)
        helpd.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        helpd.layout = QFormLayout()
        helpd.layout.setContentsMargins(40, 40, 40, 40)
        helpd.layout.addRow(QLabel("How to use:", helpd))
        helpd.layout.addRow(QLabel("", helpd))
        sect_help = QLabel("""
            In the 'sections' portion at the bottom of the insertion and shelling tabs,
            you may specify any number of words which the algorithm will then check each section
            of the DemoMate XML for. Steps contained in a section which merely contains one of these
            words will be considered for shelling/insertion. That means, if you put "sect" or "se" in this
            textbox, a section titled "Section 1" will be considered. If you want all steps of the demo
            to be shelled/to have an image inserted, leave as "All" or manually input "All" if default
            has been overwritten.
        """, helpd)
        sect_help.setWordWrap(True)
        helpd.layout.addRow(sect_help)
        helpd.exec_()

    def toggleMenu(self, state):
        if state: self.statusbar.show()
        else: self.statusbar.hide()

    def preview_img(self):
        self.setGeometry(10, 10, 800, 450)

    def image_paste(self, demo_path, image_path, img_loc: Tuple[int, int], img_size: Tuple[int, int], typ='shell', sect=[], 
                    sep=False, s_img_path=None, s_img_loc: Tuple[int, int]=None, s_img_size: Tuple[int, int]=None):

        bg_img_size = (1920, 1080)
        sect = [s.lower() for s in sect]

        fg_img_loc = img_loc
        fg_img_size = img_size

        if (img_size[0]+img_loc[0]>bg_img_size[0] or
            img_size[1]+img_loc[1]>bg_img_size[1]):
            raise Exception("Resized and relocated image beyond original boundaries")
        img = Image.open(image_path) #shell or insertion image

        if (typ=='shell' and sep is True and s_img_size and s_img_loc):
            shell_bound = (s_img_size[0]+s_img_loc[0], s_img_size[1]+s_img_loc[1])
            if (shell_bound[0]>bg_img_size[0] or
                shell_bound[1]>bg_img_size[1]):
                raise Exception("Resized and relocated shell beyond original boundaries of fg and/or bg")
            s_img = Image.open(s_img_path)
            s_img_resize = s_img.resize((int(s_img_size[0]), int(s_img_size[1])), Image.ANTIALIAS)
            img.paste(s_img_resize, (int(s_img_loc[0]), int(s_img_loc[1])), s_img_resize.convert('RGBA'))

        parser = ET.XMLParser(strip_cdata=False)
        demo = ET.parse(demo_path, parser)
        root = demo.getroot()
        demo_dir = demo_path.rsplit('/', 1)[0]

        ry = float(fg_img_size[1] / bg_img_size[1])
        rx = float(fg_img_size[0] / bg_img_size[0])

        def transform(coords: List[float]) -> List[float]: #-> [top, bottom, left, right]
            out = []
            if len(coords) > 2: # if BOX coordinates (T, B, L, R)
                for i in range(4):
                    if i < 2: out.append(float(coords[i] * ry + fg_img_loc[1]))
                    else: out.append(float(coords[i] * rx + fg_img_loc[0]))
            elif len(coords) <= 2: # if CLICK coordinates (X, Y)
                out.append(float(coords[0] * rx + fg_img_loc[0]))
                out.append(float(coords[1] * ry + fg_img_loc[1]))
            return out

        def get_set_mouse(mouse_path) -> Tuple[List[float], List[float]]:
            old = [float(mouse_path.find(c).text) for c in ['X', 'Y']]
            new = transform(old)
            for i, c in enumerate(['X', 'Y']):
                mouse_path.find(c).text = str(new[i])
            return new, old

        def get_set_box(box_type: str) -> Tuple[List[float], List[float]]:
            dirs = ['Top', 'Bottom', 'Left', 'Right']
            cbox = step.find("StartPicture").find(box_type)
            if len(list(step.find("StartPicture").find(box_type))) != 0:
                old = [float(cbox.find(box_type[:-1]).find(d).text) for d in dirs]
                new = transform(old)
                for i, d in enumerate(dirs):
                    cbox.find(box_type[:-1]).find(d).text = str(new[i])
                if box_type == 'VideoRects':
                    video = cbox.find('VideoRect').find('Video')
                    video.find('VideoHeight').text = str(ry*float(video.find('VideoHeight').text))
                    video.find('VideoWidth').text = str(rx*float(video.find('VideoWidth').text))
                if box_type == 'TextRects':
                    font_size = float(cbox.find('TextRect').find('FontSize').text)
                    scale = float((fg_img_size[0] * fg_img_size[1]) / (bg_img_size[0] * bg_img_size[1]))
                    cbox.find('TextRect').find('FontSize').text = str(int(scale * font_size) + 2)
                return new, old
            return (0, 0)

        for chapter in list(root.iter('Chapter')):
            section = chapter.find('XmlName').find('Name').text
            if (sect == ['']) or (section.lower() in sect):
                steps = list(chapter.iter('Step'))
                for i, step in enumerate(steps):
                    asset_dir = step.find("StartPicture").find("AssetsDirectory").text
                    asset_dir = asset_dir.replace('\\', '/')
                    assetpath = demo_dir + '/' + asset_dir
                    hspot = step.find("StartPicture").find("Hotspots").find("Hotspot")
                    cby = (float(hspot.find("Top").text), float(hspot.find("Bottom").text))
                    cbx = (float(hspot.find("Left").text), float(hspot.find("Right").text))
                    mouse = step.find("StartPicture").find("MouseCoordinates")
                    if (hspot.find("MouseEnterPicture") is not None):
                        h_mouse = hspot.find("MouseEnterPicture").find("MouseCoordinates")
                    else:
                        h_mouse = None
                    if typ == "shell":
                        get_set_mouse(mouse)
                        if not (cbx[1]-cbx[0]==bg_img_size[0] and cby[1]-cby[0]==bg_img_size[1]):
                            hcloc_new, hcloc_old = None, None
                            if h_mouse is not None:
                                hcloc_new, hcloc_old = get_set_mouse(h_mouse) # -> or this one?
                            get_set_box("Hotspots")
                            print("SHIFTED:  "+str(hcloc_old)+" to "+str(hcloc_new))

                        other_boxes = ["VideoRects", "JumpRects", "TextRects", "HighlightRects"]
                        for box in other_boxes:
                            get_set_box(box)

                    for filename in os.listdir(assetpath):
                        if filename.lower().endswith('.png'):
                            impath = assetpath+filename
                            asset_img = Image.open(impath)
                            new_img = img.copy()
                            if typ == 'shell':
                                asset_img_resize = asset_img.resize((int(fg_img_size[0]), int(fg_img_size[1])), Image.ANTIALIAS)
                                new_img.paste(asset_img_resize, (int(fg_img_loc[0]), int(fg_img_loc[1])))
                                new_img.save(impath, quality=100)
                                print("SHELLED: Section: "+section+", Step: "+str(i)+", image: "+filename)
                                print(sect)
                            else:
                                fg_img_resize = new_img.resize((int(fg_img_size[0]), int(fg_img_size[1])), Image.ANTIALIAS)
                                asset_img.paste(fg_img_resize, (int(fg_img_loc[0]), int(fg_img_loc[1])), fg_img_resize.convert('RGBA'))
                                asset_img.save(impath, quality=100)
                                print("INSERTED: Section: "+section+", Step: "+str(i)+", image: "+"t")
                                print(sect)

        demo.write(demo_path, xml_declaration=True, encoding='utf-8')

if __name__ == "__main__":

    app = ImpresysApplication()
