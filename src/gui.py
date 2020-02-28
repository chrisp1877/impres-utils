import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
    QVBoxLayout, QFileDialog, QAction, QMessageBox
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
        
        self.demo_dir_tbox = QLineEdit(self)
        self.demo_dir_tbox.move(20, 40)
        self.demo_dir_tbox.resize(200,30)

        browse_demo = QPushButton('Browse...', self)
        browse_demo.setToolTip('Browse for .demo file')
        browse_demo.move(250,40)
        browse_demo.clicked.connect(self.browse_demo)

        self.bg_img_tbox = QLineEdit(self)
        self.bg_img_tbox.move(20, 80)
        self.bg_img_tbox.resize(200,30)

        browse_bg = QPushButton('Browse...', self)
        browse_bg.setToolTip('Browse for .demo file')
        browse_bg.move(250,80)
        browse_bg.clicked.connect(self.browse_img)


        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        button = QPushButton('Shell/Insert', self)
        button.setToolTip('Begin shelling/insertion')
        button.move(600,500)
        button.clicked.connect(self.on_click)
        
        self.statusBar().showMessage('Ready for shelling/insertion')
        self.show()

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