# TODO: Invesetigate why AWS 62, e4 doesn't work being imported
#TODO Handle crash when image is selected before demo (tries to read .res of demo which doesnt exist yet)

from window.window import ImpresysApplication

def main():
    DEBUG = False
    OPTIONS = {
        "START_GUI": False,
    }
    DEBUG_SETTINGS = {
        "DEMO_PATH": r"C:\\Users\\Jess\\..TEST\\RSM 2 -Disease Outbreak and Management System - phone installer [R1 V5I].demo",
        "SCRIPT_PATH": "",
        "AUDIO_PATH": "",
        "TO_SECT": ["Section 1", "Section 2", "Section 3", "Section 4"],
        "BG_PATH": r"C:\\Users\\\Jess\Pictures\hover.png",
        "SHELL_PATH": None,
        "ASSET_NEW_SIZE": (300, 800),
        "SHELL_NEW_SIZE": (1500, 750),
        "SHELL_NEW_COORD": (200, 50),
        "ASSET_NEW_COORD": (600, 100),
        "SHELL_NEW_SIZE": None,
        "SHELL_NEW_COORD": None,
    }
    app = ImpresysApplication(debug=DEBUG, options = OPTIONS, debug_settings = DEBUG_SETTINGS)

if __name__ == "__main__":
    main()

# TODO Change shell separate mode so that it goes through a round of shelling just with bg then inserts the shelling image over the bg + asset combined