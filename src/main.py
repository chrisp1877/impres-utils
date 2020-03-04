import sys, os
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox, QFrame, QStatusBar,
    QTabWidget, QSpacerItem, QSizePolicy, QRadioButton, QProgressBar,
    QButtonGroup, QDoubleSpinBox, QGraphicsScene
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QFileSelector
import lxml.etree as ET
from PIL import Image
from typing import List, Tuple
import sys, os

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

class ImpresysWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Impresys Utilities'
        self.left = 10
        self.top = 10
        self.width = 450
        self.height = 600
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)
        
        self.addStatusBar()
        self.addMenuBar()
        self.setTabs()
        self.setFirstTab()
        self.setSecondTab()
        self.setXmlTab()
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)

        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def addMenuBar(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolsMenu = mainMenu.addMenu('Tools')
        aboutMenu = mainMenu.addMenu('About')
        helpMenu = mainMenu.addMenu('Help')

        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        viewMenu.addAction(viewStatAct)

        aboutButton = QAction(QIcon("about1.png"), "About", self)
        aboutButton.setShortcut('Ctrl+A')
        aboutButton.setStatusTip('About application')
        aboutButton.triggered.connect(self.open_about)
        aboutMenu.addAction(aboutButton)

        helpButton = QAction(QIcon("help.png"), "Help", self)
        helpButton.setShortcut('Ctrl+H')
        helpButton.setStatusTip('Help for shelling and inserting')
        helpButton.triggered.connect(self.open_help)
        helpMenu.addAction(helpButton)

    def setTabs(self):
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.shellTab = QWidget()
        self.shellTab.setObjectName("shellTab")
        self.insTab = QWidget()
        self.insTab.setObjectName("insTab")
        self.xmlTab = QWidget()

    def addStatusBar(self):
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("Shell or insert status")
        self.statusbar.showMessage("Ready for shelling/insertion")
        self.setStatusBar(self.statusbar)

    def setFirstTab(self):
        self.shellLayout = QVBoxLayout()

        self.shellForm = QFormLayout(self.shellTab)
        self.shellForm.setVerticalSpacing(20)
        self.shellForm.setHorizontalSpacing(10)
        self.shellForm.setContentsMargins(25, 25, 25, 25)

        self.imgPreviewLayout = QGridLayout()
        self.imgPreview = QGraphicsScene()

        shell_labels = [
            "Filepath of background .png: ",
            "Browse for filepath of .png containing BG image with or without shelling. ",
            "Enter (x, y) coords of assets on shell: ",
            "Enter new size of asset image in shell:"
        ]

        self.shellForm.addRow(self.demo_browse_layout(self.shellTab))
        self.image_paste_form(shell_labels, self.shellTab, self.shellForm)
        
        self.shellForm.addRow(QLabel())
        
        self.sh1 = QHBoxLayout()
        self.shell_label = QLabel(self.shellTab)
        self.shell_label.setText("Is shell in BG, or separate? :")
        self.num_paste = ['Combined', 'Separate']
        self.num_combo = QComboBox()
        self.num_combo.setFixedWidth(100)
        self.num_combo.addItems(self.num_paste)
        self.sh1.addWidget(self.shell_label)
        self.sh1.addStretch()
        self.sh1.addWidget(self.num_combo)
        self.shellForm.addRow(self.sh1)
        self.num_combo.currentIndexChanged.connect(self.toggle_extra_shell)

        self.sh2 = QHBoxLayout()
        self.shell_dir_label = QLabel(self.shellTab)
        self.shell_dir_label.setText("Enter shell image location:")
        self.shell_img_tbox = QLineEdit(self.shellTab)
        self.browse_shell_btn = QPushButton('Browse...', self.shellTab)
        self.browse_shell_btn.setToolTip('Browse for shelling .png')
        self.browse_shell_btn.clicked.connect(self.browse_shell)
        self.shell_dir_label.setEnabled(False)
        self.shell_img_tbox.setEnabled(False)
        self.browse_shell_btn.setEnabled(False)
        self.sh2.addWidget(self.shell_dir_label)
        self.sh2.addStretch()
        self.sh2.addWidget(self.shell_img_tbox)
        self.sh2.addWidget(self.browse_shell_btn)
        self.shellForm.addRow(self.sh2)

        self.sh3 = QHBoxLayout()
        self.sloc_label = QLabel(self.shellTab)
        self.sloc_label.setText("Enter (x, y) coords of shell on BG image: ")
        self.slocx = QDoubleSpinBox(self.shellTab)
        self.slocx.setFixedWidth(70)
        self.slocy = QDoubleSpinBox(self.shellTab)
        self.slocy.setFixedWidth(70)
        self.sx_lab = QLabel(self.shellTab)
        self.sx_lab.setText("X: ")
        self.sy_lab = QLabel(self.shellTab)
        self.sy_lab.setText("Y: ")
        self.sloc_label.setEnabled(False)
        self.slocx.setEnabled(False)
        self.slocy.setEnabled(False)
        self.sh3.addWidget(self.sloc_label)
        self.sh3.addStretch()
        self.sh3.addWidget(self.sx_lab)
        self.sh3.addWidget(self.slocx)
        self.sh3.addSpacing(10)
        self.sh3.addWidget(self.sy_lab)
        self.sh3.addWidget(self.slocy)
        self.shellForm.addRow(self.sh3)

        self.sh4 = QHBoxLayout()
        self.ssize_label = QLabel(self.shellTab)
        self.ssize_label.setText("Enter new size of shell on BG image: ")
        self.ssizex = QDoubleSpinBox(self.shellTab)
        self.ssizex.setFixedWidth(70)
        self.ssizey = QDoubleSpinBox(self.shellTab)
        self.ssizey.setFixedWidth(70)
        self.sx_labs = QLabel(self.shellTab)
        self.sx_labs.setText("X: ")
        self.sy_labs = QLabel(self.shellTab)
        self.sy_labs.setText("Y: ")
        self.ssize_label.setEnabled(False)
        self.ssizex.setEnabled(False)
        self.ssizey.setEnabled(False)
        self.sh4.addWidget(self.ssize_label)
        self.sh4.addStretch()
        self.sh4.addWidget(self.sx_labs)
        self.sh4.addWidget(self.ssizex)
        self.sh4.addSpacing(10)
        self.sh4.addWidget(self.sy_labs)
        self.sh4.addWidget(self.ssizey)
        self.shellForm.addRow(self.sh4)

        self.shellSects = QLineEdit(self.shellTab)
        self.shellForm.addRow(QLabel("Sections to apply shelling to (separated by commas, see Help): ", self.shellTab))
        self.shellForm.addRow(self.shellSects)
        self.bottom_buttons(['Shell', 'Begin shelling'], self.shellTab, self.shellForm)
        
        self.shellLayout.addLayout(self.shellForm)
        self.shellLayout.addLayout(self.imgPreviewLayout)
        self.shellTab.setLayout(self.shellLayout)

        self.tabWidget.addTab(self.shellTab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.shellTab), "Shell")

    def setSecondTab(self):
        self.insTab = QWidget()

        self.insForm = QFormLayout(self.insTab)
        self.insForm.setVerticalSpacing(20)
        self.insForm.setHorizontalSpacing(10)
        self.insForm.setContentsMargins(25, 25, 25, 25)

        self.insImgPreviewLayout = QGridLayout()
        self.insImgPreview = QGraphicsScene()

        ins_labels = [
            "Filepath of insertion .png: ",
            "Browse for filepath of .png containing insertion image",
            "Enter (x, y) coords of insertion image: ",
            "Enter new size of insertion image:"
        ]
        
        self.insForm.addRow(self.demo_browse_layout(self.insTab))
        self.image_paste_form(ins_labels, self.insTab, self.insForm)
        
        self.shellForm.addRow(QLabel())

        self.tabWidget.addTab(self.insTab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.insTab), "Insert")
        self.insSects = QLineEdit(self.insTab)
        self.insForm.addRow(QLabel("Sections to apply shelling to (separated by commas, see Help): ", self.insTab))
        self.insForm.addRow(self.insSects)
        self.bottom_buttons(['Insert', 'Begin insertion'], self.insTab, self.insForm)

    def setXmlTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.xmlTab = QWidget()
        self.xmlForm = QFormLayout(self.xmlTab)
        self.xmlForm.setVerticalSpacing(20)
        self.xmlForm.setHorizontalSpacing(10)
        self.xmlForm.setContentsMargins(25, 25, 25, 25)
        self.xmlForm.addRow(self.demo_browse_layout(self.xmlTab))
        self.xmlEditor = QTextEdit(self.xmlTab)
        self.xmlForm.addRow(self.xmlEditor)
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.xmlTab)
        reset_btn.setToolTip('Reset XML to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Save", self.xmlTab)
        save_btn.setToolTip('Save current XML changes')
        save_btn.clicked.connect(self.on_click) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.xmlForm.addRow(bot)

        self.tabWidget.addTab(self.xmlTab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.xmlTab), "XML")
        

    #----------UI ELEMENTS-----------------#

    def demo_browse_layout(self, tab):
        d = QHBoxLayout()
        demo_dir_label = QLabel(tab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_dir_tbox = QLineEdit(tab)
        self.demo_dir_tbox.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', tab)
        self.browse_demo_btn.setToolTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_dir_tbox)
        d.addWidget(self.browse_demo_btn)
        return d

    def image_paste_form(self, labels, tab, form):
        '''
        Gets *singular* insertion/bg image for shelling
        and insertion, as well as the coordinates of
        translation and scaling for either the asset (shelling)
        or insertion image, and stores them in self variables
        '''
        browse = QHBoxLayout()
        dir_label = QLabel(labels[0], tab)
        self.bg_img_tbox = QLineEdit(tab)
        self.browse_bg_btn = QPushButton('Browse...', tab)
        self.browse_bg_btn.setToolTip(labels[1])
        self.browse_bg_btn.clicked.connect(self.browse_img)
        browse.addWidget(dir_label)
        browse.addStretch()
        browse.addWidget(self.bg_img_tbox)
        browse.addWidget(self.browse_bg_btn)
        form.addRow(browse)

        loc = QHBoxLayout()
        loc_label = QLabel(labels[2], tab)
        self.locx = QDoubleSpinBox(tab)
        self.locx.setFixedWidth(70)
        self.locy = QDoubleSpinBox(tab)
        self.locy.setFixedWidth(70)
        x_lab = QLabel("X: ", tab)
        y_lab = QLabel("Y: ", tab)
        loc.addWidget(loc_label)
        loc.addStretch()
        loc.addWidget(x_lab)
        loc.addWidget(self.locx)
        loc.addSpacing(10)
        loc.addWidget(y_lab)
        loc.addWidget(self.locy)
        form.addRow(loc)

        resize = QHBoxLayout()
        size_label = QLabel(labels[3], tab)
        size_label.setText(labels[3])
        self.sizex = QDoubleSpinBox(tab)
        self.sizex.setFixedWidth(70)
        self.sizey = QDoubleSpinBox(tab)
        self.sizey.setFixedWidth(70)
        x_labs = QLabel("X: ", tab)
        y_labs = QLabel("Y: ", tab)
        resize.addWidget(size_label)
        resize.addStretch()
        resize.addWidget(x_labs)
        resize.addWidget(self.sizex)
        resize.addSpacing(10)
        resize.addWidget(y_labs)
        resize.addWidget(self.sizey)
        form.addRow(resize)

    def toggle_extra_shell(self, toggle):
        extra_on = (toggle == 1)
        self.shell_dir_label.setEnabled(extra_on)
        self.shell_img_tbox.setEnabled(extra_on)
        self.browse_shell_btn.setEnabled(extra_on)
        self.sloc_label.setEnabled(extra_on)
        self.slocx.setEnabled(extra_on)
        self.slocy.setEnabled(extra_on)
        self.ssize_label.setEnabled(extra_on)
        self.ssizex.setEnabled(extra_on)
        self.ssizey.setEnabled(extra_on)

    def bottom_buttons(self, labels, tab, form):
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        self.close_btn = QPushButton('Cancel', tab)
        self.close_btn.setToolTip('Close the program')
        self.close_btn.clicked.connect(self.close)
        self.submit_btn = QPushButton(labels[0], tab)
        self.submit_btn.setToolTip(labels[1])
        self.submit_btn.clicked.connect(self.on_click)
        bot.addWidget(self.close_btn)
        bot.addStretch()
        bot.addWidget(self.submit_btn)
        form.addRow(bot)

    # ------ FUNCTIONS --------------------#
    @pyqtSlot( )
    def addRandomTextSlot( self ):
        self.textEdit.insertPlainText( "Hello World!" )

    def browse_demo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .demo files", "","Demo files (*.demo);;All Files (*)", options=options)
        if fileName:
            print(fileName)
        self.bg_img_tbox.text = fileName

    def browse_img(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        self.demo_dir_tbox.text = fileName

    def browse_shell(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        self.demo_dir_tbox.text = fileName

    @pyqtSlot()
    def on_click(self):
        demo_dir = self.demo_dir_tbox.text()
        bg_img_dir = self.bg_img_tbox.text()
        shell = self.shell
        one_image = self.one_image
        print(demo_dir, bg_img_dir, shell, one_image)
        QMessageBox.question(
            "Hello",
            QMessageBox.Ok, 
            QMessageBox.Ok)

    def open_about(self):
        about = QDialog(self)
        about.setWindowTitle("About Impresys Utils")
        about.setGeometry(20, 20, 400, 300)
        about.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        about.layout = QFormLayout()
        about.layout.setContentsMargins(40, 40, 40, 40)
        about.layout.addRow(QLabel("Author: Chris Pecunies", about))
        about.layout.addRow(QLabel("2020", about))
        about.exec_()

    def open_help(self):
        helpd = QDialog(self)
        helpd.setWindowTitle("Impresys Utils Help")
        helpd.setGeometry(20, 20, 400, 300)
        helpd.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        helpd.layout = QFormLayout()
        helpd.layout.setContentsMargins(40, 40, 40, 40)
        helpd.layout.addRow(QLabel("How to use:", helpd))
        helpd.layout.addRow(QLabel("", helpd))
        sect_help = QLabel("""
            In the 'sections' portion at the bottom of the insertion and shelling tabs,
            you may specify any number of words which the algorithm will then check each section
            of the DemoMate XML for. Steps contained in a section which merely contains one of these
            words will be considered for shelling/insertion. That means, if you put "sect" or "se" in this
            textbox, a section titled "Section 1" will be considered. If you want all steps of the demo
            to be shelled/to have an image inserted, leave as "All" or manually input "All" if default
            has been overwritten.
        """, helpd)
        sect_help.setWordWrap(True)
        helpd.layout.addRow(sect_help)
        helpd.exec_()

    def toggleMenu(self, state):
        if state: self.statusbar.show()
        else: self.statusbar.hide()

    def image_paste(self, demo_path, image_path, img_loc, img_size, typ='shell', sect='All'):
        bg_img_size = (1920, 1080)
        fg_img_loc = img_loc
        fg_img_size = img_size
        if (fg_img_size[0]+fg_img_loc[0]>bg_img_size[0] or
            fg_img_size[1]+fg_img_loc[1]>bg_img_size[1]):
            raise Exception("Resized and relocated image beyond original boundaries")                                                                                                                   
        img = Image.open(image_path)
        parser = ET.XMLParser(strip_cdata=False)
        demo = ET.parse(demo_path, parser)
        root = demo.getroot()
        demo_dir = demo_path.rsplit('\\', 1)[0]

        ry = float(fg_img_size[1] / bg_img_size[1])
        rx = float(fg_img_size[0] / bg_img_size[0])

        def transform(coords: List[float]) -> List[str]: #-> [top, bottom, left, right]
            out = []
            if len(coords) > 2: # if BOX coordinates (T, B, L, R)
                for i in range(4):
                    if i < 2: out.append(str(coords[i] * ry + fg_img_loc[1]))
                    else: out.append(str(coords[i] * rx + fg_img_loc[0]))
            elif len(coords) <= 2: # if CLICK coordinates (X, Y)
                out.append(str(coords[0] * rx + fg_img_loc[0]))
                out.append(str(coords[1] * ry + fg_img_loc[1]))
            return out

        def get_set_mouse(mouse_path) -> Tuple[List[float], List[float]]:
            old = [float(mouse_path.find(c).text) for c in ['X', 'Y']]
            new = transform(old)
            for i, c in enumerate(['X', 'Y']):
                mouse_path.find(c).text = str(new[i])
            return new, old
                
        def get_set_box(box_type: str) -> Tuple[List[float], List[float]]:
            dirs = ['Top', 'Bottom', 'Left', 'Right']
            cbox = step.find("StartPicture").find(box_type)
            if len(list(step.find("StartPicture").find(box_type))) != 0:
                old = [float(cbox.find(box_type[:-1]).find(d).text) for d in dirs]
                new = transform(old)
                for i, d in enumerate(dirs):
                    cbox.find(box_type[:-1]).find(d).text = str(new[i])
                if box_type == 'VideoRects':
                    video = cbox.find('VideoRect').find('Video')
                    video.find('VideoHeight').text = str(ry*float(video.find('VideoHeight').text))
                    video.find('VideoWidth').text = str(rx*float(video.find('VideoWidth').text))
                if box_type == 'TextRects':
                    font_size = float(cbox.find('TextRect').find('FontSize').text)
                    scale = float((fg_img_size[0] * fg_img_size[1]) / (bg_img_size[0] * bg_img_size[1]))
                    cbox.find('TextRect').find('FontSize').text = str(int(scale * font_size) + 2)
                return new, old
        
        for chapter in list(root.iter('Chapter')):
            section = chapter.find('XmlName').find('Name').text
            if (sect == 'All') or (sect in section):
                steps = list(chapter.iter('Step'))
                for i, step in enumerate(steps):
                    asset_dir =  step.find("StartPicture").find("AssetsDirectory").text
                    assetpath = demo_dir + '\\' + asset_dir
                    hspot = step.find("StartPicture").find("Hotspots").find("Hotspot")
                    cby = (float(hspot.find("Top").text), float(hspot.find("Bottom").text))
                    cbx = (float(hspot.find("Left").text), float(hspot.find("Right").text))
                    mouse = step.find("StartPicture").find("MouseCoordinates")
                    if (hspot.find("MouseEnterPicture") is not None):
                        h_mouse = hspot.find("MouseEnterPicture").find("MouseCoordinates")
                    else:
                        h_mouse = None
                    if typ == "shell":
                        get_set_mouse(mouse)
                        if not (cbx[1]-cbx[0]==bg_img_size[0] and cby[1]-cby[0]==bg_img_size[1]):
                            hcloc_new, hcloc_old = None, None
                            if h_mouse is not None:
                                hcloc_new, hcloc_old = get_set_mouse(h_mouse) # -> or this one?
                            get_set_box("Hotspots")
                            print("SHIFTED:  "+str(hcloc_old)+" to "+str(hcloc_new))
                        
                        other_boxes = ["VideoRects", "JumpRects", "TextRects", "HighlightRects"]
                        for box in other_boxes:
                            get_set_box(box)
                            
                    for filename in os.listdir(assetpath):
                        if filename.endswith('.Png'):
                            impath = assetpath+filename
                            asset_img = Image.open(impath)
                            new_img = img.copy()
                            if typ == 'shell':
                                asset_img_resize = asset_img.resize((fg_img_size), Image.ANTIALIAS)
                                new_img.paste(asset_img_resize, fg_img_loc)
                                new_img.save(impath, quality=100)
                                print("SHELLED: Section: "+section+", Step: "+str(i)+", image: "+filename)
                            else:
                                fg_img_resize = new_img.resize((fg_img_size), Image.ANTIALIAS)
                                asset_img.paste(fg_img_resize, fg_img_loc)
                                asset_img.save(impath, quality=100)
                                print("INSERTED: Section: "+section+", Step: "+str(i)+", image: "+"t")
    
        demo.write(demo_path, xml_declaration=True, encoding='utf-8')

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = ImpresysWindow()
    MainWindow.show()
    sys.exit(app.exec_())