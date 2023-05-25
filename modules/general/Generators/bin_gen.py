from typing import List

import numpy as np
from bin_gen_gui import BinGenGUI


# Это модуль-функция
def gen_binary_data(bits_num: int = 16):
    return list(np.random.randint(low=0, high=2, size=bits_num))


name = "Binary Generator"
language = "Python"

module_type = 'function'
entry_point = gen_binary_data

bits_num = 8

output_ports = [
    {
        "label": "Выход",
        "type": List[int]
    },
]

# gui = BinGenGUI()

module_parameters = [
    {
        'name': 'bits_num',
        'type': int,
        'has_default_value': True,
        'default_value': 12,
        'validator': lambda x: isinstance(x, int) and (0 < x < 1_000_000_000)
    }
]