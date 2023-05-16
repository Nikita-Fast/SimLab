from qt import *


class ModulesTreeItem(QTreeWidgetItem):
    
    def __init__(self, name):
        super().__init__()
        self.setText(0, name)