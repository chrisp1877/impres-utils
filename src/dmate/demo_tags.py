#TODO; add default values for each

DEBUG = True

DEMO_RES = (0, 0)

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
    "x0": {"tag": "Left", "type": float}, 
    "y0": {"tag": "Top", "type": float}, 
    "x1": {"tag": "Right", "type": float},
    "y1": {"tag": "Bottom", "type": float}, 
}

MOUSE_X, MOUSE_Y = "MouseCoordinates/X", "MouseCoordinates/Y"