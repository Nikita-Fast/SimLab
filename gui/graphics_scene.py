import importlib
import itertools
import os
import sys
from typing import Tuple, Dict, List

from gui.port_connection_line import PortConnectionLine
from gui.port_widget import PortWidget
from modules.general import mediator
from qt import *
from gui.module_widget import ModuleWidget
from gui.port_connection_status import ConnectionStatus
import networkx as nx
import json


class GraphicsScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_port = None

    @Slot(ModuleWidget)
    def add_module_widget(self, widget):
        self.addItem(widget)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.choose_ports_pair_for_connection(event.scenePos())
        super().mousePressEvent(event)

    def choose_ports_pair_for_connection(self, mouse_press_pos):
        # Выбор двух портов для их соединения. Проверка возможности соединения выбранных портов.
        # В случае успешного прохождения проверки, создание объекта соединения и добавление его на сцену
        for item in self.items(mouse_press_pos):
            if isinstance(item, PortWidget):
                other_port = item
                if not other_port.is_connected:
                    if self.selected_port is None:
                        self.selected_port = other_port
                        self.selected_port.is_selected = True
                        self.selected_port.enable_highlight()
                    else:
                        if self.selected_port != other_port:

                            if self.connection_status(self.selected_port,
                                                      other_port) == ConnectionStatus.VALID_LINE:
                                connection = PortConnectionLine(self.selected_port, other_port)
                                self.addItem(connection)

                            if self.connection_status(self.selected_port,
                                                      other_port) == ConnectionStatus.VALID_LOOP:
                                self.create_loop_type_connection(other_port)

                            self.selected_port.is_selected = False
                            self.selected_port.disable_highlight()
                            self.selected_port = None

    def create_loop_type_connection(self, other_port: PortWidget):
        mediator_widget = ModuleWidget(mediator)
        self.add_module_widget(mediator_widget)
        mediator_input_port, _ = mediator_widget.inputs[0]
        mediator_output_port, _ = mediator_widget.outputs[0]
        c1 = PortConnectionLine(self.selected_port, mediator_input_port)
        c2 = PortConnectionLine(mediator_output_port, other_port)
        self.addItem(c1)
        self.addItem(c2)

    @staticmethod
    def connection_status(source_port: PortWidget, dst_port: PortWidget) -> ConnectionStatus:
        # Проверяет могут ли два порта быть соединены

        is_valid = True
        # Один из портов None
        if source_port is None or dst_port is None:
            return ConnectionStatus.NON_VALID

        # соединение из порта в себя же
        if source_port == dst_port:
            return ConnectionStatus.NON_VALID
        source_module: ModuleWidget = source_port.parentItem()
        dst_module: ModuleWidget = dst_port.parentItem()

        # соединение стартует из входа
        if source_port in [port for port, _ in source_module.inputs]:
            return ConnectionStatus.NON_VALID
        # соединение оканчивается в выходе
        if dst_port in [port for port, _ in dst_module.outputs]:
            return ConnectionStatus.NON_VALID

        if source_module == dst_module:
            # блок посредник не может создать новую петлю
            if source_module.module.name == mediator.name:
                return ConnectionStatus.NON_VALID
            else:
                return ConnectionStatus.VALID_LOOP
        else:
            return ConnectionStatus.VALID_LINE

    def prepare_flow_graph(self) -> Tuple[List[ModuleWidget], Dict]:
        # Даёт каждому module_widget на сцене свой уникальный id от 0 до n-1, где n - число виджетов
        # сохраняем виджеты в список в порядке роста id.
        # В виде словаря сохраняет информацию об исходящих соединениях каждого module_widget

        def get_port_number(port: PortWidget):
            module: ModuleWidget = port.parentItem()
            for i, (p_out, p_in) in enumerate(itertools.zip_longest(module.outputs, module.inputs)):
                if p_out and port == p_out[0]:
                    return i
                if p_in and port == p_in[0]:
                    return i

        module_widgets = [item for item in self.items() if isinstance(item, ModuleWidget)]

        connections = {}
        for module_id, module in enumerate(module_widgets):
            block_outgoing_connections_info = []
            for output_port_id, (output, _) in enumerate(module.outputs):
                output: PortWidget

                connection_info = {
                    "src_output_port_id": output_port_id,
                    "is_connected": False,
                    "dst_module_id": None,
                    "dst_input_port_id": None
                }

                if output.is_connected:
                    connection_info['is_connected'] = True
                    connection: PortConnectionLine = output.connection
                    connection_info['dst_input_port_id'] = get_port_number(connection.dst_port)
                    dst_module = connection.dst_port.parentItem()
                    connection_info['dst_module_id'] = module_widgets.index(dst_module)

                block_outgoing_connections_info.append(connection_info)
            connections[module_id] = block_outgoing_connections_info

        with open('./code_gen/connections.json', 'w') as file:
            json.dump(connections, file)

        return module_widgets, connections

    # def create_connection_graph(self) -> Dict:
    #     def get_port_number(port: PortWidget):
    #         module: ModuleWidget = port.parentItem()
    #         for i, (p_out, p_in) in enumerate(itertools.zip_longest(module.outputs, module.inputs)):
    #             if p_out and port == p_out[0]:
    #                 return i
    #             if p_in and port == p_in[0]:
    #                 return i
    #
    #     connection_graph = nx.MultiDiGraph()
    #
    #     module_widgets = [i for i in self.items() if isinstance(i, ModuleWidget)]
    #
    #     module_to_vertex = {m: str(i) for i, m in enumerate(module_widgets)}
    #     connection_graph.add_nodes_from(list(module_to_vertex.values()))
    #
    #     for m in module_widgets:
    #         for output, _ in m.outputs:
    #             output: PortWidget
    #             if output.is_connected:
    #                 connection: PortConnectionLine = output.connection
    #
    #                 src_port_num = get_port_number(connection.source_port)
    #                 dst_port_num = get_port_number(connection.dst_port)
    #                 dst_module = connection.dst_port.parentItem()
    #                 u = module_to_vertex[m]
    #                 v = module_to_vertex[dst_module]
    #                 connection_graph.add_edge(u, v, output_num=src_port_num, input_num=dst_port_num)
    #
    #     nx.drawing.nx_pydot.write_dot(connection_graph, 'code_gen/connection_graph.dot')
    #
    #     return {'graph': connection_graph, 'module_to_vertex': module_to_vertex}

    def save_model_to_json(self):
        modules = [item for item in self.items() if isinstance(item, ModuleWidget)]
        module_to_number = {m: i for i, m in enumerate(modules)}

        connections = [item for item in self.items() if isinstance(item, PortConnectionLine)]
        with open('saved_model.json', 'w') as file:
            model = {}
            model['modules'] = {}
            for m, i in module_to_number.items():
                m: ModuleWidget
                f = m.module.__file__
                module_dir = os.path.dirname(f)
                import_name = os.path.splitext(f)[0].split('/')[-1]
                import_path = module_dir[module_dir.find('modules'):].replace('/', '.')

                d = {}
                d['module_number'] = i
                d['descriptor_file'] = import_path, import_name
                d['scene_pos'] = m.scenePos().x(), m.scenePos().y()
                d['bounding_rect_size'] = m.bounding_rect.size().width(), m.bounding_rect.size().height()
                model['modules'][i] = d

            model['connections'] = []
            for c in connections:
                src_port = c.source_port
                dst_port = c.dst_port
                src_port_number = src_port.get_descriptor_based_serial_number()
                dst_port_number = dst_port.get_descriptor_based_serial_number()
                src_module_number = module_to_number[src_port.parentItem()]
                dst_module_number = module_to_number[dst_port.parentItem()]
                model['connections'].append((src_module_number, src_port_number, dst_module_number, dst_port_number))

            json.dump(model, file)

    def load_model_from_json(self):
        with open('saved_model.json', 'r') as file:
            number_to_module = {}
            model = json.load(file)
            for dct in model['modules'].values():
                module_number = dct['module_number']
                path, name = dct['descriptor_file']
                descriptor = importlib.import_module(f'.{name}', path)
                module_widget = ModuleWidget(descriptor)

                self.add_module_widget(module_widget)

                w, h = dct['bounding_rect_size']
                module_widget.bounding_rect.setSize(QSizeF(w, h))
                x, y = dct['scene_pos']
                module_widget.setPos(x, y)
                module_widget.recalculate_rects()

                number_to_module[module_number] = module_widget

            for c in model['connections']:
                src_module_num, src_port_num, dst_module_num, dst_port_num = c

                src_port = number_to_module[src_module_num].get_port_by_serial_number('output', src_port_num)
                dst_port = number_to_module[dst_module_num].get_port_by_serial_number('input', dst_port_num)

                connection = PortConnectionLine(src_port, dst_port)
                self.addItem(connection)
