from lark import Lark, Transformer, v_args
from .models import *

from lark import Lark, Transformer, v_args
from .models import *

class LatinTransformer(Transformer):
    def programa(self, items):
        return Programa(items[0])

    def bloco(self, items):
        return Bloco(items)

    def declaracao(self, items):
        tipo = str(items[0])
        ids = [str(i) for i in items[1:]]
        return Declaracao(tipo, ids)

    def atribuicao(self, items):
        return Atribuicao(str(items[0]), items[1])

    def cmd_leitura(self, items):
        return Leitura(str(items[0]))

    def cmd_escrita(self, items):
        return Escrita(items[0])

    def cmd_if(self, items):
        condicao = items[0]
        bloco_entao = items[1]
        bloco_aliter = items[2] if len(items) > 2 else None
        return IfStmt(condicao, bloco_entao, bloco_aliter)

    def cmd_while(self, items):
        return WhileStmt(items[0], items[1])

    def cmd_for(self, items):
        return ForStmt(str(items[0]), items[1], items[2], items[3])

    def expr_relacional(self, items):
        if len(items) == 1:
            return items[0]
        else:
            return BinOp(items[0], str(items[1]), items[2])

    def OP_SOMA(self, token): return str(token)
    def OP_MULT(self, token): return str(token)
    
    def expr(self, items):
        res = items[0]
        for i in range(1, len(items), 2):
            res = BinOp(res, str(items[i]), items[i+1])
        return res

    def termo(self, items):
        res = items[0]
        for i in range(1, len(items), 2):
            res = BinOp(res, str(items[i]), items[i+1])
        return res

    def numero_inteiro(self, items):
        return Literal(int(items[0]))

    def numero_decimal(self, items):
        return Literal(float(items[0]))

    def texto(self, items):
        val = str(items[0])[1:-1]
        return Literal(val)

    def booleano(self, items):
        val = str(items[0]).lower() == "verum"
        return Literal(val)

    def variavel(self, items):
        return Variavel(str(items[0]))

def get_parser():
    with open("src/grammar.lark", "r") as f:
        grammar = f.read()
    return Lark(grammar, start='programa', parser='lalr', transformer=LatinTransformer(), maybe_placeholders=False, propagate_positions=True)
