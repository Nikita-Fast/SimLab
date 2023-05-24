import inspect
from typing import Dict


class ModuleDescriptor:

    def __init__(self, options: Dict):
        self.type = options["type"]
        self.required = options["required"]
        self.options = options
        self.value = options.get("value", {})

    def validate(self, field_value):
        if self.type == "array-struct":
            if type(field_value) != list and type(field_value) != tuple:
                return self.value.validate(field_value)
            for member in field_value:
                if not self.value.validate(member):
                    return False
            return True

        if self.type == "struct":
            if type(field_value) != dict:
                return False
            for key in self.value.keys():
                if key in field_value.keys():
                    if not self.value[key].validate(field_value[key]):
                        return False
                else:
                    if self.value[key].required == "Yes":
                        return False
            return True

        if self.type == "str":
            return type(field_value) == str

        if self.type == "class":
            return type(field_value) == type

        if self.type == "function":
            return type(field_value).__name__ == 'function'

        return True
