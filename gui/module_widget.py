import inspect
import itertools

from gui.generated_module_gui import GeneratedModuleGUI
from gui.marquee_label import MarqueeLabelProxyWidget
from gui.module_descriptor import ModuleDescriptor
from qt import *
from typing import Optional, List, Any
import math
from gui.port_widget import PortWidget


class ModuleWidget(QGraphicsItem):
    __TOP_LEFT = 0
    __TOP_RIGHT = 1
    __BOTTOM_LEFT = 2
    __BOTTOM_RIGHT = 3

    def __init__(self, module):
        super().__init__()
        self.module = module
        self.num_inputs = len(module.input_ports) if getattr(self.module, 'input_ports', None) else 0
        self.num_outputs = len(module.output_ports) if getattr(self.module, 'output_ports', None) else 0
        self._inputs = []
        self._outputs = []

        self.name_label = MarqueeLabelProxyWidget(self.module.name, self)

        self.bounding_rect = QRectF(0, 0, 275, 275)
        self.body_rect = None
        self.selection_rect: QRectF = None
        # Используются для изменения размеров модуля
        self.selection_corner_rects = None
        self.corner_size = 6
        self.min_bounding_rect_size = 2 * self.corner_size
        self.cursors = {
            self.__TOP_LEFT: Qt.SizeFDiagCursor,
            self.__TOP_RIGHT: Qt.SizeBDiagCursor,
            self.__BOTTOM_LEFT: Qt.SizeBDiagCursor,
            self.__BOTTOM_RIGHT: Qt.SizeFDiagCursor,
        }
        self.selected_corner = None
        self.setAcceptHoverEvents(True)
        self.setFlags(QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemSendsScenePositionChanges
                      | QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsFocusable
        )
        self.add_ports()
        self.recalculate_rects()
        self.gui = self.load_gui()
        self.setup_options_menu()

    def setup_options_menu(self):
        self.options_menu = QMenu()
        self.delete_action = QAction('Delete')
        self.delete_action.setIcon(QIcon(QPixmap('./resources/images/delete.png')))
        self.properties_action = QAction('Properties')
        self.properties_action.setIcon(QIcon(QPixmap('./resources/images/properties.png')))

        self.options_menu.addAction(self.delete_action)
        self.options_menu.addSeparator()
        self.options_menu.addAction(self.properties_action)

        # todo как используя QSizePolicy не хардкодить размер виджета?
        self.options_menu.setMaximumSize(130, 53)
        self.options_menu.triggered.connect(self.option_menu_triggered)

    def option_menu_triggered(self, action):
        if action == self.properties_action:
            self.gui.show()
        if action == self.delete_action:
            self.delete()

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        self._inputs = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    def get_port_by_serial_number(self, port_type: str, number: int):
        if port_type == 'input':
            inputs = [port for port, _ in self.inputs]
            if number < len(inputs):
                return inputs[number]
        if port_type == 'output':
            outputs = [port for port, _ in self.outputs]
            if number < len(outputs):
                return outputs[number]
        raise ValueError(f'Модуль {self.module.name} не имеет порта типа {port_type} с номером {number}')

    def delete(self):
        # удалить все входящие и исходящие соединения
        for port, _ in self.inputs + self.outputs:
            if port.is_connected:
                port.connection.delete()
        # удалить этот модуль со сцены
        self.scene().removeItem(self)

    def add_ports(self):
        # Создать порты и лейблы портов. Для портов с длинным названием создается бегущая текстовая строка
        inputs_iter = []
        outputs_iter = []
        if self.num_inputs > 0:
            inputs_iter = itertools.chain([(port_descr, self.inputs) for port_descr in self.module.input_ports])
        if self.num_outputs > 0:
            outputs_iter = itertools.chain([(port_descr, self.outputs) for port_descr in self.module.output_ports])
        for p, container in itertools.chain(inputs_iter, outputs_iter):
            port = PortWidget(self)

            if len(p["label"]) > 4:
                port_label = MarqueeLabelProxyWidget(p["label"], port)
            else:
                port_label = QGraphicsSimpleTextItem(parent=port)
                port_label.setText(p["label"])
                port_label.setTransformOriginPoint(port_label.boundingRect().center())

            container.append((port, port_label))

    def corner_rect_at(self, point):
        # Возвращает номер corner_rect-а, находящегося в указанной точке

        for i, rect in enumerate(self.selection_corner_rects):
            if rect.contains(point):
                return i
        return None

    def hoverMoveEvent(self, moveEvent):
        if self.isSelected():
            corner_rect_idx = self.corner_rect_at(moveEvent.pos())
            cursor = Qt.ArrowCursor if corner_rect_idx is None else self.cursors[corner_rect_idx]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def to_top_layer(self):
        # Вывести на передний план модуль

        self.setZValue(1)
        for item in self.childItems():
            item.setZValue(1)

    def out_of_top_layer(self):
        self.setZValue(0)
        for item in self.childItems():
            item.setZValue(0)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.isSelected():
            self.to_top_layer()
            self.draw_selection(painter)
        else:
            self.out_of_top_layer()
        painter.drawRect(self.body_rect)

        if not self.is_setup_properly():
            # нарисовать полупрозрачный цветной квадрат поверх модуля
            painter.fillRect(self.body_rect, QBrush(QColor(255, 112, 102, 128)))
            self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.delete()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # print(f'module mouse press')
        if event.button() == Qt.LeftButton:
            self.selected_corner = self.corner_rect_at(event.pos())
        if event.button() == Qt.RightButton:
            size = self.options_menu.size()
            self.options_menu.setGeometry(event.screenPos().x(), event.screenPos().y(), size.width(), size.height())
            self.options_menu.show()
        super(ModuleWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.selected_corner is not None:
            self.interactive_resize(event.pos())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.selected_corner = None
        super(ModuleWidget, self).mouseReleaseEvent(event)

    @staticmethod
    def projection_length(p0, p1, p2):
        # Находит длину проекции ветора p1p2 на вектор p0p1.
        # Результат будет отрицательным если получившаяся проекция направлена в противоположное p0p1 направление

        l1 = QLineF(p0, p1)
        l2 = QLineF(p1, p2)
        angle_deg = l2.angleTo(l1)
        angle_rad = angle_deg * math.pi / 180
        return l2.length() * math.cos(angle_rad)

    def get_bounding_rect_corner_pos(self, corner_rect: int):
        if corner_rect == self.__TOP_LEFT:
            return self.bounding_rect.topLeft()
        elif corner_rect == self.__TOP_RIGHT:
            return self.bounding_rect.topRight()
        elif corner_rect == self.__BOTTOM_LEFT:
            return self.bounding_rect.bottomLeft()
        elif corner_rect == self.__BOTTOM_RIGHT:
            return self.bounding_rect.bottomRight()
        else:
            raise ValueError("Передан неизвестный selection_corner_rect")

    def get_diag_corner_rect(self, corner_rect: int):
        # Для переданного corner_rect возвращает другой corner_rect, который находится с ним на одной диагонали

        if corner_rect == self.__TOP_LEFT:
            return self.__BOTTOM_RIGHT
        elif corner_rect == self.__TOP_RIGHT:
            return self.__BOTTOM_LEFT
        elif corner_rect == self.__BOTTOM_LEFT:
            return self.__TOP_RIGHT
        elif corner_rect == self.__BOTTOM_RIGHT:
            return self.__TOP_LEFT
        else:
            raise ValueError("Передан неизвестный selection_corner_rect")

    def resize(self, corner_rect, diag_corner_rect, mouse_pos):
        p0 = self.selection_corner_rects[diag_corner_rect].center()
        p1 = self.selection_corner_rects[corner_rect].center()
        projection_length = self.projection_length(p0, p1, mouse_pos)
        old_size = self.bounding_rect.width()
        new_size = old_size + projection_length
        new_size = max(new_size, self.min_bounding_rect_size)
        diff = new_size - old_size

        p = self.get_bounding_rect_corner_pos(corner_rect)
        p_diag = self.get_bounding_rect_corner_pos(diag_corner_rect)
        x_shifted = p.x() + diff * (-1 if p.x() < p_diag.x() else 1)
        y_shifted = p.y() + diff * (-1 if p.y() < p_diag.y() else 1)
        p_shifted = QPointF(x_shifted, y_shifted)
        top_left = QPointF(min(p_shifted.x(), p_diag.x()), min(p_shifted.y(), p_diag.y()))
        self.bounding_rect = QRectF(top_left, QSizeF(new_size, new_size))

    def interactive_resize(self, mouse_pos: QPointF):
        self.prepareGeometryChange()
        self.resize(
            self.selected_corner,
            self.get_diag_corner_rect(self.selected_corner),
            mouse_pos
        )
        self.recalculate_rects()

    def boundingRect(self) -> QRectF:
        return self.bounding_rect

    def draw_selection(self, painter: QPainter):
        pen = painter.pen()
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.selection_rect)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.fillRect(self.selection_corner_rects[0], Qt.black)
        painter.fillRect(self.selection_corner_rects[1], Qt.black)
        painter.fillRect(self.selection_corner_rects[2], Qt.black)
        painter.fillRect(self.selection_corner_rects[3], Qt.black)

    def recalculate_name_label(self):
        _, _, w, h = self.name_label.boundingRect().getRect()
        self.name_label.setPos(self.bounding_rect.center() - QPointF(w / 2, h / 2))
        scale = self.body_rect.width() / (2.5 * w)
        self.name_label.setScale(scale)

    def calculate_port_and_gap_size(self, num_ports):
        # Расчитываем размеры порта и вертикальное расстояние между портами

        # if not num_ports:
        #     raise ValueError('попытка расчета размеров портов при их отсутствии')
        h = self.body_rect.size().height()
        w = self.bounding_rect.size().width()
        port_height = h / (num_ports + (num_ports + 1) / 2)
        port_width = 0.2 * w
        gap_size = port_height / 2
        if port_height > 0.2 * h:
            port_height = 0.2 * h
            gap_space = h - port_height * num_ports
            gap_size = gap_space / (num_ports + 1)
        return port_width, port_height, gap_size

    def recalculate_label(self, label, port):
        x = port.rect().center().x() - label.boundingRect().width() / 2
        y = port.rect().center().y() - label.boundingRect().height() / 2
        label.setX(x)
        label.setY(y)
        label.boundingRect().setRect(x, y, port.rect().width(), port.rect().height())
        y_scale = 0.9 * port.rect().height() / label.boundingRect().height()
        x_scale = 0.9 * port.rect().width() / label.boundingRect().width()
        # todo лейблы не полностью используют горизонтальное пространство
        label.setScale(min(x_scale, y_scale))

    def recalculate_ports(self):
        port_width, port_height, gap_size = self.calculate_port_and_gap_size(self.num_inputs)
        for i, (input_port, label) in enumerate(self.inputs):
            input_port: QGraphicsRectItem
            label: QGraphicsSimpleTextItem

            y_offset = gap_size + i * (port_height + gap_size)
            input_port.setRect(
                self.body_rect.left(),
                self.body_rect.top() + y_offset,
                port_width,
                port_height
            )
            self.recalculate_label(label, input_port)

        port_width, port_height, gap_size = self.calculate_port_and_gap_size(self.num_outputs)
        for i, (output_port, label) in enumerate(self.outputs):
            output_port: QGraphicsRectItem
            label: QGraphicsSimpleTextItem

            y_offset = gap_size + i * (port_height + gap_size)
            output_port.setRect(
                self.body_rect.right() - port_width,
                self.body_rect.top() + y_offset,
                port_width,
                port_height
            )
            self.recalculate_label(label, output_port)

    # def recalculate_connections(self):
    #     for port, _ in self.inputs + self.outputs:
    #         if port.is_connected:
    #             port.connection.recalculate()

    def recalculate_rects(self):
        h = self.bounding_rect.height() * 0.8
        w = self.bounding_rect.width() * 0.8
        center = self.bounding_rect.center()
        self.body_rect = QRectF(center.x() - w / 2, center.y() - h / 2, w, h)

        self.recalculate_name_label()

        self.recalculate_ports()

        # self.recalculate_connections()

        center = self.bounding_rect.center()
        h = self.bounding_rect.height() * 0.9
        w = self.bounding_rect.width() * 0.9
        self.selection_rect = QRectF(center.x() - w / 2, center.y() - h / 2, w, h)

        x_left = self.selection_rect.x() - self.corner_size / 2
        x_right = self.selection_rect.x() + self.selection_rect.width() - self.corner_size / 2
        y_top = self.selection_rect.y() - self.corner_size / 2
        y_bottom = self.selection_rect.y() + self.selection_rect.height() - self.corner_size / 2

        self.selection_corner_rects = [None] * 4
        self.selection_corner_rects[self.__TOP_LEFT] = QRectF(x_left, y_top, self.corner_size, self.corner_size)
        self.selection_corner_rects[self.__TOP_RIGHT] = QRectF(x_right, y_top, self.corner_size, self.corner_size)
        self.selection_corner_rects[self.__BOTTOM_LEFT] = QRectF(x_left, y_bottom, self.corner_size, self.corner_size)
        self.selection_corner_rects[self.__BOTTOM_RIGHT] = QRectF(x_right, y_bottom, self.corner_size, self.corner_size)

    def are_all_input_ports_connected(self):
        for input_port_widget, _ in self.inputs:
            input_port_widget: PortWidget
            if not input_port_widget.is_connected:
                return False
        return True

    def are_all_output_ports_connected(self):
        for output_port_widget, _ in self.outputs:
            output_port_widget: PortWidget
            if not output_port_widget.is_connected:
                return False
        return True

    def are_all_ports_connected(self):
        return self.are_all_input_ports_connected() and self.are_all_output_ports_connected()

    def load_gui(self):
        # Если в дескрипторе указан готовый gui, то загужаем его
        if module_gui := self.module.__dict__.get('gui'):
            return module_gui
        # Иначе генерируем gui самостоятельно
        else:
            # module_param_names = self.get_param_names()
            return GeneratedModuleGUI(self.get_module_params(), self.module)

    def get_param_names(self):
        # todo убрать этот метод
        params_info = self.get_module_params()
        param_names = [p_info['name'] for p_info in params_info]

        return param_names

    def get_default_args(self, func):
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }

    def _derive_module_params(self):
        # Извлечем информацию о параметрах модуля анализируя конструктор модуля либо его главную функцию
        module_params = []
        f = None

        if self.module.module_type == 'class':
            f = self.module.module_class.__init__

        if self.module.module_type == 'function':
            f = self.module.entry_point

        param_names = inspect.getfullargspec(f).args
        param_default_values = self.get_default_args(f)
        params_type_annotation = inspect.getfullargspec(f).annotations

        # у метода класса параметр self заполняется автоматически
        if 'self' in param_names:
            param_names.remove('self')

        for p_name in param_names:
            param_dict = {
                'name': p_name,
                'type': params_type_annotation.get(p_name, Any),
                'has_default_value': p_name in param_default_values,
                'default_value': param_default_values.get(p_name),
                'validator': None
            }
            module_params.append(param_dict)

        # Если в дескрипторе явно присвоили параметру значение (bits_per_symbol=4),
        # то это будет значением по умолчанию [если значение по умолчанию не указано в более приоритетных местах:
        # сигнатуре функции(конструктора) или в специальном поле дескриптора module_parameters]
        for param_dict in module_params:
            p_name = param_dict['name']
            if param_dict.get('has_default_value', False) is False:
                if ((p_value := self.module.__dict__.get(p_name, 'PARAM_NOT_SET_IN_DESCRIPTOR')) !=
                        'PARAM_NOT_SET_IN_DESCRIPTOR'):
                    param_dict['has_default_value'] = True
                    param_dict['default_value'] = p_value

        # # пытаемся как-то учесть, что у модуля-функции часть параметров м.б. передана другими модулями
        # через соединения портов
        # input_port_number = len(self.module.__dict__.get('input_ports', []))
        return module_params

    def get_module_params(self):
        param_names = []
        derived_params = self._derive_module_params()
        specified_params = self.module.__dict__.get('module_parameters', [])

        def get_base_dict(parameter_name: str):
            return {
                'name': parameter_name,
                'type': Any,
                'has_default_value': False,
                'default_value': None,
                'validator': None
            }

        combined_params = {}
        for param_dict in [*specified_params, *derived_params]:
            p_name = param_dict['name']
            param_info = combined_params.get(p_name, get_base_dict(p_name))
            if param_info['type'] == Any:
                param_info['type'] = param_dict.get('type', Any)
            if param_info['has_default_value'] is False:
                param_info['has_default_value'] = param_dict.get('has_default_value', False)
            if param_info['default_value'] is None:
                param_info['default_value'] = param_dict.get('default_value', None)
            if param_info['validator'] is None:
                param_info['validator'] = param_dict.get('validator', None)

            if p_name not in combined_params:
                combined_params[p_name] = param_info

        return list(combined_params.values())

    def save_params_from_gui_to_descriptor(self, module_param_names: List[str]):
        module_gui = self.gui
        for p_name in module_param_names:
            # Если в gui у параметра выставлено валидное значение, то сохраняем его в дескриптор
            if (p_value := module_gui.__dict__.get(p_name, 'PARAM_NOT_SET')) != 'PARAM_NOT_SET':
                self.module.__dict__[p_name] = p_value
            # если значение не валидное, значит параметр в данный момент не имеет значения,
            # поэтому старое значение параметра должно быть удалено из дескриптора
            else:
                if p_name in self.module.__dict__:
                    del self.module.__dict__[p_name]

    def are_all_params_set_up(self):
        self.module: ModuleDescriptor
        module_param_names = self.get_param_names()

        # Перед проверкой, выкачиваем из gui в дескриптор значения установленных параметров
        self.save_params_from_gui_to_descriptor(module_param_names)

        for p_name in module_param_names:
            if p_value := self.module.__dict__.get(p_name, 'PARAM NOT SET') == 'PARAM NOT SET':
                return False
        return True

    def is_setup_properly(self):
        # Перед проверкой, выкачиваем из gui в дескриптор значения установленных параметров
        self.save_params_from_gui_to_descriptor(self.get_param_names())

        checks = [
            self.are_all_ports_connected,
            self.are_all_params_set_up
        ]

        return all(f() for f in checks)
