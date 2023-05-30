from qt import *


class MenuBar(QMenuBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_ebn0_db = 15
        self.min_ebn0_db = 1
        self.threads_number = 1

        modellling_settings = QMenu('Моделирование')

        menu = QMenu("Min Eb/N0")
        self.min_ebn0_ql = QLineEdit("1")
        self.min_ebn0_ql.setValidator(QIntValidator(1, 50))
        self.min_ebn0_ql.setPlaceholderText("Min Eb/N0")
        self.min_ebn0_ql.editingFinished.connect(self.on_min_ebn0)
        w_action = QWidgetAction(self)
        w_action.setDefaultWidget(self.min_ebn0_ql)
        menu.addAction(w_action)
        modellling_settings.addMenu(menu)

        menu = QMenu("Max Eb/N0")
        self.max_ebn0_ql = QLineEdit("15")
        self.max_ebn0_ql.setValidator(QIntValidator(1, 50))
        self.max_ebn0_ql.setPlaceholderText("Max Eb/N0")
        self.max_ebn0_ql.editingFinished.connect(self.on_max_ebn0)
        w_action = QWidgetAction(self)
        w_action.setDefaultWidget(self.max_ebn0_ql)
        menu.addAction(w_action)
        modellling_settings.addMenu(menu)

        menu = QMenu("Threads Number")
        self.threads_number_ql = QLineEdit("1")
        self.threads_number_ql.setValidator(QIntValidator(1, 65))
        self.threads_number_ql.setPlaceholderText("Threads Number")
        self.threads_number_ql.editingFinished.connect(self.on_threads_number)
        w_action = QWidgetAction(self)
        w_action.setDefaultWidget(self.threads_number_ql)
        menu.addAction(w_action)
        modellling_settings.addMenu(menu)

        self.addMenu(modellling_settings)

    def on_min_ebn0(self):
        text = self.min_ebn0_ql.text()
        print(text)
        self.min_ebn0_db = int(text)

    def on_max_ebn0(self):
        text = self.max_ebn0_ql.text()
        print(text)
        self.max_ebn0_db = int(text)

    def on_threads_number(self):
        text = self.threads_number_ql.text()
        print(text)
        self.threads_number = int(text)


