import os
from typing import List

import numpy as np


# Это модуль-функция
def gen_binary_data(bits_num):
    np.random.seed(os.getpid())
    data = list(np.random.randint(low=0, high=2, size=bits_num))
    return data


name = "Binary Generator"
language = "Python"
module_type = 'function'
entry_point = gen_binary_data

output_ports = [
    {
        "label": "Выход",
        "type": List[int]
    },
]
module_parameters = [
    {
        'name': 'bits_num',
        'type': int,
        'has_default_value': True,
        'default_value': 64_000,
        'validator': lambda x: isinstance(x, int) and (0 < x < 1_000_000_000)
    }
]