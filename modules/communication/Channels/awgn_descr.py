# Это модуль-класс
from modules.communication.Channels.awgn import AWGNChannel

name = "AWGNChannel"
language = "Python"

# module_type :: 'class' | 'function'
module_type = 'class'
module_class = AWGNChannel
# основная функция, выполняющая работу модуля
entry_point = AWGNChannel.process

input_ports = [
    {
        "label": "Символы"
    },
]

# "f" указывает с помощью какой функции вычисляется результат соответствующего выходного порта
# если "f" не указана, то используется значение из поля entry_point т.е. f = entry_point
# "inputs" указывает с каких входов брать аргументы для f. Если входы не уазаны, то берутся первые k,
# где k это кол-во аргументов функции f
output_ports = [
    {
        "label": "noised",
        # "f": AWGNChannel.process,
        # "inputs": [0]
    },
    # {
    #     "label": "Var(N)",
    #     "f": AWGNChannel.calc_noise_variance,
    #     # "inputs": []
    # },
]

# кодогенератор и интерпретатор сгенерированного кода может смотреть значения параметров прямо в дескрипторе
# т.к пока через GUI нельзя передать параметры, то все параметры берутся из дескриптора
information_bits_per_symbol = 4
ebn0_db = 12

module_parameters = [
    {
        'name': 'information_bits_per_symbol',
        'type': int,
        'has_default_value': True,
        'default_value': 2,
        'validator': None
    }
]