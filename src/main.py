from dmate.demo import Demo
from window.window import ImpresysWindow, ImpresysApplication
from typing import List, Tuple, Dict
from pathlib import Path
from etc.utils import timefunc
from collections import deque
from copy import deepcopy

if __name__ == "__main__":

    # scriptpath = r"C:\Users\Jess\Documents\My Demos\test2\RSM-SC - Eligibility [R1 - V3].docx"
    # demopath = r"C:\Users\Jess\Documents\My Demos\test2\RSM-SC - Eligibility [R1 - V3].demo"
    # audiodir = r"C:\Users\Jess\Documents\My Demos\test1sec\Audio" 
    # demo = Demo(path=demopath, script_path=scriptpath, audio_dir=audiodir, is_sectioned=True)



    app = ImpresysApplication()
    

# TODO
# Edge detection in shelling? To detect corners to automate shelling
# Automatic sectioning based on talking points
# !! Make XML parser into generator/iterator to save memory
    # Split XML parsing of demo files into generator functions which yield results sequentially, see Python cookbook
# add list of click, tp to tab in qt5, add insert section break/dupe functionality

# MAKE A CAPTURE BOT, User enters a bunch of links that are captured and captured by capture bot lol
# MAKE A CLICK BOX / LOC ADJUSTMENT BOT
# AUTOMATIC FORM FILLER / TEXT ADJUSTER

# things I can't seem to do:
# Create a new step with unique click instructions/tps. Or manipulate tps at all


#TODO
"""
* Implement capture automation, set up initial list of links, set up webbrowser module to go through them, capture img adn hvoer
* Use decorator in sectioning function to store the next few steps or whatever and have easy acccess
* SELENIUM!
* Checkbox GUI fro demo setep selection
* Start planning out Django or Flask or FastAPI web implemenation
* Start learning Rust
* Look into asyncio / concurrent processes?
"""