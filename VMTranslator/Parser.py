from Command import Command
from Enums import CommandType
import os


class Parser(object):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._commands = []
        self._next = 0
        
        self._filename = os.path.basename(filename)
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()

        for line in lines:
            if not line.startswith("//"):
                split = line.replace('\n', '').replace('\t', ' ').split(' ')
                if split[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
                    self._commands.append(Command(CommandType.ARITHMETIC, split[0]))
                elif split[0] == "pop":
                    self._commands.append(Command(CommandType.POP, split[1], int(split[2])))
                elif split[0] == "push":
                    self._commands.append(Command(CommandType.PUSH, split[1], int(split[2])))
                elif split[0] == "label":
                    self._commands.append(Command(CommandType.LABEL, split[1]))
                elif split[0] == "goto":
                    self._commands.append(Command(CommandType.GOTO, split[1]))
                elif split[0] == "if-goto":
                    self._commands.append(Command(CommandType.IF, split[1]))
                elif split[0] == "function":
                    self._commands.append(Command(CommandType.FUNCTION, split[1], int(split[2])))
                elif split[0] == "call":
                    self._commands.append(Command(CommandType.CALL, split[1], int(split[2])))
                elif split[0] == "return":
                    self._commands.append(Command(CommandType.RETURN, ""))

    def getFileName(self) -> str:
        return self._filename
        
    def commandAvailable(self) -> bool:
        return self._next < len(self._commands)

    def nextCommand(self) -> Command:
        self._next += 1
        return self._commands[self._next - 1]
