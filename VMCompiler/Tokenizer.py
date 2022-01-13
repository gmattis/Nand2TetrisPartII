import re, os

from Enums import Keyword, Symbol, TokenType
from Token import Token

class TokenizerError(Exception):
    pass

class Tokenizer(object):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self._tokenList = []
        self._next = 0

        self._filename = os.path.basename(filename)
        file = open(filename, 'r')
        content = file.read()
        file.close()

        start = 0
        while start < len(content):
            if match := re.match(r"(\/\/.*\n+?)|(\/\*\*[\s\S]*?(\*\/))|(\s+)", content[start:]):
                start += match.end()
            elif match := re.match(r"\b(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b", content[start:]):
                self._tokenList.append(Token(TokenType.KEYWORD, Keyword(match.group())))
                start += match.end()
            elif match := re.match(r"({|}|\(|\)|\[|\]|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~)", content[start:]):
                self._tokenList.append(Token(TokenType.SYMBOL, Symbol(match.group())))
                start += match.end()
            elif match := re.match(r"\d+", content[start:]):
                val = int(match.group())
                if (val < 0 or val > 32767):
                    raise TokenizerError("Invalid integer constant")
                self._tokenList.append(Token(TokenType.INT_CONST, val))
                start += match.end()
            elif match := re.match(r"\"[^\"\n]*?\"", content[start:]):
                self._tokenList.append(Token(TokenType.STRING_CONST, match.group()[1:-1]))
                start += match.end()
            elif match := re.match(r"[a-zA-Z_]\w*", content[start:]):
                self._tokenList.append(Token(TokenType.IDENTIFIER, match.group()))
                start += match.end()
            else:
                raise TokenizerError("Token unrecognized")

    def getFileName(self) -> str:
        return self._filename
        
    def tokenAvailable(self) -> bool:
        return self._next < len(self._tokenList)

    def nextToken(self) -> Token:
        if not self.tokenAvailable():
            raise TokenizerError("No more tokens available")
        self._next += 1
        return self._tokenList[self._next - 1]

    def peekNextToken(self) -> Token:
        if not self.tokenAvailable():
            raise TokenizerError("No more tokens available")
        return self._tokenList[self._next]
