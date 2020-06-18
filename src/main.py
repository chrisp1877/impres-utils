# TODO: Invesetigate why AWS 62, e4 doesn't work being imported

from window.window import ImpresysApplication

DEBUG = False
OPTIONS = {
    "START_GUI": True,
}
DEBUG_SETTINGS = {
    "DEMO_PATH": r"C:\\Users\\Jess\\..TEST\\RSM - Disease Outbreak and Management System - phone installer [R1 V5H].demo",
    "SCRIPT_PATH": "",
    "AUDIO_PATH": "",
    "TO_SECT": ["Section 6", "Section 7", "Section 8", "Section 9"],
    "BG_PATH": r"C:\\Users\\\Jess\Pictures\hover.png",
    "SHELL_PATH": r"C:\Users\Jess\Pictures\hover.png",
    "ASSET_NEW_SIZE": (300, 800),
    "ASSET_NEW_COORD": (600, 100),
    "SHELL_NEW_SIZE": (1500, 750),
    "SHELL_NEW_COORD": (200, 50),
}

def main():
    if DEBUG:
        OPTIONS += DEBUG_SETTINGS
    app = ImpresysApplication(debug=DEBUG, options=OPTIONS)

if __name__ == "__main__":
    main()

