from qt import *


class GeneratedModuleGUI(QWidget):
    def __init__(self, module_param_names, descriptor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_names = module_param_names
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

    def _create_general_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        for p_name in self.param_names:
            self.__dict__[p_name] = 'PARAM_NOT_SET'

            line_edit = QLineEdit(tab)
            self._color_line_edit_to_red(line_edit)

            line_edit.editingFinished.connect(self.simple_handler)

            layout.addRow(p_name, line_edit)
            self.__dict__[f'{p_name}_line_edit'] = line_edit

            # self.bits_num = 'PARAM_NOT_SET'
            # self.bits_num_line_edit = QLineEdit(tab)
            # self.bits_num_range = range(1, 1_000_000_000)

            # self._color_bits_num_line_edit_to_red()

            # self.bits_num_line_edit.editingFinished.connect(self.process_bits_num_input)
            #
            # layout = QFormLayout(tab)
            # layout.addRow('Bits Number', self.bits_num_line_edit)
        return tab

    def simple_handler(self):
        for p_name in self.param_names:
            line_edit: QLineEdit = self.__dict__.get(f'{p_name}_line_edit')
            text = line_edit.text()

            # todo как парсить текст?
            def parse(data):
                return data

            value = parse(text)

            # todo валидация значения
            def is_valid(val):
                if val != '':
                    return True
                return False

            if is_valid(value):
                self.__dict__[p_name] = value
                self._color_line_edit_to_green(line_edit)
            else:
                self.__dict__[p_name] = 'PARAM_NOT_SET'
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

    # def process_bits_num_input(self):
    #     try:
    #         bits_num = int(self.bits_num_line_edit.text())
    #         if self.bits_num_range.start <= bits_num <= self.bits_num_range.stop:
    #             self.bits_num = bits_num
    #             self._color_bits_num_line_edit_to_green()
    #         else:
    #             raise ValueError()
    #     except ValueError as e:
    #         self.bits_num = 'PARAM_NOT_SET'
    #         self.bits_num_line_edit.clear()
    #         self._color_bits_num_line_edit_to_red()

    # def get_param_values(self):
    #     parameter_is_set = self.bits_num is not None
    #     return {'bits_num': {'param_is_set': parameter_is_set, 'param_value': self.bits_num}}
