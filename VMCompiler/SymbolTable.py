from typing import Union
from Enums import *


class SymbolException(Exception):
    pass

class SymbolItem(object):
    def __init__(self, name: str, symbolType: str, kind: VarKind, index: int) -> None:
        super().__init__()
        self.name = name
        self.type = symbolType
        self.kind = kind
        self.index = index

    def __repr__(self) -> str:
        return f"{self.name}: {self.type} {self.kind} [{self.kind}]"

class SymbolTable(object):
    def __init__(self) -> None:
        super().__init__()
        self._symbols = []

    def add(self, name: str, symbolType: str, kind: VarKind) -> None:
        count = 0
        for sym in self._symbols:
            if name == sym.name:
                raise SymbolException(f"Symbol '{name}' already exists in this scope")
            if kind == sym.kind:
                count += 1
        self._symbols.append(SymbolItem(name, symbolType, kind, count))

    def get(self, name: str) -> Union[SymbolItem, None]:
        for sym in self._symbols:
            if sym.name == name:
                return sym
        return None

    def count(self, kind: VarKind) -> int:
        count = 0
        for sym in self._symbols:
            if sym.kind == kind:
                count += 1
        return count

    def clear(self) -> None:
        self._symbols = []
