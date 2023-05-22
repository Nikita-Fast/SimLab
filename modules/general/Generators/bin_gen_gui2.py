from qt import *


class BinGenGUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_gui()

    def _init_gui(self):
        self.setWindowTitle('Properties: Binary Generator')
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget(self)
        tab_widget.addTab(self._create_general_tab(), 'General')
        tab_widget.addTab(self._create_advanced_tab(), 'Advanced')
        tab_widget.addTab(self._create_documentation_tab(), 'Documentation')

        ports_info_widget = QTextBrowser(self)
        ports_info_widget.setText('Ports connection status:')

        ports_info_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))

        layout.addWidget(tab_widget)
        layout.addWidget(ports_info_widget)

    def _create_general_tab(self):
        tab = QWidget()
        self.bits_num = None
        self.bits_num_line_edit = QLineEdit(tab)
        self.bits_num_range = range(1, 1_000_000_000)

        palette = QPalette()
        palette.setColor(QPalette.Base, QColor.fromRgb(242, 115, 46, a=200))
        self.bits_num_line_edit.setPalette(palette)

        self.bits_num_line_edit.editingFinished.connect(self.process_bits_num_input)

        layout = QFormLayout(tab)
        layout.addRow('Bits Number', self.bits_num_line_edit)
        return tab

    def _color_bits_num_line_edit_to_green(self):
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor.fromRgb(131, 242, 142, a=200))
        self.bits_num_line_edit.setPalette(palette)

    def _color_bits_num_line_edit_to_red(self):
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor.fromRgb(242, 115, 46, a=200))
        self.bits_num_line_edit.setPalette(palette)

    def _create_advanced_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        return tab

    def _create_documentation_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        documentation_text = """Binary Generator module can generate specified number of bits."""
        documentation_browser = QTextBrowser(tab)
        documentation_browser.setText(documentation_text)
        layout.addWidget(documentation_browser)
        return tab

    def process_bits_num_input(self):
        try:
            bits_num = int(self.bits_num_line_edit.text())
            if self.bits_num_range.start <= bits_num <= self.bits_num_range.stop:
                self.bits_num = bits_num
                self._color_bits_num_line_edit_to_green()
            else:
                raise ValueError()
        except ValueError as e:
            self.bits_num = None
            self.bits_num_line_edit.clear()
            self._color_bits_num_line_edit_to_red()
        print(self.bits_num)

    def get_param_values(self):
        parameter_is_set = self.bits_num is not None
        return {'bits_num': {'param_is_set': parameter_is_set, 'param_value': self.bits_num}}
