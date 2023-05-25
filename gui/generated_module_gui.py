import ast
from typing import Dict
import typeguard

from qt import *


class GeneratedModuleGUI(QWidget):
    def __init__(self, module_params_info, descriptor, input_ports_info, output_ports_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params_info: Dict = module_params_info
        self.descriptor = descriptor
        self.input_ports_info = input_ports_info
        self.output_ports_info = output_ports_info
        self._init_gui()

    def _init_gui(self):
        self.setWindowTitle(f'Properties: {self.descriptor.name}')
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget(self)
        tab_widget.addTab(self._create_general_tab(), 'General')
        tab_widget.addTab(self._create_advanced_tab(), 'Advanced')
        tab_widget.addTab(self._create_documentation_tab(self.descriptor), 'Documentation')

        layout.addWidget(tab_widget)
        layout.addWidget(self._create_ports_widget())

        self.simple_handler()

    def _create_ports_widget(self):
        ports_info_widget = QTextBrowser(self)
        ports_info_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))

        lines = ['Ports connection status:']
        lines.append("Input Ports:")
        for input_port_info in self.input_ports_info:
            i = input_port_info["number"]
            label = input_port_info["label"]
            type = self._param_type_to_str(input_port_info["type"])
            lines.append(f"\t{label}({i}) of {type}")

        lines.append("Output Ports:")
        for output_port_info in self.output_ports_info:
            i = output_port_info["number"]
            label = output_port_info["label"]
            type = self._param_type_to_str(output_port_info["type"])
            lines.append(f"\t{label}({i}) of {type}")

        ports_info_widget.setText('\n'.join(lines))

        return ports_info_widget

    def _create_general_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        for p_info in self.params_info:
            p_name = p_info['name']
            self.__dict__[p_name] = 'PARAM_NOT_SET'

            line_edit = QLineEdit(tab)

            # Если предоставлено значение по умолчанию, то выставляем его
            if p_info['has_default_value']:
                default_value = p_info['default_value']
                line_edit.setText(f'{default_value}')
                self._color_line_edit_to_green(line_edit)
            else:
                self._color_line_edit_to_red(line_edit)

            line_edit.editingFinished.connect(self.simple_handler)

            # param_type = p_info['type'].__name__ if type(p_info['type']) == type else p_info['type']._name
            # row_name = f"{p_name}: {param_type}"

            # p_type_str = str(p_info['type'])
            p_type_str = self._param_type_to_str(p_info['type'])

            row_name = f"{p_name}: {p_type_str}"
            layout.addRow(row_name, line_edit)
            self.__dict__[f'{p_name}_line_edit'] = line_edit

        return tab

    def _param_type_to_str(self, param_type):
        p_type_str = str(param_type)
        p_type_str = p_type_str.replace('<class ', '')
        p_type_str = p_type_str.replace('>', '')
        p_type_str = p_type_str.replace("'", '')
        p_type_str = p_type_str.replace("typing.", '')
        return p_type_str


    def simple_handler(self):
        for p_info in self.params_info:
            p_name = p_info['name']
            line_edit: QLineEdit = self.__dict__.get(f'{p_name}_line_edit')
            text = line_edit.text()

            def parse(data):
                try:
                    return ast.literal_eval(data)
                except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as e:
                    return ''

            value = parse(text)

            # валидация значения
            def is_valid(value):
                try:
                    typeguard.check_type(value, p_info['type'])
                except typeguard.TypeCheckError:
                    return False

                if validator := p_info.get('validator'):
                    if type(validator).__name__ == 'class':
                        if not validator.is_valid(value):
                            return False
                    if type(validator).__name__ == 'function':
                        if not validator(value):
                            return False

                if value == '':
                    return False
                return True

            if is_valid(value):
                self.__dict__[p_name] = value
                self._color_line_edit_to_green(line_edit)
            else:
                if p_info['has_default_value']:
                    default_value = p_info['default_value']

                    if isinstance(default_value, str):
                        default_value = f"'{default_value}'"

                    # todo проверка типа для default_value
                    self.__dict__[p_name] = default_value

                    line_edit.setText(f'{default_value}')
                    self._color_line_edit_to_green(line_edit)
                else:
                    self.__dict__[p_name] = 'PARAM_NOT_SET'
                    line_edit.clear()
                    self._color_line_edit_to_red(line_edit)

    def _color_line_edit_to_red(self, line_edit: QLineEdit):
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor.fromRgb(242, 115, 46, a=200))
        line_edit.setPalette(palette)

    def _color_line_edit_to_green(self, line_edit: QLineEdit):
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor.fromRgb(131, 242, 142, a=200))
        line_edit.setPalette(palette)

    def _create_advanced_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        return tab

    def _create_documentation_tab(self, descriptor):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        documentation_text = f'{descriptor.name} module has no documentation.'
        documentation_browser = QTextBrowser(tab)
        documentation_browser.setText(documentation_text)
        layout.addWidget(documentation_browser)
        return tab

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.rect().contains(event.pos()):
            self.close()
            # self.releaseMouse()

