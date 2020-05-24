from pathlib import Path, PurePath
from mutagen.mp3 import MP3
from itertools import islice
from typing import List, Tuple
from etc.utils import validate_path

class AudioFolder:

    def __init__(self, path: str = ""):
        self.dir = path
        self.mp3: List[SoundBite] = []
        self.len = 0
        self.loaded = self.load(path)

    def load(self, path: str = ""):
        if not path or not validate_path(path, 'directory', '.mp3', 'Audio', 'open'):
            print("Audio failed to import.")
            return False
        self.path = Path(path)
        for filepath in self.path.glob("*.mp3"):
            soundbite = SoundBite(path=str(filepath)) #guaranteed to load
            self.mp3.append(soundbite)
            self.len += 1
        print("Audio loaded {} soundbites.".format(self.len))
        return True

    def iter_paths(self):
        return (p.resolve() for p in sorted(self.path.glob("*.mp3")))

    def iter_durations(self):
        return (MP3(audio).info.length for audio in self.iter_paths())

    def __len__(self):
        return self.len

    def __iter__(self):
        return zip(self.iter_paths(), self.iter_dur())

    def __getitem__(self, idx: int):
        return next(islice(self, idx, None))

class SoundBite:

    def __init__(self, path: str):
        self.path = Path(path)