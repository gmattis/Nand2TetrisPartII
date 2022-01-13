from enum import Enum

class CommandType(Enum):
    ARITHMETIC = 0
    CALL = 1
    FUNCTION = 2
    GOTO = 3
    IF = 4
    LABEL = 5
    POP = 6
    PUSH = 7
    RETURN = 8
