from qt import *


class MenuBar(QMenuBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        settings = QMenu('Файл')
        self.addMenu(settings)
        modellling_settings = QMenu('Моделирование')
        modellling_settings.addMenu(QMenu("Min Eb/N0"))
        modellling_settings.addMenu(QMenu("Max Eb/N0"))
        self.addMenu(modellling_settings)

