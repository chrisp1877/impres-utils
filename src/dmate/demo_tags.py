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

DIRS = {
    "y1": {"tag": "Top", "type": int}, 
    "y0": {"tag": "Bottom", "type": int}, 
    "x0": {"tag": "Left", "type": int}, 
    "x1": {"tag": "Right", "type": int}
}

MOUSE_X, MOUSE_Y = "MouseCoordinates/X", "MouseCoordinates/Y"