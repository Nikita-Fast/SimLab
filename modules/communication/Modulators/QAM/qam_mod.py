import numpy as np
import default_qam_constellations


def shifting(bit_list):
    out = 0
    for bit in bit_list:
        out = (out << 1) | bit
    return out


def bits_to_ints(bits, bits_per_int):
    i = 0
    symbols = np.empty(len(bits) // bits_per_int, dtype=int)
    k = 0
    while i < len(bits):
        symbols[k] = shifting(bits[i:i + bits_per_int])
        i += bits_per_int
        k += 1
    return symbols


def gray_codes(bits_per_symbol: int):
    if bits_per_symbol % 2 != 0:
        raise Exception("Генерация кодов Грея для нечетного bits_per_symbol ещё не реализована")
    order = 2 ** bits_per_symbol
    codes = []
    for i in range(order):
        codes.append(i ^ (i >> 1))

    length = int(np.sqrt(order))
    for i in range(length):
        if i % 2 == 1:
            start = i * length
            end = (i + 1) * length
            codes[start:end] = codes[start:end][::-1]
    return codes


def sort_constellation_points(complex_numbers):
    return sorted(complex_numbers, key=lambda x: (-x.imag, x.real))


class QAMModulator:
    """Класс описывающий КАМ модулятор"""

    def __init__(self, bits_per_symbol: int, constellation=None):
        self.bits_per_symbol = bits_per_symbol
        self.constellation = constellation
        if constellation is None:
            self.constellation = default_qam_constellations.get_qam_constellation[bits_per_symbol]

    def execute(self, bits):
        if len(bits) % self.bits_per_symbol != 0:
            diff = len(bits) % self.bits_per_symbol
            r = self.bits_per_symbol - diff
            # добавить r нулей в конец списка битов
            data = np.pad(bits, (0, r), 'constant')

        ints = bits_to_ints(bits, self.bits_per_symbol)
        return list(self.constellation[ints])


name = "QAM Modulator"
language = "Python"

# module_type :: 'class' | 'function'
module_type = 'class'
module_class = QAMModulator
# основная функция, выполняющая работу модуля
entry_point = QAMModulator.execute

input_ports = [
    {
        "label": "bits"
    },
]

# "f" указывает с помощью какой функции вычисляется результат соответствующего выходного порта
# если "f" не указана, то используется значение из поля entry_point т.е. f = entry_point
# "inputs" указывает с каких входов брать аргументы для f. Если входы не уазаны, то берутся первые k,
# где k это кол-во аргументов функции f
output_ports = [
    {
        "label": "symbols",
    },
]

# кодогенератор и интерпретатор сгенерированного кода может смотреть значения параметров прямо в дескрипторе
# т.к пока через GUI нельзя передать параметры, то все параметры берутся из дескриптора

bits_per_symbol = 4
