from Command import Command
from Enums import CommandType
import os

class Writer(object):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._file = filename
        self._filename = filename
        self._lines = []
        self._nextLabel = 0

    def _getNextLabel(self) -> str:
        nextLabel = f"JMP_{self._nextLabel}"
        self._nextLabel += 1
        return nextLabel

    def changeFile(self, filename: str) -> None:
        self._filename = os.path.basename(filename)
    
    def writeBootCode(self) -> None:
        lines = [f"// BOOTCODE"]
        
        lines.append("@256")
        lines.append("D=A")
        lines.append("@SP")
        lines.append("M=D")

        self._lines.extend(lines)

        self.writeFunctions(Command(CommandType.CALL, "Sys.init", 0))

    def writeArithmetic(self, command: Command) -> None:
        lines = [f"// {command.toString()}"]

        lines.append("@SP")
        lines.append("M=M-1")
        lines.append("A=M")
        lines.append("D=M")

        if command.arg1 == "add":
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=D+M")
        elif command.arg1 == "sub":
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M-D")
        elif command.arg1 == "neg":
            lines.append("D=-M")
        elif command.arg1 == "eq":
            labelCond = self._getNextLabel()
            labelExit = self._getNextLabel()
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=D-M")
            lines.append(f"@{labelCond}")
            lines.append("D;JNE")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=-1")
            lines.append(f"@{labelExit}")
            lines.append("0;JMP")
            lines.append(f"({labelCond})")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=0")
            lines.append(f"({labelExit})")
        elif command.arg1 == "gt":
            labelCond = self._getNextLabel()
            labelExit = self._getNextLabel()
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M-D")
            lines.append(f"@{labelCond}")
            lines.append("D;JLE")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=-1")
            lines.append(f"@{labelExit}")
            lines.append("0;JMP")
            lines.append(f"({labelCond})")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=0")
            lines.append(f"({labelExit})")
        elif command.arg1 == "lt":
            labelCond = self._getNextLabel()
            labelExit = self._getNextLabel()
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M-D")
            lines.append(f"@{labelCond}")
            lines.append("D;JGE")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=-1")
            lines.append(f"@{labelExit}")
            lines.append("0;JMP")
            lines.append(f"({labelCond})")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=0")
            lines.append(f"({labelExit})")
        elif command.arg1 == "and":
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=D&M")
        elif command.arg1 == "or":
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=D|M")
        elif command.arg1 == "not":
            lines.append("D=!D")

        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("M=M+1")
        self._lines.extend(lines)

    def writePushPop(self, command: Command) -> None:
        lines = [f"// {command.toString()}"]

        if command.commandType == CommandType.POP:
            if command.arg1 == "local":
                lines.append("@LCL")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("D=D+A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "argument":
                lines.append("@ARG")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("D=D+A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "this":
                lines.append("@THIS")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("D=D+A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "that":
                lines.append("@THAT")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("D=D+A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "static":
                lines.append(f"@{self._filename}.{command.arg2}")
                lines.append("D=A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "temp":
                lines.append("@5")
                lines.append("D=A")
                lines.append(f"@{command.arg2}")
                lines.append("D=D+A")
                lines.append("@addr")
                lines.append("M=D")
            elif command.arg1 == "pointer":
                if command.arg2 == 0:
                    lines.append("@THIS")
                    lines.append("D=A")
                elif command.arg2 == 1:
                    lines.append("@THAT")
                    lines.append("D=A")
                lines.append("@addr")
                lines.append("M=D")

            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@addr")
            lines.append("A=M")
            lines.append("M=D")

        elif command.commandType == CommandType.PUSH:
            if command.arg1 == "local":
                lines.append("@LCL")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("A=D+A")
                lines.append("D=M")
            elif command.arg1 == "argument":
                lines.append("@ARG")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("A=D+A")
                lines.append("D=M")
            elif command.arg1 == "this":
                lines.append("@THIS")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("A=D+A")
                lines.append("D=M")
            elif command.arg1 == "that":
                lines.append("@THAT")
                lines.append("D=M")
                lines.append(f"@{command.arg2}")
                lines.append("A=D+A")
                lines.append("D=M")
            elif command.arg1 == "constant":
                lines.append(f"@{command.arg2}")
                lines.append("D=A")
            elif command.arg1 == "static":
                lines.append(f"@{self._filename}.{command.arg2}")
                lines.append("D=M")
            elif command.arg1 == "pointer":
                if command.arg2 == 0:
                    lines.append("@THIS")
                    lines.append("D=M")
                elif command.arg2 == 1:
                    lines.append("@THAT")
                    lines.append("D=M")
            elif command.arg1 == "temp":
                lines.append("@5")
                lines.append("D=A")
                lines.append(f"@{command.arg2}")
                lines.append("A=D+A")
                lines.append("D=M")

            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")

        self._lines.extend(lines)

    def writeFlow(self, command: Command) -> None:
        lines = [f"// {command.toString()}"]

        if command.commandType == CommandType.GOTO:
            lines.append(f"@LABEL_{command.arg1}")
            lines.append("0;JMP")
        elif command.commandType == CommandType.IF:
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M")
            lines.append(f"@LABEL_{command.arg1}")
            lines.append("D;JNE")
        elif command.commandType == CommandType.LABEL:
            lines.append(f"(LABEL_{command.arg1})")

        self._lines.extend(lines)

    def writeFunctions(self, command: Command) -> None:
        lines = [f"// {command.toString()}"]

        if command.commandType == CommandType.CALL:
            labelRet = self._getNextLabel()
            lines.append(f"@{labelRet}")
            lines.append("D=A")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@LCL")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@ARG")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@THIS")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@THAT")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@SP")
            lines.append("D=M")
            lines.append("@5")
            lines.append("D=D-A")
            lines.append(f"@{command.arg2}")
            lines.append("D=D-A")
            lines.append("@ARG")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("D=M")
            lines.append("@LCL")
            lines.append("M=D")
            lines.append(f"@FUNCTION_{command.arg1}")
            lines.append("0;JMP")
            lines.append(f"({labelRet})")
        elif command.commandType == CommandType.FUNCTION:
            lines.append(f"(FUNCTION_{command.arg1})")
            for _ in range(command.arg2):
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=0")
                lines.append("@SP")
                lines.append("M=M+1")
        elif command.commandType == CommandType.RETURN:
            lines.append("@LCL")
            lines.append("D=M")
            lines.append("@endFrame")
            lines.append("M=D")
            lines.append("@5")
            lines.append("A=D-A")
            lines.append("D=M")
            lines.append("@retAddr")
            lines.append("M=D")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@ARG")
            lines.append("A=M")
            lines.append("M=D")
            lines.append("@ARG")
            lines.append("D=M+1")
            lines.append("@SP")
            lines.append("M=D")
            lines.append("@endFrame")
            lines.append("A=M-1")
            lines.append("D=M")
            lines.append("@THAT")
            lines.append("M=D")
            lines.append("@endFrame")
            lines.append("D=M")
            lines.append("@2")
            lines.append("A=D-A")
            lines.append("D=M")
            lines.append("@THIS")
            lines.append("M=D")
            lines.append("@endFrame")
            lines.append("D=M")
            lines.append("@3")
            lines.append("A=D-A")
            lines.append("D=M")
            lines.append("@ARG")
            lines.append("M=D")
            lines.append("@endFrame")
            lines.append("D=M")
            lines.append("@4")
            lines.append("A=D-A")
            lines.append("D=M")
            lines.append("@LCL")
            lines.append("M=D")
            lines.append("@retAddr")
            lines.append("A=M")
            lines.append("0;JMP")

        self._lines.extend(lines)

    def close(self) -> None:
        file = open(self._file, 'w')
        lines = '\n'.join(self._lines)
        file.writelines(lines)
        file.close()
