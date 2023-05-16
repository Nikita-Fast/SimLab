import enum
from qt import *


@enum.unique
class ButtonNames(enum.Enum):
    MODEL_GRAPH = 'Model Graph'
    GENERATE = 'Generate Code and Run'
    # RUN = 'Run'


class ToolBar(QToolBar):
    # Идея: завести свой сигнал для каждой кнопки
    model_graph_btn_clicked = Signal()
    generate_code_btn_clicked = Signal()
    # run_btn_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAllowedAreas(Qt.TopToolBarArea)

        for name in ButtonNames:
            self.addAction(name.value)

        self.actionTriggered.connect(self.action_handler)

    def action_handler(self, action):
        if action.text() == ButtonNames.MODEL_GRAPH.value:
            # TODO Надо подумать над логированием. Возможно принтом пользоваться неправильно.
            print('<Model Graph> handler')
            self.model_graph_btn_clicked.emit()
        if action.text() == ButtonNames.GENERATE.value:
            print('<Generate Code> handler')
            self.generate_code_btn_clicked.emit()
        # if action.text() == ButtonNames.RUN.value:
        #     print('<Run> handler')
        #     self.run_btn_clicked.emit()



