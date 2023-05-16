import numpy as np


# Это модуль-функция
def gen_binary_data(bits_num: int):
    return list(np.random.randint(low=0, high=2, size=bits_num))


name = "Binary Generator"
language = "Python"

module_type = 'function'
# module_class = None
entry_point = gen_binary_data

# input_ports = [
#
# ]

bits_num = 25

output_ports = [
    {
        "label": "Выход"
    },
]