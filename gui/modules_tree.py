from qt import *
import os
import sys
import inspect

from gui.module_descriptor_tree import descriptor
from gui.module_widget import ModuleWidget
from gui.modules_tree_item import ModulesTreeItem


class ModulesTree(QTreeWidget):
    module_double_clicked = Signal(ModuleWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = "./modules"
        self.itemDoubleClicked.connect(self.item_double_clicked)

    def set_path(self, path):
        self.path = path
        self.clear()
        self.scanning()

    def scanning(self):
        for root, dirs, files in os.walk(self.path):
            sys.path.append(root)
            for f in files:
                try:
                    module_name = os.path.splitext(f)[0]
                    module = __import__(module_name)
                    if ModulesTree.is_module(module):
                        self.add_module(root, module)
                except Exception as e:
                    pass
            del sys.path[-1]

    def add_module(self, module_dir, module):
        dirs = module_dir.split("/")
        current_itm = self.topLevelItem(0)
        for d in dirs:
            if d == ".":
                continue
            if current_itm is None:
                self.addTopLevelItem(ModulesTreeItem(d))
                current_itm = self.topLevelItem(self.topLevelItemCount() - 1)
                continue
            if current_itm.text(0) == d:
                continue
            for i in range(current_itm.childCount()):
                if current_itm.child(i).text(0) == d:
                    current_itm = current_itm.child(i)
                    break
            else:
                current_itm.addChild(ModulesTreeItem(d))
                current_itm = current_itm.child(current_itm.childCount() - 1)

        module_item = ModulesTreeItem(module.name)
        module_item.setData(0, Qt.UserRole, module)
        current_itm.addChild(module_item)

    @staticmethod
    def is_module(module):
        return descriptor.validate(dict(inspect.getmembers(module)))

    @Slot(QTreeWidgetItem, int)
    def item_double_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(column, Qt.UserRole)
        if data is not None:
            self.module_double_clicked.emit(ModuleWidget(data))