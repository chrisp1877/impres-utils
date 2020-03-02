import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class ImpresysApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Impresys Bulk Image Editing Utility'
        self.left = 10
        self.top = 10
        self.width = 450
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolsMenu = mainMenu.addMenu('Tools')
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
        
        self.createGridLayout()
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)
        
        self.statusBar().showMessage('Ready for shelling/insertion')
        self.show()

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setColumnStretch(1,5)
        layout.setColumnStretch(2,5)

        ## ENTER RADIO BUTTON TO ASK FOR SHELLING OR INSERT
        ## MAKE TEXT OF FOLLOWING TEXT BOXES CORRESPOND TO SEELECTION

        ## ENTER RADIO BUTTON TO ASK IF USER WANTS TO ADD BG IMAGE AND SHELL IF SHELL
        ## MAKE TEXT BELOW COHERE TO SELECTION


        self.demo_dir_label = QLabel(self)
        self.demo_dir_label.setText("Enter .demo file location:")
        layout.addWidget(self.demo_dir_label, 0,1)
        self.demo_dir_tbox = QLineEdit(self)
        self.demo_dir_tbox.resize(200,30)
        layout.addWidget(self.demo_dir_tbox, 1,1)
        self.browse_demo_btn = QPushButton('Browse...', self)
        self.browse_demo_btn.setToolTip('Browse for .demo file')
        self.browse_demo_btn.clicked.connect(self.browse_demo)
        layout.addWidget(self.browse_demo_btn, 2, 1)

        self.bg_dir_label = QLabel(self)
        self.bg_dir_label.setText("Enter bg image location:")
        layout.addWidget(self.bg_dir_label, 0,2)
        self.bg_img_tbox = QLineEdit(self)
        self.bg_img_tbox.resize(200,30)
        layout.addWidget(self.bg_img_tbox, 1,2)
        self.browse_bg_btn = QPushButton('Browse...', self)
        self.browse_bg_btn.setToolTip('Browse for .demo file')
        self.browse_bg_btn.clicked.connect(self.browse_img)
        layout.addWidget(self.browse_bg_btn, 2,2)

        self.submit = QPushButton('Shell/Insert', self)
        self.submit.setToolTip('Begin shelling/insertion')
        self.submit.clicked.connect(self.on_click)
        layout.addWidget(self.submit, 3, 4)

        self.horizontalGroupBox.setLayout(layout)


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

    def toggleMenu(self, state):
        if state: self.statusBar.show()
        else: self.statusBar.hide()
    
    @pyqtSlot()
    def on_click(self):
        demo_dir = self.demo_dir_tbox.text()
        bg_img_dir = self.bg_img_tbox.text()
        QMessageBox.question(self, 'Message - pythonspot.com', "Demo dir: " + demo_dir, QMessageBox.Ok, QMessageBox.Ok)
        print('Test click')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImpresysApp()
    sys.exit(app.exec_())