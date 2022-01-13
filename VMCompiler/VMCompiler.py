from Tokenizer import Tokenizer
from Parser import Parser
from Writer import Writer

import sys
import os


def main():
    jackFile = sys.argv[1]

    tokenizers_writers = []
    parser = Parser()

    if os.path.isdir(jackFile):
        jackDir = os.path.normpath(jackFile)
        files = os.listdir(jackDir)
        for file in files:
            if file.endswith(".jack"):
                tokenizers_writers.append((Tokenizer(f"{jackDir}/{file}"), Writer(f"{jackDir}/{os.path.splitext(file)[0]}.vm")))
    else:
        tokenizers_writers.append((Tokenizer(jackFile), Writer(f"{os.path.splitext(jackFile)[0]}.vm")))

    for tw in tokenizers_writers:
        tokenizer, writer = tw
        ast = parser.parse(tokenizer)
        ast.write(writer)
        writer.close()


if __name__ == "__main__":
    main()
