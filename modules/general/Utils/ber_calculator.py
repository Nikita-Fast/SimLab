from typing import List


def calc_ber(sent_bits, received_bits):
    if len(sent_bits) != len(received_bits):
        raise ValueError(
            f'Битов отправлено: {len(sent_bits)} != Битов получено: {len(received_bits)}'
        )
    # print(f'{"sent:":10} {sent_bits}\n{"received:":10} {received_bits}')
    bit_errors = 0
    for i in range(len(sent_bits)):
        if sent_bits[i] != received_bits[i]:
            bit_errors += 1

    ber = bit_errors / len(sent_bits)
    # print(f"BER={ber}")
    return ber


name = "BER Calculator"
language = "Python"

module_type = 'function'
entry_point = calc_ber

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

output_ports = [
    {
        "label": "BER",
        "type": float
    }
]


# module_parameters = [
#     {
#         'name': 'name',
#         'type': str,
#         'has_default_value': True,
#         'default_value': 'DEFAULT_NAME',
#         'validator': lambda x: len(x) > 0
#     }
# ]