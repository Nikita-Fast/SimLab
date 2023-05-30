from typing import List

from utils.custom_exceptions import SourceModuleRunOutOfDataException


class EbN0dbModule:
    def __init__(self, ebn0_db_list: List):
        self.range_iterator = iter(ebn0_db_list)

    def next(self):
        # Пусть модули источники генерируют/выдают данные пока могут.
        # Когда данные заканчиваются, модуль кидает специальное исключение.
        # Это позволит выполнять нужное кол-во итераций моделирования
        try:
            return next(self.range_iterator)
        except StopIteration as e:
            raise SourceModuleRunOutOfDataException(self)


name = "Eb/N0"
language = "Python"

module_type = 'class'
module_class = EbN0dbModule
entry_point = EbN0dbModule.next

output_ports = [
    {
        "label": "Value",
        "type": int
    }
]


module_parameters = [
    {
        'name': 'ebn0_db_list',
        'type': List[int],
        'has_default_value': True,
        "default_value": list(range(1, 13)),
        'validator': lambda x: isinstance(x, list) and len(x) > 0 and all(isinstance(v, int) for v in x)
    }
]