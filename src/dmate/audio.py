from pathlib import Path, PurePath
from mutagen.mp3 import MP3
from itertools import islice
from typing import List, Tuple
from etc.utils import validate_path, logger
import lxml.etree as ET

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