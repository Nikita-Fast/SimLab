from qt import *


class MenuBar(QMenuBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        settings = QMenu('Файл')
        self.addMenu(settings)

