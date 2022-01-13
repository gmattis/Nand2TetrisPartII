from Enums import *

class Writer(object):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._file = filename
        self._lines = []

    def writePush(self, segment: Segment, index: int):
        self._lines.append(f"push {segment.value} {index}")

    def writePop(self, segment: Segment, index: int):
        self._lines.append(f"pop {segment.value} {index}")

    def writeArithmetic(self, command: Command):
        self._lines.append(f"{command.value}")

    def writeLabel(self, label: str):
        self._lines.append(f"label {label}")

    def writeGoto(self, label: str):
        self._lines.append(f"goto {label}")

    def writeIf(self, label: str):
        self._lines.append(f"if-goto {label}")

    def writeCall(self, name: str, nArgs: int):
        self._lines.append(f"call {name} {nArgs}")

    def writeFunction(self, name: str, nLocals: int):
        self._lines.append(f"function {name} {nLocals}")

    def writeReturn(self):
        self._lines.append("return")

    def close(self) -> None:
        file = open(self._file, 'w')
        lines = '\n'.join(self._lines)
        file.writelines(lines)
        file.close()
