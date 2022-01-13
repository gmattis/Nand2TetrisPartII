from Enums import CommandType


class Command(object):
    def __init__(self, commandType: CommandType, arg1: str, arg2: int = 0) -> None:
        super().__init__()
        self.commandType = commandType
        self.arg1 = arg1
        self.arg2 = arg2
    
    def toString(self) -> str:
        if self.commandType == CommandType.ARITHMETIC:
            return self.arg1
        elif self.commandType == CommandType.CALL:
            return f"call {self.arg1} {self.arg2}"
        elif self.commandType == CommandType.FUNCTION:
            return f"function {self.arg1} {self.arg2}"
        elif self.commandType == CommandType.GOTO:
            return f"goto {self.arg1}"
        elif self.commandType == CommandType.IF:
            return f"if-goto {self.arg1}"
        elif self.commandType == CommandType.LABEL:
            return f"label {self.arg1}"
        elif self.commandType == CommandType.POP:
            return f"pop {self.arg1} {self.arg2}"
        elif self.commandType == CommandType.PUSH:
            return f"push {self.arg1} {self.arg2}"
        elif self.commandType == CommandType.RETURN:
            return f"return"
        return ""
