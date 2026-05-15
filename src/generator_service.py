##Pessoa 3 (gerador de código)

from src.models import (
    Programa, Bloco, Declaracao, Atribuicao, Leitura, 
    Escrita, IfStmt, WhileStmt, ForStmt, BinOp, Literal, Variavel,DoWhileStmt
)

class PythonGenerator:
    def __init__(self):
        self.indent_level = 0

    def _indent(self):
        # Retorna 4 espaços multiplicados pelo nível atual
        return "    " * self.indent_level

    def generate(self, node) -> str:
        # Chama o método de visita baseado no nome da classe do nó
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Método visit_{type(node).__name__} não implementado.")

    def visit_Programa(self, node: Programa):
        # O programa começa processando o bloco principal
        return self.generate(node.bloco)
   
    def visit_Bloco(self, node: Bloco):
        lines = []
        for comando in node.comandos:
            # Pula declarações, pois Python usa tipagem dinâmica
            if isinstance(comando, Declaracao):
                continue
            code = self.generate(comando)
            lines.append(f"{self._indent()}{code}")
        
       # Se o bloco estiver vazio (ex: um 'if' sem nada), retorna 'pass'
        return "\n".join(lines) if lines else f"{self._indent()}pass"

    def visit_Atribuicao(self, node: Atribuicao):
        return f"{node.id} = {self.generate(node.expr)}"

    def visit_Leitura(self, node: Leitura):
        # Converte 'lege' para 'input'
        return f"{node.id} = input()"

    def visit_Escrita(self, node: Escrita):
        # Converte 'scribe' para 'print'
        return f"print({self.generate(node.expr)})"
    
    def visit_Nulo(self, node):
        return "None"
    
    def visit_Lista(self, node):
        elementos = [self.generate(e) for e in node.elementos]
        return "[" + ", ".join(elementos) + "]"
    
    def visit_IfStmt(self, node: IfStmt):
        # Estrutura: if condicao:
        condicao = self.generate(node.condicao)
        resultado = f"if {condicao}:\n"
        self.indent_level += 1
        resultado += self.generate(node.bloco_entao)
        self.indent_level -= 1
        
        if node.bloco_aliter:
            resultado += f"\n{self._indent()}else:\n"
            self.indent_level += 1
            resultado += self.generate(node.bloco_aliter)
            self.indent_level -= 1
        return resultado

    def visit_WhileStmt(self, node: WhileStmt):
        condicao = self.generate(node.condicao)
        resultado = f"while {condicao}:\n"
        self.indent_level += 1
        resultado += self.generate(node.bloco)
        self.indent_level -= 1
        return resultado

    def visit_ForStmt(self, node: ForStmt):
        inicio = self.generate(node.inicio) if hasattr(node, 'inicio') else "0"
        fim = self.generate(node.fim) if hasattr(node, 'fim') else "5"
        
        resultado = f"for {node.id} in range({inicio}, {fim}):\n"
        self.indent_level += 1
        resultado += self.generate(node.bloco)
        self.indent_level -= 1
        return resultado
    
    def visit_DoWhileStmt(self, node:DoWhileStmt):
        resultado = "while True:\n"
        
        self.indent_level += 1
        corpo_bloco = self.generate(node.bloco)
        resultado += corpo_bloco + '\n'
        
        condicao = self.generate(node.condicao)
        resultado += f"{self._indent()}if not ({condicao}):\n"
        
        self.indent_level += 1
        resultado += f"{self._indent()}break"
        
        self.indent_level -= 2
        return resultado
        
    def visit_BinOp(self, node: BinOp):
        # Garante a precedência usando parênteses na saída
        return f"({self.generate(node.esquerda)} {node.operador} {self.generate(node.direita)})"

    def visit_Literal(self, node: Literal):
        if isinstance(node.valor, bool):
            return "True" if node.valor else "False"
        if isinstance(node.valor, str):
            return f'"{node.valor}"' if not (node.valor.startswith('"') or node.valor.startswith("'")) else node.valor
        return str(node.valor)

    def visit_Variavel(self, node: Variavel):
        return node.nome