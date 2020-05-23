from pathlib import Path, PurePath
from mutagen.mp3 import MP3

class Audio:

    def __init__(self, audio_dir: str):
        self.audio_dir = Path(audio_dir)

    def iter_paths(self):
        return (p.resolve() for p in sorted(self.audio_dir.glob("*.mp3")))

    def iter_durations(self):
        return (MP3(audio).info.length for audio in self.iter_paths())

    def __iter__(self):
        return zip(self.iter_paths(), self.iter_dur())

    def __getitem__(self, idx: int):
        return next(islice(self, idx, None))