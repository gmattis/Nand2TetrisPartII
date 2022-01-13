from typing import List, Tuple, Union
from Enums import *
from SymbolTable import SymbolItem, SymbolTable
from Token import Token
from Writer import Writer
from Context import Context, ParsingException


class Term(object):
    def write(self, context: Context) -> None:
        pass

class Statement(object):
    def write(self, context: Context) -> None:
        pass

class Structure(object):
    def write(self, context: Context) -> None:
        pass

class Expression(object):
    def __init__(self, termList: List[Tuple[Union[Symbol, None], Term]]) -> None:
        super().__init__()
        self.termList = termList
        
    def __str__(self):
        return f"Expression: {self.termList}"
    
    def __repr__(self):
        return f"Expression: {self.termList}"

    def write(self, context: Context) -> None:
        for expr in self.termList:
            symbol, term = expr
            term.write(context)
            if symbol:
                if symbol == Symbol.PLUS:
                    context.writer.writeArithmetic(Command.ADD)
                elif symbol == Symbol.MINUS:
                    context.writer.writeArithmetic(Command.SUB)
                elif symbol == Symbol.TIMES:
                    context.writer.writeCall("Math.multiply", 2)
                elif symbol == Symbol.DIVIDE:
                    context.writer.writeCall("Math.divide", 2)
                elif symbol == Symbol.AND:
                    context.writer.writeArithmetic(Command.AND)
                elif symbol == Symbol.OR:
                    context.writer.writeArithmetic(Command.OR)
                elif symbol == Symbol.INFERIOR:
                    context.writer.writeArithmetic(Command.LT)
                elif symbol == Symbol.SUPERIOR:
                    context.writer.writeArithmetic(Command.GT)
                elif symbol == Symbol.EQUAL:
                    context.writer.writeArithmetic(Command.EQ)
                else:
                    raise ParsingException("Unknown operator: {symbol}")

class SubroutineCall(Term):
    def __init__(self, className: Union[None, str], subroutineName: str, expressionList: List[Expression]) -> None:
        super().__init__()
        self.className = className
        self.subroutineName = subroutineName
        self.expressionList = expressionList

    def __str__(self):
        return f"SubroutineCall: {self.className}.{self.subroutineName}({self.expressionList})"
    
    def __repr__(self):
        return f"SubroutineCall: {self.className}.{self.subroutineName}({self.expressionList})"

    def write(self, context: Context) -> None:
        nbArgs = len(self.expressionList)
        if self.className:
            var = context.getSymbol(self.className)
            if var:
                subroutineName = f"{var.type}.{self.subroutineName}"
                if var.kind == VarKind.FIELD:
                    context.writer.writePush(Segment.THIS, var.index)
                elif var.kind == VarKind.STATIC:
                    context.writer.writePush(Segment.STATIC, var.index)
                elif var.kind == VarKind.ARGUMENT:
                    context.writer.writePush(Segment.ARG, var.index)
                elif var.kind == VarKind.LOCAL:
                    context.writer.writePush(Segment.LOCAL, var.index)
                else:
                    raise ParsingException(f"Unknown VarKind: {var.kind}")
                nbArgs += 1
            else:
                subroutineName = f"{self.className}.{self.subroutineName}"
        else:
            subroutineName = f"{context.className}.{self.subroutineName}"
            context.writer.writePush(Segment.POINTER, 0)
            nbArgs += 1
        for expr in self.expressionList:
            expr.write(context)
        context.writer.writeCall(subroutineName, nbArgs)

class UnaryOpTerm(Term):
    def __init__(self, unaryOp: Symbol, term: Term) -> None:
        super().__init__()
        self.unaryOp = unaryOp
        self.term = term

    def __str__(self):
        return f"UnaryOpTerm: {self.unaryOp} {self.term}"
    
    def __repr__(self):
        return f"UnaryOpTerm: {self.unaryOp} {self.term}"

    def write(self, context: Context) -> None:
        self.term.write(context)
        if self.unaryOp == Symbol.MINUS:
            context.writer.writeArithmetic(Command.NEG)
        elif self.unaryOp == Symbol.TILDE:
            context.writer.writeArithmetic(Command.NOT)

class ParenthesizedExpression(Term):
    def __init__(self, expression: Expression) -> None:
        super().__init__()
        self.expression = expression

    def __str__(self):
        return f"ParenthesizedExpression: {self.expression}"
    
    def __repr__(self):
        return f"ParenthesizedExpression: {self.expression}"

    def write(self, context: Context) -> None:
        self.expression.write(context)

class VarTerm(Term):
    def __init__(self, varName: str, arrayExpression: Union[None, Expression]) -> None:
        super().__init__()
        self.varName = varName
        self.arrayExpression = arrayExpression

    def __str__(self):
        return f"ValTerm: {self.varName} [{self.arrayExpression}]"
    
    def __repr__(self):
        return f"ValTerm: {self.varName} [{self.arrayExpression}]"

    def write(self, context: Context) -> None:
        var = context.getSymbol(self.varName)
        if var.kind == VarKind.FIELD:
            context.writer.writePush(Segment.THIS, var.index)
        elif var.kind == VarKind.STATIC:
            context.writer.writePush(Segment.STATIC, var.index)
        elif var.kind == VarKind.ARGUMENT:
            context.writer.writePush(Segment.ARG, var.index)
        elif var.kind == VarKind.LOCAL:
            context.writer.writePush(Segment.LOCAL, var.index)
        else:
            raise ParsingException(f"Unknown VarKind: {var.kind}")
        if self.arrayExpression:
            self.arrayExpression.write(context)
            context.writer.writeArithmetic(Command.ADD)
            context.writer.writePop(Segment.POINTER, 1)
            context.writer.writePush(Segment.THAT, 0)

class ConstantTerm(Term):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.value = value

    def __str__(self):
        return f"ConstantTerm: {self.value}"
    
    def __repr__(self):
        return f"ConstantTerm: {self.value}"

    def write(self, context: Context) -> None:
        if self.value.type == TokenType.INT_CONST:
            if self.value.value < 0:
                context.writer.writePush(Segment.CONST, -(self.value.value))
                context.writer.writeArithmetic(Command.NEG)
            else:
                context.writer.writePush(Segment.CONST, self.value.value)
        elif self.value.type == TokenType.KEYWORD:
            if self.value.value == Keyword.TRUE:
                context.writer.writePush(Segment.CONST, 0)
                context.writer.writeArithmetic(Command.NOT)
            elif self.value.value == Keyword.FALSE:
                context.writer.writePush(Segment.CONST, 0)
            elif self.value.value == Keyword.NULL:
                context.writer.writePush(Segment.CONST, 0)
            elif self.value.value == Keyword.THIS:
                context.writer.writePush(Segment.POINTER, 0)
        elif self.value.type == TokenType.STRING_CONST:
            context.writer.writePush(Segment.CONST, len(self.value.value))
            context.writer.writeCall("String.new", 1)
            for c in self.value.value:
                context.writer.writePush(Segment.CONST, ord(c))
                context.writer.writeCall("String.appendChar", 2)

class LetStatement(Statement):
    def __init__(self, varName: Token, arrayExpression: Union[None, Expression], value: Expression) -> None:
        super().__init__()
        self.varName = varName
        self.arrayExpression = arrayExpression
        self.value = value

    def __str__(self):
        return f"LetStatement: {self.varName} [{self.arrayExpression}] = {self.value}\n"
    
    def __repr__(self):
        return f"LetStatement: {self.varName} [{self.arrayExpression}] = {self.value}\n"

    def write(self, context: Context) -> None:
        self.value.write(context)
        var = context.getSymbol(self.varName)
        if self.arrayExpression:
            if var.kind == VarKind.FIELD:
                context.writer.writePush(Segment.THIS, var.index)
            elif var.kind == VarKind.STATIC:
                context.writer.writePush(Segment.STATIC, var.index)
            elif var.kind == VarKind.ARGUMENT:
                context.writer.writePush(Segment.ARG, var.index)
            elif var.kind == VarKind.LOCAL:
                context.writer.writePush(Segment.LOCAL, var.index)
            else:
                raise ParsingException(f"Unknown VarKind: {var.kind}")
            self.arrayExpression.write(context)
            context.writer.writeArithmetic(Command.ADD)
            context.writer.writePop(Segment.POINTER, 1)
            context.writer.writePop(Segment.THAT, 0)
        else:
            if var.kind == VarKind.FIELD:
                context.writer.writePop(Segment.THIS, var.index)
            elif var.kind == VarKind.STATIC:
                context.writer.writePop(Segment.STATIC, var.index)
            elif var.kind == VarKind.ARGUMENT:
                context.writer.writePop(Segment.ARG, var.index)
            elif var.kind == VarKind.LOCAL:
                context.writer.writePop(Segment.LOCAL, var.index)
            else:
                raise ParsingException(f"Unknown VarKind: {var.kind}")

class IfStatement(Statement):
    def __init__(self, conditionExpression: Expression, statementList: List[Statement], elseStatementList: List[Statement]) -> None:
        super().__init__()
        self.conditionExpression = conditionExpression
        self.statementList = statementList
        self.elseStatementList = elseStatementList

    def __str__(self):
        return f"IfStatement:\n{self.conditionExpression}\n{self.statementList}\nElse:\n{self.elseStatementList}\n"
    
    def __repr__(self):
        return f"IfStatement:\n{self.conditionExpression}\n{self.statementList}\nElse:\n{self.elseStatementList}\n"

    def write(self, context: Context) -> None:
        label1 = context.getLabel()
        label2 = context.getLabel()
        label3 = context.getLabel()
        self.conditionExpression.write(context)
        context.writer.writeIf(label1)
        context.writer.writeGoto(label2)
        context.writer.writeLabel(label1)
        for expr in self.statementList:
            expr.write(context)
        context.writer.writeGoto(label3)
        context.writer.writeLabel(label2)
        for expr in self.elseStatementList:
            expr.write(context)
        context.writer.writeLabel(label3)

class WhileStatement(Statement):
    def __init__(self, conditionExpression: Expression, statementList: List[Statement]) -> None:
        super().__init__()
        self.conditionExpression = conditionExpression
        self.statementList = statementList

    def __str__(self):
        return f"WhileStatement:\n{self.conditionExpression}\n{self.statementList}\n"

    def __repr__(self):
        return f"WhileStatement:\n{self.conditionExpression}\n{self.statementList}\n"

    def write(self, context: Context) -> None:
        label1 = context.getLabel()
        label2 = context.getLabel()
        context.writer.writeLabel(label1)
        self.conditionExpression.write(context)
        context.writer.writeArithmetic(Command.NOT)
        context.writer.writeIf(label2)
        for expr in self.statementList:
            expr.write(context)
        context.writer.writeGoto(label1)
        context.writer.writeLabel(label2)

class DoStatement(Statement):
    def __init__(self, subroutineCall: SubroutineCall) -> None:
        super().__init__()
        self.subroutineCall = subroutineCall

    def __str__(self):
        return f"DoStatement: {self.subroutineCall}\n"
    
    def __repr__(self):
        return f"DoStatement: {self.subroutineCall}\n"

    def write(self, context: Context) -> None:
        self.subroutineCall.write(context)
        context.writer.writePop(Segment.TEMP, 0)

class ReturnStatement(Statement):
    def __init__(self, returnExpression: Union[None, Expression]) -> None:
        super().__init__()
        self.returnExpression = returnExpression

    def __str__(self):
        return f"ReturnStatement: {self.returnExpression}\n"
    
    def __repr__(self):
        return f"ReturnStatement: {self.returnExpression}\n"

    def write(self, context: Context) -> None:
        if self.returnExpression:
            self.returnExpression.write(context)
        context.writer.writeReturn()

class SubroutineBody(Structure):
    def __init__(self, statementList: List[Statement]) -> None:
        super().__init__()
        self.statementList = statementList

    def __str__(self):
        return f"SubroutineBody:\n{self.statementList}"
    
    def __repr__(self):
        return f"SubroutineBody:\n{self.varDecList}\n{self.statementList}"

    def write(self, context: Context) -> None:
        for statement in self.statementList:
            statement.write(context)

class SubroutineDec(Structure):
    def __init__(self, kind: SubroutineKind, returnType: str, subroutineName: str, parameterList: List[Tuple[str, str]], varDecList: List[Tuple[str, str]], subroutineBody: SubroutineBody) -> None:
        super().__init__()
        self.kind = kind
        self.returnType = returnType
        self.subroutineName = subroutineName
        self.parameterList = parameterList
        self.varDecList = varDecList
        self.subroutineBody = subroutineBody

    def __str__(self):
        return f"SubroutineDec: {self.kind} {self.returnType} {self.subroutineName} ({self.parameterList})\n{self.subroutineBody}\n"

    def __repr__(self):
        return f"SubroutineDec: {self.kind} {self.returnType} {self.subroutineName} ({self.parameterList})\n{self.subroutineBody}\n"

    def write(self, context: Context) -> None:
        if self.kind == SubroutineKind.METHOD:
            context.functionSymbolTable.add("this", context.className, VarKind.ARGUMENT)
        for parameter in self.parameterList:
            varType, varName = parameter
            context.functionSymbolTable.add(varName, varType, VarKind.ARGUMENT)
        for varDec in self.varDecList:
            varType, varName = varDec
            context.functionSymbolTable.add(varName, varType, VarKind.LOCAL)
        context.writer.writeFunction(f"{context.className}.{self.subroutineName}", context.functionSymbolTable.count(VarKind.LOCAL))
        if self.kind == SubroutineKind.CONSTRUCTOR:
            context.writer.writePush(Segment.CONST, context.classSymbolTable.count(VarKind.FIELD))
            context.writer.writeCall("Memory.alloc", 1)
            context.writer.writePop(Segment.POINTER, 0)
        if self.kind == SubroutineKind.METHOD:
            context.writer.writePush(Segment.ARG, 0)
            context.writer.writePop(Segment.POINTER, 0)
        self.subroutineBody.write(context)
        context.functionSymbolTable.clear()

class ClassVarDec(Structure):
    def __init__(self, kind: VarKind, varType: str, varName: str) -> None:
        super().__init__()
        self.kind = kind
        self.varType = varType
        self.varName = varName

    def __str__(self):
        return f"ClassVarDec: {self.kind} {self.varType} {self.varName}\n"
    
    def __repr__(self):
        return f"ClassVarDec: {self.kind} {self.varType} {self.varName}\n"

    def write(self, context: Context) -> None:
        context.classSymbolTable.add(self.varName, self.varType, self.kind)

class Class(Structure):
    def __init__(self, className: str, varDec: List[ClassVarDec], subroutineDec: List[SubroutineDec]) -> None:
        super().__init__()
        self.className = className
        self.varDec = varDec
        self.subroutineDec = subroutineDec

    def __str__(self):
        return f"Class: {self.className}\n{str(self.varDec)}\n{str(self.subroutineDec)}"

    def __repr__(self):
        return f"Class: {self.className}\n{str(self.varDec)}\n{str(self.subroutineDec)}"

    def write(self, writer: Writer):
        context = Context(self.className, writer)
        for varDec in self.varDec:
            varDec.write(context)
        for subroutineDec in self.subroutineDec:
            subroutineDec.write(context)
        context.classSymbolTable.clear()
