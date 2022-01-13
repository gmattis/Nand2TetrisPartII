from typing import Union
from xml.etree.ElementTree import Element
from Enums import Keyword, Symbol, TokenType

import xml.etree.cElementTree as ET

class Token(object):
    def __init__(self, tokenType: TokenType, value: Union[Keyword, Symbol, str, int]) -> None:
        super().__init__()
        self.type = tokenType
        self.value = value

    def toXMLElement(self, parent: Element) -> Element:
        if self.type == TokenType.KEYWORD:
            elt = ET.SubElement(parent, "keyword")
            elt.text = self.value.value
            return elt
        elif self.type == TokenType.SYMBOL:
            elt = ET.SubElement(parent, "symbol")
            elt.text = self.value.value
            return elt
        elif self.type == TokenType.IDENTIFIER:
            elt = ET.SubElement(parent, "identifier")
            elt.text = self.value
            return elt
        elif self.type == TokenType.INT_CONST:
            elt = ET.SubElement(parent, "int_const")
            elt.text = str(self.value)
            return elt
        elif self.type == TokenType.STRING_CONST:
            elt = ET.SubElement(parent, "string_const")
            elt.text = self.value
            return elt
        return None

    def toString(self) -> str:
        if self.type == TokenType.KEYWORD:
            return f"keyword '{self.value.value}'"
        elif self.type == TokenType.SYMBOL:
            return f"symbol '{self.value.value}'"
        elif self.type == TokenType.IDENTIFIER:
            return f"identifier '{self.value}'"
        elif self.type == TokenType.INT_CONST:
            return f"int_const '{self.value}'"
        elif self.type == TokenType.STRING_CONST:
            return f"string_const '{self.value}'"
        return ""
