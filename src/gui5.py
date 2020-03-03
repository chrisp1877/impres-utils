from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
import sys, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox, QFrame, QStatusBar,
    QTabWidget, QSpacerItem, QSizePolicy, QRadioButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

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
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir+os.path.sep+'logo.png'))
        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.addStatusBar()
        self.addMenuBar()
        self.setTabs()
        self.setFirstTab()
        self.setSecondTab()

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

    def setTabs(self):
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")

    def addStatusBar(self):
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("Shell or insert status")
        self.statusbar.showMessage("Ready for shelling/insertion")
        self.setStatusBar(self.statusbar)

    def setFirstTab(self):
        self.imgLayout = QFormLayout(self.tab)

        self.h1 = QHBoxLayout()
        self.h1.addSpacing(5)
        self.typ_label = QLabel(self.tab)
        self.typ_label.setText("Choose whether to shell or insert:")
        self.typ_shell = QRadioButton("Shell")
        self.typ_shell.setLayoutDirection
        self.typ_insert = QRadioButton("Insert")
        self.h1.addWidget(self.typ_label)
        self.h1.addWidget(self.typ_shell, )
        self.h1.addWidget(self.typ_insert)
        self.imgLayout.addRow(self.h1)
        shell: bool = True

        self.h2 = QHBoxLayout()
        self.shell_label = QLabel(self.tab)
        self.shell_label.setText("Single shell, or shell and BG?")
        self.one_img = QRadioButton("Combined")
        self.two_img = QRadioButton("Shell + BG")
        self.h2.addWidget(self.shell_label)
        self.h2.addWidget(self.one_img)
        self.h2.addWidget(self.two_img)
        self.imgLayout.addRow(self.h2)
        one_image: bool = True

        self.h3 = QHBoxLayout()
        self.demo_dir_label = QLabel(self.tab)
        self.demo_dir_label.setText("Enter .demo file location:")
        self.demo_dir_tbox = QLineEdit(self.tab)
        self.demo_dir_tbox.resize(100, 30)
        self.browse_demo_btn = QPushButton('Browse...', self.tab)
        self.browse_demo_btn.setToolTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        self.h3.addWidget(self.demo_dir_label)
        self.h3.addWidget(self.demo_dir_tbox)
        self.h3.addWidget(self.browse_demo_btn)
        self.imgLayout.addRow(self.h3)
        
        one_two_labels = [
            "Filepath of background + shell .png: ",
            "Filepath of background (no shell) .png: ",
        ]
        self.h4 = QHBoxLayout()
        self.bg_dir_label = QLabel(self.tab)
        self.bg_dir_label.setText(one_two_labels[0] if one_image else one_two_labels[1])
        self.bg_img_tbox = QLineEdit(self.tab)
        self.browse_bg_btn = QPushButton('Browse...', self.tab)
        self.browse_bg_btn.setToolTip(one_two_labels[0])
        self.browse_bg_btn.clicked.connect(self.browse_img)
        self.h4.addWidget(self.bg_dir_label)
        self.h4.addWidget(self.bg_img_tbox)
        self.h4.addWidget(self.browse_bg_btn)
        self.imgLayout.addRow(self.h4)

        # -- SHOW THE IMAGE SELECTED FOR BG / BG + SHELL

        # Browse for shell image: #@TODO still need to implement this feature in the paste image code
        self.h5 = QHBoxLayout()
        self.shell_dir_label = QLabel(self.tab)
        self.shell_dir_label.setText("Enter shell image location:")
        self.shell_img_tbox = QLineEdit(self.tab)
        self.browse_shell_btn = QPushButton('Browse...', self.tab)
        self.browse_shell_btn.setToolTip('Browse for shelling .png')
        self.browse_shell_btn.clicked.connect(self.browse_shell)
        if one_image:
            self.shell_dir_label.setEnabled(False)
            self.shell_img_tbox.setEnabled(False)
            self.browse_shell_btn.setEnabled(False)
        self.h5.addWidget(self.shell_dir_label)
        self.h5.addWidget(self.shell_img_tbox)
        self.h5.addWidget(self.browse_shell_btn)
        self.imgLayout.addRow(self.h5)

        # -- SHOW THE IMAGE SELECTED FOR SHELL
        
        loc_labels = [
            "Enter (x, y) coords of asset image in shell:",
            "Enter (x, y) coords for image to be inserted:"
        ]
        self.h6 = QHBoxLayout()
        self.loc_label = QLabel(self.tab)
        self.loc_label.setText(loc_labels[0] if shell else loc_labels[1])
        self.locx = QLineEdit(self.tab)
        self.locy = QLineEdit(self.tab)
        self.h6.addWidget(self.loc_label)
        self.h6.addWidget(self.locx)
        self.h6.addWidget(self.locy)
        self.imgLayout.addRow(self.h6)

        size_labels = [
            "Enter new size of asset image in shell:",
            "Enter new size of image to be inserted:"
        ]
        self.h7 = QHBoxLayout()
        self.size_label = QLabel(self.tab)
        self.size_label.setText(size_labels[0] if shell else size_labels[1])
        self.sizex = QLineEdit(self.tab)
        self.sizey = QLineEdit(self.tab)
        self.h7.addWidget(self.size_label)
        self.h7.addWidget(self.sizex)
        self.h7.addWidget(self.sizey)
        self.imgLayout.addRow(self.h7)

        self.h8 = QHBoxLayout()
        self.close_btn = QPushButton('Cancel', self.tab)
        self.close_btn.setToolTip('Close the program')
        self.close_btn.clicked.connect(self.close)
        self.submit_btn = QPushButton('Shell/Insert', self.tab)
        self.submit_btn.setToolTip('Begin shelling/insertion')
        self.submit_btn.clicked.connect(self.on_click)
        self.h7.addWidget(self.close_btn)
        self.h7.addWidget(self.submit_btn)
        self.imgLayout.addRow(self.h8)

        self.tab.setLayout(self.imgLayout)
  
        #self.setLayout(self.imgForm)

        self.tabWidget.addTab(self.tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Bulk Image")

    def setSecondTab(self):
        self.tab_2 = QWidget()
        self.gridLayout_4 = QGridLayout(self.tab_2)
        self.textEdit = QTextEdit(self.tab_2)
        self.gridLayout_4.addWidget(self.textEdit, 0, 0, 1, 1)
        self.gridLayout_3 = QGridLayout()
        self.horizontalLayout_2 = QHBoxLayout()
        self.pushButton = QPushButton(self.tab_2)
        self.pushButton.setText("Clear")
        self.horizontalLayout_2.addWidget(self.pushButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButton_2 = QPushButton(self.tab_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Exit")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "Other")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.pushButton_2.clicked.connect( self.addRandomTextSlot)
        self.pushButton.clicked.connect(self.textEdit.clear)
    
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
        QMessageBox.question(self, 'Message - pythonspot.com', "Demo dir: " + demo_dir, QMessageBox.Ok, QMessageBox.Ok)
        print('Test click')

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = ImpresysWindow()
    MainWindow.show()
    sys.exit(app.exec_())