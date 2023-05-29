

def identity(value):
    return value


name = "Constant"
language = "Python"

module_type = 'function'
entry_point = identity

output_ports = [
    {
        "label": "Value",
    }
]


module_parameters = [
    {
        'name': 'value',
        # 'type': Any,
        'has_default_value': False,
        # 'default_value': 'DEFAULT_NAME',
        # 'validator': lambda x: x is not None
    }
]