from window.window import ImpresysWindow
from demo.demo import Demo


if __name__ == "__main__":
    scriptpath = r"C:\Users\Jess\Documents\My Demos\Solano Eligibility\RSM-SC - Eligibility [R1 - V3] - ready to import.docx"
    demopath = r"C:\Users\Jess\Documents\My Demos\test\RSM-SC - Eligibility [R1 - V3].demo"
    audiodir = r"C:\Users\Jess\Documents\My Demos\Solano Eligibility\Audio"
    
    demo = Demo(demopath, scriptpath, audiodir)

    """
    app = QApplication(sys.argv)
    MainWindow = ImpresysWindow()
    MainWindow.show()
    sys.exit(app.exec_())
    """

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

    