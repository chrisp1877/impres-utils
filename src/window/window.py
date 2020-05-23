import sys, os
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox, QFrame, QStatusBar,
    QTabWidget, QSpacerItem, QSizePolicy, QRadioButton, QProgressBar,
    QButtonGroup, QDoubleSpinBox, QGraphicsScene, QProgressDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QFileSelector
import lxml.etree as ET
from PIL import Image
from typing import List, Tuple
from pathlib import Path

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

class ImpresysWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.DEMO_PATH = None
        self.IMG_PATH = None
        self.SHELL_PATH = None
        self.SECTS = list()
        self.FG_LOC = [None, None]
        self.FG_SIZE = [None, None]
        self.SHELL_BG_SEPARATE = bool()
        self.SHELL_LOC = [None, None]
        self.SHELL_SIZE = [None, None]

        self.title = 'Impresys Utilities'
        self.left = 10
        self.top = 10
        self.width = 450
        self.height = 550
        self.width_with_rightpane = 900
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon(SCRIPTDIR+os.path.sep+'logo.png'))
        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.addStatusBar()
        self.addMenuBar()
        self.configPreview()
        self.setTabs()
        self.setFirstTab()
        self.setSecondTab()
        self.setXmlTab()
        self.progBar = QProgressBar()
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        #self.gridLayout.addWidget(self.progBar, 1, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def addMenuBar(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        #toolsMenu = mainMenu.addMenu('Tools')
        aboutMenu = mainMenu.addMenu('About')
        helpMenu = mainMenu.addMenu('Help')
        saveConfig = QAction(QIcon('save.png'), 'Save inputs', self)
        saveConfig.setShortcut('Ctrl+S')
        saveConfig.setStatusTip('Save currently inputted variables to a text file')
        #saveButton.triggered.connect(self.saveConfig)
        fileMenu.addAction(saveConfig)

        preferences = QAction(QIcon('prefs.png'), 'Preferences', self)
        preferences.setShortcut('Ctrl+P')
        preferences.setStatusTip('Change preferences for different utilities')
        #preferences.triggered.connect(self.preferences)
        editMenu.addAction(preferences)

        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setShortcut('Ctrl+Shift+V')
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)
        viewMenu.addAction(viewStatAct)

        viewPrev = QAction('View preview', self, checkable=True)
        viewPrev.setShortcut('Ctrl+Shift+P')
        viewPrev.setStatusTip('View preview of shelling / insertion points')
        viewPrev.setChecked(True)
        viewPrev.triggered.connect(self.preview_img)
        viewMenu.addAction(viewPrev)

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

    def configPreview(self):
        self.shellLayout = QVBoxLayout()

    def setTabs(self):
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
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

        d = QHBoxLayout()
        demo_dir_label = QLabel(self.shellTab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_tbox1 = QLineEdit(self.shellTab)
        self.demo_tbox1.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', self.shellTab)
        self.browse_demo_btn.setStatusTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_tbox1)
        d.addWidget(self.browse_demo_btn)

        self.shellForm.addRow(d)
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

        self.shellSects = QLineEdit(self.shellTab)
        #self.shellSects.setPlaceholderText('All')
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

        d = QHBoxLayout()
        demo_dir_label = QLabel(self.insTab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_tbox2 = QLineEdit(self.insTab)
        self.demo_tbox2.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', self.insTab)
        self.browse_demo_btn.setStatusTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_tbox2)
        d.addWidget(self.browse_demo_btn)

        self.insForm.addRow(d)
        self.image_paste_form(ins_labels, self.insTab, self.insForm)

        self.shellForm.addRow(QLabel())

        self.tabWidget.addTab(self.insTab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.insTab), "Insert")
        self.insSects = QLineEdit(self.insTab)
        #self.insSects.setPlaceholderText('All')
        self.to_ins = self.insSects.text().split(",") #@FIELD
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

        d = QHBoxLayout()
        demo_dir_label = QLabel(self.xmlTab)
        demo_dir_label.setText("Enter .demo file location:")
        self.demo_tbox3 = QLineEdit(self.xmlTab)
        self.demo_tbox3.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', self.xmlTab)
        self.browse_demo_btn.setStatusTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        d.addWidget(demo_dir_label)
        d.addStretch()
        d.addWidget(self.demo_tbox3)
        d.addWidget(self.browse_demo_btn)

        self.xmlForm.addRow(d)
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

        self.tabWidget.addTab(self.xmlTab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.xmlTab), "XML")


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
    @pyqtSlot( )
    def addRandomTextSlot( self ):
        self.textEdit.insertPlainText( "Hello World!" )

    def browse_demo(self, tnum):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Browse for .demo files", "","Demo files (*.demo);;All Files (*)", options=options)
        if fileName:
            print(fileName)
        self.demo_tbox1.setText(fileName)
        self.demo_tbox2.setText(fileName)
        self.demo_tbox3.setText(fileName)
        self.DEMO_PATH = fileName

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

        if (typ=='shell' and sep is True):
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

