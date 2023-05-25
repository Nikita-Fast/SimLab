import ast
from typing import Dict
import typeguard

from qt import *


class GeneratedModuleGUI(QWidget):
    def __init__(self, module_params_info, descriptor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params_info: Dict = module_params_info
        self.descriptor = descriptor
        self._init_gui()

    def _init_gui(self):
        self.setWindowTitle(f'Properties: {self.descriptor.name}')
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget(self)
        tab_widget.addTab(self._create_general_tab(), 'General')
        tab_widget.addTab(self._create_advanced_tab(), 'Advanced')
        tab_widget.addTab(self._create_documentation_tab(self.descriptor), 'Documentation')

        ports_info_widget = QTextBrowser(self)
        ports_info_widget.setText('Ports connection status:')

        ports_info_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))

        layout.addWidget(tab_widget)
        layout.addWidget(ports_info_widget)

        self.simple_handler()

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

            param_type = p_info['type'].__name__ if type(p_info['type']) == type else p_info['type']._name

            row_name = f"{p_name}: {param_type}"
            layout.addRow(row_name, line_edit)
            self.__dict__[f'{p_name}_line_edit'] = line_edit

        return tab

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

            # todo валидация значения
            def is_valid(val):
                try:
                    typeguard.check_type(val, p_info['type'])
                except typeguard.TypeCheckError:
                    return False

                if val == '':
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
            self.releaseMouse()
