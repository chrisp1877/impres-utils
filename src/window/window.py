import sys, os
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox, QFrame, QStatusBar,
    QTabWidget, QSpacerItem, QSizePolicy, QRadioButton, QProgressBar,
    QButtonGroup, QDoubleSpinBox, QGraphicsScene, QProgressDialog, QListView,
    QListWidget, QListWidgetItem, QTableView, QHeaderView, QTreeView,
    QAbstractItemView
    
)
from PyQt5.QtGui import (QIcon, QStandardItemModel, QStandardItem, )
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QFileSelector, QItemSelectionModel
import lxml.etree as ET
from PIL import Image
from typing import List, Tuple
from pathlib import Path
from dmate.demo import Demo
from dmate.script import Script
from dmate.audio import Audio
import dmate.demo_tags as dt

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

class ImpresysApplication(QApplication):

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ImpresysWindow()
        self.window.show()
        self.app.exec_()

class ImpresysWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.DEMO_PATH = ""
        self.SCRIPT_PATH = ""
        self.AUDIO_PATH = ""
        self.IMG_PATH = None
        self.SHELL_PATH = None
        self.SECTS = list()
        self.FG_LOC = [None, None]
        self.FG_SIZE = [None, None]
        self.SHELL_BG_SEPARATE = bool()
        self.SHELL_LOC = [None, None]
        self.SHELL_SIZE = [None, None]
        self.SECTS_SELECTED = set()
        self.STEPS_SELECTED = set()

        self.title = 'Impresys Utilities'
        self.left = 10
        self.top = 10
        self.width = 950
        self.height = 550
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        
        self.demo = None
        self.script = None
        self.audio = None

        self.centralwidget = QWidget(self)
        self.col_layout = QHBoxLayout(self.centralwidget)
        self.tab_widget = QTabWidget(self.centralwidget)
        self.entry_layout = QVBoxLayout()
        self.demo_pane = QVBoxLayout()
        self.demo_title = "No demo loaded"
        self.demo_tree = QTreeView()
        self.demo_info = QTreeView()
        self.demo_info.setFixedHeight(225)
        #self.demo_title = QLabel("No demo loaded")
        #self.demo_pane.addWidget(self.demo_title)
        self.demo_pane.addWidget(self.demo_tree)
        self.demo_pane.addWidget(self.demo_info)
        self.col_layout.addLayout(self.entry_layout)
        self.col_layout.addLayout(self.demo_pane)

        self.demo_layout = QHBoxLayout()
        self.demo_label = QLabel()
        self.demo_label.setText("Enter .demo file location:")
        self.demo_tbox = QLineEdit()
        self.demo_tbox.resize(150, 30)
        self.demo_btn = QPushButton('Browse...')
        self.demo_btn.setStatusTip('Browse for .demo file')
        self.demo_btn.clicked.connect(self.browse_demo)
        self.demo_layout.addWidget(self.demo_label)
        self.demo_layout.addStretch()
        self.demo_layout.addWidget(self.demo_tbox)
        self.demo_layout.addWidget(self.demo_btn)

        self.script_layout = QHBoxLayout()
        self.script_label = QLabel()
        self.script_label.setText("Enter script .docx location:")
        self.script_tbox = QLineEdit()
        self.script_tbox.resize(150, 30)
        self.script_btn = QPushButton('Browse...')
        self.script_btn.setStatusTip('Browse for .docx file')
        self.script_btn.clicked.connect(self.browse_script)
        self.script_layout.addWidget(self.script_label)
        self.script_layout.addStretch()
        self.script_layout.addWidget(self.script_tbox)
        self.script_layout.addWidget(self.script_btn)

        self.audio_layout = QHBoxLayout()
        self.audio_label = QLabel()
        self.audio_label.setText("Enter audio folder location:")
        self.audio_tbox = QLineEdit()
        self.audio_tbox.resize(150, 30)
        self.audio_btn = QPushButton('Browse...')
        self.audio_btn.setStatusTip('Browse for audio folder')
        self.audio_btn.clicked.connect(self.browse_audio)
        self.audio_layout.addWidget(self.audio_label)
        self.audio_layout.addStretch()
        self.audio_layout.addWidget(self.audio_tbox)
        self.audio_layout.addWidget(self.audio_btn)

        self.entry_layout.addLayout(self.demo_layout)
        self.entry_layout.addLayout(self.script_layout)
        self.entry_layout.addLayout(self.audio_layout)
        self.entry_layout.addWidget(self.tab_widget)

        self.addStatusBar()
        self.addMenuBar()
        self.configPreview()
        self.setTabs()
        self.setFirstTab()
        self.setSecondTab()
        self.setSectionTab()
        self.setAudioTab()
        self.setXmlTab()
        self.progBar = QProgressBar()
        self.entry_layout.addWidget(self.tab_widget)
        #self.entry_layout.addWidget(self.progBar, 1, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def addMenuBar(self):

        def additem(menu, icon, name, shortcut, tip, func=None):
            item = QAction(QIcon(icon), name, self)
            item.setShortcut(shortcut)
            item.setStatusTip(tip)
            if func is not None:
                item.triggered.connect(func)
            menu.addAction(item)
        
        mainMenu = self.menuBar()
        filem = mainMenu.addMenu('File')
        editm = mainMenu.addMenu('Edit')
        viewm = mainMenu.addMenu('View')
        toolsm = mainMenu.addMenu('Tools')
        aboutm = mainMenu.addMenu('About')
        helpm = mainMenu.addMenu('Help')

        additem(filem, 'open1.png', 'Import Demo', 'Ctrl+Shift+D', 'Import demo', self.browse_demo)
        additem(filem, 'open2.png', 'Import Script', 'Ctrl+Shift+S', 'Import script', self.browse_script)
        additem(filem, 'open3.png', 'Import Audio', 'Ctrl+Shift+A', 'Import audio', self.browse_audio)
        additem(filem, 'save.png', 'Save config', 'Ctrl+S', 'Save currently inputted variables to a text file', self.saveConfig)
        additem(filem, 'load.png', 'Load config', 'Ctrl+O', 'Load variables previously saved to a text file', self.loadConfig)
        additem(filem, 'exit24.png', 'Exit', 'Ctrl+Q', 'Exit application', self.close)
        """
        impDemo = QAction(QIcon('open.png'), 'Import Demo', self)
        impDemo.setShortcut('Ctrl+D')
        impDemo.setStatusTip('Import demo')
        impDemo.triggered.connect(self.browse_demo)
        impDemo = QAction(QIcon('open.png'), 'Import Demo', self)
        impDemo.setShortcut('Ctrl+D')
        impDemo.setStatusTip('Import demo')
        impDemo.triggered.connect(self.browse_demo)
        saveConfig = QAction(QIcon('save.png'), 'Save inputs', self)
        saveConfig.setShortcut('Ctrl+S')
        saveConfig.setStatusTip('Save currently inputted variables to a text file')
        #saveButton.triggered.connect(self.saveConfig)
        fileMenu.addAction(saveConfig)
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        film.addAction(exitButton)
        """
        preferences = QAction(QIcon('prefs.png'), 'Preferences', self)
        preferences.setShortcut('Ctrl+P')
        preferences.setStatusTip('Change preferences for different utilities')
        #preferences.triggered.connect(self.preferences)
        editm.addAction(preferences)

        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setShortcut('Ctrl+Shift+V')
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)
        viewm.addAction(viewStatAct)

        viewPrev = QAction('View preview', self, checkable=True)
        viewPrev.setShortcut('Ctrl+Shift+P')
        viewPrev.setStatusTip('View preview of shelling / insertion points')
        viewPrev.setChecked(True)
        viewPrev.triggered.connect(self.preview_img)
        viewm.addAction(viewPrev)

        aboutButton = QAction(QIcon("about1.png"), "About", self)
        aboutButton.setShortcut('Ctrl+A')
        aboutButton.setStatusTip('About application')
        aboutButton.triggered.connect(self.open_about)
        aboutm.addAction(aboutButton)

        helpButton = QAction(QIcon("help.png"), "Help", self)
        helpButton.setShortcut('Ctrl+H')
        helpButton.setStatusTip('Help for shelling and inserting')
        helpButton.triggered.connect(self.open_help)
        helpm.addAction(helpButton)

    def configPreview(self):
        self.shellLayout = QVBoxLayout()

    def setTabs(self):
        
        self.tab_widget.setObjectName("tabWidget")
        self.shellTab = QWidget()
        self.shellTab.setObjectName("shellTab")
        self.shellTab.setStatusTip("Performing shelling on demo assets")
        self.insTab = QWidget()
        self.insTab.setObjectName("insTab")
        self.insTab.setStatusTip("Insert an image into demo assets")
        self.xmlTab = QWidget()
        self.xmlTab.setObjectName("xmlTab")
        self.xmlTab.setStatusTip("Perform bulk XML edits on demo")

    def addStatusBar(self):
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("Shell or insert status")
        self.statusbar.showMessage("Ready for shelling/insertion")
        self.setStatusBar(self.statusbar)

    def setFirstTab(self):
        self.shellForm = QFormLayout(self.shellTab)
        self.shellForm.setVerticalSpacing(10)
        self.shellForm.setHorizontalSpacing(5)
        self.shellForm.setContentsMargins(15, 15, 15, 15)

        self.imgPreviewLayout = QGridLayout()
        self.imgPreview = QGraphicsScene()

        shell_labels = [
            "Filepath of background .png: ",
            "Browse for filepath of .png containing BG image with or without shelling. ",
            "Enter (x, y) coords of assets on shell: ",
            "Enter new size of asset image in shell:"
        ]

        self.image_paste_form(shell_labels, self.shellTab, self.shellForm)

        self.shellForm.addRow(QLabel())

        self.sh1 = QHBoxLayout()
        self.shell_label = QLabel(self.shellTab)
        self.shell_label.setText("Is shell in BG, or separate? :")
        self.num_paste = ['Combined', 'Separate']
        self.num_combo = QComboBox()
        self.extra_on = self.num_combo.currentIndex == 1
        self.num_combo.setFixedWidth(100)
        self.num_combo.addItems(self.num_paste)
        self.sh1.addWidget(self.shell_label)
        self.sh1.addStretch()
        self.sh1.addWidget(self.num_combo)
        self.shellForm.addRow(self.sh1)
        self.num_combo.currentIndexChanged.connect(self.toggle_extra_shell)

        # EXTRA SHELLING
        self.sh2 = QHBoxLayout()
        self.shell_dir_label = QLabel(self.shellTab)
        self.shell_dir_label.setText("Enter shell image location:")
        self.shell_img_tbox = QLineEdit(self.shellTab)
        self.browse_shell_btn = QPushButton('Browse...', self.shellTab)
        self.browse_shell_btn.setStatusTip('Browse for shelling .png')
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
        self.s_shlocx = QLineEdit(self.shellTab) #@FIELD
        self.s_shlocx.setFixedWidth(70)
        self.s_shlocy = QLineEdit(self.shellTab) #@FIELD
        self.s_shlocy.setFixedWidth(70)
        self.sx_lab = QLabel(self.shellTab)
        self.sx_lab.setText("X: ")
        self.sy_lab = QLabel(self.shellTab)
        self.sy_lab.setText("Y: ")
        self.sloc_label.setEnabled(False)
        self.s_shlocx.setEnabled(False)
        self.s_shlocy.setEnabled(False)
        self.sh3.addWidget(self.sloc_label)
        self.sh3.addStretch()
        self.sh3.addWidget(self.sx_lab)
        self.sh3.addWidget(self.s_shlocx)
        self.sh3.addSpacing(10)
        self.sh3.addWidget(self.sy_lab)
        self.sh3.addWidget(self.s_shlocy)
        self.shellForm.addRow(self.sh3)

        self.sh4 = QHBoxLayout()
        self.ssize_label = QLabel(self.shellTab)
        self.ssize_label.setText("Enter new size of shell on BG image: ")
        self.s_shsizex = QLineEdit(self.shellTab) #@FIELD
        self.s_shsizex.setFixedWidth(70)
        self.s_shsizey = QLineEdit(self.shellTab) #@FIELD
        self.s_shsizey.setFixedWidth(70)
        self.sx_labs = QLabel(self.shellTab)
        self.sx_labs.setText("X: ")
        self.sy_labs = QLabel(self.shellTab)
        self.sy_labs.setText("Y: ")
        self.ssize_label.setEnabled(False)
        self.s_shsizex.setEnabled(False)
        self.s_shsizey.setEnabled(False)
        self.sh4.addWidget(self.ssize_label)
        self.sh4.addStretch()
        self.sh4.addWidget(self.sx_labs)
        self.sh4.addWidget(self.s_shsizex)
        self.sh4.addSpacing(10)
        self.sh4.addWidget(self.sy_labs)
        self.sh4.addWidget(self.s_shsizey)
        self.shellForm.addRow(self.sh4)

        self.sects_sel = QLineEdit(self.shellTab)
        self.shellForm.addRow(QLabel("Sections to apply shelling to (separated by commas, see Help): ", self.shellTab))
        self.shellForm.addRow(self.sects_sel)

        self.steps_sel = QLineEdit(self.shellTab)
        self.shellForm.addRow(QLabel("Steps to apply shelling to (by demo index, select in sidebar): ", self.shellTab))
        self.shellForm.addRow(self.steps_sel)

        self.bottom_buttons(['Shell', 'Begin shelling'], self.shellTab, self.shellForm)

        self.shellLayout.addLayout(self.shellForm)
        self.shellLayout.addLayout(self.imgPreviewLayout)
        self.shellTab.setLayout(self.shellLayout)

        self.tab_widget.addTab(self.shellTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.shellTab), "Shell")

    def setSecondTab(self):
        self.insTab = QWidget()

        self.insForm = QFormLayout(self.insTab)
        self.insForm.setVerticalSpacing(10)
        self.insForm.setHorizontalSpacing(5)
        self.insForm.setContentsMargins(15, 15, 15, 15)

        self.insImgPreviewLayout = QGridLayout()
        self.insImgPreview = QGraphicsScene()

        ins_labels = [
            "Filepath of insertion .png: ",
            "Browse for filepath of .png containing insertion image",
            "Enter (x, y) coords of insertion image: ",
            "Enter new size of insertion image:"
        ]

        self.image_paste_form(ins_labels, self.insTab, self.insForm)

        self.insForm.addRow(QLabel())

        self.tab_widget.addTab(self.insTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.insTab), "Insert")

        self.sects_sel = QLineEdit(self.insTab)
        self.insForm.addRow(QLabel("Sections to insert image into (separated by commas, see Help): ", self.insTab))
        self.insForm.addRow(self.sects_sel)

        self.steps_sel = QLineEdit(self.insTab)
        self.insForm.addRow(QLabel("Steps to apply insertion to (by demo index, select in sidebar): ", self.insTab))
        self.insForm.addRow(self.steps_sel)

        self.bottom_buttons(['Insert', 'Begin insertion'], self.insTab, self.insForm)

    def setSectionTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.sectionTab = QWidget()
        self.sectionForm = QFormLayout(self.sectionTab)
        self.sectionForm.setVerticalSpacing(10)
        self.sectionForm.setHorizontalSpacing(5)
        self.sectionForm.setContentsMargins(15, 15, 15, 15)

        self.sectionForm.addRow("We can tell your demo is/is not sectioned...", self.sectionTab)

        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.sectionTab)
        reset_btn.setStatusTip('Reset demo to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Section", self.sectionTab)
        save_btn.setStatusTip('Begin sectioning')
        save_btn.clicked.connect(self.begin_sectioning) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.sectionForm.addRow(bot)

        self.tab_widget.addTab(self.sectionTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.sectionTab), "Sectioning")

    def setAudioTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.audioTab = QWidget()
        self.audioForm = QFormLayout(self.xmlTab)
        self.audioForm.setVerticalSpacing(10)
        self.audioForm.setHorizontalSpacing(5)
        self.audioForm.setContentsMargins(15, 15, 15, 15)

        self.audioForm.addRow("We can tell your demo has/does not have audio...", self.audioTab)

        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.audioTab)
        reset_btn.setStatusTip('Reset demo to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Add Audio", self.audioTab)
        save_btn.setStatusTip('Begin adding audio')
        save_btn.clicked.connect(self.add_audio) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.audioForm.addRow(bot)

        self.tab_widget.addTab(self.audioTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.audioTab), "Audio")

    def setXmlTab(self):
        #@TODO Add real functionality here involving mass XML edits by tag, not just as an XML editor
        self.xmlTab = QWidget()
        self.xmlForm = QFormLayout(self.xmlTab)
        self.xmlForm.setVerticalSpacing(20)
        self.xmlForm.setHorizontalSpacing(10)
        self.xmlForm.setContentsMargins(25, 25, 25, 25)

        self.xmlEditor = QTextEdit(self.xmlTab)
        self.xmlEditor.setStatusTip("This is where the XML bulk editor will live...")
        self.xmlForm.addRow(self.xmlEditor)
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        reset_btn = QPushButton('Reset', self.xmlTab)
        reset_btn.setStatusTip('Reset XML to default')
        reset_btn.clicked.connect(self.close) #@TODO Make actually reset
        save_btn = QPushButton("Save", self.xmlTab)
        save_btn.setStatusTip('Save current XML changes')
        save_btn.clicked.connect(self.ins_submit) #@TODO Actually save XML
        bot.addWidget(reset_btn)
        bot.addStretch()
        bot.addWidget(save_btn)
        self.xmlForm.addRow(bot)

        self.tab_widget.addTab(self.xmlTab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.xmlTab), "XML")


    #----------UI ELEMENTS-----------------#

    def demo_browse_layout(self, tab):
        #@TODO Take demo textbox as parameter so you dont have to paste the demo browse layout
        # code into every tab
        d = QHBoxLayout()
        demo_dir_label = QLabel(tab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_tbox = QLineEdit(tab)
        self.demo_tbox.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', tab)
        self.browse_demo_btn.setStatusTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_tbox)
        d.addWidget(self.browse_demo_btn)
        return d

    def image_paste_form(self, labels, tab, form):
        '''
        Gets *singular* insertion/bg image for shelling
        and insertion, as well as the coordinates of
        translation and scaling for either the asset (shelling)
        or insertion image, and stores them in self variables
        '''
        #@TODO Take Img textbox as parameter so you dont have to repaste this in each tab
        # for the textbox to be filled out when an image is brwosed for
        browse = QHBoxLayout()
        dir_label = QLabel(labels[0], tab)
        if tab is self.shellTab:
            self.img_tbox1 = QLineEdit(tab)
        if tab is self.insTab:
            self.img_tbox2 = QLineEdit(tab)
        self.browse_img_btn = QPushButton('Browse...', tab)
        self.browse_img_btn.setStatusTip(labels[1])
        self.browse_img_btn.clicked.connect(self.browse_img)
        browse.addWidget(dir_label)
        browse.addStretch()
        browse.addWidget(self.img_tbox1 if tab is self.shellTab else self.img_tbox2)
        browse.addWidget(self.browse_img_btn)
        form.addRow(browse)

        loc = QHBoxLayout()
        loc_label = QLabel(labels[2], tab)
        if tab is self.shellTab:
            self.shlocx = QLineEdit(tab)
            self.shlocx.setFixedWidth(70)
            self.shlocy = QLineEdit(tab)
            self.shlocy.setFixedWidth(70)
        elif tab is self.insTab:
            self.inslocx = QLineEdit(tab)
            self.inslocx.setFixedWidth(70)
            self.inslocy = QLineEdit(tab)
            self.inslocy.setFixedWidth(70)
        x_lab = QLabel("X: ", tab)
        y_lab = QLabel("Y: ", tab)
        loc.addWidget(loc_label)
        loc.addStretch()
        loc.addWidget(x_lab)
        loc.addWidget(self.shlocx if tab is self.shellTab else self.inslocx)
        loc.addSpacing(10)
        loc.addWidget(y_lab)
        loc.addWidget(self.shlocy if tab is self.shellTab else self.inslocy)
        form.addRow(loc)

        resize = QHBoxLayout()
        size_label = QLabel(labels[3], tab)
        size_label.setText(labels[3])
        if tab is self.shellTab:
            self.shsizex = QLineEdit(tab)
            self.shsizex.setFixedWidth(70)
            self.shsizey = QLineEdit(tab)
            self.shsizey.setFixedWidth(70)
        elif tab is self.insTab:
            self.inssizex = QLineEdit(tab)
            self.inssizex.setFixedWidth(70)
            self.inssizey = QLineEdit(tab)
            self.inssizey.setFixedWidth(70)
        x_labs = QLabel("X: ", tab)
        y_labs = QLabel("Y: ", tab)
        resize.addWidget(size_label)
        resize.addStretch()
        resize.addWidget(x_labs)
        resize.addWidget(self.shsizex if tab is self.shellTab else self.inssizex)
        resize.addSpacing(10)
        resize.addWidget(y_labs)
        resize.addWidget(self.shsizey if tab is self.shellTab else self.inssizey)
        form.addRow(resize)

    def toggle_extra_shell(self, toggle):
        self.extra_on = (toggle == 1)
        print("Toggling extra shell...  toggled: " + str(self.extra_on))
        self.shell_dir_label.setEnabled(self.extra_on)
        self.shell_img_tbox.setEnabled(self.extra_on)
        self.browse_shell_btn.setEnabled(self.extra_on)
        self.sloc_label.setEnabled(self.extra_on)
        self.s_shlocx.setEnabled(self.extra_on)
        self.s_shlocy.setEnabled(self.extra_on)
        self.ssize_label.setEnabled(self.extra_on)
        self.s_shsizex.setEnabled(self.extra_on)
        self.s_shsizey.setEnabled(self.extra_on)

    def bottom_buttons(self, labels, tab, form):
        bot = QHBoxLayout()
        bot.setAlignment(Qt.AlignBottom)
        self.close_btn = QPushButton('Cancel', tab)
        self.close_btn.setStatusTip('Close the program')
        self.close_btn.clicked.connect(self.close)
        self.submit_btn = QPushButton(labels[0], tab)
        self.submit_btn.setStatusTip(labels[1])
        if tab is self.shellTab:
            self.submit_btn.clicked.connect(self.shell_submit)
        elif tab is self.insTab:
            self.submit_btn.clicked.connect(self.ins_submit)
        bot.addWidget(self.close_btn)
        bot.addStretch()
        bot.addWidget(self.submit_btn)
        form.addRow(bot)

    # ------ FUNCTIONS --------------------#

    def begin_sectioning(self):
        pass

    def add_audio(self):
        pass

    def saveConfig(self):
        pass

    def loadConfig(self):
        pass

    def browse_demo(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .demo files", "","Demo files (*.demo);;All Files (*)", options=options)
        self.demo_tbox.setText(fileName)
        self.DEMO_PATH = fileName
        self.load_demo()

    def browse_script(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .docx files", "","Word files (*.docx);;All Files (*)", options=options)
        self.script_tbox.setText(fileName)
        self.SCRIPT_PATH = fileName
        self.load_demo()

    def browse_audio(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderName, _ = QFileDialog.getExistingDirectory(self,"Browse for audio folder", "","All Files (*)", options=options)
        self.audio_tbox.setText(folderName)
        self.AUDIO_PATH = folderName
        self.load_demo()

    
    #TODO Add "Select all" to QTreeView through top left behavior
    #TODO Maybe subclass QTreeView for demo tree to allow for easier handling
    #     of checkbox emitting signals upon selection and de-selection?
    #TODO I'm sure there's already selected checkboxes being stored in a list
    #     somewhere, find a way to access it rather than making for loops everywhere
    def load_demo(self):
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        self.demo = Demo(path=self.DEMO_PATH, script_path=self.SCRIPT_PATH, audio_dir=self.AUDIO_PATH)
        self.xmlEditor.setText(self.demo.xml())
        self.demo_title = QLabel(self.demo.title)
        self.demo_model = QStandardItemModel(self.demo_tree)
        self.demo_model.setHorizontalHeaderLabels([self.demo.title, "Has TP", "Animated"])
        for i, sect in enumerate(self.demo):
            section = QStandardItem(sect.title)
            section.setColumnCount(3)
            section.setCheckable(True)
            section.setDragEnabled(True)
            section.setSelectable(True)
            section.setEditable(True)
            section.setDropEnabled(True)
            section.setFlags(section.flags() | Qt.ItemIsTristate \
                            | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            for j, step in enumerate(sect):
                qstep = QStandardItem(step.name)
                qstep.setCheckable(True)
                qstep.setSelectable(True)
                qstep.setDragEnabled(True)
                qstep.setDropEnabled(True)
                qtp = QStandardItem(str(step.tp.text is not ""))
                qan = QStandardItem(str(step.animated))
                qt = QStandardItem()
                section.appendRow([qstep, qtp, qan])
                section.setChild(j, qstep)
            self.demo_model.appendRow(section)
        self.demo_model.itemChanged.connect(self.displayInfo)
        self.demo_tree.setModel(self.demo_model)
        #TODO set demo tree selection model?

    def displayDemoInfo(self):
        #implement for TreeView selectionChanged, add this logic to modelitemlist itemChanged
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        demo_info = QStandardItemModel(self.demo_info)
        demo_info.setColumnCount(2)
        demo_info.setHorizontalHeaderLabels(["Property", "Value"])
        demo_info.appendRow(Q(["Title", self.demo.title]))
        demo_info.appendRow(Q(["ID", self.demo.id]))
        demo_info.appendRow(Q(["Demo path", str(self.demo.path)]))
        demo_info.appendRow(Q(["Script loaded", self.demo.script.loaded]))
        demo_info.appendRow(Q(["Audio loaded", self.demo.audio.loaded]))
        demo_info.appendRow(Q(["Number steps", len(self.demo.steps)]))
        demo_info.appendRow(Q(["Number sections", len(self.demo.sections)]))
        self.demo_info.setModel(demo_info)
            
    def displayInfo(self, item):
        def Q(ls: list): return [QStandardItem(q) for q in ls]
        if item.checkState():
            index = self.demo_model.indexFromItem(item).row()
            item_info = QStandardItemModel(self.demo_info)
            if item.hasChildren():
                self.getChecked(item,True,index)
                sect = self.demo.sections[index]
                item_info.appendRow([QStandardItem("Title: "), QStandardItem(sect.title)])
                item_info.appendRow([QStandardItem("ID: "), QStandardItem(sect.id)])
                item_info.appendRow(Q(["Demo index: ", sect.demo_idx]))
                item_info.appendRow(Q(["Section index: ", sect.idx]))
                item_info.appendRow(Q(["Assets: ", str(sect.assets)]))
                item_info.appendRow(Q(["Audio: ", str(sect.audio)]))
            else:
                self.getChecked(item,False,index)
                sect_idx = self.demo_model.indexFromItem(item.parent()).row()
                step = self.demo.sections[sect_idx].steps[index]
                item_info.appendRow(Q(["Name: ", step.name]))
                item_info.appendRow(Q(["ID: ", step.id]))
                item_info.appendRow(Q(["Demo index: ", step.demo_idx]))
                item_info.appendRow(Q(["Step index: ", step.idx]))
                item_info.appendRow(Q(["Assets: ", str(step.assets)]))
                item_info.appendRow(Q(["Audio: ", str(step.audio)]))
                item_info.appendRow(Q(["Instructions: ", str(step.ci)]))
                item_info.appendRow(Q(["Talking Point: ", str(step.tp)]))
                for i, (attr, adict) in enumerate(dt.STEP_PROPS.items()):
                    item_info.appendRow(Q([attr.capitalize()+": ", getattr(step, attr)]))
                for box, bdict in dt.BOX_PROPS.items():
                    for i, (prop, bdictall) in enumerate(\
                        {**bdict["props"], **dt.DIRS}.items()):
                        try:
                            tag = bdict[box]['tag'][:-1].capitalize()
                            proptag = bdictall[prop]['tag']
                            val = getattr(step,box)[prop]
                            item_info.appendRow(Q([f"{tag} {proptag}", str(val)]))
                        except:
                            pass
            self.demo_info.setModel(item_info)
            self.demo_info.setColumnWidth(0, 250)
            self.demo_info.setColumnWidth(1, 100)
            self.demo_info.setColumnWidth(1, 100)
        else:
            self.displayDemoInfo()

    def getChecked(self,item,item_is_sect,index):
        model = item.model()
        print(f"signal emitted! getChecked called! Is sect? {str(item_is_sect)} index: {index}")
        sel = self.demo_tree.selectedIndexes()
        print(sel)
        count = 0
        sel_sects, sel_steps = self.SECTS_SELECTED, self.STEPS_SELECTED
        #TODO I'm sure this logic is already all implemented in Qt already... find it
        #at least minimize redundant logic present here
        for rowi in range(model.rowCount()):
            sect = model.item(rowi)
            title = self.demo.sections[rowi].title
            sect_checked = sect.checkState()
            if sect_checked:
                sel_sects.add(title)
                #self.demo_tree.setExpanded(rowi, True)
            else:
                sel_sects.discard(title)
            for stepi in range(sect.rowCount()):
                step = sect.child(stepi, 0)
                step_checked = step.checkState()
                if sect_checked and item_is_sect:
                    step.setCheckState(True)
                    sel_steps.add(count)
                else:
                    if step_checked and item_is_sect:
                        step.setCheckState(False)
                        sel_steps.discard(count)
                    elif step_checked and not item_is_sect:
                        sel_steps.add(count)
                    else:
                        sel_steps.discard(count)
                count += 1
        if len(sel_sects):
            self.sects_sel.setText(str(sorted(sel_sects))[1:-1])
        else:
            self.sects_sel.setText("")
        if len(sel_steps):
            self.steps_sel.setText(str(sorted(sel_steps))[1:-1])
        else:
            self.steps_sel.setText("")
        self.SECTS_SELECTED, self.STEPS_SELECTED = sel_sects, sel_steps

    def getSelectedInfo(self, item):
        raise NotImplementedError()

    def browse_img(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        img_tmp = Image.open(fileName)
        iwidth, iheight = img_tmp.size
        self.img_tbox1.setText(fileName)
        self.img_tbox2.setText(fileName)
        self.shsizex.setText(str(iwidth))
        self.shsizey.setText(str(iheight))
        self.inssizex.setText(str(iwidth))
        self.inssizey.setText(str(iheight))
        self.IMG_PATH = fileName

    # FOR SECOND SHELL, I.E. IF EXTRA_ON=TRUE
    def browse_shell(self, tbox):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for image files", "","All Files (*);;PNG files (*.png)", options=options)
        if fileName:
            print(fileName)
        img_tmp = Image.open(fileName)
        iwidth, iheight = img_tmp.size
        self.s_shsizex.setText(str(int(iwidth)))
        self.s_shsizey.setText(str(int(iheight)))
        self.s_shlocx.setText(str(int((1920-iwidth)/2)))
        self.s_shlocy.setText(str(int((1080-iheight)/2)))
        self.shell_img_tbox.setText(fileName)
        self.SHELL_PATH = fileName

    @pyqtSlot()
    def shell_submit(self):
        demo_dir = self.demo_tbox1.text()
        bg_img_dir = self.img_tbox1.text()
        bg_img_loc = None
        bg_img_size = None
        if ((len(self.shlocx.text()) > 0 and len(self.shlocy.text()) > 0) and
           (len(self.shsizex.text()) > 0 and len(self.shsizey.text()) > 0)):
            bg_img_loc = (int(self.shlocx.text()), int(self.shlocy.text()))
            bg_img_size = (int(self.shsizex.text()), int(self.shsizey.text()))
        shell_img_tbox = None; shell_img_loc = None; shell_img_size = None;
        to_shell = [s.strip() for s in self.shellSects.text().split(",")]
        if self.extra_on:
            shell_img_tbox = self.shell_img_tbox.text()
            if ((len(self.s_shlocx.text()) > 0 and len(self.s_shlocy.text()) > 0) and
               (len(self.s_shsizex.text()) > 0 and len(self.s_shsizey.text()) > 0)):
                shell_img_loc = (int(self.s_shlocx.text()), int(self.s_shlocy.text()))
                shell_img_size = (int(self.s_shsizex.text()), int(self.s_shsizey.text()))
        print(demo_dir, bg_img_dir, bg_img_loc, bg_img_size, to_shell, self.extra_on, shell_img_tbox, shell_img_loc, shell_img_size)
        """
        self.shellProg = QProgressDialog("Shelling asset files...", "Cancel", 0, 100)
        self.shellProg.setWindowTitle("Impresys Utilities - Shelling...")
        self.shellProg.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.shellProg.setGeometry(10, 10, 300, 100)
        self.shellProg.show()
        """
        self.statusbar.showMessage("Shelling...")
        self.image_paste(demo_dir, bg_img_dir, bg_img_loc, bg_img_size, typ='shell', sect=to_shell, 
                         sep=self.extra_on, s_img_path=shell_img_tbox, s_img_loc=shell_img_loc, s_img_size=shell_img_size)
        self.statusbar.showMessage("Finished shelling!")
        #self.shellProg.setWindowTitle("Impresys Utilities - Shelling completed!")
        print("Shelling finished")

    @pyqtSlot()
    def ins_submit(self):
        demo_dir = self.demo_tbox2.text()
        fg_img_dir = self.img_tbox2.text()
        fg_img_loc = None
        fg_img_size = None
        to_ins = [s.strip() for s in self.insSects.text().split(',')]
        if ((len(self.inslocx.text()) > 0 and len(self.inslocy.text()) > 0) and
           (len(self.inssizex.text()) > 0 and len(self.inssizey.text()) > 0)):
            fg_img_loc = (int(self.inslocx.text()), int(self.inslocy.text()))
            fg_img_size = (int(self.inssizex.text()), int(self.inssizey.text()))
        print(demo_dir, fg_img_dir, fg_img_loc, fg_img_size)
        self.statusbar.showMessage("Beginning insertion...")
        self.image_paste(demo_dir, fg_img_dir, fg_img_loc, fg_img_size, typ='insert', sect=to_ins)
        self.statusbar.showMessage("Insertion complete!")
        print("Insertion finished!")
        '''
        self.insProg = QProgressDialog("Inserting into asset files...", "Cancel", 0, 100)
        self.insProg.setWindowTitle("Impresys Utilities - Inserting...")
        self.insProg.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.insProg.setGeometry(10, 10, 300, 100)
        '''
        #self.image_paste(props...)

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

    def preview_img(self):
        self.setGeometry(10, 10, 800, 450)

    def image_paste(self, demo_path, image_path, img_loc: Tuple[int, int], img_size: Tuple[int, int], typ='shell', sect=[], 
                    sep=False, s_img_path=None, s_img_loc: Tuple[int, int]=None, s_img_size: Tuple[int, int]=None):

        bg_img_size = (1920, 1080)
        sect = [s.lower() for s in sect]

        fg_img_loc = img_loc
        fg_img_size = img_size

        if (img_size[0]+img_loc[0]>bg_img_size[0] or
            img_size[1]+img_loc[1]>bg_img_size[1]):
            raise Exception("Resized and relocated image beyond original boundaries")
        img = Image.open(image_path) #shell or insertion image

        if (typ=='shell' and sep is True and s_img_size and s_img_loc):
            shell_bound = (s_img_size[0]+s_img_loc[0], s_img_size[1]+s_img_loc[1])
            if (shell_bound[0]>bg_img_size[0] or
                shell_bound[1]>bg_img_size[1]):
                raise Exception("Resized and relocated shell beyond original boundaries of fg and/or bg")
            s_img = Image.open(s_img_path)
            s_img_resize = s_img.resize((int(s_img_size[0]), int(s_img_size[1])), Image.ANTIALIAS)
            img.paste(s_img_resize, (int(s_img_loc[0]), int(s_img_loc[1])), s_img_resize.convert('RGBA'))

        parser = ET.XMLParser(strip_cdata=False)
        demo = ET.parse(demo_path, parser)
        root = demo.getroot()
        demo_dir = demo_path.rsplit('/', 1)[0]

        ry = float(fg_img_size[1] / bg_img_size[1])
        rx = float(fg_img_size[0] / bg_img_size[0])

        def transform(coords: List[float]) -> List[float]: #-> [top, bottom, left, right]
            out = []
            if len(coords) > 2: # if BOX coordinates (T, B, L, R)
                for i in range(4):
                    if i < 2: out.append(float(coords[i] * ry + fg_img_loc[1]))
                    else: out.append(float(coords[i] * rx + fg_img_loc[0]))
            elif len(coords) <= 2: # if CLICK coordinates (X, Y)
                out.append(float(coords[0] * rx + fg_img_loc[0]))
                out.append(float(coords[1] * ry + fg_img_loc[1]))
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
            return None

        for chapter in list(root.iter('Chapter')):
            section = chapter.find('XmlName').find('Name').text
            if (sect == ['']) or (section.lower() in sect):
                steps = list(chapter.iter('Step'))
                for i, step in enumerate(steps):
                    asset_dir = step.find("StartPicture").find("AssetsDirectory").text
                    asset_dir = asset_dir.replace('\\', '/')
                    assetpath = demo_dir + '/' + asset_dir
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
                        if filename.lower().endswith('.png'):
                            impath = assetpath+filename
                            asset_img = Image.open(impath)
                            new_img = img.copy()
                            if typ == 'shell':
                                asset_img_resize = asset_img.resize((int(fg_img_size[0]), int(fg_img_size[1])), Image.ANTIALIAS)
                                new_img.paste(asset_img_resize, (int(fg_img_loc[0]), int(fg_img_loc[1])))
                                new_img.save(impath, quality=100)
                                print("SHELLED: Section: "+section+", Step: "+str(i)+", image: "+filename)
                            else:
                                fg_img_resize = new_img.resize((int(fg_img_size[0]), int(fg_img_size[1])), Image.ANTIALIAS)
                                asset_img.paste(fg_img_resize, (int(fg_img_loc[0]), int(fg_img_loc[1])), fg_img_resize.convert('RGBA'))
                                asset_img.save(impath, quality=100)
                                print("INSERTED: Section: "+section+", Step: "+str(i)+", image: "+"t")

        demo.write(demo_path, xml_declaration=True, encoding='utf-8')

class BrowseDemo(QHBoxLayout):

    def __init__(self, window):
        self.window = window
        

    @pyqtSlot()
    def browse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .demo files", "","Demo files (*.demo);;All Files (*)", options=options)
        self.tbox.setText(fileName)
        self.window.DEMO_PATH = fileName

class ShellTab(QWidget):

    def __init__(self):
        pass

class InsertTab(QWidget):

    def __init__(self):
        pass

class AudioTab(QWidget):

    def __init__(self):
        pass

