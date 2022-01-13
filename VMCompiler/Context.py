from Enums import Symbol
from Writer import Writer
from SymbolTable import *

class ParsingException(Exception):
    pass

class Context(object):
    def __init__(self, className: str, writer: Writer) -> None:
        super().__init__()
        self._nextLabel = 0
        self.className = className
        self.classSymbolTable = SymbolTable()
        self.functionSymbolTable = SymbolTable()
        self.writer = writer

    def getSymbol(self, name: str):
        symbol = self.functionSymbolTable.get(name) or self.classSymbolTable.get(name)
        return symbol

    def getLabel(self) -> str:
        self._nextLabel += 1
        return f"LABEL_{self._nextLabel - 1}"
