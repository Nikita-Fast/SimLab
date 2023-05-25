import numpy as np

def power(sig):
    """ Рассчитываем мощность сигнала."""
    return (((np.abs(sig)) ** 2).sum()) / len(sig)


def calc_noise_power(ebn0_db, symbols, information_bits_per_symbol):
    """ Рассчитываем необходимую мощность шума для переданного массива символов и требуемого EB_N0_db."""
    Es_N0_dB = ebn0_db + 10 * np.log10(information_bits_per_symbol)
    SNR_dB = Es_N0_dB
    SNR = 10 ** (SNR_dB / 10)
    return power(symbols) / SNR


class AWGNChannel:

    def __init__(self, information_bits_per_symbol, ebn0_db):
        self.information_bits_per_symbol = information_bits_per_symbol
        self.ebn0_db = ebn0_db

    def process(self, data: np.ndarray) -> np.ndarray:
        print(f'{AWGNChannel.process}')
        p = calc_noise_power(self.ebn0_db, data, self.information_bits_per_symbol)

        symbols_num = len(data)
        awgn = np.sqrt(p / 2) * np.random.randn(symbols_num) + 1j * np.sqrt(p / 2) * np.random.randn(symbols_num)
        return data + awgn

    def calc_noise_variance(self) -> float:
        snr_db = self.ebn0_db + 10 * np.log10(self.information_bits_per_symbol)  # Signal-to-Noise ratio (in dB)
        noise_var = 10 ** (-snr_db / 10)  # noise variance (power)
        return noise_var