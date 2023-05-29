from typing import List

from matplotlib import pyplot as plt


def calc_ber(sent_bits, received_bits):
    if len(sent_bits) != len(received_bits):
        raise ValueError(
            f'Битов отправлено: {len(sent_bits)} != Битов получено: {len(received_bits)}'
        )
    bit_errors = 0
    for i in range(len(sent_bits)):
        if sent_bits[i] != received_bits[i]:
            bit_errors += 1

    ber = bit_errors / len(sent_bits)
    print('BER = {}'.format(ber))
    return ber


def plot_ber(ebn0_db_list, ber_list, name: str):
    if len(ebn0_db_list) != len(ber_list):
        raise ValueError('Число значений по оси Х должно быть равно числу значений по оси У')
    plt.yscale("log")
    plt.grid(visible='true')
    plt.xlabel("Eb/N0, dB")
    plt.ylabel("BER")
    plt.plot(*zip(ebn0_db_list, ber_list), '--o', label=name)
    plt.legend()
    plt.show()


name = "BER Calculator"
language = "Python"

module_type = 'function'
entry_point = plot_ber

input_ports = [
    {
        "label": "sent_bits",
        "type": List[int]
    },
    {
        "label": "received_bits",
        "type": List[int]
    }
]


module_parameters = [
    {
        'name': 'name',
        'type': str,
        'has_default_value': True,
        'default_value': 'DEFAULT_NAME',
        'validator': lambda x: len(x) > 0
    }
]