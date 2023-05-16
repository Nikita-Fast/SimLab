from enum import Enum


class ConnectionStatus(Enum):
    VALID_LINE = 1
    VALID_LOOP = 2
    NON_VALID = 3