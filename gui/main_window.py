from qt import *

from gui.menu_bar import MenuBar
from gui.status_bar import StatusBar
from gui.tool_bar import ToolBar
from gui.graphics_scene import GraphicsScene
from gui.graphics_view import GraphicsView
from gui.modules_tree import ModulesTree

from code_gen.basic import run_test_code_generation2


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simlab')

        self.tool_bar = ToolBar(self)
        self.addToolBar(self.tool_bar)
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(StatusBar(self))
        self.setCentralWidget(GraphicsView(GraphicsScene(self), self))

        self.modules_dock_widget = QDockWidget(self)
        self.modules_dock_widget.setWidget(ModulesTree(self))

        self.addDockWidget(Qt.LeftDockWidgetArea, self.modules_dock_widget)
        self.modules_dock_widget.widget().scanning()

        self.modules_dock_widget.widget().module_double_clicked.connect(self.centralWidget().scene().add_module_widget)
        self.tool_bar.generate_code_btn_clicked.connect(self.helper)
        self.tool_bar.model_graph_btn_clicked.connect(self.centralWidget().scene().create_connection_graph)

        self.show()

    def helper(self):
        dct = self.centralWidget().scene().create_connection_graph()
        # run_test_code_generation2(dct['graph'], dct['module_to_vertex'])
        run_test_code_generation2(dct['module_to_vertex'])
