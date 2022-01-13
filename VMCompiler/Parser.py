from Enums import *
from Token import Token
from Tokenizer import Tokenizer
from AST import *


class ParsingError(Exception):
    pass

class Parser(object):
    def __init__(self) -> None:
        super().__init__()

    def compileClass(self, tokenizer: Tokenizer) -> Class:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.CLASS):
            raise ParsingError(f"Expected keyword 'class', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.IDENTIFIER):
            raise ParsingError(f"Expected identifier, got {token.toString()}")
        className = token

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACE):
            raise ParsingError(f"Expected symbol '{{', got {token.toString()}")

        varDec = self.compileClassVarDec(tokenizer)
        subroutineDec = self.compileSubroutineDec(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACE):
            raise ParsingError(f"Expected symbol '}}', got {token.toString()}")

        return Class(className.value, varDec, subroutineDec)

    def compileClassVarDec(self, tokenizer: Tokenizer) -> List[ClassVarDec]:
        varDecList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        endVarDec = not (token.type == TokenType.KEYWORD and token.value in [Keyword.STATIC, Keyword.FIELD])

        while not endVarDec:
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.STATIC, Keyword.FIELD]):
                raise ParsingError(f"Expected keyword 'static' or 'field', got {token.toString()}")
            if (token.value == Keyword.STATIC):
                varKind = VarKind.STATIC
            elif (token.value == Keyword.FIELD):
                varKind = VarKind.FIELD

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]) and not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected type, got {token.toString()}")
            if (token.type == TokenType.KEYWORD):
                varType = token.value.value
            elif (token.type == TokenType.IDENTIFIER):
                varType = token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not token.type == TokenType.IDENTIFIER:
                raise ParsingError(f"Expected identifier, got {token.toString()}")
            varName = token.value

            varDecList.append(ClassVarDec(varKind, varType, varName))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endVar = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

            while not endVar:
                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA):
                    raise ParsingError(f"Expected symbol ',', got {token.toString()}")

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.IDENTIFIER):
                    raise ParsingError(f"Expected identifier, got {token.toString()}")
                varName = token.value

                varDecList.append(ClassVarDec(varKind, varType, varName))

                token = tokenizer.peekNextToken()
                endVar = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
                raise ParsingError(f"Expected symbol ';', got {token.toString()}")

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endVarDec = not (token.type == TokenType.KEYWORD and token.value in [Keyword.STATIC, Keyword.FIELD])

        return varDecList

    def compileSubroutineDec(self, tokenizer: Tokenizer) -> List[SubroutineDec]:
        subroutineDecList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        endSubroutineDec = not (token.type == TokenType.KEYWORD and token.value in [Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD])

        while not endSubroutineDec:
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD]):
                raise ParsingError(f"Expected keyword 'constructor' or 'function' or 'method', got {token.toString()}")
            if (token.value == Keyword.CONSTRUCTOR):
                subroutineKind = SubroutineKind.CONSTRUCTOR
            elif (token.value == Keyword.FUNCTION):
                subroutineKind = SubroutineKind.FUNCTION
            elif (token.value == Keyword.METHOD):
                subroutineKind = SubroutineKind.METHOD

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN, Keyword.VOID]) and not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected keyword 'void' or type, got {token.toString()}")
            if (token.type == TokenType.KEYWORD):
                subroutineReturnType = token.value.value
            elif (token.type == TokenType.IDENTIFIER):
                subroutineReturnType = token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected identifier, got {token.toString()}")
            subroutineName = token.value

            subroutineParameterList = self.compileParameterList(tokenizer)

            subroutineVarDecList, subroutineBody = self.compileSubroutineBody(tokenizer)

            subroutineDecList.append(SubroutineDec(subroutineKind, subroutineReturnType, subroutineName, subroutineParameterList, subroutineVarDecList, subroutineBody))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endSubroutineDec = not (token.type == TokenType.KEYWORD and token.value in [Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD])

        return subroutineDecList

    def compileParameterList(self, tokenizer: Tokenizer) -> List[Tuple[str, str]]:
        parameterList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_PARENTHESIS):
            raise ParsingError(f"Expected symbol '(', got {token.toString()}")
        
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        if (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]) or (token.type == TokenType.IDENTIFIER):
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]) and not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected type, got {token.toString()}")
            if (token.type == TokenType.KEYWORD):
                parameterType = token.value.value
            elif (token.type == TokenType.IDENTIFIER):
                parameterType = token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected identifier, got {token.toString()}")
            parameterName = token.value

            parameterList.append((parameterType, parameterName))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endParameterList = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)
            while not endParameterList:
                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA):
                    raise ParsingError(f"Expected symbol ',', got {token.toString()}")

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]) and not (token.type == TokenType.IDENTIFIER):
                    raise ParsingError(f"Expected type, got {token.toString()}")
                if (token.type == TokenType.KEYWORD):
                    parameterType = token.value.value
                elif (token.type == TokenType.IDENTIFIER):
                    parameterType = token.value

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.IDENTIFIER):
                    raise ParsingError(f"Expected identifier, got {token.toString()}")
                parameterName = token.value

                parameterList.append((parameterType, parameterName))

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.peekNextToken()
                endParameterList = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
            raise ParsingError(f"Expected symbol ')', got {token.toString()}")

        return parameterList

    def compileSubroutineBody(self, tokenizer: Tokenizer) -> Tuple[List[Tuple[str, str]], SubroutineBody]:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACE):
            raise ParsingError(f"Expected symbol '{{', got {token.toString()}")
        
        varDecList = self.compileVarDec(tokenizer)

        statementList = self.compileStatements(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACE):
            raise ParsingError(f"Expected symbol '}}', got {token.toString()}")

        return varDecList, SubroutineBody(statementList)

    def compileVarDec(self, tokenizer: Tokenizer) -> List[Tuple[str, str]]:
        varDecList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        endVarDec = not (token.type == TokenType.KEYWORD and token.value == Keyword.VAR)

        while not endVarDec:
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value == Keyword.VAR):
                raise ParsingError(f"Expected keyword 'var', got {token.toString()}")

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]) and not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected type, got {token.toString()}")
            if (token.type == TokenType.KEYWORD):
                varType = token.value.value
            elif (token.type == TokenType.IDENTIFIER):
                varType = token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected identifier, got {token.toString()}")
            varName = token.value

            varDecList.append((varType, varName))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endVarName = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

            while not endVarName:
                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA):
                    raise ParsingError(f"Expected symbol ',', got {token.toString()}")

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.IDENTIFIER):
                    raise ParsingError(f"Expected identifier, got {token.toString()}")
                varName = token.value

                varDecList.append((varType, varName))

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.peekNextToken()
                endVarName = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
                raise ParsingError(f"Expected symbol ';', got {token.toString()}")

            token = tokenizer.peekNextToken()
            endVarDec = not (token.type == TokenType.KEYWORD and token.value == Keyword.VAR)

        return varDecList

    def compileStatements(self, tokenizer: Tokenizer) -> List[Statement]:
        statementList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        endStatements = not (token.type == TokenType.KEYWORD and token.value in [Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN])

        while not endStatements:
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            if not (token.type == TokenType.KEYWORD and token.value in [Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN]):
                raise ParsingError(f"Expected keyword 'let' or 'if' or 'while' or 'do' or 'return', got {token.toString()}")

            if token.value == Keyword.LET:
                statementList.append(self.compileLet(tokenizer))
            elif token.value == Keyword.IF:
                statementList.append(self.compileIf(tokenizer))
            elif token.value == Keyword.WHILE:
                statementList.append(self.compileWhile(tokenizer))
            elif token.value == Keyword.DO:
                statementList.append(self.compileDo(tokenizer))
            elif token.value == Keyword.RETURN:
                statementList.append(self.compileReturn(tokenizer))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endStatements = not (token.type == TokenType.KEYWORD and token.value in [Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN])

        return statementList

    def compileLet(self, tokenizer: Tokenizer) -> LetStatement:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.LET):
            raise ParsingError(f"Expected keyword 'let', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.IDENTIFIER):
            raise ParsingError(f"Expected identifier, got {token.toString()}")
        varName = token.value

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        if (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACKET):
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACKET):
                raise ParsingError(f"Expected symbol '[', got {token.toString()}")

            arrayExpression = self.compileExpression(tokenizer)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACKET):
                raise ParsingError(f"Expected symbol ']', got {token.toString()}")

        else:
            arrayExpression = None

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.EQUAL):
            raise ParsingError(f"Expected symbol '=', got {token.toString()}")

        value = self.compileExpression(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
            raise ParsingError(f"Expected symbol ';', got {token.toString()}")

        return LetStatement(varName, arrayExpression, value)

    def compileIf(self, tokenizer: Tokenizer) -> IfStatement:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.IF):
            raise ParsingError(f"Expected keyword 'if', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_PARENTHESIS):
            raise ParsingError(f"Expected symbol '(', got {token.toString()}")

        conditionExpression = self.compileExpression(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
            raise ParsingError(f"Expected symbol ')', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACE):
            raise ParsingError(f"Expected symbol '{{', got {token.toString()}")

        statementList = self.compileStatements(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACE):
            raise ParsingError(f"Expected symbol '}}', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        if (token.type == TokenType.KEYWORD and token.value == Keyword.ELSE):
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.KEYWORD and token.value == Keyword.ELSE):
                raise ParsingError(f"Expected keyword 'else', got {token.toString()}")

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACE):
                raise ParsingError(f"Expected symbol '{{', got {token.toString()}")

            elseStatementList = self.compileStatements(tokenizer)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACE):
                raise ParsingError(f"Expected symbol '}}', got {token.toString()}")

        else:
            elseStatementList = []

        return IfStatement(conditionExpression, statementList, elseStatementList)

    def compileWhile(self, tokenizer: Tokenizer) -> WhileStatement:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.WHILE):
            raise ParsingError(f"Expected keyword 'while', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_PARENTHESIS):
            raise ParsingError(f"Expected symbol '(', got {token.toString()}")

        conditionExpression = self.compileExpression(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
            raise ParsingError(f"Expected symbol ')', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACE):
            raise ParsingError(f"Expected symbol '{{', got {token.toString()}")

        statementList = self.compileStatements(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACE):
            raise ParsingError(f"Expected symbol '}}', got {token.toString()}")

        return WhileStatement(conditionExpression, statementList)

    def compileDo(self, tokenizer: Tokenizer) -> DoStatement:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.DO):
            raise ParsingError(f"Expected keyword 'do', got {token.toString()}")

        subroutineCall = self.compileSubroutineCall(tokenizer)

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
            raise ParsingError(f"Expected symbol ';', got {token.toString()}")

        return DoStatement(subroutineCall)

    def compileReturn(self, tokenizer: Tokenizer) -> ReturnStatement:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.KEYWORD and token.value == Keyword.RETURN):
            raise ParsingError(f"Expected keyword 'return', got {token.toString()}")

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
            returnExpression = self.compileExpression(tokenizer)
        else:
            returnExpression = None

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL and token.value == Symbol.SEMICOLON):
            raise ParsingError(f"Expected symbol ';', got {token.toString()}")

        return ReturnStatement(returnExpression)

    def compileExpression(self, tokenizer: Tokenizer) -> Expression:
        termList = [(None, self.compileTerm(tokenizer))]

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        endExpression = not (token.type == TokenType.SYMBOL and token.value in [Symbol.PLUS, Symbol.MINUS, Symbol.TIMES, Symbol.DIVIDE, Symbol.AND, Symbol.OR, Symbol.INFERIOR, Symbol.SUPERIOR, Symbol.EQUAL])
        
        while not endExpression:
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value in [Symbol.PLUS, Symbol.MINUS, Symbol.TIMES, Symbol.DIVIDE, Symbol.AND, Symbol.OR, Symbol.INFERIOR, Symbol.SUPERIOR, Symbol.EQUAL]):
                raise ParsingError(f"Expected operator, got {token.toString()}")
            operator = token.value
            
            term = self.compileTerm(tokenizer)

            termList.append((operator, term))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endExpression = not (token.type == TokenType.SYMBOL and token.value in [Symbol.PLUS, Symbol.MINUS, Symbol.TIMES, Symbol.DIVIDE, Symbol.AND, Symbol.OR, Symbol.INFERIOR, Symbol.SUPERIOR, Symbol.EQUAL])

        return Expression(termList)

    def compileTerm(self, tokenizer: Tokenizer) -> Term:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()

        if ((token.type in [TokenType.INT_CONST, TokenType.STRING_CONST]) or (token.type == TokenType.KEYWORD and token.value in [Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS])):
            return ConstantTerm(token)

        elif (token.type == TokenType.IDENTIFIER):
            varName = token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            nextToken = tokenizer.peekNextToken()

            if (nextToken.type == TokenType.SYMBOL and nextToken.value == Symbol.LEFT_BRACKET):
                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.LEFT_BRACKET):
                    raise ParsingError(f"Expected symbol '[', got {token.toString()}")
                
                arrayExpression = self.compileExpression(tokenizer)

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_BRACKET):
                    raise ParsingError(f"Expected symbol ']', got {token.toString()}")

                return VarTerm(varName, arrayExpression)

            elif (nextToken.type == TokenType.SYMBOL and nextToken.value in [Symbol.LEFT_PARENTHESIS, Symbol.POINT]):
                return self.compileSubroutineCall(tokenizer, token)

            else:
                return VarTerm(varName, None)

        elif (token.type == TokenType.SYMBOL):
            if (token.value == Symbol.LEFT_PARENTHESIS):
                expression = self.compileExpression(tokenizer)

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
                    raise ParsingError(f"Expected symbol ')', got {token.toString()}")
                return ParenthesizedExpression(expression)

            elif (token.value in [Symbol.MINUS, Symbol.TILDE]):
                operator = token.value
                
                term = self.compileTerm(tokenizer)

                return UnaryOpTerm(operator, term)
            else:
                raise ParsingError(f"Expected expression, got {token.toString()}")

        else:
            raise ParsingError(f"Expected expression, got {token.toString()}")

    def compileExpressionList(self, tokenizer: Tokenizer) -> None:
        expressionList = []

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.peekNextToken()
        if ((token.type == TokenType.KEYWORD and token.value in [Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS]) or (token.type == TokenType.SYMBOL and token.value in [Symbol.LEFT_PARENTHESIS, Symbol.MINUS, Symbol.TILDE]) or (token.type in [TokenType.INT_CONST, TokenType.STRING_CONST, TokenType.IDENTIFIER])):
            expressionList.append(self.compileExpression(tokenizer))

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.peekNextToken()
            endExpressionList = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

            while not endExpressionList:
                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.nextToken()
                if not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA):
                    raise ParsingError(f"Expected symbol ',', got {token.toString()}")
                
                expressionList.append(self.compileExpression(tokenizer))

                if not tokenizer.tokenAvailable():
                    raise ParsingError("No more tokens available")
                token = tokenizer.peekNextToken()
                endExpressionList = not (token.type == TokenType.SYMBOL and token.value == Symbol.COMMA)

        return expressionList

    def compileSubroutineCall(self, tokenizer: Tokenizer, firstToken: Token = None) -> None:
        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        if firstToken == None:
            token = tokenizer.nextToken()
        else:
            token = firstToken
        if not (token.type == TokenType.IDENTIFIER):
            raise ParsingError(f"Expected identifier, got {token.toString()}")
        subroutineName = token.value

        if not tokenizer.tokenAvailable():
            raise ParsingError("No more tokens available")
        token = tokenizer.nextToken()
        if not (token.type == TokenType.SYMBOL):
            raise ParsingError(f"Expected symbol '(' or '.', got {token.toString()}")

        if (token.value == Symbol.LEFT_PARENTHESIS):
            expressionList = self.compileExpressionList(tokenizer)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
                raise ParsingError(f"Expected symbol ')', got {token.toString()}")

            return SubroutineCall(None, subroutineName, expressionList)

        elif (token.value == Symbol.POINT):
            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.IDENTIFIER):
                raise ParsingError(f"Expected identifier, got {token.toString()}")
            className, subroutineName = subroutineName, token.value

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL):
                raise ParsingError(f"Expected symbol '(' or '.', got {token.toString()}")

            expressionList = self.compileExpressionList(tokenizer)

            if not tokenizer.tokenAvailable():
                raise ParsingError("No more tokens available")
            token = tokenizer.nextToken()
            if not (token.type == TokenType.SYMBOL and token.value == Symbol.RIGHT_PARENTHESIS):
                raise ParsingError(f"Expected symbol ')', got {token.toString()}")

            return SubroutineCall(className, subroutineName, expressionList)

        else:
            raise ParsingError(f"Expected symbol '(' or '.', got {token.toString()}")

    def parse(self, tokenizer: Tokenizer) -> Class:
        return self.compileClass(tokenizer)
