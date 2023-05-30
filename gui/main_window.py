from qt import *

from gui.menu_bar import MenuBar
from gui.status_bar import StatusBar
from gui.tool_bar import ToolBar
from gui.graphics_scene import GraphicsScene
from gui.graphics_view import GraphicsView
from gui.modules_tree import ModulesTree

from code_gen.basic import run_test_code_generation2, run_modelling_code, run_concurrently


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
        # self.tool_bar.run_code_btn_clicked.connect(run_modelling_code)
        self.tool_bar.run_code_btn_clicked.connect(self.code_runner_helper)

        self.tool_bar.save_model_btn_clicked.connect(self.centralWidget().scene().save_model_to_json)
        self.tool_bar.load_model_btn_clicked.connect(self.centralWidget().scene().load_model_from_json)

        self.show()

    def code_runner_helper(self):
        threads_number = self.menuBar().threads_number
        min_ebn0_db = self.menuBar().min_ebn0_db
        max_ebn0_db = self.menuBar().max_ebn0_db
        run_concurrently(threads_number, min_ebn0_db, max_ebn0_db)

    def helper(self):
        module_widget_list, _ = self.centralWidget().scene().prepare_flow_graph()
        run_test_code_generation2(module_widget_list)
