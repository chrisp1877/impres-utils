from dmate.demo import Demo
from window.window import ImpresysWindow
import pickle

#TODO: investigate why there are extra steps? at the end of the demo when iterating through it
    # "Thakns for watching..." appears at lke sect 47, but demo iterates till 58

if __name__ == "__main__":
    scriptpath = r"C:\Users\Jess\Documents\My Demos\test\Simplify your BYOL Experience with Dedicated Host Management Capabilities in AWS License Manager.docx"
    demopath = r"C:\Users\Jess\Documents\My Demos\test\Simplify your BYOL Experience with Dedicated Host Management Capabilities in AWS License Manager.demo"
    audiodir = r"C:\Users\Jess\Documents\My Demos\Solano Eligibility\Audio"
    
    demo = Demo(demopath, scriptpath, audiodir)
    #demo_pickle = pickle.dumps(demo)
    #steps = [sect for sect in demo.sections]
    #sects = [step for sect in demo.sections for step in sect.steps]
    print(len(demo), len(demo.sections), [len(sect) for sect in demo.sections])
    #%%
            
    words = {}
    past = False
    for sect in demo:
        for step in sect:
            if step.tp.text:
                word_count = step.tp.word_count()
                for word in word_count:
                    if word in words:
                        words[word] += 1
                    else:
                        words[word] = 1
            # print(step.tp.word_count())
            # print(step.tp.text)
            # if "Thanks for watching".lower() in step.tp.text.lower():
            #     past = True
            # if past:
            #     print(step.prop)

    # %% 
    print(len(demo.sections))
    print(words)
    freq_word = ()
    # %%

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
