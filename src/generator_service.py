##Pessoa 3 (gerador de código)

from src.models import (
    Programa, Bloco, Declaracao, Atribuicao, Leitura, 
    Escrita, IfStmt, WhileStmt, ForStmt, BinOp, Literal, Variavel
)

class PythonGenerator:
    def __init__(self):
        self.indent_level = 0

    def _indent(self):
        return "    " * self.indent_level

    def generate(self, node) -> str:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Método visit_{type(node).__name__} não implementado.")

    def visit_Programa(self, node: Programa):
        return self.generate(node.bloco)

    def visit_Bloco(self, node: Bloco):
        lines = []
        for comando in node.comandos:
            if isinstance(comando, Declaracao):
                continue
            lines.append(f"{self._indent()}{self.generate(comando)}")
        
        if not lines:
            return f"{self._indent()}pass"
        return "\n".join(lines)

    def visit_Atribuicao(self, node: Atribuicao):
        return f"{node.id} = {self.generate(node.expr)}"

    def visit_Leitura(self, node: Leitura):
        return f"{node.id} = input()"

    def visit_Escrita(self, node: Escrita):
        return f"print({self.generate(node.expr)})"

    def visit_IfStmt(self, node: IfStmt):
        result = f"if {self.generate(node.condicao)}:\n"
        self.indent_level += 1
        result += self.generate(node.bloco_entao)
        self.indent_level -= 1
        
        if node.bloco_aliter:
            result += f"\n{self._indent()}else:\n"
            self.indent_level += 1
            result += self.generate(node.bloco_aliter)
            self.indent_level -= 1
        return result

    def visit_WhileStmt(self, node: WhileStmt):
        result = f"while {self.generate(node.condicao)}:\n"
        self.indent_level += 1
        result += self.generate(node.bloco)
        self.indent_level -= 1
        return result

    def visit_ForStmt(self, node: ForStmt):
        inicio = self.generate(node.inicio) if hasattr(node, 'inicio') else "0"
        fim = self.generate(node.fim) if hasattr(node, 'fim') else "5"
        
        result = f"for {node.id} in range({inicio}, {fim}):\n"
        self.indent_level += 1
        result += self.generate(node.bloco)
        self.indent_level -= 1
        return result

    def visit_BinOp(self, node: BinOp):
        return f"({self.generate(node.esquerda)} {node.operador} {self.generate(node.direita)})"

    def visit_Literal(self, node: Literal):
        if isinstance(node.valor, bool):
            return "True" if node.valor else "False"
        if isinstance(node.valor, str):
            return f'"{node.valor}"' if not (node.valor.startswith('"') or node.valor.startswith("'")) else node.valor
        return str(node.valor)

    def visit_Variavel(self, node: Variavel):
        return node.nome