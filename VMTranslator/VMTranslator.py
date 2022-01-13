import sys
import os

from Enums import CommandType
from Parser import Parser
from Writer import Writer


def main():
    vmFile = sys.argv[1]

    parsers = []
    writer = None

    if os.path.isdir(vmFile):
        vmDir = os.path.normpath(vmFile)
        writer = Writer(f"{vmDir}/{os.path.basename(vdDir)}.asm")
        files = os.listdir(vmDir)
        for file in files:
            if file.endswith(".vm"):
                parsers.append(Parser(f"{vmDir}/{file}"))
        writer.writeBootCode()
    else:
        writer = Writer(f"{os.path.splitext(vmFile)[0]}.asm")
        parsers.append(Parser(vmFile))

    for parser in parsers:
        writer.changeFile(parser.getFileName())
        while parser.commandAvailable():
            command = parser.nextCommand()

            if command.commandType == CommandType.ARITHMETIC:
                writer.writeArithmetic(command)
            elif command.commandType == CommandType.POP or command.commandType == CommandType.PUSH:
                writer.writePushPop(command)
            elif command.commandType == CommandType.GOTO or command.commandType == CommandType.IF or command.commandType == CommandType.LABEL:
                writer.writeFlow(command)
            elif command.commandType == CommandType.CALL or command.commandType == CommandType.FUNCTION or command.commandType == CommandType.RETURN:
                writer.writeFunctions(command)

    writer.close()


if __name__ == "__main__":
    main()
