import json
import pickle

from code_gen.model_executor import ModelExecutor
from gui.module_widget import ModuleWidget
from gui.progress_bar import ProgressBar
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
        self.modules_on_model = []
        self.executor = None
        self.setWindowTitle('Simlab')

        self.tool_bar = ToolBar(self)
        self.addToolBar(self.tool_bar)
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(StatusBar(self))
        self.setCentralWidget(GraphicsView(GraphicsScene(self), self))

        self.progress_bar = ProgressBar(self)
        self.statusBar().addPermanentWidget(self.progress_bar, 1)

        self.modules_dock_widget = QDockWidget(self)
        self.modules_dock_widget.setWidget(ModulesTree(self))
        self.modules_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.modules_dock_widget)
        self.modules_dock_widget.widget().scanning()

        self.output_dock_widget = QDockWidget(self)
        self.output_dock_widget.setWidget(QTextBrowser(self))
        self.output_dock_widget.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.output_dock_widget)

        self.modules_dock_widget.widget().module_double_clicked.connect(self.centralWidget().scene().add_module_widget)
        self.tool_bar.generate_code_btn_clicked.connect(self.generate_code_helper)
        # self.tool_bar.run_code_btn_clicked.connect(run_modelling_code)
        self.tool_bar.run_code_btn_clicked.connect(self.code_runner_helper)

        self.tool_bar.save_model_btn_clicked.connect(self.centralWidget().scene().save_model_to_json)
        self.tool_bar.load_model_btn_clicked.connect(self.centralWidget().scene().load_model_from_json)

        self.show()

    def code_runner_helper(self):
        if len(self.modules_on_model) > 0 and all(m.is_setup_correctly for m in self.modules_on_model):
            threads_number = self.menuBar().threads_number
            min_ebn0_db = self.menuBar().min_ebn0_db
            max_ebn0_db = self.menuBar().max_ebn0_db

            # ebn0_points = max_ebn0_db - min_ebn0_db + 1
            ebn0_points = 12

            self.executor = ModelExecutor(threads_number, self.output_dock_widget.widget())
            self.progress_bar.setMaximum(ebn0_points * threads_number)
            self.progress_bar.setValue(0)
            self.executor.process_completes_iteration.connect(self.progress_bar.setValue)
            self.executor.execute()
        else:
            print('Can not run model that not setup correctly')

    def generate_code_helper(self):
        module_widget_list, _ = self.centralWidget().scene().prepare_flow_graph()
        self.modules_on_model = module_widget_list

        m: ModuleWidget
        if len(self.modules_on_model) > 0 and all(m.is_setup_correctly for m in self.modules_on_model):
            module_id_to_module_params = {
                i: m.extract_params_from_gui()
                for i, m in enumerate(self.modules_on_model)
            }
            with open("./code_gen/module_params.txt", 'wb') as param_file:
                pickle.dump(module_id_to_module_params, param_file)

            threads_number = self.menuBar().threads_number
            run_test_code_generation2(self.modules_on_model, threads_number)
        else:
            print('Can not generate code for model that not setup correctly')
