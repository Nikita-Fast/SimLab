import numpy as np
from bin_gen_gui import BinGenGUI


# Это модуль-функция
def gen_binary_data(bits_num: int):
    return list(np.random.randint(low=0, high=2, size=bits_num))


name = "Binary Generator"
language = "Python"

module_type = 'function'
entry_point = gen_binary_data

# bits_num = 8

output_ports = [
    {
        "label": "Выход"
    },
]

gui = BinGenGUI()
