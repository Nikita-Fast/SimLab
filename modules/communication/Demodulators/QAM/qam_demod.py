import numpy as np

from modules.communication.Modulators.QAM import default_qam_constellations
from modules.communication.Modulators.QAM.qam_mod import QAMModulator


class QAMDemodulator:

    def __init__(self, bits_per_symbol, constellation=None, mode='hard'):
        self.bits_per_symbol = bits_per_symbol
        self.constellation = constellation
        self.mode = mode
        if constellation is None:
            self.constellation = default_qam_constellations.get_qam_constellation[bits_per_symbol]

    def process(self, data: np.ndarray, noise_variance=None) -> np.ndarray:
        if self.mode == 'hard':
            return self.demodulate_hard(data)
        elif self.mode == 'soft':
            # как посчитать дисперсию шума?
            raise Exception('not implemented')
            return self.demodulate_soft(data, noise_variance)
        else:
            raise ValueError("У демодулятора есть только два режима работы: 'hard' и 'soft'")

    @classmethod
    def from_qam_modulator(cls, qam_modulator: QAMModulator, mode='hard'):
        return cls(qam_modulator.bits_per_symbol, qam_modulator.constellation, mode)

    def get_special_constellation_points(self, bit_value, bit_num):
        """Получить точки созвездия, у которых бит с номером bit_num имеет значение равное bit_value"""
        points = []
        for i in range(len(self.constellation)):
            mask = 1 << bit_num
            if i & mask == bit_value << bit_num:
                points.append(self.constellation[i])
        return points

    def _ints_to_bits(self, ints):
        """Конвертирует массив int-ов в их битовое представление, за количество битов, выделяемых
        на каждый int отвечает поле bits_per_symbol."""
        b_len = self.bits_per_symbol
        if b_len > 16:
            raise Exception("Используется модуляция слишком высокого порядка. Поддерживаются только те, что "
                            "кодируют символ числом бит не превосходящим 16")
        if b_len > 8:
            bits = np.unpackbits(ints.astype(">u2").view("u1"))
            mask = np.tile(np.r_[np.zeros(16 - b_len, int), np.ones(b_len, int)], len(ints))
            return bits[np.nonzero(mask)]
        else:
            bits = np.unpackbits(ints.astype(np.uint8))
            mask = np.tile(np.r_[np.zeros(8 - b_len, int), np.ones(b_len, int)], len(ints))
            return bits[np.nonzero(mask)]

    def demodulate_hard(self, symbols):
        c = np.array(self.constellation)

        l = len(symbols)
        idxs = [0]
        acc = 0

        magic_const = 51_200_000 // int(2 ** self.bits_per_symbol)
        while acc < l:
            acc = min(acc + magic_const, l)
            idxs.append(acc)

        n = len(idxs)
        z = zip(idxs[0:n - 1], idxs[1:n])
        pairs = [(i, j) for i, j in z]

        demod_ints = np.empty(l, dtype=int)
        for (a, b) in pairs:
            res = np.abs(symbols[a:b, None] - c[None, :]).argmin(axis=1)
            for i in range(a, b):
                demod_ints[i] = res[i - a]

        demod_bits = self._ints_to_bits(demod_ints)
        return demod_bits


name = "QAM Demodulator"
language = "Python"

module_type = 'class'
module_class = QAMDemodulator
# основная функция, выполняющая работу модуля
entry_point = QAMDemodulator.process

# если hard демодулятор
input_ports = [
    {
        "label": "symbols"
    }
]

# # если soft демодулятор
# input_ports = [
#     {
#         "label": "symbols"
#     },
#     {
#         "label": "noise_var"
#     },
# ]

# "f" указывает с помощью какой функции вычисляется результат соответствующего выходного порта
# если "f" не указана, то используется значение из поля entry_point т.е. f = entry_point
# "inputs" указывает с каких входов брать аргументы для f. Если входы не уазаны, то берутся первые k,
# где k это кол-во аргументов функции f
output_ports = [
    {
        "label": "bits",
    },
]
# если soft демодулятор
# output_ports = [
#     {
#         "label": "llrs",
#     },
# ]

# кодогенератор и интерпретатор сгенерированного кода может смотреть значения параметров прямо в дескрипторе
# т.к пока через GUI нельзя передать параметры, то все параметры берутся из дескриптора

bits_per_symbol = 4