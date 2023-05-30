import enum
from qt import *


@enum.unique
class ButtonNames(enum.Enum):
    # MODEL_GRAPH = 'Model Graph'
    GENERATE = 'Generate Code'
    RUN = 'Run Code'
    SAVE_MODEL = 'Save Model'
    LOAD_MODEL = 'Load Model'


class ToolBar(QToolBar):
    # Идея: завести свой сигнал для каждой кнопки
    # model_graph_btn_clicked = Signal()
    generate_code_btn_clicked = Signal()
    save_model_btn_clicked = Signal()
    load_model_btn_clicked = Signal()
    run_code_btn_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAllowedAreas(Qt.TopToolBarArea)

        for name in ButtonNames:
            self.addAction(name.value)

        self.actionTriggered.connect(self.action_handler)

    def action_handler(self, action):
        # if action.text() == ButtonNames.MODEL_GRAPH.value:
            # TODO Надо подумать над логированием. Возможно принтом пользоваться неправильно.
            # print('<Model Graph> handler')
            # self.model_graph_btn_clicked.emit()
        if action.text() == ButtonNames.GENERATE.value:
            self.generate_code_btn_clicked.emit()
        if action.text() == ButtonNames.RUN.value:
            self.run_code_btn_clicked.emit()
        if action.text() == ButtonNames.SAVE_MODEL.value:
            self.save_model_btn_clicked.emit()
        if action.text() == ButtonNames.LOAD_MODEL.value:
            self.load_model_btn_clicked.emit()




